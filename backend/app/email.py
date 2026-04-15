import structlog
from app.config import settings

logger = structlog.get_logger()

async def send_email(to_email: str, subject: str, content: str):
    """
    Отправка email (Mock)
    
    В реальном продакшене здесь была бы интеграция с SMTP
    или сервисом рассылок (SendGrid, Mailgun).
    
    Args:
        to_email: Email получателя
        subject: Тема письма
        content: Текст письма
    """
    # Эмуляция отправки
    logger.info(
        "sending_email",
        to_email=to_email,
        subject=subject,
        content_preview=content[:50] + "..." if len(content) > 50 else content
    )
    
    # В будущем:
    # message = MessageSchema(
    #    subject=subject,
    #    recipients=[to_email],
    #    body=content,
    #    subtype="html"
    # )
    # await fast_mail.send_message(message)
    
    return True

async def send_new_ticket_notification(email: str, ticket_id: int, title: str):
    await send_email(
        to_email=email,
        subject=f"Тикет #{ticket_id} создан",
        content=f"Ваш тикет '{title}' успешно создан. Мы свяжемся с вами в ближайшее время."
    )

async def send_new_comment_notification(email: str, ticket_id: int, comment_text: str):
    await send_email(
        to_email=email,
        subject=f"Новый комментарий в тикете #{ticket_id}",
        content=f"Новый комментарий: {comment_text}"
    )
