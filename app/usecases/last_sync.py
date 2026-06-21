from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends

from app.schemas.sync import SyncRunSchema, SyncStatus

if TYPE_CHECKING:
    from app.repositories.sync_repository import SyncRepository


class LastSyncUseCase:
    def __init__(
        self,
        sync_repo: "SyncRepository",
    ):
        self.sync_repo = sync_repo

    async def do(
        self,
    ) -> SyncRunSchema:
        last_sync = await self.sync_repo.get()

        return last_sync