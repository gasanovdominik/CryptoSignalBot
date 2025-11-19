from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============ USERS ============
class UserCreate(BaseModel):
    tg_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    lang: Optional[str] = "ru"
    tz: Optional[str] = "Europe/Berlin"
    role: Optional[str] = "guest"

class UserOut(BaseModel):
    id: int
    tg_id: int
    username: Optional[str]
    full_name: Optional[str]
    email: Optional[str]
    lang: str
    tz: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============ SUBSCRIPTIONS ============
class SubscriptionCreate(BaseModel):
    user_id: int
    plan_code: str                        # например: basic / pro / trial


class SubscriptionOut(BaseModel):
    id: int
    user_id: int
    plan_id: int
    status: str
    start_at: Optional[datetime]
    end_at: Optional[datetime]
    source: Optional[str]

    class Config:
        from_attributes = True


# ============ SIGNALS ============
class SignalBase(BaseModel):
    market: str
    symbol: str
    tf: str
    direction: str
    entry: Dict[str, Any]
    sl: Optional[float]
    tps: List[float]

    risk_rr: Optional[float] = None
    leverage: Optional[int] = None
    risk_pct: Optional[float] = None

    indicators: Optional[Dict[str, Any]] = None
    comment: Optional[str] = None
    image_url: Optional[str] = None


class SignalCreate(SignalBase):
    pass


class SignalUpdate(SignalBase):
    pass


class SignalOut(SignalBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

