from aiogram import Router, types, F

router = Router()

ABOUT = (
    "ℹ️ <b>О нас</b>\n\n"
    "CryptoSignalBot — сигналы, новости и аналитика по споту и фьючерсам.\n"
    "Интеграции: Binance / Bybit / MEXC (read-only в MVP).\n"
    "Подписки: 1 мес, 3 мес (−10%), пробная неделя через реф.\n"
)

@router.callback_query(F.data == "menu_about")
async def about(callback: types.CallbackQuery):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])
    await callback.message.edit_text(ABOUT, parse_mode="HTML", reply_markup=kb)

