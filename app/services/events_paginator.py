from __future__ import annotations

from datetime import date
from typing import AsyncIterator, TYPE_CHECKING

from app.schemas.event import ExternalAPIEventDescribeSchema

if TYPE_CHECKING:
    from app.services.external_api_service import ExternalAPIService


class EventsPaginator:
    def __init__(
        self,
        external: ExternalAPIService,
        changed_at: date,
    ) -> None:
        self.external = external
        self.changed_at = changed_at

    # def _url_to_https(
    #     self,
    #     url: str | None
    # ) -> str | None:
    #     if not url:
    #         return None
    #     return url.replace("http://", "https://")

    async def __aiter__(self) -> AsyncIterator[ExternalAPIEventDescribeSchema]:
        page = await self.external._fetch_events(
            changed_at=self.changed_at,
        )

        while True:
            for event in page.results:
                yield event

            if not page.next:
                break

            # page = await self.external._next_events(self._url_to_https(page.next))
            page = await self.external._next_events(page.next)