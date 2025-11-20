from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models
from backend.schemas import SignalCreate, SignalOut

router = APIRouter(
    prefix="/admin/signals",
    tags=["admin-signals"],
)


# ================================================
# ADMIN: Создать сигнал (расширенная версия)
# POST /admin/signals
# ================================================
@router.post("/", response_model=SignalOut)
def admin_create_signal(
    data: SignalCreate,
    admin_id: int,
    db: Session = Depends(get_db),
):
    """
    Создание сигнала администратором.
    """

    # --- Проверка роли ---
    admin = db.query(models.User).filter(models.User.id == admin_id).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin user not found")

    if admin.role.value != "admin":  # UserRole enum
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # --- Создаем сигнал ---
    signal = models.Signal(
        market=data.market,
        symbol=data.symbol,
        direction=data.direction,
        tf=data.tf,
        entry=data.entry,
        sl=data.sl,
        tps=data.tps,
        risk_rr=data.risk_rr,
        leverage=data.leverage,
        risk_pct=data.risk_pct,
        indicators=data.indicators,
        comment=data.comment,
        image_url=data.image_url,
        created_by=admin_id
    )

    db.add(signal)
    db.commit()
    db.refresh(signal)

    return signal
