from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.schemas.ticket import (
    CreatedTicketSchema,
    ExternalAPICreateTicketSchema,
)

if TYPE_CHECKING:
    from app.clients.events_provider_client import EventsProviderClient
    from app.repositories.ticket_repository import TicketRepository
    from app.services.seats_cache import SeatsCache


class RegisterTicketUseCase:
    def __init__(
        self,
        repo: "TicketRepository",
        client: "EventsProviderClient",
        cache: "SeatsCache",
    ) -> None:
        self.repo = repo
        self.client = client
        self.cache = cache

    async def do(
        self,
        event_id: uuid.UUID,
        payload: ExternalAPICreateTicketSchema,
    ) -> CreatedTicketSchema:
        ticket = await self.client.register(
            event_id=event_id,
            payload=payload,
        )

        if ticket.ticket_id:
            await self.repo.create(
                ticket_id=ticket.ticket_id,
                event_id=event_id,
            )

            seats = self.cache.get(event_id=event_id)
            if seats is not None:
                seats = seats.remove(payload.seat)
                self.cache.set(
                    event_id=event_id,
                    seats=seats,
                )

        return ticket
