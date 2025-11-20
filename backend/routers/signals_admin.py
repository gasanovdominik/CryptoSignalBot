from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models
from backend.schemas import SignalCreate, SignalOut

router = APIRouter(
    prefix="/admin/signals",
    tags=["admin-signals"],
)

# ============================
#   ANTI-SPAM CONFIG
# ============================

# Минимальный интервал между ЛЮБЫМИ сигналами (глобальный кулдаун)
COOLDOWN_GLOBAL_SECONDS = 30

# Минимальный интервал между сигналами по одному и тому же символу
COOLDOWN_PER_SYMBOL_SECONDS = 60

# Лимиты на количество сигналов
MAX_SIGNALS_PER_ADMIN_PER_DAY = 50
MAX_SIGNALS_PER_SYMBOL_PER_DAY = 20

# Разрешённые таймфреймы и направления
ALLOWED_TFS = ["M5", "M15", "M30", "H1", "H4", "D1"]
ALLOWED_DIRECTIONS = ["long", "short"]


# ============================
#   HELPERS
# ============================

def zones_intersect(entry1: dict, entry2: dict) -> bool:
    """
    Проверка пересечения зон:
    {min: 10, max: 12} и {min: 11, max: 13} -> True
    """
    if not entry1 or not entry2:
        return False

    if entry1.get("type") != "zone" or entry2.get("type") != "zone":
        return False

    a1, b1 = entry1.get("min"), entry1.get("max")
    a2, b2 = entry2.get("min"), entry2.get("max")

    if a1 is None or b1 is None or a2 is None or b2 is None:
        return False

    return max(a1, a2) <= min(b1, b2)


def is_exact_duplicate(signal: models.Signal, data: SignalCreate) -> bool:
    """
    Дубль = полностью одинаковый сигнал:
    - market
    - symbol
    - tf
    - direction
    - entry (min/max для зоны)
    - sl
    - tps
    """
    if signal.market != data.market:
        return False
    if signal.symbol != data.symbol:
        return False
    if signal.tf != data.tf:
        return False
    if signal.direction != data.direction:
        return False

    # entry сравниваем только для type=zone
    if signal.entry and data.entry:
        if signal.entry.get("type") == "zone" and data.entry.get("type") == "zone":
            if (
                signal.entry.get("min") != data.entry.get("min")
                or signal.entry.get("max") != data.entry.get("max")
            ):
                return False
        else:
            # разные типы entry — уже не дубль
            return False
    else:
        # один из entry пустой
        return False

    # SL
    if signal.sl is None and data.sl is None:
        pass
    elif signal.sl is None or data.sl is None:
        return False
    else:
        if float(signal.sl) != float(data.sl):
            return False

    # TPs
    if not signal.tps or not data.tps:
        return False

    try:
        existing_tps = [float(x) for x in signal.tps]
        new_tps = [float(x) for x in data.tps]
    except Exception:
        return False

    if len(existing_tps) != len(new_tps):
        return False

    for a, b in zip(existing_tps, new_tps):
        if a != b:
            return False

    return True


def validate_signal_payload(data: SignalCreate) -> None:
    """
    Бизнес-валидация содержимого сигнала.
    Если что-то не так — кидаем 400.
    """
    # direction
    if data.direction not in ALLOWED_DIRECTIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid direction '{data.direction}'. Allowed: {ALLOWED_DIRECTIONS}",
        )

    # tf
    if data.tf not in ALLOWED_TFS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid timeframe '{data.tf}'. Allowed: {ALLOWED_TFS}",
        )

    # entry
    if not data.entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entry is required",
        )

    if data.entry.get("type") != "zone":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only entry.type = 'zone' is supported for admin signals",
        )

    try:
        entry_min = float(data.entry.get("min"))
        entry_max = float(data.entry.get("max"))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entry zone must have numeric 'min' and 'max'",
        )

    if entry_min >= entry_max:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="entry.min must be less than entry.max",
        )

    # SL
    if data.sl is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SL (stop-loss) is required",
        )

    sl = float(data.sl)

    # TPs
    if not data.tps or len(data.tps) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one TP is required",
        )

    try:
        tps = [float(x) for x in data.tps]
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TPs must be numeric",
        )

    # Логика для long / short
    if data.direction == "long":
        # SL должен быть ниже зоны входа
        if sl >= entry_min:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="For long, SL must be below entry.min",
            )
        # TP должны быть выше зоны
        if min(tps) <= entry_max:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="For long, all TPs must be above entry.max",
            )

    elif data.direction == "short":
        # SL должен быть выше зоны
        if sl <= entry_max:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="For short, SL must be above entry.max",
            )
        # TP должны быть ниже зоны
        if max(tps) >= entry_min:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="For short, all TPs must be below entry.min",
            )


