from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.schemas.ticket import (
    UnregisteredTicketSchema,
)

if TYPE_CHECKING:
    from app.services import (
        SeatsCache as SCache,
    )
    from app.services import (
        TicketService,
    )


class UnregisterTicketUseCase:
    def __init__(
        self,
        service: "TicketService",
        cache: "SCache",
    ) -> None:
        self.service = service
        self.cache = cache

    def _trial_cache(
        self,
        event_id: uuid.UUID,
    ) -> None:
        self.cache.delete(event_id)

    async def do(
        self,
        ticket_id: uuid.UUID,
    ) -> UnregisteredTicketSchema:
        ticket = await self.service.cancel_ticket(ticket_id)

        self._trial_cache(ticket.event_id)

        return UnregisteredTicketSchema(
            success=True,
        )
