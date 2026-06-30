from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, AsyncIterator

from app.schemas.event import ExternalAPIEventDescribeSchema

if TYPE_CHECKING:
    from app.clients.events_provider_client import EventsProviderClient


class EventsPaginator:
    def __init__(
        self,
        client: EventsProviderClient,
        changed_at: date,
    ) -> None:
        self.client = client
        self.changed_at = changed_at



    async def __aiter__(self) -> AsyncIterator[ExternalAPIEventDescribeSchema]:
        page = await self.client.fetch_events(
            changed_at=self.changed_at,
        )

        while True:
            for event in page.results:
                yield event

            if not page.next:
                break

            page = await self.client.next_events(page.next)
