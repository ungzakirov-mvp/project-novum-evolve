import logging
from datetime import datetime
from typing import Optional, Any
from sqlalchemy.orm import Session
from app.models import AuditLog
import json

logger = logging.getLogger(__name__)

class AuditService:
    @staticmethod
    def log(
        db: Session,
        tenant_id: int,
        action: str,
        user_id: Optional[int] = None,
        target_type: Optional[str] = None,
        target_id: Optional[int] = None,
        details: Optional[Any] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Запись события в журнал аудита
        """
        try:
            # Convert details to dict if it's a string, or keep as is if it's a dict
            if details and isinstance(details, str):
                try:
                    details = json.loads(details)
                except:
                    details = {"message": details}
            
            new_log = AuditLog(
                tenant_id=tenant_id,
                user_id=user_id,
                action=action,
                target_type=target_type,
                target_id=target_id,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.add(new_log)
            db.commit()
            
            logging.info(f"Audit Log recorded: {action} by user {user_id}")
            
        except Exception as e:
            logging.error(f"Failed to record audit log: {str(e)}")
            # We don't want to crash the main request if logging fails
            db.rollback()
