from __future__ import annotations

from typing import TYPE_CHECKING

import os
from datetime import datetime, date, timezone

from app.schemas.sync import SyncRunSchema, SyncStatus
from app.schemas.event import ExternalAPIEventDescribeSchema
from app.services.events_paginator import EventsPaginator

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

    async def sync_events(
        self,
        changed_at_init: date | None = None,
    ) -> SyncRunSchema:
        started_at = datetime.now(timezone.utc)

        sync_run = await self.local.create_sync_run(
            status=SyncStatus.RUNNING,
            started_at=started_at,
        )

        latest_changed_at: datetime | None = None

        try:
            last_success_sync = await self.local.get_last_sync_run(
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

            async for event in EventsPaginator(
                external=self.external,
                changed_at=changed_at,
            ):
                batch.append(event)

                latest_changed_at = self._max_datetime(
                    latest_changed_at,
                    self._extract_changed_at(event.changed_at),
                )

                if len(batch) >= 100:
                    await self.local.upsert_events(batch)
                    batch.clear()

            if batch:
                await self.local.upsert_events(batch)

            updated = await self.local.update_sync_run(
                sync_id=sync_run.id,
                status=SyncStatus.SUCCESS,
                finished_at=datetime.now(timezone.utc),
                changed_at=latest_changed_at,
                describe=None,
            )

            return SyncRunSchema.model_validate(updated)

        except Exception as exc:
            await self.local.update_sync_run(
                sync_id=sync_run.id,
                status=SyncStatus.FAILED,
                finished_at=datetime.now(timezone.utc),
                changed_at=latest_changed_at,
                describe=self._normalize_error(exc),
            )

            failed = await self.local.session.get(type(sync_run), sync_run.id)

            return SyncRunSchema.model_validate(failed)