"""
Telegram Bot Integration (aiogram 3.x)

Функциональность:
- /start — приветствие
- /login email password — привязка аккаунта агента к Telegram
- /status — проверка статуса последней заявки клиента
- /mytickets — показать все открытые заявки
- Свободный текст — создание новой заявки
- Reply на сообщение бота — ответ агента в тикете (добавление комментария)
"""
import os
import asyncio
from typing import Optional
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import SessionLocal
from app.models import (
    User, Ticket, TicketStatus, Tenant, UserRole, 
    TimelineEventType, TicketTimeline
)
from app.security import verify_password, hash_password
from app.services.routing_service import find_best_agent
from app.sla import calculate_sla_due_date
from app.config import settings
import structlog

logger = structlog.get_logger()

# Initialize bot
token = settings.TELEGRAM_BOT_TOKEN or os.getenv("TELEGRAM_BOT_TOKEN")
if token:
    default_props = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=token, default=default_props)
    dp = Dispatcher()
else:
    print("⚠️  TELEGRAM_BOT_TOKEN not set — Telegram bot disabled.")
    bot = None
    dp = None


# ─────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────

def get_default_tenant(db: Session) -> Optional[Tenant]:
    """Get default tenant for Telegram users."""
    tenant = db.query(Tenant).filter(Tenant.slug == "novum").first()
    if not tenant:
        tenant = db.query(Tenant).first()
    return tenant


