import sys
import os

# Add backend directory to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.security import hash_password

def reset_admin():
    db: Session = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@servicedesk.com").first()
        if admin:
            print(f"Resetting password for admin: {admin.email}")
            admin.password = hash_password("admin")
            db.commit()
            print("Admin password reset complete! 🔑")
        else:
            print("Admin user not found.")
        
    except Exception as e:
        print(f"Error during reset: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin()
