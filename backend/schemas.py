from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SignalBase(BaseModel):
    symbol: str
    direction: str
    market: str
    entry: float
    sl: float
    tp: float
    rr: float
    risk: str
    comment: str

class SignalCreate(SignalBase):
    pass

class SignalOut(SignalBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    telegram_id: str
    username: Optional[str]
    language: Optional[str] = "ru"
    subscribed: bool = False

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True


class SubscriptionBase(BaseModel):
    user_id: int
    plan: str
    active: bool = True
    expires_at: datetime

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionOut(SubscriptionBase):
    id: int
    class Config:
        orm_mode = True
