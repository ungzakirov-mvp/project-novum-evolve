from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Ticket, TimeEntry, User, UserRole
from app.dependencies import get_current_user
from app import schemas

router = APIRouter(prefix="/timetracking", tags=["Time Tracking"])

@router.post("/log", response_model=schemas.TimeEntryResponse, status_code=201)
def log_time(
    entry_in: schemas.TimeEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Логирование времени по тикету (только для агентов и админов)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    # Verify ticket belongs to tenant
    ticket = db.query(Ticket).filter(
        Ticket.id == entry_in.ticket_id,
        Ticket.tenant_id == current_user.tenant_id
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Тикет не найден")

    new_entry = TimeEntry(
        tenant_id=current_user.tenant_id,
        ticket_id=entry_in.ticket_id,
        user_id=current_user.id,
        minutes=entry_in.minutes,
        description=entry_in.description
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry

@router.get("/ticket/{ticket_id}", response_model=List[schemas.TimeEntryResponse])
def get_ticket_time_entries(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить все записи времени по тикету"""
    # Verify ticket belongs to tenant
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.tenant_id == current_user.tenant_id
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Тикет не найден")

    return db.query(TimeEntry).filter(TimeEntry.ticket_id == ticket_id).all()

@router.get("/ticket/{ticket_id}/total")
def get_ticket_total_time(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить общее время, затраченное на тикет (в минутах)"""
    # Verify ticket belongs to tenant
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.tenant_id == current_user.tenant_id
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Тикет не найден")

    entries = db.query(TimeEntry).filter(TimeEntry.ticket_id == ticket_id).all()
    total_minutes = sum(entry.minutes for entry in entries)
    
    return {
        "ticket_id": ticket_id,
        "total_minutes": total_minutes,
        "total_hours": round(total_minutes / 60, 2)
    }
