from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import (
    OutboxEventType,
    OutboxStatus,
)
from app.core.exceptions import (
    CapashinoError,
    CapashinoIdempotencyParsedError,
    CapashinoRepeatEncounterError,
)
from app.schemas.capashino import CapashinoRequestSchema
from app.schemas.outbox import (
    CapashinoProcessingOutbox,
    OutboxRepositorySchema,
)

if TYPE_CHECKING:
    from logging import Logger

    from app.clients.capashino_client import CapashinoClient
    from app.services.repositories import OutboxRepository


class CapashinoOutboxPorcessor:
    def __init__(
        self,
        session: AsyncSession,
        capashino: "CapashinoClient",
        outbox_repo: "OutboxRepository",
    ) -> None:
        self.session = session
        self.capashino = capashino
        self.outbox_repo = outbox_repo

    async def run(
        self,
        logger: "Logger" | None = None,
    ) -> int:
        async with self.session.begin():
            batch = await self.outbox_repo.acquire_batch(
                limit=2,
                timeout_retry_seconds=30,
                prefix_type="capashino",
            )

        if logger:
            logger.info("Capashino outbox batch size: %s", len(batch))

        for message in batch:
            await self.process_message(message, logger=logger)

        return len(batch)

    async def process_message(
        self,
        message: OutboxRepositorySchema,
        logger: "Logger" | None = None,
    ) -> None:
        try:
            if message.type == OutboxEventType.CAPASHINO_CREATED_TICKET:
                result = await self._process_capashino(message)
            elif message.type == OutboxEventType.CAPASHINO_CANCELED_TICKET:
                result = await self._process_capashino(message)
            else:
                result = CapashinoProcessingOutbox(
                    outbox_status=OutboxStatus.FAILED,
                )

            await self._apply_result(message, result)
        except Exception:
            if logger:
                logger.exception("Unexpected ticket outbox processing error")

            async with self.session.begin():
                await self.outbox_repo.update_status(
                    outbox_id=message.id,
                    status=OutboxStatus.PROCESSING,
                )

    async def _apply_result(
        self,
        message: OutboxRepositorySchema,
        result: CapashinoProcessingOutbox,
    ) -> None:
        async with self.session.begin():
            await self.outbox_repo.update_status(
                outbox_id=message.id,
                status=result.outbox_status,
            )

    async def _process_capashino(
        self,
        message: OutboxRepositorySchema,
    ) -> CapashinoProcessingOutbox:
        message_data = CapashinoRequestSchema.model_validate(message.payload)

        try:
            await self.capashino.send_message(message_data)
        except CapashinoIdempotencyParsedError:
            return CapashinoProcessingOutbox(
                outbox_status=OutboxStatus.CONFIRMED,
            )
        except CapashinoRepeatEncounterError:
            return CapashinoProcessingOutbox(
                outbox_status=OutboxStatus.PROCESSING,
            )
        except CapashinoError:
            return CapashinoProcessingOutbox(
                outbox_status=OutboxStatus.FAILED,
            )

        return CapashinoProcessingOutbox(
            outbox_status=OutboxStatus.CONFIRMED,
        )
