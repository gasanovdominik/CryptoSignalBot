from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine
from backend.routers import signals, users, subscriptions
from backend import models

# ===========================
#   Создаём таблицы в PostgreSQL
# ===========================
models.Base.metadata.create_all(bind=engine)

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
app.include_router(signals.router)
app.include_router(users.router)
app.include_router(subscriptions.router)

# ===========================
#   Тестовый корневой эндпоинт
# ===========================
@app.get("/")
async def root():
    return {"status": "ok", "message": "CryptoSignalBot API is running 🚀"}
