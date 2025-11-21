import os
import requests

from aiogram import Router, types
from aiogram.filters import CommandStart
from bot.keyboards.main_menu import get_main_menu

router = Router()

BACKEND_URL = os.getenv("BACKEND_URL")


@router.message(CommandStart())
async def start_command(message: types.Message):
    """
    Старт: регистрируем/обновляем пользователя в backend,
    чтобы у него был user_id, роль, подписка и т.д.
    """
    if BACKEND_URL:
        try:
            payload = {
                "tg_id": message.from_user.id,
                "username": message.from_user.username,
                "full_name": message.from_user.full_name,
                "email": None,
                "lang": "ru",
                "tz": "Europe/Berlin",
                "role": "guest",
            }
            # create_or_get_user
            resp = requests.post(f"{BACKEND_URL}/users/", json=payload, timeout=5)
            resp.raise_for_status()
        except Exception:
            # Для MVP просто молчим, чтобы не ломать UX
            pass

    text = (
        "🎉 <b>Добро пожаловать в CryptoSignalBot!</b>\n\n"
        "🔓 <b>Полный доступ к функциям:</b>\n"
        "📈 Торговля — Спот и Фьючерсы\n"
        "🔔 Сигналы — реальные торговые идеи\n"
        "📰 Новости — по монетам и важным событиям\n"
        "⚙️ Настройки — язык, уведомления и интеграции\n\n"
        "👇 <b>Выбирай раздел для начала работы:</b>"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_menu())

