import os
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc

from . import models, crud
from .database import SessionLocal, engine, Base

app = FastAPI(title="CryptoSignal Backend")

# БД
Base.metadata.create_all(bind=engine)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ENV
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, "envs", "backend.env")
load_dotenv(ENV_PATH)
API_KEY = os.getenv("API_KEY")

# DB DI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Проверка API-ключа
def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    return True

@app.get("/health")
async def health():
    return {"status": "ok"}

# ----- SIGNALS -----

@app.get("/signals")
async def get_signals(db: Session = Depends(get_db)):
    return crud.get_signals(db)

@app.post("/signals")
async def add_signal(
    signal: dict,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
    x_admin_id: str | None = Header(default="unknown")
):
    created = crud.create_signal(db, signal)
    crud.create_log(
        db,
        admin_id=x_admin_id or "unknown",
        action="add",
        details=f"Added {created.symbol} #{created.id} ({created.direction})"
    )
    return created

@app.put("/signals/{signal_id}")
async def update_signal(
    signal_id: int,
    signal_data: dict,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
    x_admin_id: str | None = Header(default="unknown")
):
    signal = db.query(models.Signal).filter(models.Signal.id == signal_id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    for key, value in signal_data.items():
        if hasattr(signal, key):
            setattr(signal, key, value)

    db.commit()
    db.refresh(signal)

    crud.create_log(
        db,
        admin_id=x_admin_id or "unknown",
        action="update",
        details=f"Updated {signal.symbol} #{signal.id}"
    )
    return {"message": f"Signal {signal_id} updated successfully"}

@app.delete("/signals/{signal_id}")
async def delete_signal(
    signal_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key),
    x_admin_id: str | None = Header(default="unknown")
):
    signal = db.query(models.Signal).filter(models.Signal.id == signal_id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    info = f"{signal.symbol} #{signal.id}"
    db.delete(signal)
    db.commit()

    crud.create_log(
        db,
        admin_id=x_admin_id or "unknown",
        action="delete",
        details=f"Deleted {info}"
    )
    return {"message": f"Signal {signal_id} deleted successfully"}

# ----- STATS -----

@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    signals = db.query(models.Signal).order_by(desc(models.Signal.id)).all()
    total = len(signals)
    last_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if total > 0 else None

    latest = [
        {
            "id": s.id,
            "symbol": s.symbol,
            "direction": s.direction,
            "entry_min": s.entry_min,
            "entry_max": s.entry_max,
        }
        for s in signals[:5]
    ]
    return {"total_signals": total, "last_update": last_date, "latest": latest}

# ----- LOGS -----

@app.get("/logs")
async def list_logs(
    limit: int = 20,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    logs = crud.get_logs(db, limit=limit)
    return [
        {
            "id": l.id,
            "admin_id": l.admin_id,
            "action": l.action,
            "details": l.details,
            "created_at": l.created_at.isoformat() + "Z",
        }
        for l in logs
    ]