def get_or_create_client(chat_id: str, full_name: str, username: str) -> int:
    """Returns User ID for Telegram client, creates if doesn't exist."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_chat_id == chat_id).first()
        if user:
            return user.id
            
        tenant = get_default_tenant(db)
        if not tenant:
            tenant = Tenant(name="Novum Tech", slug="novum", domain="novumtech.uz", is_active=True)
            db.add(tenant)
            db.commit()
            db.refresh(tenant)

        email = f"tg_{chat_id}@telegram.local"
        new_user = User(
            tenant_id=tenant.id,
            email=email,
            password=hash_password("tg_user_no_login"),
            full_name=full_name or username or f"TG User {chat_id}",
            role=UserRole.CLIENT,
            telegram_chat_id=chat_id
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info("tg_user_created", user_id=new_user.id, chat_id=chat_id)
        return new_user.id
    finally:
        db.close()


def get_user_by_chat_id(db: Session, chat_id: str) -> Optional[User]:
    """Find user by Telegram chat_id."""
    return db.query(User).filter(User.telegram_chat_id == chat_id).first()


# ─────────────────────────────────────────────
# Notification Functions (called from other parts of the app)
# ─────────────────────────────────────────────

async def notify_agent_new_ticket(agent_id: int, ticket_id: int, readable_id: int, title: str, client_name: str = None):
    """Send notification to agent about new ticket assignment via Telegram."""
    if not bot:
        return
    
    db = SessionLocal()
    try:
        agent = db.query(User).filter(User.id == agent_id).first()
        if not agent or not agent.telegram_chat_id:
            return
        
        msg = f"🔔 <b>Новая заявка #{readable_id}</b>\n\n"
        msg += f"<b>Тема:</b> {title}\n"
        if client_name:
            msg += f"<b>Клиент:</b> {client_name}\n"
        msg += f"<b>Статус:</b> Назначено вам.\n\n"
        msg += f"Ответьте на это сообщение чтобы добавить комментарий."
        
        await bot.send_message(chat_id=agent.telegram_chat_id, text=msg)
        logger.info("tg_agent_notified", agent_id=agent_id, ticket_id=ticket_id)
    except Exception as e:
        logger.error("tg_notify_agent_error", error=str(e), agent_id=agent_id)
    finally:
        db.close()


async def notify_agent_new_comment(agent_id: int, ticket_readable_id: int, commenter_name: str, comment_text: str):
    """Notify agent of a new comment on their assigned ticket."""
    if not bot:
        return
    
    db = SessionLocal()
    try:
        agent = db.query(User).filter(User.id == agent_id).first()
        if not agent or not agent.telegram_chat_id:
            return
        
        msg = f"💬 <b>Новый комментарий в заявке #{ticket_readable_id}</b>\n\n"
        msg += f"<b>От:</b> {commenter_name}\n"
        msg += f"<b>Текст:</b> {comment_text[:300]}"
        
        await bot.send_message(chat_id=agent.telegram_chat_id, text=msg)
    except Exception as e:
        logger.error("tg_notify_comment_error", error=str(e))
    finally:
        db.close()


async def notify_client_status_change(ticket_id: int, new_status_name: str):
    """Notify client via Telegram that ticket status changed."""
    if not bot:
        return
    
    db = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return
        
        creator = db.query(User).filter(User.id == ticket.created_by).first()
        if not creator or not creator.telegram_chat_id:
            return
        
        msg = f"📋 <b>Обновление заявки #{ticket.readable_id}</b>\n\n"
        msg += f"<b>Тема:</b> {ticket.title}\n"
        msg += f"<b>Новый статус:</b> {new_status_name}\n"
        
        await bot.send_message(chat_id=creator.telegram_chat_id, text=msg)
    except Exception as e:
        logger.error("tg_notify_client_error", error=str(e))
    finally:
        db.close()


async def notify_client_new_reply(ticket_id: int, agent_name: str, reply_text: str):
    """Notify client via Telegram that agent replied to their ticket."""
    if not bot:
        return
    
    db = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return
        
        creator = db.query(User).filter(User.id == ticket.created_by).first()
        if not creator or not creator.telegram_chat_id:
            return
        
        msg = f"💬 <b>Ответ по заявке #{ticket.readable_id}</b>\n\n"
        msg += f"<b>Агент:</b> {agent_name}\n"
        msg += f"<b>Ответ:</b> {reply_text[:500]}\n"
        
        await bot.send_message(chat_id=creator.telegram_chat_id, text=msg)
    except Exception as e:
        logger.error("tg_notify_client_reply_error", error=str(e))
    finally:
        db.close()


# ─────────────────────────────────────────────
# Bot Handlers
# ─────────────────────────────────────────────

if dp:

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer(
            "Здравствуйте! 👋\n\n"
            "Я — бот Service Desk от <b>Novum Tech</b>.\n\n"
            "📝 <b>Создать заявку:</b> Просто напишите описание проблемы.\n"
            "📊 <b>Статус заявки:</b> /status\n"
            "📋 <b>Мои заявки:</b> /mytickets\n\n"
            "Если вы <b>агент поддержки</b>, отправьте:\n"
            "<code>/login ваш_email ваш_пароль</code>\n"
            "для получения уведомлений."
        )

    @dp.message(Command("login"))
    async def cmd_login(message: types.Message):
        parts = message.text.split()
        if len(parts) != 3:
            await message.answer("❌ Формат: <code>/login email пароль</code>")
            return
            
        email_addr = parts[1]
        password = parts[2]
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email_addr).first()
            if not user or not verify_password(password, user.password):
                await message.answer("❌ Неверный email или пароль.")
                return
                
            if user.role not in [UserRole.AGENT, UserRole.ADMIN]:
                await message.answer("⚠️ Эта команда только для агентов и администраторов.")
                return
                
            user.telegram_chat_id = str(message.chat.id)
            db.commit()
            
            await message.answer(
                f"✅ Добро пожаловать, <b>{user.full_name}</b>!\n\n"
                f"Теперь вы будете получать уведомления о новых заявках в этот чат.\n"
                f"Ответьте на сообщение о заявке, чтобы добавить комментарий."
            )
            
            # Delete the message with password for security
            try:
                await message.delete()
            except Exception:
                pass
                
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
        finally:
            db.close()

    @dp.message(Command("status"))
    async def cmd_status(message: types.Message):
        """Show status of user's latest ticket."""
        chat_id = str(message.chat.id)
        
        db = SessionLocal()
        try:
            user = get_user_by_chat_id(db, chat_id)
            if not user:
                await message.answer("❌ Вы ещё не подавали заявок. Просто напишите описание проблемы!")
                return
            
            # Get latest ticket
            ticket = db.query(Ticket).filter(
                Ticket.created_by == user.id
            ).order_by(desc(Ticket.created_at)).first()
            
            if not ticket:
                await message.answer("📭 У вас пока нет заявок. Напишите описание проблемы для создания.")
                return
            
            status = db.query(TicketStatus).filter(TicketStatus.id == ticket.status_id).first()
            status_name = status.name if status else "Неизвестен"
            
            assignee = None
            if ticket.assigned_to:
                assignee = db.query(User).filter(User.id == ticket.assigned_to).first()
            
            msg = f"📋 <b>Заявка #{ticket.readable_id}</b>\n\n"
            msg += f"<b>Тема:</b> {ticket.title}\n"
            msg += f"<b>Статус:</b> {status_name}\n"
            msg += f"<b>Приоритет:</b> {ticket.priority}\n"
            if assignee:
                msg += f"<b>Назначен:</b> {assignee.full_name or assignee.email}\n"
            if ticket.created_at:
                msg += f"<b>Создан:</b> {ticket.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            
            await message.answer(msg)
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
        finally:
            db.close()

    @dp.message(Command("mytickets"))
    async def cmd_mytickets(message: types.Message):
        """Show all open tickets for the user."""
        chat_id = str(message.chat.id)
        
        db = SessionLocal()
        try:
            user = get_user_by_chat_id(db, chat_id)
            if not user:
                await message.answer("❌ Вы ещё не подавали заявок.")
                return
            
            # Determine query based on role
            if user.role in [UserRole.AGENT, UserRole.ADMIN]:
                # Show assigned tickets
                tickets = db.query(Ticket).filter(
                    Ticket.assigned_to == user.id,
                    Ticket.tenant_id == user.tenant_id
                ).join(TicketStatus).filter(
                    TicketStatus.is_final == False
                ).order_by(desc(Ticket.created_at)).limit(10).all()
                header = "📋 <b>Ваши назначенные заявки:</b>\n\n"
            else:
                # Show created tickets
                tickets = db.query(Ticket).filter(
                    Ticket.created_by == user.id
                ).order_by(desc(Ticket.created_at)).limit(10).all()
                header = "📋 <b>Ваши заявки:</b>\n\n"
            
            if not tickets:
                await message.answer("📭 Нет открытых заявок.")
                return
            
            msg = header
            for t in tickets:
                status = db.query(TicketStatus).filter(TicketStatus.id == t.status_id).first()
                status_name = status.name if status else "?"
                priority_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(t.priority, "⚪")
                msg += f"{priority_emoji} <b>#{t.readable_id}</b> — {t.title[:40]}\n"
                msg += f"    Статус: {status_name}\n\n"
            
            await message.answer(msg)
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
        finally:
            db.close()

    @dp.message(F.reply_to_message & F.text & ~F.text.startswith('/'))
    async def handle_reply(message: types.Message):
        """
        Handle reply to bot's ticket notification.
        If the replied message contains ticket #ID, add comment to that ticket.
        """
        chat_id = str(message.chat.id)
        reply_text = message.reply_to_message.text or ""
        
        # Try to find ticket ID in the original message
        import re
        match = re.search(r'#(\d+)', reply_text)
        if not match:
            await message.answer("⚠️ Не удалось определить номер заявки. Ответьте на сообщение с номером заявки.")
            return
        
        readable_id = int(match.group(1))
        
        db = SessionLocal()
        try:
            user = get_user_by_chat_id(db, chat_id)
            if not user:
                await message.answer("❌ Ваш аккаунт не найден. Отправьте /start для начала.")
                return
            
            tenant = get_default_tenant(db)
            ticket = db.query(Ticket).filter(
                Ticket.readable_id == readable_id,
                Ticket.tenant_id == tenant.id if tenant else True
            ).first()
            
            if not ticket:
                await message.answer(f"❌ Заявка #{readable_id} не найдена.")
                return
            
            # Determine if internal note or public comment
            is_agent = user.role in [UserRole.AGENT, UserRole.ADMIN]
            is_internal = False  # Public by default
            
            comment_text = message.text
            if comment_text.startswith("!"):
                # Agent internal note: starts with !
                is_internal = True
                comment_text = comment_text[1:].strip()
            
            # Add timeline event
            event = TicketTimeline(
                ticket_id=ticket.id,
                user_id=user.id,
                event_type=TimelineEventType.COMMENT,
                content=comment_text,
                is_internal=is_internal
            )
            db.add(event)
            db.commit()
            
            if is_internal:
                await message.answer(f"📝 Внутренняя заметка добавлена к заявке #{readable_id}.")
            else:
                await message.answer(f"✅ Комментарий добавлен к заявке #{readable_id}.")
                
                # Notify the other party
                if is_agent and ticket.created_by:
                    # Agent replied → notify client
                    await notify_client_new_reply(
                        ticket.id, 
                        user.full_name or user.email,
                        comment_text
                    )
                elif not is_agent and ticket.assigned_to:
                    # Client replied → notify agent
                    await notify_agent_new_comment(
                        ticket.assigned_to,
                        ticket.readable_id,
                        user.full_name or user.email,
                        comment_text
                    )
            
            logger.info("tg_comment_added", ticket_id=ticket.id, user_id=user.id, is_internal=is_internal)
            
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
            logger.error("tg_reply_error", error=str(e))
        finally:
            db.close()

    @dp.message(F.text & ~F.text.startswith('/'))
    async def process_ticket_message(message: types.Message):
        """Handle free text — create a new ticket."""
        chat_id = str(message.chat.id)
        text = message.text
        
        # Get or create Client user
        client_id = get_or_create_client(
            chat_id=chat_id,
            full_name=message.from_user.full_name,
            username=message.from_user.username
        )
        
        db = SessionLocal()
        try:
            client = db.query(User).filter(User.id == client_id).first()
            tenant = get_default_tenant(db)
            
            if not tenant:
                await message.answer("❌ Система не настроена. Обратитесь к администратору.")
                return
            
            status = db.query(TicketStatus).filter(
                TicketStatus.tenant_id == tenant.id,
                TicketStatus.order == 1
            ).first()
            
            if not status:
                status = db.query(TicketStatus).filter(
                    TicketStatus.tenant_id == tenant.id
                ).first()
            
            if not status:
                await message.answer("❌ Статусы не настроены. Обратитесь к администратору.")
                return
            
            # Readable ID
            last_ticket = db.query(Ticket).filter(
                Ticket.tenant_id == tenant.id
            ).order_by(desc(Ticket.readable_id)).first()
            readable_id = (last_ticket.readable_id + 1) if last_ticket else 1000
            
            # Auto-routing using improved service
            assigned_to = find_best_agent(db, tenant.id)
            
            # SLA
            sla_due = calculate_sla_due_date("medium")
            
            # Create Ticket
            title = text[:50] + "..." if len(text) > 50 else text
            ticket = Ticket(
                tenant_id=tenant.id,
                readable_id=readable_id,
                title=title,
                description=text,
                status_id=status.id,
                priority="medium",
                created_by=client.id,
                company_id=client.company_id,
                assigned_to=assigned_to,
                sla_due_at=sla_due
            )
            db.add(ticket)
            db.commit()
            db.refresh(ticket)
            
            # Timeline Event
            event = TicketTimeline(
                ticket_id=ticket.id,
                user_id=client.id,
                event_type=TimelineEventType.create,
                content=text
            )
            db.add(event)
            db.commit()
            
            await message.answer(
                f"✅ <b>Заявка #{ticket.readable_id} создана!</b>\n\n"
                f"Наш специалист скоро свяжется с вами.\n"
                f"Проверьте статус: /status"
            )
            
            # Notify assigned agent
            if assigned_to:
                await notify_agent_new_ticket(
                    agent_id=assigned_to,
                    ticket_id=ticket.id,
                    readable_id=ticket.readable_id,
                    title=title,
                    client_name=client.full_name
                )
            
            logger.info("tg_ticket_created", 
                        ticket_id=ticket.id, 
                        readable_id=readable_id,
                        assigned_to=assigned_to)
                
        except Exception as e:
            await message.answer("❌ Произошла ошибка при создании заявки. Попробуйте позже.")
            logger.error("tg_create_ticket_error", error=str(e))
        finally:
            db.close()


async def start_polling():
    """Start Telegram bot polling."""
    if bot and dp:
        print("🤖 Starting Telegram Bot Polling...")
        try:
            await dp.start_polling(bot)
        except Exception as e:
            print(f"Telegram Bot Error: {e}")
    else:
        print("⚠️  Telegram Bot not started (token missing)")
