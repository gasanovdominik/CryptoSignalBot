from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models
from backend.schemas import SubscriptionCreate, SubscriptionOut

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
)


# ===== POST /subscriptions — создать подписку =====
@router.post("/", response_model=SubscriptionOut)
def create_subscription(
    data: SubscriptionCreate,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    plan = db.query(models.Plan).filter(models.Plan.code == data.plan_code).first()
    if not plan:
        raise HTTPException(404, "Plan not found")

    start_at = datetime.utcnow()
    end_at = start_at + timedelta(days=30 * plan.months) if plan.months else None

    sub = models.Subscription(
        user_id=user.id,
        plan_id=plan.id,
        status="active" if not plan.trial else "trial",
        start_at=start_at,
        end_at=end_at,
        source="manual",
    )

    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


# ===== GET /subscriptions/{user_id} — список подписок =====
@router.get("/{user_id}", response_model=list[SubscriptionOut])
def list_user_subscriptions(user_id: int, db: Session = Depends(get_db)):
    subs = (
        db.query(models.Subscription)
        .filter(models.Subscription.user_id == user_id)
        .order_by(models.Subscription.start_at.desc())
        .all()
    )
    return subs

