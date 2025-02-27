from aiogram import Dispatcher, Bot

from app.core.config import BOT_TOKEN

bot = Bot(token=str(BOT_TOKEN))
dp = Dispatcher()
