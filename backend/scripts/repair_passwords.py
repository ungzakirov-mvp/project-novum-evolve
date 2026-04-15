import sys
import os

# Add backend directory to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.security import hash_password

def repair():
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            # If password doesn't look like a hash (bcrypt hashes start with $)
            if not user.password.startswith('$'):
                print(f"Hashing password for user: {user.email}")
                user.password = hash_password(user.password)
            elif user.password.startswith('$2b$'):
                # Optional: convert $2b$ to $2a$ if passlib has issues, 
                # but usually it's better to just re-hash if suspicious.
                # For now, let's just leave bcrypt hashes as they are unless they fail.
                pass
        
        db.commit()
        print("Password repair complete! 🔑")
        
    except Exception as e:
        print(f"Error during repair: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    repair()
