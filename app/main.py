from contextlib import asynccontextmanager

from aiogram.utils.web_app import WebAppUser
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.bases import router as bases_router
from app.api.items import router as items_router
from app.api.maps import router as maps_router
from app.api.players import router as players_router
from app.api.resources import router as resources_router
from app.api.telegram import router as telegram_router
from app.bot.bot import bot, dp
from app.core.config import DEV, APP_URL, TG_SECRET
from app.depends.deps import check_auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await bot.set_webhook(url=str(APP_URL) + '/telegram/',
    #                       allowed_updates=dp.resolve_used_update_types(),
    #                       drop_pending_updates=True,
    #                       secret_token=TG_SECRET)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router=maps_router, dependencies=[Depends(check_auth)])
app.include_router(router=players_router, dependencies=[Depends(check_auth)])
app.include_router(router=bases_router, dependencies=[Depends(check_auth)])
app.include_router(router=items_router, dependencies=[Depends(check_auth)])
app.include_router(router=resources_router, dependencies=[Depends(check_auth)])
app.include_router(router=telegram_router)


class UserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not DEV:
            if request.url.path in ["/docs", "/redoc", "/openapi.json", '/telegram/']:
                return await call_next(request)
            token = request.headers.get("Authorization")
            if not token:
                return JSONResponse(status_code=401, content={"detail": "Token is missing"})
            try:
                request.state.user = check_auth(token)
            except HTTPException:
                return JSONResponse(status_code=401, content={"detail": "Invalid token"})
        else:
            request.state.user = WebAppUser(first_name="Tom", username="tom", id=111, photo_url="photo_url_tom")

        return await call_next(request)


app.add_middleware(UserMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
