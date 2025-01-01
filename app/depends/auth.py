from typing import Any

from aiogram.utils.web_app import safe_parse_webapp_init_data, WebAppInitData
from fastapi import Security, Request
from fastapi.security import APIKeyHeader
from fastapi import HTTPException
from starlette import status

from app.core.config import BOT_TOKEN

api_key_header = APIKeyHeader(name="Authorization")

token=BOT_TOKEN

async def check_auth(api_key: str = Security(api_key_header)) -> WebAppInitData:
     try:
          data = safe_parse_webapp_init_data(token, api_key)
     except ValueError:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
     return data


async def get_user_data_from_request(request: Request) -> dict[str, Any]:
     user: WebAppInitData = getattr(request.state, "user", None)
     user_data = user.model_dump()
     return user_data["user"]
