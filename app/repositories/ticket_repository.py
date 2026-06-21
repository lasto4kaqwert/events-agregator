import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_session

from app.models.ticket import Ticket
from app.schemas.ticket import LocalRepoTicketSchema

from app.core.exceptions import TicketNotFoundError


class TicketRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def get(
        self,
        ticket_id: uuid.UUID,
    ) -> LocalRepoTicketSchema | None:
        stmt = select(Ticket.event_id).where(Ticket.ticket_id == ticket_id)

        result = await self.session.execute(stmt)
        event_id = result.scalar_one_or_none()

        if event_id is None:
            raise TicketNotFoundError(f"Ticket {ticket_id} not found")
        
        return LocalRepoTicketSchema(
            event_id=event_id,
            ticket_id=ticket_id,
        )
    
    async def delete(
        self,
        ticket_id: uuid.UUID,
    ) -> None:
        ticket = await self.session.get(Ticket, ticket_id)

        if ticket is None:
            raise TicketNotFoundError(f"Ticket {ticket_id} not found")

        await self.session.delete(ticket)
        await self.session.commit()

    async def create(
        self,
        event_id: uuid.UUID,
        ticket_id: uuid.UUID,
    ) -> None:
        ticket = Ticket(
            ticket_id=ticket_id,
            event_id=event_id,
        )

        self.session.add(ticket)
        await self.session.commit()