# ============================
#   ADMIN CREATE SIGNAL + ANTISPAM
# ============================

@router.post("/", response_model=SignalOut)
def admin_create_signal(
    data: SignalCreate,
    admin_id: int,
    db: Session = Depends(get_db),
):
    """
    Создание сигнала администратором + комплексный антиспам.

    Валидации:
    - admin_id должен быть админом
    - проверка содержимого сигнала (direction, tf, entry/sl/tps)
    - глобальный кулдаун между любыми сигналами
    - кулдаун по символу
    - лимит сигналов в сутки для админа
    - лимит сигналов в сутки по символу
    - запрет точных дублей
    - запрет пересекающихся зон по тому же символу и TF
    """

    # --- 1. Проверка роли ---
    admin = db.query(models.User).filter(models.User.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    if admin.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # --- 2. Бизнес-валидация payload ---
    validate_signal_payload(data)

    now = datetime.utcnow()

    # --- 3. Глобальный кулдаун: между любыми сигналами ---
    last_any = (
        db.query(models.Signal)
        .order_by(models.Signal.created_at.desc())
        .first()
    )
    if last_any:
        diff = (now - last_any.created_at).total_seconds()
        if diff < COOLDOWN_GLOBAL_SECONDS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Global cooldown: wait {int(COOLDOWN_GLOBAL_SECONDS - diff)} seconds before creating next signal.",
            )

    # --- 4. Кулдаун по символу ---
    last_symbol = (
        db.query(models.Signal)
        .filter(models.Signal.symbol == data.symbol)
        .order_by(models.Signal.created_at.desc())
        .first()
    )
    if last_symbol:
        diff = (now - last_symbol.created_at).total_seconds()
        if diff < COOLDOWN_PER_SYMBOL_SECONDS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Symbol cooldown: wait {int(COOLDOWN_PER_SYMBOL_SECONDS - diff)} seconds before creating next {data.symbol} signal.",
            )

    # --- 5. Лимиты по дню ---
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Лимит по админу
    admin_count_today = (
        db.query(models.Signal)
        .filter(
            models.Signal.created_by == admin_id,
            models.Signal.created_at >= day_start,
        )
        .count()
    )
    if admin_count_today >= MAX_SIGNALS_PER_ADMIN_PER_DAY:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily limit reached for this admin ({MAX_SIGNALS_PER_ADMIN_PER_DAY} signals per day).",
        )

    # Лимит по символу
    symbol_count_today = (
        db.query(models.Signal)
        .filter(
            models.Signal.symbol == data.symbol,
            models.Signal.created_at >= day_start,
        )
        .count()
    )
    if symbol_count_today >= MAX_SIGNALS_PER_SYMBOL_PER_DAY:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily limit reached for symbol {data.symbol} ({MAX_SIGNALS_PER_SYMBOL_PER_DAY} signals per day).",
        )

    # --- 6. Проверка на дубли и пересечение зон (по символу+TF) ---
    recent_same_pair = (
        db.query(models.Signal)
        .filter(
            models.Signal.symbol == data.symbol,
            models.Signal.tf == data.tf,
        )
        .order_by(models.Signal.created_at.desc())
        .limit(20)
        .all()
    )

    for s in recent_same_pair:
        # точный дубль
        if is_exact_duplicate(s, data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate signal: identical signal for this symbol/tf already exists.",
            )

        # пересечение зон
        if zones_intersect(s.entry or {}, data.entry or {}):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Overlapping entry zone with recent signal for this symbol and TF.",
            )

    # --- 7. Создаём сигнал, если все проверки пройдены ---
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
        created_by=admin_id,
        created_at=now,
    )

    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal
