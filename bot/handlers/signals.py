import asyncio
import html
import os

import requests
from aiogram import Router, types, F

router = Router()

BACKEND_URL = os.getenv("BACKEND_URL")


@router.callback_query(F.data == "menu_signals")
async def show_signals(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "⏳ <i>Загружаем актуальные сигналы...</i>", parse_mode="HTML"
    )
    await asyncio.sleep(0.3)

    if not BACKEND_URL:
        await callback.message.edit_text(
            "⚠️ BACKEND_URL не настроен.", parse_mode="HTML"
        )
        return

    try:
        params = {
            "tg_id": callback.from_user.id,
            "limit": 20,
        }
        response = requests.get(
            f"{BACKEND_URL}/signals/", params=params, timeout=10
        )
        response.raise_for_status()
        signals = response.json()
    except Exception as e:
        safe_error = html.escape(str(e))
        await callback.message.edit_text(
            f"⚠️ Ошибка при загрузке сигналов:\n<code>{safe_error}</code>",
            parse_mode="HTML",
        )
        return

    if not signals:
        await callback.message.edit_text(
            "❌ Нет доступных сигналов (возможно, нет активной подписки).",
            parse_mode="HTML",
        )
        return

    text = (
        "💹 <b>Актуальные торговые сигналы</b>\n\n"
        "Выбери интересующий актив ниже 👇"
    )

    # Кнопки по каждому сигналу
    kb_rows = []
    for s in signals:
        symbol = s.get("symbol", "UNKNOWN")
        direction = str(s.get("direction", "")).upper()
        btn_text = f"💎 {symbol} ({direction})"
        kb_rows.append(
            [
                types.InlineKeyboardButton(
                    text=btn_text,
                    callback_data=f"signal_{symbol}",
                )
            ]
        )

    kb_rows.append(
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    )

    kb = types.InlineKeyboardMarkup(inline_keyboard=kb_rows)

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)


@router.callback_query(F.data.startswith("signal_"))
async def show_signal_details(callback: types.CallbackQuery):
    symbol = callback.data.split("_", 1)[1]

    if not BACKEND_URL:
        await callback.message.edit_text(
            "⚠️ BACKEND_URL не настроен.", parse_mode="HTML"
        )
        return

    try:
        params = {
            "tg_id": callback.from_user.id,
            "symbol": symbol,
            "limit": 1,
        }
        response = requests.get(
            f"{BACKEND_URL}/signals/", params=params, timeout=10
        )
        response.raise_for_status()
        data = response.json()
        s = data[0] if data else None
    except Exception as e:
        safe_error = html.escape(str(e))
        await callback.message.edit_text(
            f"⚠️ Ошибка при получении сигнала:\n<code>{safe_error}</code>",
            parse_mode="HTML",
        )
        return

    if not s:
        await callback.answer("Сигнал не найден или нет доступа", show_alert=True)
        return

    # direction в БД: "long" / "short"
    direction_raw = str(s.get("direction", "")).lower()
    is_long = direction_raw == "long"

    entry = s.get("entry")
    sl = s.get("sl")
    tps = s.get("tps", [])
    risk_pct = s.get("risk_pct")
    comment = s.get("comment")

    text = (
        f"💎 <b>{s.get('symbol')}</b> — {s.get('market')}\n"
        f"{'🟢 LONG' if is_long else '🔴 SHORT'}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Вход:</b> <code>{entry}</code>\n"
        f"🛑 <b>Stop-Loss:</b> <code>{sl}</code>\n"
        f"🎯 <b>Take-Profit:</b> <code>{tps}</code>\n"
        f"⚖️ <b>Риск %:</b> {risk_pct}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🧠 <i>{comment}</i>"
    )

    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="⏰ Напомнить", callback_data=f"remind_{s.get('id')}"
                ),
                types.InlineKeyboardButton(
                    text="⭐ В избранное", callback_data=f"fav_{s.get('id')}"
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="📈 Открыть на бирже",
                    url=f"https://www.binance.com/en/trade/{s.get('symbol')}",
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="⬅️ Назад к списку", callback_data="menu_signals"
                )
            ],
        ]
    )

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
