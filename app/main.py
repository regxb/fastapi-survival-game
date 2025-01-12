import os
from contextlib import asynccontextmanager, contextmanager

from aiogram.utils.web_app import WebAppInitData, WebAppUser
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.gameplay import router as gameplay_router
from app.api.maps import router as maps_router
from app.api.players import router as players_router
from app.core.config import BOT_TOKEN, DEV
from app.depends.deps import check_auth, get_user_data_from_request
from app.faststream.main import broker


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.connect()
    try:
        yield
    finally:
        await broker.close()

if not DEV:
    app = FastAPI(dependencies=[Depends(check_auth)], lifespan=lifespan)
else:
    app = FastAPI(lifespan=lifespan)

app.include_router(maps_router)
app.include_router(players_router)
app.include_router(gameplay_router)


class UserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not DEV:
            if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
                return await call_next(request)
            token = request.headers.get("Authorization")
            if not token:
                return JSONResponse(status_code=401, content={"detail": "Token is missing"})
            try:
                request.state.user = check_auth(token)
            except HTTPException:
                return JSONResponse(status_code=401, content={"detail": "Invalid token"})
        else:
            request.state.user = WebAppUser(first_name="Tom", username="tom", id=1, photo_url="photo_url_tom")

        return await call_next(request)


app.add_middleware(UserMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
