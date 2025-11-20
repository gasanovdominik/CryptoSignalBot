from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.routers.signals import router as signals_router
from backend.routers.users import router as users_router
from backend.routers.subscriptions import router as subscriptions_router
from backend.routers.profiles import router as profiles_router
from backend.routers.payments import router as payments_router
from backend.routers.news import router as news_router
from backend.routers.subscriptions_admin import router as subs_admin_router
from backend.routers.signals_admin import router as signals_admin_router
from backend.routers.users_me import router as users_me_router
from backend.routers.signal_deliveries import router as signal_deliveries_router



from sqlalchemy import text
from backend.database import engine

app = FastAPI(
    title="CryptoSignalBot API",
    version="1.0.0",
    description="Backend API для CryptoSignalBot (FastAPI + PostgreSQL)"
)

# ============================
#  Создание таблиц ПРАВИЛЬНО
# ============================
@app.on_event("startup")
def on_startup():
    init_db()   # <-- создаёт таблицы после загрузки моделей

# force redeploy
# ============================
#  Debug endpoint
# ============================
@app.get("/debug-db")
async def debug_db():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            value = list(result)[0][0]
        return {"ok": True, "result": value}
    except Exception as e:
        return {"ok": False, "error": repr(e)}


# ============================
#   CORS
# ============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================
#   Routers
# ============================
app.include_router(signals_router)
app.include_router(users_router)
app.include_router(subscriptions_router)
app.include_router(profiles_router)
app.include_router(payments_router)
app.include_router(news_router)
app.include_router(subs_admin_router)
app.include_router(signals_admin_router)
app.include_router(users_me_router)
app.include_router(signal_deliveries_router)

@app.get("/")
async def root():
    return {"status": "ok", "message": "CryptoSignalBot API is running 🚀"}
