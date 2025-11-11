from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import crud, schemas
from backend.database import SessionLocal

router = APIRouter(prefix="/signals", tags=["Signals"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.SignalOut])
def list_signals(db: Session = Depends(get_db)):
    return crud.get_signals(db)

@router.post("/", response_model=schemas.SignalOut)
def create_signal(signal: schemas.SignalCreate, db: Session = Depends(get_db)):
    return crud.create_signal(db, signal)
