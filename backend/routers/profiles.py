from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models

router = APIRouter(
    prefix="/profiles",
    tags=["profiles"]
)


# ===== GET /profiles/{user_id} =====
@router.get("/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


# ===== POST /profiles/{user_id} — создать профиль =====
@router.post("/{user_id}")
def create_profile(user_id: int, db: Session = Depends(get_db)):
    # Проверяем что пользователь существует
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Если профиль уже есть — возвращаем
    existing = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
    if existing:
        return existing

    profile = models.Profile(
        user_id=user_id,
        exchange_uids={},
        api_keys={},
        notifications={},
        favorites=[]
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


# ===== PUT /profiles/{user_id} — обновление профиля =====
@router.put("/{user_id}")
def update_profile(user_id: int, data: dict, db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for key, value in data.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return profile
