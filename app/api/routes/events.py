from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Request

from app.core.dependencies import (
    get_getter_event_usecase,
    get_getter_events_usecase,
    get_getter_seats_usecase,
)
from app.schemas.event import (
    LocalRepoEventDescribeSchema,
    LocalRepoEventsSchema,
)
from app.schemas.seat import LocalRepoAvaiableSeatsSchema

if TYPE_CHECKING:
    from app.usecases import (
        GetEventsUseCase,
        GetEventUseCase,
        GetSeatsUseCase,
    )

router = APIRouter(
    prefix="/events",
    tags=["events"],
)


@router.get("", response_model=LocalRepoEventsSchema)
async def get_events(
    request: Request,
    date_from: date | None = None,
    page: int = 1,
    page_size: int = 20,
    usecase: GetEventsUseCase = Depends(get_getter_events_usecase),
) -> LocalRepoEventsSchema:
    offset = (page - 1) * page_size

    events = await usecase.do(
        date_from=date_from,
        page=page,
        page_size=page_size,
    )

    next_url = None
    previous_url = None

    if offset + page_size < events.count:
        next_url = str(
            request.url.include_query_params(
                page=page + 1,
                page_size=page_size,
            )
        )
    if page > 1:
        previous_url = str(
            request.url.include_query_params(
                page=page - 1,
                page_size=page_size,
            )
        )

    events.next = next_url
    events.previous = previous_url

    return events


@router.get("/{event_id}", response_model=LocalRepoEventDescribeSchema)
async def get_event_by_id(
    event_id: uuid.UUID,
    usecase: GetEventUseCase = Depends(get_getter_event_usecase),
) -> LocalRepoEventDescribeSchema:
    return await usecase.do(
        event_id=event_id,
    )


@router.get("/{event_id}/seats", response_model=LocalRepoAvaiableSeatsSchema)
async def get_seats(
    event_id: uuid.UUID,
    usecase: GetSeatsUseCase = Depends(get_getter_seats_usecase),
) -> LocalRepoAvaiableSeatsSchema:
    seats = await usecase.do(
        event_id=event_id,
    )

    return LocalRepoAvaiableSeatsSchema(
        event_id=event_id,
        available_seats=seats.available_seats,
    )
