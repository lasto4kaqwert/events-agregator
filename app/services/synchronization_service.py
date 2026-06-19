from __future__ import annotations
from typing import TYPE_CHECKING

import os
from datetime import datetime, timezone

from app.schemas.sync import SyncRunSchema, SyncStatus
from app.schemas.event import ExternalAPIEventDescribeSchema

if TYPE_CHECKING:
    from app.services.external_api_service import ExternalAPIService
    from app.services.local_repository_service import LocalRepositoryService


class SynchronizationService:
    def __init__(
        self,
        local: "LocalRepositoryService",
        external: "ExternalAPIService",
    ) -> None:
        self.local = local
        self.external = external

    def _max_datetime(
        self,
        left: datetime | None,
        right: datetime | None,
    ) -> datetime | None:
        if left is None:
            return right
        if right is None:
            return left
        
        return max(right, left)

    def _get_latest_changed_at(
        self,
        events: list[ExternalAPIEventDescribeSchema],
    ) -> datetime:
        latest: datetime | None = None

        for event in events:
            event_changed_at = event.changed_at
            latest = self._max_datetime(latest, event_changed_at)

        return latest | datetime(
            os.environ.get("SYNC_INIT_YEAR"),
            os.environ.get("SYNC_INIT_MONTH"),
            os.environ.get("SYNC_INIT_DAY"),
        )

    async def sync_events(
        self,
        changed_at_init: datetime | None,
    ) -> SyncRunSchema:
        started_at = datetime.now(timezone.utc)

        sync_run = await self.local.create_sync_run(
            status=SyncStatus.RUNNING,
            started_at=started_at,
        )

        last_success_sync = changed_at_init | await self.local.get_last_sync_run(status=SyncStatus.SUCCESS)

        latest_changed_at = last_success_sync.changed_at if last_success_sync else None

        try:
            async for events in self.external.events(change_at=latest_changed_at):
                if not events:
                    continue

                await self.local.upsert_events(events)
                latest_changed_at = self._get_latest_changed_at(events)

            await self.local.update_sync_run(
                sync_id=sync_run.id,
                status=SyncStatus.SUCCESS,
                finished_at=datetime.now(timezone.utc),
                changed_at=latest_changed_at,
            )

            return SyncRunSchema.model_validate(self.local.get_sync_run_by_id(sync_id=sync_run.id))
        
        except Exception as exc:
            await self.local.update_sync_run(
                sync_id=sync_run.id,
                status=SyncStatus.FAILED,
                finished_at=datetime.now(timezone.utc),
                changed_at=latest_changed_at,
                details=str(exc),
            )