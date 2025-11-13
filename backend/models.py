from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    username = Column(String)
    language = Column(String, default="ru")
    subscribed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    subscriptions = relationship("Subscription", back_populates="user")


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    market = Column(String)
    symbol = Column(String)
    direction = Column(String)
    tf = Column(String)

    entry = Column(JSONB)                       # {"type": "zone", "min": 152.9, "max": 153.4}
    sl = Column(Float)
    tps = Column(JSONB)                         # [155.2,156.0,157.4]

    leverage = Column(Integer)
    risk_pct = Column(Float)

    indicators = Column(JSONB)                  # {"vwap":"above","ema200":"uptrend",...}

    comment = Column(String)
    image_url = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan = Column(String)
    active = Column(Boolean, default=True)
    expires_at = Column(DateTime)

    user = relationship("User", back_populates="subscriptions")
