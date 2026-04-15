import sys
import os
import time
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Ticket, TicketStatus, Notification, TicketTimeline, TimelineEventType, User

def check_sla_breaches():
    db: Session = SessionLocal()
    try:
        now = datetime.now()
        
        # 1. Find tickets that are OPEN (not resolved/closed) and SLA is passed
        # We need to know which statuses are "open".
        # For simplicity, we assume is_final=False means open.
        
        open_statuses = db.query(TicketStatus.id).filter(TicketStatus.is_final == False).all()
        open_status_ids = [s.id for s in open_statuses]
        
        breached_tickets = db.query(Ticket).filter(
            Ticket.status_id.in_(open_status_ids),
            Ticket.sla_due_at < now
        ).all()
        
        print(f"Checking SLA at {now}. Found {len(breached_tickets)} potential breaches.")
        
        for ticket in breached_tickets:
            # Check if already notified/escalated?
            # Implemented via simple check if last timeline event is SLA Breach
            # Real world: add 'is_sla_breached' column to Ticket
            
            last_event = db.query(TicketTimeline).filter(
                TicketTimeline.ticket_id == ticket.id,
                TicketTimeline.event_type == TimelineEventType.NOTE
            ).order_by(TicketTimeline.created_at.desc()).first()
            
            if last_event and "SLA Breached" in last_event.content:
                continue # Already marked
            
            print(f"Breach detected for Ticket #{ticket.readable_id}")
            
            # 1. Add Timeline Note
            timeline = TicketTimeline(
                ticket_id=ticket.id,
                user_id=ticket.created_by, # System? Using creator for now or need System User
                event_type=TimelineEventType.NOTE,
                content="⚠️ SLA Breached! Deadline exceeded.",
                is_internal=True
            )
            db.add(timeline)
            
            # 2. Notify Assignee or Admin
            target_user_id = ticket.assigned_to if ticket.assigned_to else ticket.created_by
            
            notif = Notification(
                tenant_id=ticket.tenant_id,
                user_id=target_user_id,
                title="SLA Breach Alert",
                message=f"Ticket #{ticket.readable_id} has exceeded its SLA deadline.",
                link=f"/agent.html?id={ticket.id}"
            )
            db.add(notif)
            
        db.commit()
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    while True:
        check_sla_breaches()
        time.sleep(60) # Check every minute
