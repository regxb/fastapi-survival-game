from aiogram.utils.web_app import WebAppInitData
from fastapi.responses import JSONResponse

from fastapi import FastAPI, HTTPException, Depends
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware

from app.api.maps import router as maps_router
from app.api.users import router as users_router
from app.api.players import router as players_router
from app.api.gameplay import router as gameplay_router
from app.depends.auth import check_auth

app = FastAPI(dependencies=[Depends(check_auth)])

app.include_router(maps_router)
app.include_router(users_router)
app.include_router(players_router)
app.include_router(gameplay_router)


class UserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        token = request.headers.get("Authorization")
        if not token:
            return JSONResponse(status_code=401, content={"detail": "Token is missing"})
        try:
            request.state.user = await check_auth(token)
        except HTTPException:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})
        return await call_next(request)


app.add_middleware(UserMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
