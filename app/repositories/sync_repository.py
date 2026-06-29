import uuid
from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import SyncStatus
from app.core.exceptions import SynchronizationNotFoundError
from app.models.sync_run import SyncRun
from app.schemas.sync import SyncRunSchema


class SyncRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def get(
        self,
        sync_id: uuid.UUID | None = None,
        status: SyncStatus | None = None,
        limit: int = 1,
        raise_if_empty: bool = True,
    ) -> SyncRunSchema | list[SyncRunSchema] | None:
        stmt = select(SyncRun)

        if sync_id is not None:
            stmt = stmt.where(SyncRun.id == sync_id)
        if status is not None:
            stmt = stmt.where(SyncRun.status == status.value)

        stmt = stmt.order_by(desc(SyncRun.started_at)).limit(limit)

        result = await self.session.execute(stmt)
        syncs = result.scalars().all()

        if not syncs:
            if raise_if_empty:
                raise SynchronizationNotFoundError("Syncs with params not found")
            return None
        elif len(syncs) == 1:
            return SyncRunSchema.model_validate(syncs[0])
        else:
            return [SyncRunSchema.model_validate(sync) for sync in syncs]

    async def upsert(
        self,
        sync_id: uuid.UUID | None = None,
        status: SyncStatus | None = None,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
        changed_at: datetime | None = None,
        describe: str | None = None,
    ) -> SyncRunSchema:
        if sync_id is None:
            sync_id = uuid.uuid4()

        sync_run = await self.session.get(SyncRun, sync_id)

        if sync_run is None:
            sync_run = SyncRun(id=sync_id)
            self.session.add(sync_run)

        sync_run.status = status or sync_run.status or SyncStatus.RUNNING
        sync_run.started_at = (
            started_at or sync_run.started_at or datetime.now(timezone.utc)
        )
        sync_run.finished_at = finished_at or sync_run.finished_at
        sync_run.changed_at = changed_at or sync_run.changed_at
        sync_run.describe = describe or sync_run.describe

        await self.session.commit()
        await self.session.refresh(sync_run)

        return SyncRunSchema.model_validate(sync_run)
