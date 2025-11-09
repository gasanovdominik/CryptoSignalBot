# backend/crud.py
from sqlalchemy.orm import Session
from . import models

def get_signals(db: Session):
    return db.query(models.Signal).all()

def create_signal(db: Session, data: dict):
    signal = models.Signal(**data)
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal

from .models import AdminLog

def create_log(db: Session, admin_id: str, action: str, details: str):
    log = AdminLog(admin_id=str(admin_id), action=action, details=details)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def get_logs(db: Session, limit: int = 50):
    return db.query(AdminLog).order_by(AdminLog.id.desc()).limit(limit).all()
