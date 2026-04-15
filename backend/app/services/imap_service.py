"""
IMAP Email Parsing Service
Периодически проверяет почтовый ящик на новые письма и создает тикеты.
"""
import imaplib
import email
from email.header import decode_header
from email.utils import parseaddr
import asyncio
import re
from typing import Optional, Tuple
import structlog

from app.config import settings
from app.database import SessionLocal
from app.models import User, Ticket, TicketStatus, Tenant, TicketTimeline, TimelineEventType, UserRole, Company
from app.security import hash_password
from app.services.routing_service import find_best_agent
from app.sla import calculate_sla_due_date

logger = structlog.get_logger()


def decode_mime_header(header_value: str) -> str:
    """Decode MIME-encoded email header."""
    if not header_value:
        return ""
    decoded_parts = decode_header(header_value)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(part)
    return " ".join(result)


def extract_email_body(msg) -> str:
    """Extract plain text body from email message."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            
            # Skip attachments
            if "attachment" in content_disposition:
                continue
                
            if content_type == "text/plain":
                charset = part.get_content_charset() or "utf-8"
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode(charset, errors="replace")
                    break
            elif content_type == "text/html" and not body:
                charset = part.get_content_charset() or "utf-8"
                payload = part.get_payload(decode=True)
                if payload:
                    html = payload.decode(charset, errors="replace")
                    # Simple HTML to text: strip tags
                    body = re.sub(r'<[^>]+>', '', html)
                    body = re.sub(r'\s+', ' ', body).strip()
    else:
        charset = msg.get_content_charset() or "utf-8"
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(charset, errors="replace")
    
    return body.strip()


def detect_reply_ticket_id(subject: str) -> Optional[int]:
    """
    Detect if email is a reply to existing ticket.
    Looks for patterns like: Re: [#1234] Original Subject
    """
    match = re.search(r'\[#(\d+)\]', subject)
    if match:
        return int(match.group(1))
    return None


def get_or_create_email_user(db, email_addr: str, sender_name: str, tenant) -> User:
    """Find existing user by email or create a new Client user."""
    user = db.query(User).filter(User.email == email_addr).first()
    if user:
        return user
    
    # CRM: Try to match company by email domain
    company_id = None
    domain = email_addr.split('@')[-1].lower() if '@' in email_addr else None
    
    # Skip common public domains to avoid grouping everyone into 'Gmail'
    public_domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'icloud.com', 'mail.ru', 'yandex.ru']
    
    if domain and domain not in public_domains:
        company = db.query(Company).filter(
            Company.tenant_id == tenant.id,
            Company.domain == domain
        ).first()
        if company:
            company_id = company.id
            logger.info("crm_matched_company_by_domain", domain=domain, company_id=company_id)
    
    # Create new Client
    new_user = User(
        tenant_id=tenant.id,
        email=email_addr,
        password=hash_password("email_user_temp_pass"),
        full_name=sender_name or email_addr.split('@')[0],
        role=UserRole.CLIENT,
        company_id=company_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info("user_created_via_email", user_id=new_user.id, email=email_addr, company_id=company_id)
    return new_user


def process_single_email(db, email_from: str, sender_name: str, subject: str, body: str):
    """Process a single inbound email: create ticket or add reply."""
    
    # Resolve Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == "novum").first()
    if not tenant:
        tenant = db.query(Tenant).first()
    if not tenant:
        logger.error("imap_no_tenant_configured")
        return
    
    # Get/Create the user
    user = get_or_create_email_user(db, email_from, sender_name, tenant)
    
    # Check if this is a reply to existing ticket
    reply_ticket_id = detect_reply_ticket_id(subject)
    
    if reply_ticket_id:
        # Add comment to existing ticket
        ticket = db.query(Ticket).filter(
            Ticket.readable_id == reply_ticket_id,
            Ticket.tenant_id == tenant.id
        ).first()
        
        if ticket:
            timeline = TicketTimeline(
                ticket_id=ticket.id,
                user_id=user.id,
                event_type=TimelineEventType.COMMENT,
                content=body
            )
            db.add(timeline)
            db.commit()
            logger.info("email_reply_added", ticket_id=ticket.id, user=email_from)
            return ticket
    
    # Create new ticket
    default_status = db.query(TicketStatus).filter(
        TicketStatus.tenant_id == tenant.id,
        TicketStatus.order == 1
    ).first()
    
    if not default_status:
        default_status = db.query(TicketStatus).filter(
            TicketStatus.tenant_id == tenant.id
        ).first()
    
    # Calculate readable ID
    from sqlalchemy import desc
    last_ticket = db.query(Ticket).filter(
        Ticket.tenant_id == tenant.id
    ).order_by(desc(Ticket.readable_id)).first()
    next_id = (last_ticket.readable_id + 1) if last_ticket else 1000
    
    # Auto-routing
    assigned_agent_id = find_best_agent(db, tenant.id)
    
    # SLA
    sla_due = calculate_sla_due_date("medium")
    
    # Clean subject (remove Re:, Fwd: prefixes)
    clean_subject = re.sub(r'^(Re|Fwd|FW|RE):\s*', '', subject).strip()
    if not clean_subject:
        clean_subject = "Заявка по Email"
    
    ticket = Ticket(
        tenant_id=tenant.id,
        readable_id=next_id,
        title=clean_subject[:200],
        description=body,
        priority="medium",
        status_id=default_status.id,
        created_by=user.id,
        assigned_to=assigned_agent_id,
        company_id=user.company_id,
        sla_due_at=sla_due
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    # Timeline event
    timeline = TicketTimeline(
        ticket_id=ticket.id,
        user_id=user.id,
        event_type=TimelineEventType.create,
        content=f"Тикет создан через Email от {email_from}"
    )
    db.add(timeline)
    db.commit()
    
    logger.info("ticket_created_via_email", 
                ticket_id=ticket.id, 
                readable_id=next_id,
                from_email=email_from,
                assigned_to=assigned_agent_id)
    
    return ticket


def check_imap_mailbox():
    """
    Connect to IMAP server, fetch unread emails, process them, mark as read.
    This is a synchronous function that runs in a thread.
    """
    if not all([settings.IMAP_HOST, settings.IMAP_USER, settings.IMAP_PASSWORD]):
        return []
    
    processed = []
    mail = None
    
    try:
        # Connect
        if settings.IMAP_USE_SSL:
            mail = imaplib.IMAP4_SSL(settings.IMAP_HOST, settings.IMAP_PORT)
        else:
            mail = imaplib.IMAP4(settings.IMAP_HOST, settings.IMAP_PORT)
        
        mail.login(settings.IMAP_USER, settings.IMAP_PASSWORD)
        mail.select(settings.IMAP_FOLDER)
        
        # Search for unread emails
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            logger.warning("imap_search_failed", status=status)
            return []
        
        email_ids = messages[0].split()
        if not email_ids:
            return []
        
        logger.info("imap_found_emails", count=len(email_ids))
        
        db = SessionLocal()
        try:
            for email_id in email_ids:
                try:
                    # Fetch the email
                    status, msg_data = mail.fetch(email_id, "(RFC822)")
                    if status != "OK":
                        continue
                    
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    # Parse headers
                    subject = decode_mime_header(msg.get("Subject", "Без темы"))
                    from_header = msg.get("From", "")
                    sender_name, sender_email = parseaddr(from_header)
                    sender_name = decode_mime_header(sender_name)
                    
                    # Skip own emails (avoid loops)
                    if sender_email == settings.IMAP_USER:
                        continue
                    
                    # Extract body
                    body = extract_email_body(msg)
                    if not body:
                        body = "(Пустое письмо)"
                    
                    # Process
                    ticket = process_single_email(db, sender_email, sender_name, subject, body)
                    if ticket:
                        processed.append(ticket.id)
                    
                    # Mark as read (SEEN)
                    mail.store(email_id, '+FLAGS', '\\Seen')
                    
                except Exception as e:
                    logger.error("imap_process_email_error", email_id=str(email_id), error=str(e))
                    continue
        finally:
            db.close()
        
    except Exception as e:
        logger.error("imap_connection_error", error=str(e))
    finally:
        if mail:
            try:
                mail.logout()
            except Exception:
                pass
    
    return processed


async def imap_polling_loop():
    """
    Async loop that periodically checks IMAP mailbox.
    Runs in the background as an asyncio task.
    """
    if not settings.IMAP_HOST:
        logger.info("imap_not_configured", message="IMAP_HOST not set, skipping email polling")
        return
    
    logger.info("imap_polling_started", 
                host=settings.IMAP_HOST, 
                user=settings.IMAP_USER,
                interval=settings.IMAP_CHECK_INTERVAL)
    
    while True:
        try:
            # Run synchronous IMAP check in a thread to not block event loop
            loop = asyncio.get_event_loop()
            processed = await loop.run_in_executor(None, check_imap_mailbox)
            
            if processed:
                logger.info("imap_processed_emails", count=len(processed), ticket_ids=processed)
                
        except asyncio.CancelledError:
            logger.info("imap_polling_stopped")
            break
        except Exception as e:
            logger.error("imap_polling_error", error=str(e))
        
        await asyncio.sleep(settings.IMAP_CHECK_INTERVAL)
