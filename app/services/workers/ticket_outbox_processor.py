from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import (
    OutboxEventType,
    OutboxStatus,
    TicketStatus,
)
from app.core.exceptions import (
    TicketOccupiedError,
)
from app.schemas.capashino import CapashinoRequestSchema
from app.schemas.outbox import OutboxRepositorySchema, TicketProcessingOutbox
from app.schemas.ticket import (
    RegisterTicketSchema,
    TicketOutboxCreateSchema,
    TicketRepositorySchema,
)

if TYPE_CHECKING:
    from logging import Logger

    from app.clients.events_provider_client import EventsProviderClient as EPC
    from app.repositories.event_repository import EventRepository
    from app.services import TicketService
    from app.services.repositories import OutboxRepository


class TicketOutboxProcessor:
    def __init__(
        self,
        session: AsyncSession,
        client: "EPC",
        service: "TicketService",
        outbox_repo: "OutboxRepository",
        event_repo: "EventRepository",
    ) -> None:
        self.session = session
        self.client = client
        self.service = service
        self.outbox_repo = outbox_repo
        self.event_repo = event_repo

    async def run(
        self,
        logger: "Logger" | None = None,
    ) -> int:
        async with self.session.begin():
            batch = await self.outbox_repo.acquire_batch(
                limit=2,
                prefix_type="ticket",
                timeout_retry_seconds=30,
            )

        if logger:
            logger.info("Ticket outbox batch size: %s", len(batch))

        for message in batch:
            await self.process_message(message, logger=logger)

        return len(batch)

    async def process_message(
        self,
        message: "OutboxRepositorySchema",
        logger: "Logger" | None = None,
    ) -> None:
        try:
            if message.type == OutboxEventType.TICKET_CREATE_REQUEST:
                result = await self._process_ticket_create(message)
            elif message.type == OutboxEventType.TICKET_CANCEL_REQUEST:
                result = await self._process_ticket_cancel(message)
            else:
                result = TicketProcessingOutbox(
                    outbox_status=OutboxStatus.FAILED,
                )

            await self._apply_result(message, result)
        except Exception:
            if logger:
                logger.exception("Unexpected ticket outbox processing error")

            async with self.session.begin():
                await self.outbox_repo.update_status(
                    outbox_id=message.id,
                    status=OutboxStatus.PENDING,
                )

    async def _apply_result(
        self,
        message: "OutboxRepositorySchema",
        result: TicketProcessingOutbox,
    ) -> None:
        message_data = TicketOutboxCreateSchema.model_validate(message.payload)

        async with self.session.begin():
            if result.ticket_status == TicketStatus.CONFIRMED:
                if result.external_ticket_id is None:
                    raise ValueError(
                        "external_ticket_id is required for confirmet ticket."
                    )

                await self.service.confirm_ticket(
                    ticket_id=message_data.ticket_id,
                    external_ticket_id=result.external_ticket_id,
                )
            elif result.ticket_status == TicketStatus.CANCELED:
                await self.service.fail_ticket(
                    ticket_id=message_data.ticket_id,
                )

            await self.outbox_repo.update_status(
                outbox_id=message.id,
                status=result.outbox_status,
            )

            if result.create_capashino_outbox:
                await self.outbox_repo.create(
                    outbox_type=OutboxEventType.CAPASHINO_CREATED_TICKET,
                    payload=CapashinoRequestSchema(
                        message=result.capashino_message,
                        reference_id=message_data.ticket_id,
                        idempotency_key=f"ticket-created-{message_data.ticket_id}",
                    ).model_dump(mode="json"),
                )

    async def _process_ticket_create(
        self,
        message: "OutboxRepositorySchema",
    ) -> TicketProcessingOutbox:
        message_data = TicketOutboxCreateSchema.model_validate(message.payload)

        async with self.session.begin():
            ticket_model = await self.service.get(message_data.ticket_id)
            ticket = TicketRepositorySchema.model_validate(ticket_model)

        if ticket.status == TicketStatus.CANCELED:
            return TicketProcessingOutbox(
                outbox_status=OutboxStatus.CANCELED,
            )
        elif ticket.status == TicketStatus.CONFIRMED:
            return TicketProcessingOutbox(
                outbox_status=OutboxStatus.CONFIRMED,
            )

        try:
            registered_ticket = await self.client.register(
                event_id=ticket.event_id,
                payload=RegisterTicketSchema.model_validate(message_data.payload),
            )
        except TicketOccupiedError:
            return TicketProcessingOutbox(
                outbox_status=OutboxStatus.FAILED,
                ticket_status=TicketStatus.CANCELED,
            )
        except Exception:
            return TicketProcessingOutbox(
                outbox_status=OutboxStatus.PENDING,
            )

        async with self.session.begin():
            event = await self.event_repo.get_describe(ticket.event_id)

        return TicketProcessingOutbox(
            outbox_status=OutboxStatus.CONFIRMED,
            ticket_status=TicketStatus.CONFIRMED,
            external_ticket_id=registered_ticket.ticket_id,
            create_capashino_outbox=True,
            capashino_message=event.name,
        )

    async def _process_ticket_cancel(
        self,
        message: "OutboxRepositorySchema",
    ) -> None:
        return TicketProcessingOutbox(
            outbox_status=OutboxStatus.CONFIRMED,
            ticket_status=TicketStatus.CANCELED,
        )
