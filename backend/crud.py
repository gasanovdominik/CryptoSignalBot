from sqlalchemy.orm import Session
from backend import models, schemas
from datetime import datetime

# ---------- Signals ----------
def get_signals(db: Session):
    return db.query(models.Signal).all()

def create_signal(db: Session, signal: schemas.SignalCreate):
    db_signal = models.Signal(**signal.dict())
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)
    return db_signal


# ---------- Users ----------
def get_user_by_tg(db: Session, telegram_id: str):
    return db.query(models.User).filter(models.User.telegram_id == telegram_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ---------- Subscriptions ----------
def create_subscription(db: Session, sub: schemas.SubscriptionCreate):
    db_sub = models.Subscription(**sub.dict())
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub

def get_user_subscriptions(db: Session, user_id: int):
    return db.query(models.Subscription).filter(models.Subscription.user_id == user_id).all()
