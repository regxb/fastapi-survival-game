from typing import Any

from aiogram.utils.web_app import safe_parse_webapp_init_data, WebAppInitData, WebAppUser
from fastapi import Security, Request, BackgroundTasks
from fastapi.security import APIKeyHeader
from fastapi import HTTPException
from starlette import status

from app.core.config import BOT_TOKEN

api_key_header = APIKeyHeader(name="Authorization")


async def check_auth(api_key: str = Security(api_key_header)) -> WebAppInitData:
    try:
        data = safe_parse_webapp_init_data(BOT_TOKEN, api_key)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return data.user


async def get_user_data_from_request(request: Request) -> WebAppUser:
    # user: WebAppInitData = getattr(request.state, "user", None)
    # return user.user
    user: WebAppUser = request.state.user
    return user
