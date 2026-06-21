from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.repositories.event_repository import EventRepository


class GetEventsUseCase:
    def __init__(
        self,
        repo: "EventRepository",
    ) -> None:
        self.repo = repo

    async def do(
        self,
        date_from: datetime | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> None:
        pagination = await self.repo.get(
            date_from=date_from,
            page=page,
            page_size=page_size,
        )

        return pagination