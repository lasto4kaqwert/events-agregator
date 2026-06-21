from __future__ import annotations

import os
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

from app.schemas.event import ExternalAPIEventDescribeSchema
from app.schemas.sync import SyncRunSchema, SyncStatus

if TYPE_CHECKING:
    from app.clients.events_provider_client import EventsProviderClient
    from app.repositories.event_repository import EventRepository
    from app.repositories.sync_repository import SyncRepository


class TriggerSyncUseCase:
    def __init__(
        self,
        sync_repo: "SyncRepository",
        event_repo: "EventRepository",
        client: "EventsProviderClient",
    ) -> None:
        self.sync_repo = sync_repo
        self.event_repo = event_repo
        self.client = client

    def _normalize_error(self, error: Exception) -> str:
        msg = str(error)
        if not msg:
            msg = repr(error)
        return f"{type(error).__name__}: {msg}"[:1000]

    def _max_datetime(
        self,
        left: datetime | None,
        right: datetime | None,
    ) -> datetime | None:
        if left is None:
            return right
        if right is None:
            return left
        return max(left, right)

    def _get_init_date(self, changed_at_init: date | None) -> date:
        if changed_at_init:
            return changed_at_init

        return date(
            int(os.environ.get("SYNC_INIT_YEAR", "2000")),
            int(os.environ.get("SYNC_INIT_MONTH", "1")),
            int(os.environ.get("SYNC_INIT_DAY", "1")),
        )

    def _extract_changed_at(self, dt: datetime | None) -> datetime | None:
        if dt is None:
            return None

        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)

        return dt

    async def do(
        self,
        changed_at_init: date | None = None,
    ) -> SyncRunSchema:
        sync_run = await self.sync_repo.upsert()

        latest_changed_at: datetime | None = None

        try:
            last_success_sync = await self.sync_repo.get(
                status=SyncStatus.SUCCESS,
                raise_if_empty=False,
            )

            if last_success_sync and last_success_sync.changed_at:
                changed_at = last_success_sync.changed_at.date()
                latest_changed_at = self._extract_changed_at(
                    last_success_sync.changed_at
                )
            else:
                changed_at = self._get_init_date(changed_at_init)

            batch: list[ExternalAPIEventDescribeSchema] = []

            async for event in self.client.iter_events(
                changed_at=changed_at,
            ):
                batch.append(event)

                latest_changed_at = self._max_datetime(
                    latest_changed_at,
                    self._extract_changed_at(event.changed_at),
                )

                if len(batch) >= 100:
                    await self.event_repo.upsert(batch)
                    batch.clear()

            if batch:
                await self.event_repo.upsert(batch)

            updated = await self.sync_repo.upsert(
                sync_id=sync_run.id,
                status=SyncStatus.SUCCESS,
                finished_at=datetime.now(timezone.utc),
                changed_at=latest_changed_at,
                describe=None,
            )

            return SyncRunSchema.model_validate(updated)

        except Exception as exc:
            failed = await self.sync_repo.upsert(
                sync_id=sync_run.id,
                status=SyncStatus.FAILED,
                finished_at=datetime.now(timezone.utc),
                changed_at=latest_changed_at,
                describe=self._normalize_error(exc),
            )

            return failed
