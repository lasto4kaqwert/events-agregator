import uuid
from datetime import datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    StringConstraints,
)

from app.core.enums import TicketStatus

NameStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
    ),
]

SeatStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=20,
    ),
]

IdempotencyKeyStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=128,
    ),
]


class ExternalAPIRegisterTicketSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: NameStr
    last_name: NameStr
    seat: SeatStr
    email: EmailStr

class RegisterTicketSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: NameStr
    last_name: NameStr
    seat: SeatStr
    email: EmailStr
    idempotency_key: IdempotencyKeyStr | None = None


class InRouteRegisterTicketSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: uuid.UUID
    first_name: NameStr
    last_name: NameStr
    seat: SeatStr
    email: EmailStr
    idempotency_key: IdempotencyKeyStr | None = None


class UnregisterTicketSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_id: uuid.UUID


class RegisteredTicketSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_id: uuid.UUID


class UnregisteredTicketSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    success: bool


class TicketRepositorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: uuid.UUID
    ticket_id: uuid.UUID
    external_ticket_id: uuid.UUID | None
    status: TicketStatus
    seat: str
    email: EmailStr
    created_at: datetime | None
    updated_at: datetime | None
    idempotency_key: str | None = None
    request_hash: str | None = None


class TicketOutboxCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: uuid.UUID
    ticket_id: uuid.UUID

    payload: RegisterTicketSchema


class TicketOutboxDeleteSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_id: uuid.UUID

    payload: UnregisterTicketSchema
