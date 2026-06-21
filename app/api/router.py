from fastapi import APIRouter

from app.api.routes import routers

api_router = APIRouter()

for router in routers:
    api_router.include_router(router)
