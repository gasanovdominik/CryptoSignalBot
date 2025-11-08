import os
import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from httpx import AsyncClient
from dotenv import load_dotenv
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# 🔹 Загружаем .env по абсолютному пути
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, "envs", "bot.env")
load_dotenv(ENV_PATH)

# 🔹 Получаем токен и URL backend'а
TOKEN = os.getenv("TG_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

if not TOKEN:
    raise RuntimeError(f"❌ TG_BOT_TOKEN не найден в {ENV_PATH}")

# 🔹 Создаём объекты бота, диспетчера и роутера
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# 🔹 Кнопки
kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/signals")]
    ],
    resize_keyboard=True
)

# 🔹 /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я — CryptoSignalBot.\n"
        "Нажми /signals, чтобы получить тестовый сигнал 💹",
        reply_markup=kb
    )

# 🔹 /signals
@router.message(Command("signals"))
async def cmd_signals(message: types.Message):
    async with AsyncClient() as client:
        try:
            r = await client.get(f"{BACKEND_URL}/signals", timeout=10.0)
            r.raise_for_status()
            data = r.json()
            if not data:
                await message.answer("📉 Пока нет сигналов.")
                return
            first = data[0]
            text = (
                f"💰 {first['symbol']} | {first['direction'].upper()}\n"
                f"🎯 Entry: {first['entry']}\n"
                f"🛡 SL: {first['sl']}\n"
                f"📈 TPs: {first['tps']}"
            )
            await message.answer(text)
        except Exception as e:
            await message.answer(f"⚠️ Ошибка получения сигналов: {e}")

# 🔹 🔸 Фейковый HTTP-сервер для Render (чтобы не засыпал)
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

def run_ping_server():
    server = HTTPServer(("0.0.0.0", 10000), PingHandler)
    server.serve_forever()

threading.Thread(target=run_ping_server, daemon=True).start()

# 🔹 Основной запуск
async def main():
    print("🚀 Бот запущен и слушает Telegram...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


