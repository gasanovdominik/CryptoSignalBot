import asyncio
import os
import requests
from aiogram import Router, types, F
from dotenv import load_dotenv

router = Router()

# Загружаем BACKEND_URL из корневого .env
BACKEND_URL = os.getenv("BACKEND_URL")



@router.callback_query(F.data == "menu_signals")
async def show_signals(callback: types.CallbackQuery):
    await callback.message.edit_text("⏳ <i>Загружаем актуальные сигналы...</i>", parse_mode="HTML")
    await asyncio.sleep(0.6)

    try:
        response = requests.get(f"{BACKEND_URL}/signals")
        response.raise_for_status()
        signals = response.json()
    except Exception as e:
        await callback.message.edit_text(
            f"⚠️ Ошибка при загрузке сигналов:\n<code>{e}</code>",
            parse_mode="HTML"
        )
        return

    if not signals:
        await callback.message.edit_text("❌ Нет доступных сигналов.", parse_mode="HTML")
        return

    text = (
        "💹 <b>Актуальные торговые сигналы</b>\n\n"
        "Выбери интересующий актив ниже 👇"
    )

    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        *[
            [types.InlineKeyboardButton(
                text=f"💎 {s['symbol']} ({s['direction']})",
                callback_data=f"signal_{s['symbol']}"
            )]
            for s in signals
        ],
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)


@router.callback_query(F.data.startswith("signal_"))
async def show_signal_details(callback: types.CallbackQuery):
    symbol = callback.data.split("_", 1)[1]

    try:
        response = requests.get(f"{BACKEND_URL}/signals")
        response.raise_for_status()
        signals = response.json()
        s = next((sig for sig in signals if sig["symbol"] == symbol), None)
    except Exception as e:
        await callback.message.edit_text(
            f"⚠️ Ошибка при получении сигнала:\n<code>{e}</code>",
            parse_mode="HTML"
        )
        return

    if not s:
        await callback.answer("Сигнал не найден", show_alert=True)
        return

    text = (
        f"💎 <b>{s['symbol']}</b> — {s['market']}\n"
        f"{'🟢 LONG' if s['direction'] == 'LONG' else '🔴 SHORT'}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Вход:</b> <code>{s['entry']}</code>\n"
        f"🛑 <b>Stop-Loss:</b> <code>{s['sl']}</code>\n"
        f"🎯 <b>Take-Profit:</b> <code>{s['tp']}</code>\n"
        f"⚖️ <b>R:R:</b> {s['rr']}   •   <b>Риск:</b> {s['risk']}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🧠 <i>{s['comment']}</i>"
    )

    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="⏰ Напомнить", callback_data=f"remind_{s['symbol']}"),
            types.InlineKeyboardButton(text="⭐ В избранное", callback_data=f"fav_{s['symbol']}")
        ],
        [
            types.InlineKeyboardButton(
                text="📈 Открыть на бирже",
                url=f"https://www.binance.com/en/trade/{s['symbol']}"
            )
        ],
        [
            types.InlineKeyboardButton(text="⬅️ Назад к списку", callback_data="menu_signals")
        ]
    ])

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)


@router.callback_query(F.data.startswith("remind_"))
async def remind_signal(callback: types.CallbackQuery):
    await callback.answer("⏰ Напоминание установлено!", show_alert=True)


@router.callback_query(F.data.startswith("fav_"))
async def add_favorite(callback: types.CallbackQuery):
    await callback.answer("⭐ Добавлено в избранное", show_alert=True)




