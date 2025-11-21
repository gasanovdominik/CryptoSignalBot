import asyncio
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.utils.mock_data import signals

router = Router()

# временное хранение выбора (на пользователя)
user_trade_state = {}  # {tg_id: {"market": "Spot"/"Futures", "pair": "BTCUSDT", "tf": "M15", "risk":"low"}}

@router.callback_query(F.data == "menu_trade")
async def trade_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("⏳ <i>Подготовка торгового модуля...</i>", parse_mode="HTML")
    await asyncio.sleep(0.6)

    text = "📈 <b>Выбери рынок для торговли:</b>"
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🟢 Спот", callback_data="trade_market_Spot")],
        [types.InlineKeyboardButton(text="🔴 Фьючерсы", callback_data="trade_market_Futures")],
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)

@router.callback_query(F.data.startswith("trade_market_"))
async def trade_choose_market(callback: types.CallbackQuery):
    tg = callback.from_user.id
    market = callback.data.split("_")[-1]
    user_trade_state.setdefault(tg, {})["market"] = market

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="BTCUSDT", callback_data="trade_pair_BTCUSDT"),
         InlineKeyboardButton(text="ETHUSDT", callback_data="trade_pair_ETHUSDT"),
         InlineKeyboardButton(text="SOLUSDT", callback_data="trade_pair_SOLUSDT")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_trade"),
         InlineKeyboardButton(text="Далее ➡️", callback_data="trade_next_tf")]
    ])
    await callback.message.edit_text(f"{market}: выбери пару", reply_markup=kb)

@router.callback_query(F.data == "trade_next_tf")
async def trade_choose_tf(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="M5", callback_data="trade_tf_M5"),
         InlineKeyboardButton(text="M15", callback_data="trade_tf_M15"),
         InlineKeyboardButton(text="H1", callback_data="trade_tf_H1")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_trade"),
         InlineKeyboardButton(text="Далее ➡️", callback_data="trade_next_risk")]
    ])
    await callback.message.edit_text("Выбери таймфрейм", reply_markup=kb)

@router.callback_query(F.data.startswith("trade_pair_"))
async def trade_set_pair(callback: types.CallbackQuery):
    tg = callback.from_user.id
    user_trade_state.setdefault(tg, {})["pair"] = callback.data.split("_")[-1]
    await callback.answer(f"Пара: {user_trade_state[tg]['pair']}")

@router.callback_query(F.data.startswith("trade_tf_"))
async def trade_set_tf(callback: types.CallbackQuery):
    tg = callback.from_user.id
    user_trade_state.setdefault(tg, {})["tf"] = callback.data.split("_")[-1]
    await callback.answer(f"ТФ: {user_trade_state[tg]['tf']}")

@router.callback_query(F.data == "trade_next_risk")
async def trade_choose_risk(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Низкий", callback_data="trade_risk_low"),
         InlineKeyboardButton(text="Средний", callback_data="trade_risk_mid"),
         InlineKeyboardButton(text="Высокий", callback_data="trade_risk_high")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_trade"),
         InlineKeyboardButton(text="✅ Получить сигнал", callback_data="trade_get_signal")]
    ])
    await callback.message.edit_text("Выбери риск-профиль", reply_markup=kb)

@router.callback_query(F.data.startswith("trade_risk_"))
async def trade_set_risk(callback: types.CallbackQuery):
    tg = callback.from_user.id
    user_trade_state.setdefault(tg, {})["risk"] = callback.data.split("_")[-1]
    await callback.answer(f"Риск: {user_trade_state[tg]['risk']}")

@router.callback_query(F.data == "trade_get_signal")
async def trade_get_signal(callback: types.CallbackQuery):
    tg = callback.from_user.id
    st = user_trade_state.get(tg, {"market":"Spot","pair":"BTCUSDT"})
    market = st["market"] or "Spot"
    pair = st["pair"]

    # простейший фильтр по market/pair (моки)
    found = next((s for s in signals if s["market"] == market and s["symbol"] == pair), None)
    if not found:
        await callback.answer("Нет подходящих сигналов", show_alert=True)
        return

    text = (
        f"💎 *{found['symbol']}* ({found['market']}, {found['direction']})\n"
        f"💰 Вход: `{found['entry']}`\n"
        f"🛑 SL: `{found['sl']}`\n"
        f"🎯 TP: `{found['tp']}`\n"
        f"⚖️ R:R: {found['rr']} • Риск {found['risk']}\n"
        f"🧠 {found['comment']}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ К фильтрам", callback_data="menu_trade")],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_main")],
    ])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)

