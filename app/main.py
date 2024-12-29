from fastapi import FastAPI
from app.api.map_objects import router as maps_router

app = FastAPI()

app.include_router(maps_router)
