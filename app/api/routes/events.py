from datetime import date

from fastapi import APIRouter, Depends

from app.services.agregator_service import AgregatorService
from app.core.dependencies import get_agregator_service

from app.schemas.event import (
    LocalRepoEventsSchema,
    LocalRepoEventDescribeSchema,
)
from app.schemas.seat import ExternalAPIAvaiableSeatsSchema

router = APIRouter(
    prefix="/events",
    tags=["events"],
)


@router.get("", response_model=LocalRepoEventsSchema)
async def get_events(
    date_from: date | None = None,
    page: int = 1,
    page_size: int = 20,
    service: AgregatorService = Depends(get_agregator_service),
) -> LocalRepoEventsSchema:
    return await service.get_events(
        date_from=date_from,
        page=page,
        page_size=page_size,
    )


@router.get("/{event_id}", response_model=LocalRepoEventDescribeSchema)
async def get_event_by_id(
    event_id: str,
    service: AgregatorService = Depends(get_agregator_service),
) -> LocalRepoEventDescribeSchema:
    return await service.get_event_by_id(
        event_id=event_id,
    )


@router.get("/{event_id}/seats", response_model=ExternalAPIAvaiableSeatsSchema)
async def get_seats(
    event_id: str,
    service: AgregatorService = Depends(get_agregator_service),
) -> ExternalAPIAvaiableSeatsSchema:
    return await service.get_avaiable_seats(
        event_id=event_id,
    )