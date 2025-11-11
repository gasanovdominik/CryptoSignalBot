import asyncio
from aiogram import Router, types, F
from utils.mock_data import news

router = Router()

# Главное меню новостей
@router.callback_query(F.data == "menu_news")
async def news_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("⏳ <i>Загружаем последние новости...</i>", parse_mode="HTML")
    await asyncio.sleep(0.6)

    text = (
        "📰 <b>Новости крипторынка</b>\n\n"
        "Выбери фильтр или просмотри все новости 👇"
    )

    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="🔥 Важно", callback_data="news_list_hot"),
            types.InlineKeyboardButton(text="💰 BTC", callback_data="news_list_BTC"),
            types.InlineKeyboardButton(text="🌞 SOL", callback_data="news_list_SOL")
        ],
        [types.InlineKeyboardButton(text="📋 Все новости", callback_data="news_list_all")],
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)


# Список новостей
@router.callback_query(F.data.startswith("news_list_"))
async def news_list(callback: types.CallbackQuery):
    flt = callback.data.split("_")[-1]
    items = news
    if flt == "BTC":
        items = [n for n in news if "BTC" in n.get("symbols", [])]
    elif flt == "SOL":
        items = [n for n in news if "SOL" in n.get("symbols", [])]
    elif flt == "hot":
        items = [n for n in news if n.get("important")]

    text = "🗞 <b>Новости:</b>\n\n" + "\n".join(
        [f"• {n['title']}" for n in items]
    )

    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text=f"🔹 {n['title'][:25]}...",
                callback_data=f"news_{i}"
            )
        ]
        for i, n in enumerate(items)
    ] + [[types.InlineKeyboardButton(text="⬅️ Фильтры", callback_data="menu_news")]])

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)


# Детальная новость
@router.callback_query(F.data.startswith("news_"))
async def news_details(callback: types.CallbackQuery):
    idx = int(callback.data.split("_")[1])
    n = news[idx]
    text = (
        f"📰 <b>{n['title']}</b>\n\n"
        f"🔗 <a href=\"{n['url']}\">Читать подробнее</a>"
    )

    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="⬅️ К новостям", callback_data="menu_news")]
    ])

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)


