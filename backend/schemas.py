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


class SignalUpdate(BaseModel):
    market: Optional[str] = None
    symbol: Optional[str] = None
    tf: Optional[str] = None
    direction: Optional[str] = None
    entry: Optional[Dict[str, Any]] = None
    sl: Optional[float] = None
    tps: Optional[List[float]] = None
    risk_rr: Optional[float] = None
    leverage: Optional[int] = None
    risk_pct: Optional[float] = None
    indicators: Optional[Dict[str, Any]] = None
    comment: Optional[str] = None
    image_url: Optional[str] = None



class SignalOut(SignalBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True



# ============ PAYMENTS ============

class PaymentWebhookIn(BaseModel):
    user_id: Optional[int] = None
    tg_id: Optional[int] = None
    amount_cents: int
    currency: str         # TON / XTR / USD
    provider: str         # telegram_wallet / stars
    tx_id: str
    status: str           # pending / success / failed / refunded
    extra: Optional[Dict[str, Any]] = None


class PaymentOut(BaseModel):
    id: int
    user_id: int
    amount_cents: int
    currency: str
    provider: str
    tx_id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
