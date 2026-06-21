import uuid
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    StringConstraints,
)

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


class ExternalAPICreateTicketSchema(BaseModel):
    first_name: NameStr
    last_name: NameStr
    seat: SeatStr
    email: EmailStr


class LocalRepoCreateTicketSchema(BaseModel):
    event_id: uuid.UUID
    first_name: NameStr
    last_name: NameStr
    seat: SeatStr
    email: EmailStr


class LocalRepoTicketSchema(BaseModel):
    event_id: uuid.UUID
    ticket_id: uuid.UUID


class ExternalAPIDeleteTicketSchema(BaseModel):
    ticket_id: uuid.UUID


class CreatedTicketSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_id: uuid.UUID


class DeletedTicketSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    success: bool
