from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine
from backend.routers import signals_router, users_router, subscriptions_router




# Важно: импортировать модели, чтобы SQLAlchemy их зарегистрировал

# ===========================
#   Создаём таблицы в PostgreSQL
# ===========================
Base.metadata.create_all(bind=engine)

# ===========================
#   Инициализация FastAPI
# ===========================
app = FastAPI(
    title="CryptoSignalBot API",
    version="1.0.0",
    description="Backend API для CryptoSignalBot (FastAPI + PostgreSQL)"
)

# ===========================
#   CORS — разрешить запросы от бота
# ===========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================
#   Подключение роутеров
# ===========================
app.include_router(signals_router)
app.include_router(users_router)
app.include_router(subscriptions_router)

# ===========================
#   Тестовый корневой эндпоинт g
# ===========================
@app.get("/")
async def root():
    return {"status": "ok", "message": "CryptoSignalBot API is running 🚀"}

from sqlalchemy import text
from backend.database import engine

@app.get("/debug-db")
async def debug_db():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            value = list(result)[0][0]
        return {"ok": True, "result": value}
    except Exception as e:
        # Временно возвращаем текст ошибки наружу, чтобы понять, что именно падает
        return {"ok": False, "error": repr(e)}
