from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.database import get_db
from backend import models
from backend.schemas import SubscriptionCreate, SubscriptionOut

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"]
)


# ===== Helper =====
def calculate_end_date(plan):
    """Возвращает дату окончания подписки."""
    if plan.trial:
        return datetime.utcnow() + timedelta(days=7)  # TRIAL = 7 дней
    return datetime.utcnow() + timedelta(days=30 * plan.months)


# ===== POST /subscriptions — создать =====
@router.post("/", response_model=SubscriptionOut)
def create_subscription(data: SubscriptionCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    plan = db.query(models.Plan).filter(models.Plan.code == data.plan_code).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Деактивируем старую активную подписку
    active = db.query(models.Subscription).filter(
        models.Subscription.user_id == data.user_id,
        models.Subscription.status == "active"
    ).first()

    if active:
        active.status = "expired"

    # Создаём новую
    now = datetime.utcnow()
    end_at = calculate_end_date(plan)

    sub = models.Subscription(
        user_id=data.user_id,
        plan_id=plan.id,
        status="trial" if plan.trial else "active",
        start_at=now,
        end_at=end_at,
        source="manual"
    )

    db.add(sub)
    db.commit()
    db.refresh(sub)

    return sub


# ===== GET /subscriptions/{user_id} =====
@router.get("/{user_id}", response_model=SubscriptionOut)
def get_user_subscription(user_id: int, db: Session = Depends(get_db)):
    sub = db.query(models.Subscription).filter(
        models.Subscription.user_id == user_id
    ).order_by(models.Subscription.start_at.desc()).first()

    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Авто-истечение
    if sub.end_at and sub.end_at < datetime.utcnow() and sub.status == "active":
        sub.status = "expired"
        db.commit()
        db.refresh(sub)

    return sub
