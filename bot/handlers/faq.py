from aiogram import Router, types, F

router = Router()

FAQ_TEXT = (
    "❓ <b>FAQ / Поддержка</b>\n\n"
    "• <b>Что такое подписка?</b> — Доступ к сигналам, новостям и уведомлениям.\n"
    "• <b>Пробная неделя?</b> — Активируется через реферальную регистрацию на бирже.\n"
    "• <b>Риски?</b> — Торговля рискованна. Не инвестируй больше, чем готов потерять.\n\n"
    "Поддержка: @your_support"
)

@router.callback_query(F.data == "menu_faq")
async def faq(callback: types.CallbackQuery):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])
    # Используем HTML вместо Markdown, чтобы не падать на символах
    await callback.message.edit_text(FAQ_TEXT, parse_mode="HTML", reply_markup=kb)

