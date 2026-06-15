from .events import router as events_router
from .sync import router as sync_router
from .tickets import router as tickets_router

routers = [
    events_router,
    sync_router,
    tickets_router,
]