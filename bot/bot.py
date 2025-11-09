import os
import asyncio
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.types import (
    KeyboardButton, ReplyKeyboardMarkup,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from httpx import AsyncClient
from dotenv import load_dotenv
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# === ENV ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, "envs", "bot.env")
load_dotenv(ENV_PATH)

TOKEN = os.getenv("TG_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
API_KEY = os.getenv("API_KEY")
HEADERS = {"X-API-KEY": API_KEY}
BOT_VERSION = os.getenv("BOT_VERSION", "v1.0")

if not TOKEN:
    raise RuntimeError("❌ TG_BOT_TOKEN не найден в bot.env")

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# === Клавиатура ===
kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/signals"), KeyboardButton(text="/stats")],
        [KeyboardButton(text="/addsignal"), KeyboardButton(text="/status")]
    ],
    resize_keyboard=True
)



# === FSM ===
class AddSignalForm(StatesGroup):
    waiting_for_signal = State()

class EditSignalForm(StatesGroup):
    waiting_for_data = State()
    signal_id = State()

# === /start ===
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я — CryptoSignalBot.\n"
        "💹 /signals — активные сигналы\n"
        "➕ /addsignal — добавить сигнал (только админ)",
        reply_markup=kb
    )

# === /signals ===
@router.message(Command("signals"))
async def cmd_signals(message: types.Message):
    async with AsyncClient() as client:
        try:
            r = await client.get(f"{BACKEND_URL}/signals", timeout=10.0)
            r.raise_for_status()
            data = r.json()
            if not data:
                await message.answer("📉 Пока нет сигналов.")
                return

            for s in data:
                text = (
                    f"💰 {s['symbol']} | {s['direction'].upper()}\n"
                    f"🎯 Entry: {s['entry_min']} - {s['entry_max']}\n"
                    f"🛡 SL: {s['sl']}\n"
                    f"📈 TPs: {s['tp1']}, {s['tp2']}, {s['tp3']}"
                )

                if message.from_user.id == ADMIN_ID:
                    kb_inline = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(text="✏ Изменить", callback_data=f"edit_{s['id']}"),
                                InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{s['id']}")
                            ]
                        ]
                    )
                    await message.answer(text, reply_markup=kb_inline)
                else:
                    await message.answer(text)
        except Exception as e:
            await message.answer(f"⚠️ Ошибка получения сигналов: {e}")

