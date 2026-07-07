from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.error_tracking import error_tracking
from app.core.exceptions import (
    EventNotFoundError,
    SeatIsNotAvaiableError,
    SynchronizationNotFoundError,
    TicketIdempotencyConflictError,
    TicketNotFoundError,
)

error_tracking()

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
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(SeatIsNotAvaiableError)
async def seat_not_avaiable_handler(
    _: Request,
    exc: SeatIsNotAvaiableError,
):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(TicketNotFoundError)
async def ticket_not_found_handler(
    _: Request,
    exc: TicketNotFoundError,
):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(SynchronizationNotFoundError)
async def sync_not_found_handler(
    _: Request,
    exc: SynchronizationNotFoundError,
):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _: Request,
    exc: RequestValidationError,
):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(TicketIdempotencyConflictError)
async def ticket_idempotency_conflict_handler(
    _: Request,
    exc: TicketIdempotencyConflictError,
):
    return JSONResponse(status_code=409, content={"detail": str(exc)})
