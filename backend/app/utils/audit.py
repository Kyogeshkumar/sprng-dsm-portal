from sqlalchemy.orm import Session
from ..schemas import AuditLog

def log_action(db: Session, user_id: int, action: str, details: dict = None):
    """
    Log user actions to audit_logs table.
    """
    db_log = AuditLog(user_id
