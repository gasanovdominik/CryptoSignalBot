from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.database import get_db
from backend import models

router = APIRouter(
    prefix="/subs",
    tags=["subscriptions-admin"]
)


# =========================================
#  ADMIN: Ручная активация подписки
#  POST /subs/activate
# =========================================
@router.post("/activate")
def activate_subscription(
    user_id: int,
    plan_code: str,
    db: Session = Depends(get_db)
):
    """
    Ручная активация подписки админом.

    Используется после проверки оплаты вручную (TON/Stars/чек).
    """

    # === 1. Проверяем пользователя ===
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    # === 2. Ищем план ===
    plan = db.query(models.Plan).filter(models.Plan.code == plan_code).first()
    if not plan:
        raise HTTPException(404, "Plan not found")

    # === 3. Сбрасываем предыдущую активную ===
    active = (
        db.query(models.Subscription)
        .filter(
            models.Subscription.user_id == user_id,
            models.Subscription.status.in_(["active", "trial"])
        )
        .first()
    )

    if active:
        active.status = "expired"

    # === 4. Создаём новую подписку ===
    now = datetime.utcnow()
    end_at = (
        now + timedelta(days=7) if plan.trial
        else now + timedelta(days=30 * plan.months)
    )

    sub = models.Subscription(
        user_id=user_id,
        plan_id=plan.id,
        status="trial" if plan.trial else "active",
        start_at=now,
        end_at=end_at,
        source="manual"
    )

    db.add(sub)
    db.commit()
    db.refresh(sub)

    return {
        "status": "ok",
        "message": "Subscription activated manually",
        "subscription_id": sub.id,
        "user_id": user_id,
        "plan_code": plan.code,
        "start_at": sub.start_at,
        "end_at": sub.end_at
    }
