from uuid import UUID

from pydantic import BaseModel


class CreateTicketResponse(BaseModel):
    ticket_id: UUID


class CreateTicketRequest(BaseModel):
    event_id: UUID
    first_name: str
    last_name: str
    email: str
    seat: str


class DeleteTicketResponse(BaseModel):
    success: bool