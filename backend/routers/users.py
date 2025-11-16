from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models
from backend.schemas import UserCreate, UserOut

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


# ===== POST /users — создать или найти по tg_id =====
@router.post("/", response_model=UserOut)
def create_or_get_user(data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.tg_id == data.tg_id).first()
    if user:
        # обновим базовую инфу (username/full_name/lang/tz)
        for field, value in data.dict().items():
            if value is not None:
                setattr(user, field, value)
    else:
        user = models.User(
            tg_id=data.tg_id,
            username=data.username,
            full_name=data.full_name,
            email=data.email,
            lang=data.lang,
            tz=data.tz,
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    return user

