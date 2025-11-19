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

@router.post("/{user_id}/role")
def change_user_role(user_id: int, role: str, db: Session = Depends(get_db)):
    valid_roles = ["guest", "trial", "subscriber", "expired", "banned", "admin"]

    if role not in valid_roles:
        raise HTTPException(status_code=400, detail="Invalid role")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = role
    db.commit()
    db.refresh(user)

    return {"ok": True, "new_role": role}
