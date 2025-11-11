from aiogram import Router, types, F
from aiogram.filters import CommandStart
from keyboards.main_menu import get_main_menu

router = Router()

@router.message(CommandStart())
async def start_command(message: types.Message):
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
