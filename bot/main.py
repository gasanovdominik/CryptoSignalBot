import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from keyboards.main_menu import get_main_menu
from handlers import start, trade, signals, news, profile, subscription, common, faq, about, settings

# === 🧩 Загружаем переменные окружения (.env) ===
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")

if not BOT_TOKEN or not BACKEND_URL:
    raise ValueError("❌ BOT_TOKEN или BACKEND_URL не найдены в .env!")

# === 🔧 Логирование и инициализация ===
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# === 🔌 Подключение роутеров ===
dp.include_router(start.router)
dp.include_router(trade.router)
dp.include_router(signals.router)
dp.include_router(news.router)
dp.include_router(profile.router)
dp.include_router(subscription.router)
dp.include_router(settings.router)
dp.include_router(faq.router)
dp.include_router(about.router)
dp.include_router(common.router)

# === Команда /start ===
@dp.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer(
        "👋 Привет, трейдер!\n\n"
        "Я — CryptoSignalBot 💎\n"
        "Выбирай раздел ниже 👇",
        reply_markup=get_main_menu()
    )

# === Точка входа ===
async def main():
    logging.info(f"🚀 Бот запущен и слушает обновления...\nBackend: {BACKEND_URL}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


