import asyncio
from aiogram import Router, types, F

router = Router()

REF_LINK = "https://bybit.com/register?ref=YOURCODE"

@router.callback_query(F.data == "menu_subscription")
async def show_subscription(callback: types.CallbackQuery):
    await callback.message.edit_text("⏳ <i>Загрузка тарифов...</i>", parse_mode="HTML")
    await asyncio.sleep(0.5)
    text = (
        "💎 <b>Подписка CryptoSignalBot</b>\n\n"
        "📊 <b>Доступ включает:</b>\n"
        "• Торговые сигналы и новости\n"
        "• Фильтры по монетам и таймфреймам\n"
        "• Реферальные бонусы и поддержка 24/7\n\n"
        "Выбери тариф ниже 👇"
    )

    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="💰 1 месяц — 10$", callback_data="sub_1m"),
            types.InlineKeyboardButton(text="💎 3 месяца — 27$ (-10%)", callback_data="sub_3m")
        ],
        [
            types.InlineKeyboardButton(text="🎁 Пробная неделя (через рефку)", url=REF_LINK)
        ],
        [
            types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")
        ]
    ])

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)


@router.callback_query(F.data.startswith("sub_"))
async def buy_subscription(callback: types.CallbackQuery):
    sub_type = callback.data.split("_")[1]
    if sub_type == "1m":
        msg = "✅ Подписка активирована на 1 месяц!"
    else:
        msg = "✅ Подписка активирована на 3 месяца (-10%)!"
    await callback.answer(msg, show_alert=True)
