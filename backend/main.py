from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import Base, engine
from backend.routers import signals, users, subscriptions

# Инициализация базы
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CryptoSignalBot API",
    version="1.0.0",
    description="Backend API для CryptoSignalBot (FastAPI + PostgreSQL)"
)

# Разрешаем запросы от бота и фронта
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роуты
app.include_router(signals.router)
app.include_router(users.router)
app.include_router(subscriptions.router)

@app.get("/")
async def root():
    return {"status": "ok", "message": "CryptoSignalBot API is running 🚀"}
