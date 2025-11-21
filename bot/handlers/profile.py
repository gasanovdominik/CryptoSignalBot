import html
import os

import requests
from aiogram import Router, types, F

router = Router()

BACKEND_URL = os.getenv("BACKEND_URL")


def _get_user_and_sub(tg_id: int):
    """
    Помощник: тянем /users/me и /subscriptions/{user_id} из backend.
    """
    if not BACKEND_URL:
        raise RuntimeError("BACKEND_URL not set")

    # 1) /users/me?tg_id=
    resp_user = requests.get(
        f"{BACKEND_URL}/users/me",
        params={"tg_id": tg_id},
        timeout=10,
    )
    resp_user.raise_for_status()
    user = resp_user.json()

    # 2) /subscriptions/{user_id}
    sub = None
    try:
        resp_sub = requests.get(
            f"{BACKEND_URL}/subscriptions/{user['id']}",
            timeout=10,
        )
        if resp_sub.status_code == 200:
            sub = resp_sub.json()
    except Exception:
        sub = None

    return user, sub


@router.callback_query(F.data == "menu_profile")
async def show_profile(callback: types.CallbackQuery):
    if not BACKEND_URL:
        await callback.message.edit_text(
            "⚠️ BACKEND_URL не настроен.", parse_mode="HTML"
        )
        return

    try:
        user, sub = _get_user_and_sub(callback.from_user.id)
    except Exception as e:
        safe_error = html.escape(str(e))
        await callback.message.edit_text(
            f"⚠️ Ошибка при загрузке профиля:\n<code>{safe_error}</code>",
            parse_mode="HTML",
        )
        return

    role = user.get("role")
    tg_id = user.get("tg_id")
    full_name = user.get("full_name") or callback.from_user.full_name
    username = user.get("username") or callback.from_user.username

    if sub and sub.get("status") in ("active", "trial"):
        sub_status = "✅ Активна" if sub["status"] == "active" else "🧪 Пробная"
        sub_until = sub.get("end_at")
        sub_text = f"{sub_status} до <code>{sub_until}</code>"
    else:
        sub_text = "❌ Нет активной подписки"

    text = (
        "👤 <b>Профиль пользователя</b>\n\n"
        f"Имя: {html.escape(full_name or '—')}\n"
        f"Username: @{html.escape(username or '-')}\n"
        f"TG ID: <code>{tg_id}</code>\n"
        f"Роль в системе: <b>{role}</b>\n\n"
        f"💳 <b>Подписка:</b> {sub_text}\n\n"
        "⚙️ <b>Настройки:</b>"
    )

    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🌐 Язык", callback_data="profile_lang"
                ),
                types.InlineKeyboardButton(
                    text="🔔 Уведомления", callback_data="profile_notify"
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="🕓 Часовой пояс", callback_data="profile_timezone"
                ),
                types.InlineKeyboardButton(
                    text="⬅️ Назад", callback_data="back_to_main"
                ),
            ],
        ]
    )

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
