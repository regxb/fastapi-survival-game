from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.keyboards.inline import web_app

router = Router()
@router.message(CommandStart())
async def start(message: Message) -> None:
    description = (
        '<b>🎮 Добро пожаловать в игру!</b>\n\n'
        'Твое приключение начинается прямо сейчас! 🌍\n'
        'Прими участие в захватывающих битвах, фарме ресурсов и развивай своего персонажа! ⚔️\n\n'
        'Готов ли ты стать героем? 💪\n\n'
        'Нажми на кнопку ниже, чтобы начать и погрузиться в увлекательный мир! 🎲\n\n'
    )
    await message.answer(
        description,
        reply_markup=web_app(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == 'instructions')
async def instructions(message: Message) -> None:
    instructions_text = (
        '<b>📖 Инструкция по игре</b>\n\n'
        '<b>1️⃣ Начало:</b> После начала игры вы будете находиться в городе.Вам нужно добыть ресурсы и построить дом.\n\n'
        '<b>2️⃣ Фарминг:</b> Вам нужно собирать ресурсы, чтобы развиваться. Это может занять некоторое время.\n\n'
        '<b>3️⃣ Бои:</b> В момент фарма на вас может напасть зомби и между вами будет бой.🧟‍♂️\n\n'
        '<b>✨ Совет:</b> Не забывайте следить за состоянием персонажа, чтобы вовремя восстановить его здоровье и энергию! ⚡\n\n'
    )

    await message.answer(
        instructions_text,
        reply_markup=web_app(),
        parse_mode="HTML"
    )