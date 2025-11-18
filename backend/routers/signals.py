from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models
from backend.schemas import SignalCreate, SignalUpdate, SignalOut

router = APIRouter(
    prefix="/signals",
    tags=["signals"],
)

# ===== GET /signals — основной эндпоинт =====
@router.get("/", response_model=list[SignalOut])
def get_signals(
    market: str | None = None,
    symbol: str | None = None,
    tf: str | None = None,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    query = db.query(models.Signal)

    if market:
        query = query.filter(models.Signal.market == market)
    if symbol:
        query = query.filter(models.Signal.symbol == symbol)
    if tf:
        query = query.filter(models.Signal.tf == tf)

    signals = (
        query.order_by(models.Signal.created_at.desc())
        .limit(limit)
        .all()
    )

    return signals


# ===== GET /signals/feed — второстепенный =====
@router.get("/feed", response_model=list[SignalOut])
def get_signals_feed(
    market: str | None = None,
    symbol: str | None = None,
    tf: str | None = None,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    query = db.query(models.Signal)

    if market:
        query = query.filter(models.Signal.market == market)
    if symbol:
        query = query.filter(models.Signal.symbol == symbol)
    if tf:
        query = query.filter(models.Signal.tf == tf)

    signals = (
        query.order_by(models.Signal.created_at.desc())
        .limit(limit)
        .all()
    )

    return signals


# ===== POST /signals — создать сигнал =====
@router.post("/", response_model=SignalOut)
def create_signal(
    data: SignalCreate,
    db: Session = Depends(get_db),
):
    signal = models.Signal(**data.dict())
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal


# ===== PUT /signals/{id} =====
@router.put("/{signal_id}", response_model=SignalOut)
def update_signal(
    signal_id: int,
    data: SignalUpdate,
    db: Session = Depends(get_db),
):
    signal = db.query(models.Signal).filter(models.Signal.id == signal_id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    for key, value in data.dict().items():
        setattr(signal, key, value)

    db.commit()
    db.refresh(signal)
    return signal


# ===== DELETE /signals/{id} =====
@router.delete("/{signal_id}")
def delete_signal(signal_id: int, db: Session = Depends(get_db)):
    signal = db.query(models.Signal).filter(models.Signal.id == signal_id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    db.delete(signal)
    db.commit()
    return {"status": "ok", "deleted_id": signal_id}



