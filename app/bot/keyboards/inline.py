from aiogram.types import WebAppInfo, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.config import WEB_APP_URL


def web_app() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Начать играть", web_app=WebAppInfo(url=str(WEB_APP_URL)))
    kb.button(text='📚Гайд', callback_data='instructions')
    return kb.as_markup()
