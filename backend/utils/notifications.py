from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend import models


def create_notification(db: Session, user_id: int, type: str, title: str, message: str):
    ntf = models.Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        is_read=False,
        created_at=datetime.now(timezone.utc)
    )
    db.add(ntf)
    db.commit()
    db.refresh(ntf)
    return ntf
