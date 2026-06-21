from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.schemas.sync import SyncRunSchema

if TYPE_CHECKING:
    from app.repositories.sync_repository import SyncRepository


class GetSyncUseCase:
    def __init__(
        self,
        sync_repo: "SyncRepository",
    ):
        self.sync_repo = sync_repo

    async def do(
        self,
        sync_id: uuid.UUID,
    ) -> SyncRunSchema:
        sync = await self.sync_repo.get(sync_id=sync_id)

        return sync