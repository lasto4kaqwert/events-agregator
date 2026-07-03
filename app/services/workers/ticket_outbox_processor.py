from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import (
    OutboxEventType,
    OutboxStatus,
    TicketStatus,
)
from app.schemas.ticket import (
    RegisterTicketSchema,
    TicketOutboxCreateSchema,
    TicketRepositorySchema,
)

if TYPE_CHECKING:
    from logging import Logger

    from app.clients.events_provider_client import EventsProviderClient as EPC
    from app.schemas.outbox import OutboxRepositorySchema
    from app.services import TicketService
    from app.services.repositories import OutboxRepository


class TicketOutboxProcessor:
    def __init__(
        self,
        session: AsyncSession,
        client: "EPC",
        service: "TicketService",
        outbox_repo: "OutboxRepository",
    ) -> None:
        self.session = session
        self.client = client
        self.service = service
        self.outbox_repo = outbox_repo

    async def _handle_ticket_create_request(
        self,
        message: dict[str, Any],
        logger: Logger | None = None,
    ) -> OutboxStatus | None:
        message_data = TicketOutboxCreateSchema.model_validate(message)

        async with self.session.begin():
            ticket_model = await self.service.get(message_data.ticket_id)
            ticket = TicketRepositorySchema.model_validate(ticket_model)

        if ticket.status is TicketStatus.PENDING:
            try:
                registered_ticket = await self.client.register(
                    event_id=ticket.event_id,
                    payload=RegisterTicketSchema.model_validate(message_data.payload),
                )

                await self.service.confirm_ticket(
                    message_data.ticket_id,
                    external_ticket_id=registered_ticket.ticket_id,
                )

                return OutboxStatus.CONFIRMED
            except Exception as exc:
                if logger is not None:
                    logger.info("Can't register with error: %s", exc)
                return OutboxStatus.PENDING
        elif ticket.status is TicketStatus.CANCELED:
            return OutboxStatus.CANCELED

    async def _handle_ticket_cancle_request(
        self,
    ) -> None:
        pass

    def _outbox_model_log(
        self,
        schema: OutboxRepositorySchema,
    ) -> dict[str, str]:
        return {
            "id": schema.id,
            "type": schema.type.value,
            "status": schema.status.value,
        }

    async def process_message(
        self,
        message: OutboxRepositorySchema,
        logger: Logger | None = None
    ) -> None:
        status = OutboxStatus.FAILED

        if message.type == OutboxEventType.TICKET_CREATE_REQUEST:
            status = await self._handle_ticket_create_request(
                message.payload,
                logger=logger,
            )

        if message.type == OutboxEventType.TICKET_CANCEL_REQUEST:
            status = await self._handle_ticket_cancle_request(
                message.payload
            )

        if logger is not None:
            logger.info("%s set status %s", message.id, status.value)

        async with self.session.begin():
            await self.outbox_repo.update_status(
                message.id,
                status,
            )

    async def run(
        self,
        logger: Logger | None = None,
    ) -> None:
        async with self.session.begin():
            batch = await self.outbox_repo.acquire_batch(
                limit=2,
                timeout_retry_seconds=30,
            )
            if logger is not None:
                logger.info("%s: Batch size: %s", datetime.now(), len(batch))

        for message in batch:
            if logger is not None:
                logger.info("%s", self._outbox_model_log(message))
            await self.process_message(message, logger=logger)
