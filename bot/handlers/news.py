import asyncio
import html
import os

import requests
from aiogram import Router, types, F

router = Router()

BACKEND_URL = os.getenv("BACKEND_URL")


@router.callback_query(F.data == "menu_news")
async def news_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "⏳ <i>Загружаем последние новости...</i>", parse_mode="HTML"
    )
    await asyncio.sleep(0.6)

    text = (
        "📰 <b>Новости крипторынка</b>\n\n"
        "Выбери фильтр или просмотри все новости 👇"
    )

    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🔥 Важно", callback_data="news_list_hot"
                ),
                types.InlineKeyboardButton(
                    text="💰 BTC", callback_data="news_list_BTC"
                ),
                types.InlineKeyboardButton(
                    text="🌞 SOL", callback_data="news_list_SOL"
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="📋 Все новости", callback_data="news_list_all"
                )
            ],
            [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")],
        ]
    )

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)


def _fetch_news(callback: types.CallbackQuery, flt: str):
    """
    Вспомогательная функция: тянем новости из backend с ACL.
    """
    if not BACKEND_URL:
        raise RuntimeError("BACKEND_URL not set")

    params = {
        "tg_id": callback.from_user.id,
        "limit": 20,
    }

    # Фильтры совпадают с backend: symbol / tag
    if flt == "BTC":
        params["symbol"] = "BTC"
    elif flt == "SOL":
        params["symbol"] = "SOL"
    elif flt == "hot":
        params["tag"] = "important"

    resp = requests.get(f"{BACKEND_URL}/news/", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


@router.callback_query(F.data.startswith("news_list_"))
async def news_list(callback: types.CallbackQuery):
    flt = callback.data.split("_")[-1]

    try:
        items = _fetch_news(callback, flt if flt != "all" else "")
    except Exception as e:
        safe_error = html.escape(str(e))
        await callback.message.edit_text(
            f"⚠️ Ошибка при загрузке новостей:\n<code>{safe_error}</code>",
            parse_mode="HTML",
        )
        return

    if not items:
        await callback.message.edit_text(
            "❌ Нет доступных новостей (возможно, нет активной подписки).",
            parse_mode="HTML",
        )
        return

    text = "🗞 <b>Новости:</b>\n\n" + "\n".join(
        [f"• {n['title']}" for n in items]
    )

    kb_rows = [
        [
            types.InlineKeyboardButton(
                text=f"🔹 {n['title'][:25]}...",
                callback_data=f"news_{n['id']}",
            )
        ]
        for n in items
    ]
    kb_rows.append(
        [
            types.InlineKeyboardButton(
                text="⬅️ Фильтры", callback_data="menu_news"
            )
        ]
    )

    kb = types.InlineKeyboardMarkup(inline_keyboard=kb_rows)
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)


@router.callback_query(F.data.startswith("news_"))
async def news_details(callback: types.CallbackQuery):
    if not BACKEND_URL:
        await callback.message.edit_text(
            "⚠️ BACKEND_URL не настроен.", parse_mode="HTML"
        )
        return

    try:
        news_id = int(callback.data.split("_")[1])
    except Exception:
        await callback.answer("Некорректная новость", show_alert=True)
        return

    # Тянем пачку и ищем по id (для MVP)
    try:
        params = {
            "tg_id": callback.from_user.id,
            "limit": 50,
        }
        resp = requests.get(f"{BACKEND_URL}/news/", params=params, timeout=10)
        resp.raise_for_status()
        all_news = resp.json()
        n = next((x for x in all_news if x["id"] == news_id), None)
    except Exception as e:
        safe_error = html.escape(str(e))
        await callback.message.edit_text(
            f"⚠️ Ошибка при загрузке новости:\n<code>{safe_error}</code>",
            parse_mode="HTML",
        )
        return

    if not n:
        await callback.answer("Новость не найдена или нет доступа", show_alert=True)
        return

    text = (
        f"📰 <b>{n['title']}</b>\n\n"
        f"🔗 <a href=\"{n['url']}\">Читать подробнее</a>"
    )

    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="⬅️ К новостям", callback_data="menu_news"
                )
            ]
        ]
    )

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
