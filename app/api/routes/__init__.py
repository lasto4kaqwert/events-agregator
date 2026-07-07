from .events import router as events_router
from .health import router as health_router
from .sync import router as sync_router
from .tickets import router as tickets_router
from .debug import router as debug_router


routers = [
    events_router,
    sync_router,
    tickets_router,
    health_router,
    debug_router,
]
