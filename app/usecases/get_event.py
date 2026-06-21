from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.repositories.event_repository import EventRepository


class GetEventUseCase:
    def __init__(
        self,
        repo: "EventRepository",
    ) -> None:
        self.repo = repo

    async def do(
        self,
        event_id: uuid.UUID,
    ) -> None:
        return await self.repo.get_describe(event_id=event_id)