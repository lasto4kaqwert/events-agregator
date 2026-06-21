from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.core.exceptions import TicketNotFoundError
from app.schemas.ticket import (
    DeletedTicketSchema,
    ExternalAPIDeleteTicketSchema,
)

if TYPE_CHECKING:
    from app.clients.events_provider_client import EventsProviderClient
    from app.repositories.ticket_repository import TicketRepository
    from app.services.seats_cache import SeatsCache


class UnregisterTicketUseCase:
    def __init__(
        self,
        repo: "TicketRepository",
        client: "EventsProviderClient",
        cache: "SeatsCache",
    ) -> None:
        self.repo = repo
        self.client = client
        self.cache = cache

    async def do(self, ticket_id: uuid.UUID) -> DeletedTicketSchema:
        ticket = await self.repo.get(ticket_id=ticket_id)

        success = await self.client.unregister(
            event_id=ticket.event_id,
            payload=ExternalAPIDeleteTicketSchema(
                ticket_id=ticket_id,
            ),
        )

        if success.success is True:
            await self.repo.delete(ticket_id=ticket_id)
            self.cache.delete(event_id=ticket.event_id)
        else:
            raise TicketNotFoundError(f"Ticket {ticket_id} not found")

        return success