# === /addsignal ===
@router.message(Command("addsignal"))
async def cmd_addsignal(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У тебя нет прав для этой команды.")
        return

    await message.answer(
        "✏️ Введи сигнал:\n"
        "`SYMBOL,DIRECTION,ENTRY_MIN,ENTRY_MAX,SL,TP1,TP2,TP3`\n\n"
        "Пример:\n`BTCUSDT,long,67000,67500,66500,68000,68500,69000`",
        parse_mode="Markdown"
    )
    await state.set_state(AddSignalForm.waiting_for_signal)

@router.message(AddSignalForm.waiting_for_signal)
async def add_signal_data(message: types.Message, state: FSMContext):
    try:
        parts = [p.strip() for p in message.text.split(",")]
        if len(parts) != 8:
            await message.answer("⚠️ Неверный формат.")
            return

        payload = {
            "symbol": parts[0],
            "direction": parts[1],
            "entry_min": float(parts[2]),
            "entry_max": float(parts[3]),
            "sl": float(parts[4]),
            "tp1": float(parts[5]),
            "tp2": float(parts[6]),
            "tp3": float(parts[7]),
        }

        async with AsyncClient() as client:
            r = await client.post(f"{BACKEND_URL}/signals", json=payload)
            r.raise_for_status()

        await message.answer("✅ Сигнал добавлен!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    finally:
        await state.clear()

# === /stats ===
@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    async with AsyncClient() as client:
        try:
            r = await client.get(f"{BACKEND_URL}/stats", timeout=10.0)
            r.raise_for_status()
            stats = r.json()

            text = (
                f"📊 <b>Статистика сигналов</b>\n\n"
                f"📈 Всего сигналов: <b>{stats['total_signals']}</b>\n"
                f"🕓 Последнее обновление: <b>{stats['last_update']}</b>\n\n"
            )

            if stats["latest"]:
                text += "🧩 Последние сигналы:\n"
                for s in stats["latest"]:
                    text += (
                        f"• {s['symbol']} | {s['direction'].upper()} "
                        f"({s['entry_min']}–{s['entry_max']})\n"
                    )

            await message.answer(text, parse_mode="HTML")
        except Exception as e:
            await message.answer(f"⚠️ Ошибка получения статистики: {e}")
# === /status ===
@router.message(Command("status"))
async def cmd_status(message: types.Message):
    async with AsyncClient() as client:
        try:
            # Проверяем backend
            r = await client.get(f"{BACKEND_URL}/health", timeout=5.0)
            backend_status = "🟢 online" if r.status_code == 200 else "🔴 offline"
        except Exception:
            backend_status = "🔴 offline"

    api_status = "🔒 включена" if API_KEY else "⚠️ отсутствует"

    text = (
        f"📡 <b>Состояние системы</b>\n\n"
        f"🌐 Backend: {backend_status}\n"
        f"{'='*20}\n"
        f"🔑 API защита: {api_status}\n"
        f"🤖 Версия бота: <b>{BOT_VERSION}</b>"
    )

    await message.answer(text, parse_mode="HTML")

# === Callback: Удаление ===
@router.callback_query(F.data.startswith("delete_"))
async def delete_signal_callback(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Только админ может удалять!", show_alert=True)
        return

    signal_id = int(callback.data.split("_")[1])
    async with AsyncClient() as client:
        try:
            r = await client.delete(f"{BACKEND_URL}/signals/{signal_id}")
            if r.status_code == 200:
                await callback.message.edit_text("🗑 Сигнал удалён!")
            else:
                await callback.answer("❌ Ошибка удаления!", show_alert=True)
        except Exception as e:
            await callback.answer(f"⚠️ Ошибка: {e}", show_alert=True)

# === Callback: Изменение ===
@router.callback_query(F.data.startswith("edit_"))
async def edit_signal_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Только админ может изменять!", show_alert=True)
        return

    signal_id = int(callback.data.split("_")[1])
    await state.update_data(signal_id=signal_id)
    await state.set_state(EditSignalForm.waiting_for_data)
    await callback.message.answer(
        "✏ Введи новые значения сигнала в формате:\n"
        "`SYMBOL,DIRECTION,ENTRY_MIN,ENTRY_MAX,SL,TP1,TP2,TP3`",
        parse_mode="Markdown"
    )

@router.message(EditSignalForm.waiting_for_data)
async def process_edit_signal(message: types.Message, state: FSMContext):
    data = await state.get_data()
    signal_id = data.get("signal_id")
    try:
        parts = [p.strip() for p in message.text.split(",")]
        if len(parts) != 8:
            await message.answer("⚠️ Неверный формат данных.")
            return

        payload = {
            "symbol": parts[0],
            "direction": parts[1],
            "entry_min": float(parts[2]),
            "entry_max": float(parts[3]),
            "sl": float(parts[4]),
            "tp1": float(parts[5]),
            "tp2": float(parts[6]),
            "tp3": float(parts[7]),
        }

        async with AsyncClient() as client:
            r = await client.put(f"{BACKEND_URL}/signals/{signal_id}", json=payload)
            r.raise_for_status()

        await message.answer("✅ Сигнал успешно обновлён!")
    except Exception as e:
        await message.answer(f"❌ Ошибка при обновлении: {e}")
    finally:
        await state.clear()

# === Пинг-сервер для Render ===
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

def run_ping_server():
    server = HTTPServer(("0.0.0.0", 10000), PingHandler)
    server.serve_forever()

threading.Thread(target=run_ping_server, daemon=True).start()

# === MAIN ===
async def main():
    print("🚀 Бот запущен и слушает Telegram...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())




