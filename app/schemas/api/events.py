from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class EventPlace(BaseModel):
    id: UUID
    name: str
    city: str
    address: str
    seats_pattern: str


class EventResult(BaseModel):
    id: UUID
    name: str
    place: EventPlace
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int = Field(gt=0)


class EventsResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    results: list[EventResult]


class SingleEventResponse(BaseModel):
    id: UUID
    name: str
    place: EventPlace
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int = Field(gt=0)


class EventSeatsResponse(BaseModel):
    event_id: UUID
    available_seats: list[str]