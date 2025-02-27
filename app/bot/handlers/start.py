from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.bot import dp
from app.bot.keyboards.inline import web_app


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer('🎲 Начни играть сейчас', reply_markup=web_app())
