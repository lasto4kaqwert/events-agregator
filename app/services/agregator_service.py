from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
import os
from datetime import datetime

from app.schemas.event import LocalRepoEventsSchema, LocalRepoEventDescribeSchema
from app.schemas.seat import LocalRepoAvaiableSeatsSchema
from app.schemas.sync import SyncRunSchema
from app.schemas.ticket import (
    ExternalAPICreateTicketSchema, 
    ExternalAPIDeleteTicketSchema,
    CreatedTicketSchema,
    DeletedTicketSchema,
)

from app.core.exceptions import (
    EventNotFoundError,
    TicketNotFoundError,
    SeatIsNotAvaiableError,
    SynchronizationNotFoundError,
)

if TYPE_CHECKING:
    from app.services.local_repository_service import LocalRepositoryService
    from app.services.external_api_service import ExternalAPIService
    from app.services.synchronization_service import SynchronizationService


class AgregatorService:
    def __init__(
        self,
        local: "LocalRepositoryService",
        external: "ExternalAPIService",
        sync: "SynchronizationService",
    ) -> None:
        self.local = local
        self.external = external
        self.sync = sync

    async def get_events(
        self,
        date_from: datetime | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> LocalRepoEventsSchema:
        events_pagination = await self.local.get_events(
            date_from=date_from,
            page=page,
            page_size=page_size,
        )

        if not events_pagination:
            raise EventNotFoundError(
                f"Events with {date_from}, page: {page}, page_size: {page_size} not found."
            )

        return LocalRepoEventsSchema.model_validate(events_pagination)
    
    async def get_event_by_id(
        self,
        event_id: uuid.UUID,
    ) -> LocalRepoEventDescribeSchema:
        event = await self.local.get_event_by_id(event_id=event_id)

        if not event:
            raise EventNotFoundError(f"Event with event_id: {event_id} not found")
        
        return LocalRepoEventDescribeSchema.model_validate(event)
    
    async def get_avaiable_seats(
        self,
        event_id: uuid.UUID,
    ) -> LocalRepoAvaiableSeatsSchema:
        await self.get_event_by_id(event_id=event_id)

        seats_result = await self.external.seats(event_id=event_id)

        return LocalRepoAvaiableSeatsSchema(
            event_id=event_id,
            seats=seats_result.seats,
        )
    
    async def create_ticket(
        self,
        event_id,
        payload: ExternalAPICreateTicketSchema,
    ) -> CreatedTicketSchema:
        avaiable_seats = await self.get_avaiable_seats(event_id=event_id)

        if payload.seat not in avaiable_seats.seats:
            raise SeatIsNotAvaiableError(f"Seat {payload.seat} is not avaiable for {event_id}")
        
        ticket = await self.external.register(
            event_id=event_id,
            payload=payload,
        )
        if ticket.ticket_id:
            await self.local.create_ticket(
                event_id=event_id,
                ticket_id=ticket.ticket_id,
            )

        return CreatedTicketSchema.model_validate(ticket)
    
    async def delete_ticket(
        self,
        ticket_id: uuid.UUID,
    ) -> DeletedTicketSchema:
        event_id = await self.local.get_event_id_by_ticket(ticket_id=ticket_id)

        if not event_id:
            raise EventNotFoundError(f"Event with ticket_id: {ticket_id} not found")

        result = await self.external.unregister(
            event_id=event_id,
            payload=ExternalAPIDeleteTicketSchema(
                ticket_id=ticket_id,
            ),
        )
        if result.success is True:
            await self.local.delete_ticket(
                ticket_id=ticket_id,
            )
        else:
            raise TicketNotFoundError(f"Ticket {ticket_id} is not found for {event_id}")
        
        return DeletedTicketSchema.model_validate(result)
    
    async def get_last_sync(
        self,
    ) -> SyncRunSchema:
        sync = await self.local.get_last_sync_run()

        if not sync:
            raise SynchronizationNotFoundError(f"Sync not found")
        
        return SyncRunSchema.model_validate(sync)
    
    async def get_sync_by_id(
        self,
        sync_id: uuid.UUID,
    ) -> SyncRunSchema:
        sync = await self.local.get_sync_run_by_id(sync_id=sync_id)

        if not sync:
            raise SynchronizationNotFoundError(f"Sync with id: {sync_id} not found")
        
        return SyncRunSchema.model_validate(sync)
    
    async def run_sync(
        self,
    ) -> SyncRunSchema:
        sync = await self.sync.sync_events(
            changed_at_init=datetime(
                int(os.environ.get("SYNC_INIT_YEAR", "2000")),
                int(os.environ.get("SYNC_INIT_MONTH", "1")),
                int(os.environ.get("SYNC_INIT_DAY", "1")),
            )
        )

        return SyncRunSchema.model_validate(sync)