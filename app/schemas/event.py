import uuid
from datetime import datetime

from pydantic import BaseModel

class ExternalAPIPlaceDescribeSchema(BaseModel):
    id: uuid.UUID
    name: str
    city: str
    address: str
    seats_pattern: str
    changed_at: datetime
    created_at: datetime


class LocalRepoPlaceDescribeSchema(BaseModel):
    id: uuid.UUID
    name: str
    city: str
    address: str
    seats_pattern: str


class ExternalAPIEventDescribeSchema(BaseModel):
    id: uuid.UUID
    name: str
    place: ExternalAPIPlaceDescribeSchema
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int
    changed_at: datetime
    created_at: datetime
    status_changed_at: datetime


class LocalRepoEventDescribeSchema(BaseModel):
    id: uuid.UUID
    name: str
    place: LocalRepoPlaceDescribeSchema
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int


class ExternalAPIEventsSchema(BaseModel):
    next: str | None = None
    previous: str | None = None
    results: list[ExternalAPIEventDescribeSchema]

class LocalRepoEventsSchema(BaseModel):
    count: int
    next: str | None = None
    previous: str | None = None
    results: list[LocalRepoEventDescribeSchema]