import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import (
    OutboxEventType,
    OutboxStatus,
)
from app.core.exceptions import (
    OutboxConflictError,
    OutboxNotFoundError,
)
from app.models.outbox import OutboxModel
from app.schemas.outbox import OutboxRepositorySchema


class OutboxRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create(
        self,
        outbox_type: OutboxEventType,
        payload: dict[str, Any],
    ) -> OutboxModel:
        outbox = OutboxModel(id=uuid.uuid4())
        self.session.add(outbox)

        outbox.type = outbox_type
        outbox.payload = payload
        outbox.status = OutboxStatus.PENDING
        outbox.created_at = datetime.now(timezone.utc)

        try:
            await self.session.flush()
        except IntegrityError as exc:
            raise OutboxConflictError from exc

        return outbox

    async def acquire_batch(
        self,
        limit: int = 10,
        timeout_retry_seconds: int = 300,
    ) -> list[OutboxRepositorySchema]:
        timeout_at = datetime.now(timezone.utc) - timedelta(
            seconds=timeout_retry_seconds,
        )

        stmt = (
            select(OutboxModel)
            .where(and_(
                OutboxModel.type.like("ticket.%"),
                or_(
                    OutboxModel.status == OutboxStatus.PENDING,
                    and_(
                        OutboxModel.status == OutboxStatus.PROCESSING,
                        OutboxModel.updated_at < timeout_at,
                    ),
                ),
            ))
            .order_by(OutboxModel.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        in_pending = await self.session.execute(stmt)
        batch = list(in_pending.scalars().all())

        now = datetime.now(timezone.utc)

        for outbox_message in batch:
            outbox_message.status = OutboxStatus.PROCESSING
            outbox_message.updated_at = now

        try:
            await self.session.flush()
        except IntegrityError as exc:
            raise OutboxConflictError from exc

        return [OutboxRepositorySchema.model_validate(msg) for msg in batch]

    async def update_status(
        self,
        outbox_id: uuid.UUID,
        status: OutboxStatus,
    ) -> OutboxModel:
        outbox = await self.session.get(OutboxModel, outbox_id)

        if outbox is None:
            raise OutboxNotFoundError(
                f"Outbox {outbox_id} not found"
            )

        outbox.status = status

        try:
            await self.session.flush()
        except IntegrityError as exc:
            raise OutboxConflictError from exc

        return outbox

