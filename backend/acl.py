from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend import models


def _get_user(
    user_id: Optional[int],
    tg_id: Optional[int],
    db: Session,
) -> models.User:
    """Вспомогательная функция поиска пользователя."""
    if user_id is not None:
        user = db.query(models.User).filter(models.User.id == user_id).first()
    elif tg_id is not None:
        user = db.query(models.User).filter(models.User.tg_id == tg_id).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id or tg_id is required",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


def ensure_user_can_view_signals(
    *,
    user_id: Optional[int] = None,
    tg_id: Optional[int] = None,
    db: Session,
) -> models.User:
    """
    Проверяет, может ли пользователь получать сигналы.

    Правила:
    - banned -> 403
    - admin -> всегда ок
    - для остальных нужна активная подписка (trial/active, end_at > now)
    - если подписка истекла, помечаем её expired и, при необходимости,
      обновляем user.role -> expired
    """
    user = _get_user(user_id, tg_id, db)

    # Бан
    if user.role == models.UserRole.banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user is banned",
        )

    # Админ всегда может
    if user.role == models.UserRole.admin:
        return user

    # Ищем самую свежую подписку
    sub = (
        db.query(models.Subscription)
        .filter(models.Subscription.user_id == user.id)
        .order_by(models.Subscription.start_at.desc().nullslast())
        .first()
    )

    now = datetime.utcnow()

    if not sub or not sub.start_at or not sub.end_at:
        # подписки нет вообще
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: active subscription required",
        )

    # Авто-истечение
    if sub.end_at < now or sub.status not in ("active", "trial"):
        # если статус ещё active/trial, но дата уже прошла — проставим expired
        if sub.status in ("active", "trial") and sub.end_at < now:
            sub.status = "expired"
            if user.role not in (models.UserRole.admin, models.UserRole.banned):
                user.role = models.UserRole.expired
            db.add(sub)
            db.add(user)
            db.commit()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: subscription expired",
        )

    # При активной подписке можем синхронизировать роль
    if sub.status == "trial" and user.role == models.UserRole.guest:
        user.role = models.UserRole.trial
        db.add(user)
        db.commit()
    elif sub.status == "active" and user.role in (
        models.UserRole.guest,
        models.UserRole.trial,
        models.UserRole.expired,
    ):
        user.role = models.UserRole.subscriber
        db.add(user)
        db.commit()

    return user
