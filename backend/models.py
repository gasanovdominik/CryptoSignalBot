# backend/models.py
from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    direction = Column(String)
    entry_min = Column(Float)
    entry_max = Column(Float)
    sl = Column(Float)
    tp1 = Column(Float)
    tp2 = Column(Float)
    tp3 = Column(Float)
# --- LOGS ---
from sqlalchemy import DateTime, Text
from datetime import datetime

class AdminLog(Base):
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(String, index=True)        # кто сделал
    action = Column(String, index=True)          # add / update / delete
    details = Column(Text)                       # произвольное описание
    created_at = Column(DateTime, default=datetime.utcnow)
