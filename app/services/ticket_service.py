import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import OutboxEventType, TicketStatus
from app.core.exceptions import TicketIdempotencyConflictError
from app.core.idempotency import get_ticket_route_request_hash
from app.models.ticket import TicketModel
from app.schemas.ticket import (
    RegisterTicketSchema,
    TicketOutboxCreateSchema,
    TicketOutboxDeleteSchema,
    TicketRepositorySchema,
    UnregisteredTicketSchema,
)
from app.services.repositories import (
    OutboxRepository,
    TicketRepository,
)


class TicketService:
    def __init__(
        self,
        session: AsyncSession,
        ticket_repo: TicketRepository,
        outbox_repo: OutboxRepository,
    ) -> None:
        self.session = session

        self.ticket_repo = ticket_repo
        self.outbox_repo = outbox_repo

    async def get(
        self,
        ticket_id: uuid.UUID,
    ) -> TicketModel:
        return await self.ticket_repo.get(ticket_id)

    async def confirm_ticket(
        self,
        ticket_id: uuid.UUID,
        external_ticket_id: uuid.UUID,
    ) -> TicketModel:
        ticket = await self.get(ticket_id)

        await self.ticket_repo.update_extenal_id(
            external_ticket_id,
            ticket=ticket,
        )
        await self.ticket_repo.update_status(
            TicketStatus.CONFIRMED,
            ticket=ticket,
        )

        return ticket

    async def fail_ticket(
        self,
        ticket_id: uuid.UUID,
    ) -> TicketModel:
        ticket = await self.get(ticket_id)

        await self.ticket_repo.update_status(
            TicketStatus.CANCELED,
            ticket=ticket,
        )

        return ticket


    async def reserve_ticket(
        self,
        event_id: uuid.UUID,
        payload: RegisterTicketSchema,
    ) -> TicketModel:
        async with self.session.begin():
            idempotency_key = payload.idempotency_key
            request_hash: str | None = None

            if idempotency_key is not None:
                request_hash = get_ticket_route_request_hash(
                    event_id=event_id,
                    payload=payload,
                )

                existing_ticket = await self.ticket_repo.get_by_idempotency_key(
                    idempotency_key=idempotency_key,
                )

                if existing_ticket is not None:
                    if existing_ticket.request_hash != request_hash:
                        raise TicketIdempotencyConflictError

                    return existing_ticket

            ticket_id = uuid.uuid4()

            ticket = await self.ticket_repo.create(
                payload=TicketRepositorySchema(
                    event_id=event_id,
                    ticket_id=ticket_id,
                    external_ticket_id=None,
                    status=TicketStatus.PENDING,
                    seat=payload.seat,
                    email=payload.email,
                    created_at=None,
                    updated_at=None,
                    idempotency_key=idempotency_key,
                    request_hash=request_hash,
                )
            )

            await self.outbox_repo.create(
                outbox_type=OutboxEventType.TICKET_CREATE_REQUEST,
                payload=TicketOutboxCreateSchema(
                    event_id=event_id,
                    ticket_id=ticket_id,
                    payload=RegisterTicketSchema(
                        first_name=payload.first_name,
                        last_name=payload.last_name,
                        seat=payload.seat,
                        email=payload.email,
                        idempotency_key=idempotency_key,
                    ),
                ).model_dump(mode="json"),
            )

        return ticket

    async def cancel_ticket(
        self,
        ticket_id: uuid.UUID,
    ) -> TicketModel:
        async with self.session.begin():
            ticket = await self.ticket_repo.update_status(
                ticket_id=ticket_id,
                status=TicketStatus.CANCELED,
            )

            if ticket.external_ticket_id is not None:
                await self.outbox_repo.create(
                    outbox_type=OutboxEventType.TICKET_CANCEL_REQUEST,
                    payload=TicketOutboxDeleteSchema(
                        ticket_id=ticket_id,
                        payload=UnregisteredTicketSchema(
                            ticket_id=ticket.external_ticket_id,
                        ),
                    ).model_dump(mode="json"),
                )

        return ticket
