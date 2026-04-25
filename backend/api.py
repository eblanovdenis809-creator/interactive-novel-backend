from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os
import json
import logging

from .db import init_db, get_progress, save_progress

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
WEBAPP_URL = os.environ.get("WEBAPP_URL", "")

# --- Aiogram 3.x bot setup (only if TOKEN is provided) ---
bot = None
dp = None

if TOKEN:
    from aiogram import Bot, Dispatcher, types, F
    from aiogram.filters import Command
    from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

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


# --- FastAPI lifespan: init DB + set Telegram webhook ---
@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    init_db()
    if bot and TOKEN:
        render_url = os.environ.get("RENDER_EXTERNAL_URL", "")
        if render_url:
            webhook_url = f"{render_url}/webhook/{TOKEN}"
            await bot.set_webhook(webhook_url)
            logging.info("Telegram webhook set: %s", webhook_url)
    yield
    if bot:
        await bot.session.close()


app = FastAPI(title="Story Progress API + Bot", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- REST API for progress ---
class ProgressIn(BaseModel):
    user_id: int
    scene_id: str
    end_id: str | None = None

@app.get("/progress/{user_id}")
def read_progress(user_id: int):
    data = get_progress(user_id)
    if not data:
        return {"scene_id": None, "end_id": None}
    return data

@app.post("/progress")
def update_progress(p: ProgressIn):
    save_progress(p.user_id, p.scene_id, p.end_id)
    return {"status": "ok"}


# --- Telegram webhook endpoint ---
@app.post("/webhook/{token}")
async def telegram_webhook(token: str, request: Request):
    if token != TOKEN:
        return {"error": "unauthorized"}
    if not bot or not dp:
        return {"error": "bot not configured"}
    from aiogram import types as tg_types
    data = await request.json()
    update = tg_types.Update.model_validate(data, context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
def root():
    return {"status": "running", "service": "interactive-novel-api"}
