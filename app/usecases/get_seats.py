from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.schemas.seat import LocalRepoAvaiableSeatsSchema

if TYPE_CHECKING:
    from app.clients.events_provider_client import EventsProviderClient
    from app.repositories.event_repository import EventRepository
    from app.services.seats_cache import SeatsCache


class GetSeatsUseCase:
    def __init__(
        self,
        repo: "EventRepository",
        client: "EventsProviderClient",
        cache: "SeatsCache",
    ) -> None:
        self.repo = repo
        self.client = client
        self.cache = cache

    async def do(
        self,
        event_id: uuid.UUID,
    ) -> None:
        await self.repo.get_describe(event_id=event_id)

        cached_seats = self.cache.get(event_id=event_id)

        if cached_seats is not None:
            return LocalRepoAvaiableSeatsSchema(
                event_id=event_id,
                available_seats=cached_seats,
            )

        available_seats = await self.client.seats(event_id=event_id)

        self.cache.set(
            event_id=event_id,
            seats=available_seats.seats,
        )

        return LocalRepoAvaiableSeatsSchema(
            event_id=event_id,
            available_seats=available_seats.seats,
        )