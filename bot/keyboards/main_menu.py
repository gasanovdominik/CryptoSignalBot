from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👤 Профиль", callback_data="menu_profile"),
            InlineKeyboardButton(text="📈 Торговать", callback_data="menu_trade")
        ],
        [
            InlineKeyboardButton(text="🔔 Сигналы", callback_data="menu_signals"),
            InlineKeyboardButton(text="📰 Новости", callback_data="menu_news")
        ],
        [
            InlineKeyboardButton(text="💎 Подписка", callback_data="menu_subscription"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu_settings")
        ],
        [
            InlineKeyboardButton(text="❓ Поддержка", callback_data="menu_faq"),
            InlineKeyboardButton(text="⚠️ Риски", callback_data="menu_about")
        ]
    ])

