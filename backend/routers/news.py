from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

import httpx

from backend.database import get_db
from backend import models
from backend.schemas import NewsOut

router = APIRouter(
    prefix="/news",
    tags=["news"]
)

CRYPTO_PANIC_API_URL = "https://cryptopanic.com/api/v1/posts/"
CRYPTO_PANIC_API_KEY = ""   # <-- вставь сюда ключ, когда появится


# ============================
# GET /news — список новостей
# ============================
@router.get("/", response_model=list[NewsOut])
def get_news(
    limit: int = 20,
    symbol: str | None = None,
    tag: str | None = None,
    db: Session = Depends(get_db)
):
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


# ================================
# GET /news/latest — последние N
# ================================
@router.get("/latest", response_model=list[NewsOut])
def get_latest_news(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    news = (
        db.query(models.News)
        .order_by(models.News.published_at.desc())
        .limit(limit)
        .all()
    )
    return news


# =========================================
# POST /news/refresh — загрузить из CryptoPanic
# =========================================
@router.post("/refresh")
def refresh_news(db: Session = Depends(get_db)):
    """
    Загружает свежие новости из CryptoPanic и записывает в БД.
    """

    if not CRYPTO_PANIC_API_KEY:
        raise HTTPException(500, "CryptoPanic API KEY is not set")

    params = {
        "auth_token": CRYPTO_PANIC_API_KEY,
        "filter": "news",
        "kind": "news",
        "public": "true"
    }

    try:
        response = httpx.get(CRYPTO_PANIC_API_URL, params=params, timeout=10)
        data = response.json()
    except Exception as e:
        raise HTTPException(500, f"CryptoPanic request failed: {repr(e)}")

    posts = data.get("results", [])

    added = 0

    for p in posts:
        # Защита от дублей по URL
        exists = (
            db.query(models.News)
            .filter(models.News.url == p["url"])
            .first()
        )
        if exists:
            continue

        news_item = models.News(
            source="CryptoPanic",
            title=p.get("title"),
            url=p.get("url"),
            symbols=p.get("currencies") or None,
            tags=p.get("tags") or None,
            published_at=datetime.fromisoformat(p["published_at"].replace("Z", "+00:00"))
                if p.get("published_at") else None,
            summary=p.get("description")
        )

        db.add(news_item)
        added += 1

    db.commit()

    return {"status": "ok", "added": added}
