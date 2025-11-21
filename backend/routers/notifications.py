from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models, schemas

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)


@router.get("/{user_id}", response_model=list[schemas.NotificationOut])
def get_user_notifications(user_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Notification)
        .filter(models.Notification.user_id == user_id)
        .order_by(models.Notification.created_at.desc())
        .all()
    )


@router.post("/mark-read", response_model=schemas.NotificationOut)
def mark_notification_read(
    payload: schemas.NotificationMarkRead,
    db: Session = Depends(get_db)
):
    ntf = db.query(models.Notification).filter(
        models.Notification.id == payload.notification_id
    ).first()

    if not ntf:
        raise HTTPException(404, "Notification not found")

    ntf.is_read = True
    db.commit()
    db.refresh(ntf)
    return ntf
