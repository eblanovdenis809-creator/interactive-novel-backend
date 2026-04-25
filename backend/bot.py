"""
Local development: run the bot in polling mode.
In production (Render), use api.py which handles both API and webhook.
Usage: python -m backend.bot
"""
import os
import json
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from .db import init_db, save_progress

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://example.com/index.html")
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    btn = InlineKeyboardButton(
        text="Начать интерактивную новеллу",
        web_app=WebAppInfo(url=WEBAPP_URL),
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[btn]])
    await message.answer(
        "Добро пожаловать в интерактивную новеллу! "
        "Нажмите кнопку ниже, чтобы открыть веб-приложение.",
        reply_markup=keyboard,
    )

@dp.message(F.web_app_data)
async def web_app_data_handler(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
    except Exception:
        data = {}
    user_id = message.from_user.id
    scene = data.get("scene")
    end_id = data.get("end_id")
    if scene:
        save_progress(user_id, scene, end_id)
        await message.answer(f"Прогресс сохранён: сцена {scene}")
    else:
        await message.answer("Получены некорректные данные от веб-приложения.")

async def main():
    init_db()
    logging.info("Starting bot in polling mode (local dev)...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
