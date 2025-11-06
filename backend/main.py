from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CryptoSignal Backend")

# Разрешаем запросы с фронта/бота
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Пример данных (тестовый сигнал)
SIGNALS = [
    {
        "symbol": "BTCUSDT",
        "direction": "long",
        "entry": {"min": 67200, "max": 67500},
        "sl": 66900,
        "tps": [67800, 68000, 68200],
    },
    {
        "symbol": "ETHUSDT",
        "direction": "short",
        "entry": {"min": 3800, "max": 3820},
        "sl": 3835,
        "tps": [3790, 3770, 3750],
    },
]

@app.get("/health")
async def health():
    """Проверка статуса API"""
    return {"status": "ok"}

@app.get("/signals")
async def get_signals():
    """Отдаём список сигналов"""
    return SIGNALS

