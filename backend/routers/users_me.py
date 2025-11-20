from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models
from backend.schemas import UserOut

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# ===========================================
# GET /users/me — профиль текущего пользователя
# ===========================================
@router.get("/me", response_model=UserOut)
def get_me(
    user_id: int | None = None,
    tg_id: int | None = None,
    db: Session = Depends(get_db)
):
    """
    Возвращает профиль пользователя.
    Используется ботом для запроса /users/me.
    """

    if not user_id and not tg_id:
        raise HTTPException(400, "Provide user_id or tg_id")

    if user_id:
        user = db.query(models.User).filter(models.User.id == user_id).first()
    else:
        user = db.query(models.User).filter(models.User.tg_id == tg_id).first()

    if not user:
        raise HTTPException(404, "User not found")

    return user
