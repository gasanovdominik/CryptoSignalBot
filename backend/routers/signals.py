from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models

router = APIRouter(
    prefix="/signals",
    tags=["signals"]
)

@router.get("")
def get_signals(
    market: str = None,
    symbol: str = None,
    tf: str = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(models.Signal)

    if market:
        query = query.filter(models.Signal.market == market)

    if symbol:
        query = query.filter(models.Signal.symbol == symbol)

    if tf:
        query = query.filter(models.Signal.tf == tf)

    signals = (
        query
        .order_by(models.Signal.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": s.id,
            "market": s.market,
            "symbol": s.symbol,
            "direction": s.direction,
            "tf": s.tf,
            "entry": s.entry,
            "sl": float(s.sl) if s.sl else None,
            "tps": s.tps,
            "leverage": s.leverage,
            "risk_pct": float(s.risk_pct) if s.risk_pct else None,
            "indicators": s.indicators,
            "comment": s.comment,
            "image_url": s.image_url,
            "created_at": s.created_at,
        }
        for s in signals
    ]
