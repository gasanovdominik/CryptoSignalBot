from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.database import get_db
from backend import models
from backend.schemas import SignalCreate, SignalOut

router = APIRouter(
    prefix="/admin/signals",
    tags=["admin-signals"],
)


# ============================
#   ANTI-SPAM RULES
# ============================

COOLDOWN_MINUTES = 2   # кулдаун на один символ


def zones_intersect(entry1: dict, entry2: dict) -> bool:
    """
    Проверка пересечения зон:
    {min: 10, max: 12} и {min: 11, max: 13} -> True
    """
    if entry1["type"] != "zone" or entry2["type"] != "zone":
        return False

    a1, b1 = entry1["min"], entry1["max"]
    a2, b2 = entry2["min"], entry2["max"]

    return max(a1, a2) <= min(b1, b2)


def is_duplicate(signal: models.Signal, data: SignalCreate) -> bool:
    """
    Дубль = полностью одинаковый сигнал:
    - symbol
    - tf
    - direction
    - entry min/max
    """
    if signal.symbol != data.symbol:
        return False
    if signal.tf != data.tf:
        return False
    if signal.direction != data.direction:
        return False

    if signal.entry and data.entry:
        if signal.entry.get("type") == "zone" and data.entry.get("type") == "zone":
            if (
                signal.entry.get("min") == data.entry.get("min")
                and signal.entry.get("max") == data.entry.get("max")
            ):
                return True

    return False


# ===========================================
#   ADMIN CREATE SIGNAL + ANTI-SPAM RULES
# ===========================================
@router.post("/", response_model=SignalOut)
def admin_create_signal(
    data: SignalCreate,
    admin_id: int,
    db: Session = Depends(get_db),
):
    """
    Создание сигнала администратором + антиспам.
    """

    # --- Проверка роли ---
    admin = db.query(models.User).filter(models.User.id == admin_id).first()
    if not admin:
        raise HTTPException(404, "Admin not found")
    if admin.role.value != "admin":
        raise HTTPException(403, "Not enough permissions")

    # --- Получаем последние 20 сигналов по символу ---
    recent = (
        db.query(models.Signal)
        .filter(models.Signal.symbol == data.symbol)
        .order_by(models.Signal.created_at.desc())
        .limit(20)
        .all()
    )

    # ============= RULE 1: Cooldown =============
    if recent:
        last_signal = recent[0]
        diff = datetime.utcnow() - last_signal.created_at
        if diff < timedelta(minutes=COOLDOWN_MINUTES):
            raise HTTPException(
                429,
                f"Cooldown: you must wait {COOLDOWN_MINUTES} minutes before sending next {data.symbol} signal."
            )

    # ============= RULE 2: Exact duplicates =============
    for s in recent:
        if is_duplicate(s, data):
            raise HTTPException(
                400,
                "Duplicate signal: same symbol, tf, direction and entry zone already exists."
            )

    # ============= RULE 3: Intersecting zones (soft spam check) =============
    for s in recent:
        if zones_intersect(s.entry or {}, data.entry or {}):
            raise HTTPException(
                409,
                "Zone intersection detected: entry zone intersects with recent signal zone. Avoid overlapping signals."
            )

    # ============= RULE 4: Same symbol + same TF =============
    same_tf = [
        s for s in recent
        if s.tf == data.tf
    ]
    if same_tf:
        raise HTTPException(
            409,
            f"There is already a {data.symbol} signal on TF={data.tf}. Wait or update old one."
        )

    # --- Если прошли проверки: создаем сигнал ---
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
