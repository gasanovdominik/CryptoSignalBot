from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend import crud, schemas
from backend.database import SessionLocal

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.SubscriptionOut)
def create_sub(sub: schemas.SubscriptionCreate, db: Session = Depends(get_db)):
    return crud.create_subscription(db, sub)

@router.get("/{user_id}", response_model=list[schemas.SubscriptionOut])
def list_subs(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_subscriptions(db, user_id)
