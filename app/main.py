from fastapi import FastAPI
from app.api.map_objects import router as maps_objects_router
from app.api.users import router as users_router
from app.api.players import router as players_router
from app.api.gameplay import router as gameplay_router

app = FastAPI()

app.include_router(maps_objects_router)
app.include_router(users_router)
app.include_router(players_router)
app.include_router(gameplay_router)
