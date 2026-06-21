import uuid

from pydantic import BaseModel, EmailStr, ConfigDict


class ExternalAPICreateTicketSchema(BaseModel):
    first_name: str
    last_name: str
    seat: str
    email: EmailStr

class LocalRepoCreateTicketSchema(BaseModel):
    event_id: uuid.UUID
    first_name: str
    last_name: str
    seat: str
    email: EmailStr


class ExternalAPIDeleteTicketSchema(BaseModel):
    ticket_id: uuid.UUID


class CreatedTicketSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_id: uuid.UUID


class DeletedTicketSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    success: bool