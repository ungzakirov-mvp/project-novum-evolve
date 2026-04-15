import sys
import os

# Add backend directory to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Tenant, User, TicketStatus, UserRole
from app.security import hash_password

def seed():
    db: Session = SessionLocal()
    try:
        # 1. Create Default Tenant
        tenant = db.query(Tenant).filter(Tenant.slug == "demo").first()
        if not tenant:
            print("Creating Demo Tenant...")
            tenant = Tenant(
                name="Demo Company",
                slug="demo",
                domain="demo.localhost"
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
        
        # 2. Create Default Statuses
        statuses = [
            {"name": "Новый", "color": "#3B82F6", "order": 1, "is_final": False},
            {"name": "В работе", "color": "#F59E0B", "order": 2, "is_final": False},
            {"name": "Решён", "color": "#10B981", "order": 3, "is_final": True},
            {"name": "Закрыт", "color": "#6B7280", "order": 4, "is_final": True},
        ]
        
        for s_data in statuses:
            exists = db.query(TicketStatus).filter(
                TicketStatus.tenant_id == tenant.id, 
                TicketStatus.name == s_data["name"]
            ).first()
            if not exists:
                print(f"Creating Status: {s_data['name']}")
                status = TicketStatus(tenant_id=tenant.id, **s_data)
                db.add(status)
        
        db.commit()

        # 3. Create Super Admin
        admin_email = "admin@servicedesk.com"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            print("Creating Super Admin...")
            admin = User(
                email=admin_email,
                password=hash_password("admin"),
                full_name="System Administrator",
                role=UserRole.SUPER_ADMIN,
                tenant_id=tenant.id 
            )
            db.add(admin)
            db.commit()
            
        print("Seeding Complete! 🌱")
        
    except Exception as e:
        print(f"Error seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
