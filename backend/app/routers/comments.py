from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Ticket, User, TicketTimeline, TimelineEventType, UserRole
from app.dependencies import get_current_user
from app.logger import log_business_event
from app.email import send_new_comment_notification
from app.telegram_bot import notify_agent_new_comment, notify_client_new_reply
from pydantic import BaseModel
from datetime import datetime
from app.services.websocket_manager import manager

router = APIRouter(prefix="/comments", tags=["Комментарии"])

# Define local schemas for compatibility or move to app.schemas if reused
class CommentCreate(BaseModel):
    ticket_id: int
    text: str
    is_internal: bool = False

class CommentResponse(BaseModel):
    id: int
    ticket_id: int
    text: str
    author_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/", response_model=CommentResponse)
async def create_comment(
    comment: CommentCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify ticket access
    ticket = db.query(Ticket).filter(
        Ticket.id == comment.ticket_id,
        Ticket.tenant_id == current_user.tenant_id
    ).first()
    
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    # Create Timeline Event
    timeline_event = TicketTimeline(
        ticket_id=ticket.id,
        user_id=current_user.id,
        event_type=TimelineEventType.COMMENT,
        content=comment.text,
        is_internal=comment.is_internal
    )
    
    db.add(timeline_event)
    db.commit()
    db.refresh(timeline_event)
    
    log_business_event("comment_created", ticket_id=ticket.id, user_id=current_user.id)
    
    # Telegram Notifications
    is_agent = current_user.role in [UserRole.AGENT, UserRole.ADMIN]
    if not comment.is_internal:
        if is_agent and ticket.created_by:
            # Agent replied → notify client via TG
            background_tasks.add_task(
                notify_client_new_reply,
                ticket.id,
                current_user.full_name or current_user.email,
                comment.text
            )
        elif not is_agent and ticket.assigned_to:
            # Client replied → notify agent via TG
            background_tasks.add_task(
                notify_agent_new_comment,
                ticket.assigned_to,
                ticket.readable_id,
                current_user.full_name or current_user.email,
                comment.text
            )
    
    # Real-time Broadcast
    await manager.broadcast_to_tenant({
        "type": "TICKET_COMMENT_ADDED",
        "data": {
            "id": timeline_event.id,
            "ticket_id": ticket.id,
            "text": timeline_event.content,
            "author_name": current_user.full_name or current_user.email,
            "is_internal": timeline_event.is_internal
        }
    }, tenant_id=ticket.tenant_id)

    return CommentResponse(
        id=timeline_event.id,
        ticket_id=ticket.id,
        text=timeline_event.content,
        author_name=current_user.full_name or current_user.email,
        created_at=timeline_event.created_at
    )

@router.get("/ticket/{ticket_id}", response_model=List[CommentResponse])
def get_comments(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.tenant_id == current_user.tenant_id
    ).first()
    
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    # Fetch comments from timeline
    events = db.query(TicketTimeline).filter(
        TicketTimeline.ticket_id == ticket.id,
        TicketTimeline.event_type == TimelineEventType.COMMENT
    ).order_by(TicketTimeline.created_at).all()
    
    return [
        CommentResponse(
            id=e.id,
            ticket_id=e.ticket_id,
            text=e.content,
            author_name=e.actor.full_name or e.actor.email,
            created_at=e.created_at
        )
        for e in events
    ]
