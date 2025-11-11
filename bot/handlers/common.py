from aiogram import Router, types, F
from keyboards.main_menu import get_main_menu

router = Router()

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text("🏠 Главное меню:", reply_markup=get_main_menu())

