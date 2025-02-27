from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.keyboards.inline import web_app

router = Router()
@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer('🎲 Начни играть сейчас', reply_markup=web_app())
