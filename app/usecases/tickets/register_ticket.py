from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.schemas.ticket import (
    RegisteredTicketSchema,
    RegisterTicketSchema,
)

if TYPE_CHECKING:
    from app.services import (
        SeatsCache as SCache,
    )
    from app.services import (
        TicketService,
    )


class RegisterTicketUsecase:
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
        seat: str,
    ) -> None:
        seats = self.cache.get(event_id=event_id)
        if seats is not None:
            seats = seats.remove(seat)
            self.cache.set(
                event_id=event_id,
                seats=seats,
            )

    async def do(
        self,
        event_id: uuid.UUID,
        payload: RegisterTicketSchema,
    ) -> RegisteredTicketSchema:
        ticket = await self.service.reserve_ticket(event_id, payload)

        self._trial_cache(event_id, payload.seat)

        return RegisteredTicketSchema(
            ticket_id=ticket.ticket_id,
        )
