from aiogram import Router, types, F

router = Router()

@router.callback_query(F.data == "menu_settings")
async def show_settings(callback: types.CallbackQuery):
    text = (
        "⚙️ <b>Настройки</b>\n\n"
        "Управляй параметрами бота:\n"
        "🌐 Язык интерфейса\n"
        "🔔 Уведомления о сигналах\n"
        "🕓 Часовой пояс отображения\n"
        "📱 Интеграции с биржами (в разработке)\n\n"
        "Выбери опцию ниже 👇"
    )

    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="🌐 Язык", callback_data="profile_lang"),
            types.InlineKeyboardButton(text="🔔 Уведомления", callback_data="profile_notify")
        ],
        [
            types.InlineKeyboardButton(text="🕓 Часовой пояс", callback_data="profile_timezone"),
            types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")
        ]
    ])

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
