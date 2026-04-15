from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Notification
from app.dependencies import get_current_user
from app.services.websocket_manager import manager
from app import schemas

router = APIRouter(prefix="/notifications", tags=["Уведомления"])

@router.get("/", response_model=List[schemas.NotificationResponse])
def get_notifications(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active notifications for current user"""
    notifs = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).limit(limit).all()
    return notifs

@router.post("/{notif_id}/read")
def mark_read(
    notif_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notif = db.query(Notification).filter(
        Notification.id == notif_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notif:
        raise HTTPException(404, "Notification not found")
        
    notif.is_read = True
    db.commit()
    return {"status": "ok"}

@router.post("/read-all")
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"status": "ok"}

async def broadcast_notification(db: Session, user_id: int, tenant_id: int, title: str, content: str):
    """Utility to create and broadcast a notification"""
    new_notif = Notification(
        user_id=user_id,
        tenant_id=tenant_id,
        title=title,
        content=content
    )
    db.add(new_notif)
    db.commit()
    
    await manager.send_personal_message({
        "type": "NEW_NOTIFICATION",
        "message": title,
        "content": content
    }, user_id=user_id, tenant_id=tenant_id)
