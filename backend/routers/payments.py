from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)



@router.post("/webhook", response_model=schemas.PaymentOut)
def payments_webhook(
    payload: schemas.PaymentWebhookIn,
    db: Session = Depends(get_db),
):
    """
    Вебхук подтверждения оплаты.

    MVP-логика:
    1. Находим пользователя:
       - либо по user_id,
       - либо по tg_id.
    2. Ищем платёж по (provider, tx_id).
       - Если уже есть — обновляем статус и сумму (идемпотентность).
       - Если нет — создаём новый.
    3. Здесь *НЕ* активируем подписку автоматически — по ТЗ это делает админ
       через отдельный endpoint /subs/activate.
    """
    if payload.user_id is None and payload.tg_id is None:
        raise HTTPException(400, "Either user_id or tg_id must be provided")

    # --- 1. Находим пользователя ---
    user = None
    if payload.user_id is not None:
        user = (
            db.query(models.User)
            .filter(models.User.id == payload.user_id)
            .first()
        )
    elif payload.tg_id is not None:
        user = (
            db.query(models.User)
            .filter(models.User.tg_id == payload.tg_id)
            .first()
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found for this payment",
        )

    # --- 2. Идемпотентность по (provider, tx_id) ---
    existing = (
        db.query(models.Payment)
        .filter(
            models.Payment.provider == payload.provider,
            models.Payment.tx_id == payload.tx_id,
        )
        .first()
    )

    if existing:
        # Обновляем статус и сумму — на случай, если провайдер шлёт повторный вебхук
        existing.status = payload.status
        existing.amount_cents = payload.amount_cents
        existing.currency = payload.currency
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    # --- 3. Создаём новый платёж ---
    payment = models.Payment(
        user_id=user.id,
        amount_cents=payload.amount_cents,
        currency=payload.currency,
        provider=payload.provider,
        tx_id=payload.tx_id,
        status=payload.status,
        # created_at выставится по default в БД
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment
