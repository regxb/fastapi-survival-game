from aiogram import Dispatcher, Bot

from app.bot.handlers.start import router
from app.core.config import BOT_TOKEN

bot = Bot(token=str(BOT_TOKEN))
dp = Dispatcher()
dp.include_router(router)
