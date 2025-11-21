from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from backend.database import get_db
from backend import models
from backend.schemas import NewsOut
from backend.acl import ensure_user_can_view_signals
from backend.utils.notifications import create_notification

router = APIRouter(
    prefix="/news",
    tags=["news"]
)


# ============================
# GET /news
# ============================
@router.get("/", response_model=list[NewsOut])
def get_news(
    limit: int = 20,
    symbol: str | None = None,
    tag: str | None = None,
    user_id: int | None = None,
    tg_id: int | None = None,
    db: Session = Depends(get_db),
):
    """
    Новости доступны только подписчикам.
    """

    ensure_user_can_view_signals(user_id=user_id, tg_id=tg_id, db=db)

    query = db.query(models.News)

    if symbol:
        query = query.filter(models.News.symbols.contains([symbol]))
    if tag:
        query = query.filter(models.News.tags.contains([tag]))

    news = (
        query.order_by(models.News.published_at.desc())
        .limit(limit)
        .all()
    )

    return news


# ============================
# GET /news/latest
# ============================
@router.get("/latest", response_model=list[NewsOut])
def get_latest_news(
    limit: int = 10,
    user_id: int | None = None,
    tg_id: int | None = None,
    db: Session = Depends(get_db),
):
    """
    Лента последних новостей.
    Только при активной подписке.
    """

    ensure_user_can_view_signals(user_id=user_id, tg_id=tg_id, db=db)

    news = (
        db.query(models.News)
        .order_by(models.News.published_at.desc())
        .limit(limit)
        .all()
    )

    return news


# ============================
# GET /news/feed
# ============================
@router.get("/feed", response_model=list[NewsOut])
def news_feed(
    symbol: str | None = None,
    tag: str | None = None,
    since: str | None = None,
    limit: int = 50,
    user_id: int | None = None,
    tg_id: int | None = None,
    db: Session = Depends(get_db),
):
    """
    Фид новостей.
    Доступ только по активной подписке.
    """

    ensure_user_can_view_signals(user_id=user_id, tg_id=tg_id, db=db)

    query = db.query(models.News)

    if symbol:
        query = query.filter(models.News.symbols.contains([symbol]))

    if tag:
        query = query.filter(models.News.tags.contains([tag]))

    if since:
        try:
            dt = datetime.fromisoformat(since)
            query = query.filter(models.News.published_at > dt)
        except:
            pass

    news = (
        query.order_by(models.News.published_at.desc())
        .limit(limit)
        .all()
    )

    return news
