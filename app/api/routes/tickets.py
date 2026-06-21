from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from app.core.dependencies import (
    get_register_ticket_usecase,
    get_unregister_ticket_usecase,
)

from app.schemas.ticket import (
    ExternalAPICreateTicketSchema,
    LocalRepoCreateTicketSchema,
    CreatedTicketSchema,
    DeletedTicketSchema,
)

if TYPE_CHECKING:
    from app.usecases import (
        RegisterTicketUseCase,
        UnregisterTicketUseCase,
    )

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)


@router.post("", response_model=CreatedTicketSchema, status_code=201)
async def create_ticket(
    payload: LocalRepoCreateTicketSchema,
    usecase: RegisterTicketUseCase = Depends(get_register_ticket_usecase),
) -> CreatedTicketSchema:
    return await usecase.do(
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
    usecase: UnregisterTicketUseCase = Depends(get_unregister_ticket_usecase),
) -> DeletedTicketSchema:
    return await usecase.do(
        ticket_id=ticket_id,
    )