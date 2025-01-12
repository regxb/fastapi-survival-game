from aiogram.utils.web_app import WebAppUser, safe_parse_webapp_init_data
from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from starlette import status

from app.core.config import BOT_TOKEN

api_key_header = APIKeyHeader(name="Authorization")


def check_auth(api_key: str = Security(api_key_header)) -> WebAppUser:
    try:
        data = safe_parse_webapp_init_data(BOT_TOKEN, api_key)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return data.user


def get_user_data_from_request(request: Request) -> WebAppUser:
    # user: WebAppInitData = getattr(request.state, "user", None)
    # return user.user
    user: WebAppUser = request.state.user
    return user
