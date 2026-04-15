import sys
import os
sys.path.append(os.getcwd())

from app.database import SessionLocal, engine
from app.models import User, Base
from sqlalchemy import text

def check():
    print(f"Connecting to: {engine.url}")
    db = SessionLocal()
    try:
        # Check connection
        db.execute(text("SELECT 1"))
        print("Connection: OK")
        
        # Check table
        u = db.query(User).first()
        print(f"Schema check: OK. Found user: {u.email if u else 'None'}")
        
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check()
