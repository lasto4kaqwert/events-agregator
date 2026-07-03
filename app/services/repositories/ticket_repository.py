import uuid
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import TicketStatus
from app.core.exceptions import (
    TicketConflictError,
    TicketNotFoundError,
)
from app.models.ticket import TicketModel
from app.schemas.ticket import TicketRepositorySchema


class TicketRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def get(
        self,
        ticket_id: uuid.UUID,
    ) -> TicketModel:
        ticket = await self.session.get(TicketModel, ticket_id)

        if ticket is None:
            raise TicketNotFoundError(
                f"Ticker {ticket_id} not found"
            )
        return ticket

    async def create(
        self,
        payload: TicketRepositorySchema,
    ) -> TicketModel:
        try:
            ticket = await self.get(payload.ticket_id)
        except TicketNotFoundError:
            ticket = TicketModel(ticket_id=payload.ticket_id)
            self.session.add(ticket)

        ticket.event_id = payload.event_id
        ticket.status = payload.status
        ticket.seat = payload.seat
        ticket.email = payload.email
        ticket.created_at = datetime.now(timezone.utc)
        ticket.updated_at = datetime.now(timezone.utc)

        try:
            await self.session.flush()
        except IntegrityError as exc:
            raise TicketConflictError from exc

        return ticket

    async def update_status(
        self,
        status: TicketStatus,
        ticket_id: uuid.UUID | None = None,
        ticket: TicketModel | None = None,
    ) -> TicketModel:
        if ticket_id is not None:
            ticket = await self.get(ticket_id)

        if ticket is not None:
            ticket.status = status
            ticket.updated_at = datetime.now(timezone.utc)

            try:
                await self.session.flush()
            except IntegrityError as exc:
                raise TicketConflictError from exc

            return ticket
        else:
            raise TicketNotFoundError("Ticket is not received")

    async def update_extenal_id(
        self,
        external_ticket_id: uuid.UUID,
        ticket_id: uuid.UUID | None = None,
        ticket: TicketModel | None = None,
    ) -> TicketModel:
        if ticket_id is not None:
            ticket = await self.get(ticket_id)

        if ticket is not None:
            ticket.external_ticket_id = external_ticket_id
            ticket.updated_at = datetime.now(timezone.utc)

            try:
                await self.session.flush()
            except IntegrityError as exc:
                raise TicketConflictError from exc
        else:
            raise TicketNotFoundError("Ticket is not received")
