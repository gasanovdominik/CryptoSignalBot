import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from aiogram.fsm.storage.memory import MemoryStorage
import os

from keyboards.main_menu import get_main_menu
from handlers import start, trade, signals, news, profile, subscription, common, faq, about, settings

load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())

# 🔧 Подключаем каждый router отдельно
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

@dp.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer(
        "👋 Привет, трейдер!\n\n"
        "Я — CryptoSignalBot 💎\n"
        "Выбирай раздел ниже 👇",
        reply_markup=get_main_menu()
    )

async def main():
    logging.info("🚀 Бот запущен и слушает обновления...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

