from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.schemas.seat import LocalRepoAvaiableSeatsSchema

if TYPE_CHECKING:
    from app.clients.events_provider_client import EventsProviderClient
    from app.repositories.event_repository import EventRepository


class GetSeatsUseCase:
    def __init__(
        self,
        repo: "EventRepository",
        client: "EventsProviderClient",
    ) -> None:
        self.repo = repo
        self.client = client

    async def do(
        self,
        event_id: uuid.UUID,
    ) -> None:
        await self.repo.get_describe(event_id=event_id)

        available_seats = await self.client.seats(event_id=event_id)

        return LocalRepoAvaiableSeatsSchema(
            event_id=event_id,
            available_seats=available_seats.seats,
        )