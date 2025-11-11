from aiogram import Router, types, F

router = Router()

@router.callback_query(F.data == "menu_profile")
async def show_profile(callback: types.CallbackQuery):
    text = (
        "👤 <b>Профиль пользователя</b>\n\n"
        "Имя: тестовый пользователь\n"
        "ID: <code>123456789</code>\n"
        "Роль: <b>Подписчик</b>\n\n"
        "⚙️ <b>Настройки:</b>"
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


@router.callback_query(F.data == "profile_lang")
async def change_language(callback: types.CallbackQuery):
    await callback.answer("🌐 Язык: Русский", show_alert=True)

@router.callback_query(F.data == "profile_notify")
async def change_notify(callback: types.CallbackQuery):
    await callback.answer("🔔 Уведомления: Вкл", show_alert=True)

@router.callback_query(F.data == "profile_timezone")
async def change_timezone(callback: types.CallbackQuery):
    await callback.answer("🕓 Часовой пояс: Europe/Berlin", show_alert=True)
