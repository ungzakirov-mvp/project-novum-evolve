from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import AuditLog, User, UserRole
from app.dependencies import get_current_user
from app import schemas

router = APIRouter(prefix="/admin/audit", tags=["Audit Log"])

@router.get("/logs", response_model=List[schemas.AuditLogResponse])
def get_audit_logs(
    action: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    target_type: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение журнала аудита (только для администраторов)
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Недостаточно прав для просмотра аудита")

    query = db.query(AuditLog).filter(AuditLog.tenant_id == current_user.tenant_id)

    if action:
        query = query.filter(AuditLog.action == action)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if target_type:
        query = query.filter(AuditLog.target_type == target_type)

    return query.order_by(AuditLog.created_at.desc()).limit(limit).all()
