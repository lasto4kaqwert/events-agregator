from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.router import api_router

from app.core.exceptions import (
    EventNotFoundError,
    SeatIsNotAvaiableError,
    TicketNotFoundError,
    SynchronizationNotFoundError,
)


app = FastAPI(
    title="Events Agregator API",
    version="1.0.0",
)


app.include_router(api_router, prefix="/api")


@app.exception_handler(EventNotFoundError)
async def event_not_found_handler(
    _: Request,
    exc: EventNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )


@app.exception_handler(SeatIsNotAvaiableError)
async def seat_not_avaiable_handler(
    _: Request,
    exc: SeatIsNotAvaiableError,
):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)}
    )


@app.exception_handler(TicketNotFoundError)
async def ticket_not_found_handler(
    _: Request,
    exc: TicketNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )


@app.exception_handler(SynchronizationNotFoundError)
async def sync_not_found_handler(
    _: Request,
    exc: SynchronizationNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )