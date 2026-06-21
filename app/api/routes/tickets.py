import uuid
from fastapi import APIRouter, Depends

from app.services.agregator_service import AgregatorService
from app.core.dependencies import get_agregator_service

from app.schemas.ticket import (
    ExternalAPICreateTicketSchema,
    LocalRepoCreateTicketSchema,
    CreatedTicketSchema,
    DeletedTicketSchema,
)

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)


@router.post("", response_model=CreatedTicketSchema)
async def create_ticket(
    payload: LocalRepoCreateTicketSchema,
    service: AgregatorService = Depends(get_agregator_service),
) -> CreatedTicketSchema:
    return await service.create_ticket(
        event_id=payload.event_id,
        payload=ExternalAPICreateTicketSchema(
            first_name=payload.first_name,
            last_name=payload.last_name,
            seat=payload.seat,
            email=payload.email,
        )
    )


@router.delete("/{ticket_id}", response_model=DeletedTicketSchema)
async def delete_ticket(
    ticket_id: uuid.UUID,
    service: AgregatorService = Depends(get_agregator_service),
) -> DeletedTicketSchema:
    return await service.delete_ticket(
        ticket_id=ticket_id,
    )