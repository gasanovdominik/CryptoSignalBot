from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from backend.database import get_db
from backend import models
from backend.schemas import (
    SignalDeliveredIn,
    SignalSeenIn,
    SignalDeliveryOut,
    SignalDeliveryWithSignal,
)
from backend.acl import ensure_user_can_view_signals
from backend.utils.notifications import create_notification

router = APIRouter(
    prefix="/signal-deliveries",
    tags=["signal-deliveries"],
)


# ============================
# POST /signal-deliveries/delivered
# ============================
@router.post("/delivered", response_model=SignalDeliveryOut)
def mark_delivered(
    payload: SignalDeliveredIn,
    db: Session = Depends(get_db),
):
    """
    Помечает сигнал как доставленный пользователю.
    Доступ только при активной подписке.
    """

    # ACL — проверка подписки
    user = ensure_user_can_view_signals(
        user_id=payload.user_id,
        tg_id=None,
        db=db,
    )

    signal = db.query(models.Signal).filter(models.Signal.id == payload.signal_id).first()
    if not signal:
        raise HTTPException(404, "Signal not found")

    delivery = (
        db.query(models.SignalDelivery)
        .filter(
            models.SignalDelivery.signal_id == payload.signal_id,
            models.SignalDelivery.user_id == user.id,
        )
        .first()
    )

    now = datetime.utcnow()
    delivered_at = payload.delivered_at or now

    if delivery:
        if delivery.delivered_at is None:
            delivery.delivered_at = delivered_at
    else:
        delivery = models.SignalDelivery(
            signal_id=payload.signal_id,
            user_id=user.id,
            delivered_at=delivered_at,
            seen_at=None,
        )
        db.add(delivery)

    db.commit()
    db.refresh(delivery)
    return delivery


# ============================
# POST /signal-deliveries/seen
# ============================
@router.post("/seen", response_model=SignalDeliveryOut)
def mark_seen(
    payload: SignalSeenIn,
    db: Session = Depends(get_db),
):
    """
    Помечает сигнал как просмотренный пользователем.
    Доступ только при активной подписке.
    """

    # ACL
    user = ensure_user_can_view_signals(
        user_id=payload.user_id,
        tg_id=None,
        db=db,
    )

    delivery = (
        db.query(models.SignalDelivery)
        .filter(
            models.SignalDelivery.signal_id == payload.signal_id,
            models.SignalDelivery.user_id == user.id,
        )
        .first()
    )

    now = datetime.utcnow()
    seen_at = payload.seen_at or now

    if delivery is None:
        delivery = models.SignalDelivery(
            signal_id=payload.signal_id,
            user_id=user.id,
            delivered_at=None,
            seen_at=seen_at,
        )
        db.add(delivery)
    else:
        delivery.seen_at = seen_at

    db.commit()
    db.refresh(delivery)
    # 🔔 уведомление пользователю
    create_notification(
        db=db,
        user_id=user.id,
        type="signal_delivered",
        title="Сигнал доставлен",
        message=f"Сигнал #{payload.signal_id} был доставлен"
    )

    return delivery


# ============================
# GET /signal-deliveries/user/{user_id}
# ============================
@router.get("/user/{user_id}", response_model=list[SignalDeliveryWithSignal])
def get_user_deliveries(
    user_id: int,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """
    Лента доставленных сигналов.
    Доступ только при активной подписке.
    """

    ensure_user_can_view_signals(
        user_id=user_id,
        tg_id=None,
        db=db,
    )

    deliveries = (
        db.query(models.SignalDelivery)
        .filter(models.SignalDelivery.user_id == user_id)
        .order_by(
            models.SignalDelivery.delivered_at.desc().nullslast(),
            models.SignalDelivery.id.desc(),
        )
        .limit(limit)
        .all()
    )

    return deliveries
