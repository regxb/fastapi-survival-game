from typing import Annotated

from aiogram import types
from fastapi import APIRouter, Header

from app.bot.bot import dp
from app.core.config import TG_SECRET
from app.main import bot

router = APIRouter(prefix="/telegram", tags=["Telegram"], include_in_schema=False)


@router.post("/")
async def bot_webhook(update: dict,
                      x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None) -> None:
    if x_telegram_bot_api_secret_token != TG_SECRET:
        return
    telegram_update = types.Update(**update)
    await dp.feed_webhook_update(bot=bot, update=telegram_update)
