from datetime import date

from fastapi import APIRouter, HTTPException

from app.schemas.api import events as api_events
from pydantic import BaseModel

router = APIRouter(
    prefix="/events",
    tags=["events"],
)


@router.get("", response_model=api_events.EventsResponse)
async def get_events(
    date_from: date | None = None,
    page: int = 1,
    page_size: int = 1,
) -> api_events.EventsResponse:
    pass


@router.get("/{event_id}", response_model=api_events.SingleEventResponse)
async def get_single_event(
    event_id: str,
) -> api_events.SingleEventResponse:
    pass


@router.get("/{event_id}/seats", response_model=api_events.EventSeatsResponse)
async def get_seats_by_event(
    event_id: str,
) -> BaseModel:
    pass