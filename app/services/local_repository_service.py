import uuid
from datetime import datetime, timezone

from fastapi import Depends

from sqlalchemy import func, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_session

from app.models.event import Event
from app.models.ticket import Ticket
from app.models.sync_run import SyncRun
from app.schemas.event import (
    LocalRepoEventDescribeSchema, 
    LocalRepoPlaceDescribeSchema,
    LocalRepoEventsSchema,
)
from app.schemas.sync import SyncRunSchema, SyncStatus

from app.core.exceptions import (
    EventNotFoundError,
    TicketNotFoundError,
    SynchronizationNotFoundError,
)


class LocalRepositoryService:
    def __init__(
        self,
        session: AsyncSession = Depends(get_session)
    ) -> None:
        self.session = session

    def _map_event_to_schema(
        self,
        event: Event,
    ) -> LocalRepoEventDescribeSchema:
        return LocalRepoEventDescribeSchema(
            id=event.id,
            name=event.name,
            place=LocalRepoPlaceDescribeSchema.model_validate(event.place),
            event_time=event.event_time,
            registration_deadline=event.registration_deadline,
            status=event.status,
            number_of_visitors=event.number_of_visitors,
        )

    async def get_sync_run_by_id(
        self,
        sync_id: uuid.UUID,
    ) -> SyncRunSchema:
        sync_run = await self.session.get(SyncRun, sync_id)

        if not sync_run:
            raise SynchronizationNotFoundError(f"Sync run {sync_id} not found")
        
        return SyncRunSchema.model_validate(sync_run)

    async def get_last_sync_run(
        self,
        status: SyncStatus | None = None,
        raise_if_empty: bool = True,
    ) -> SyncRunSchema:
        stmt = select(SyncRun)

        if status is not None:
            stmt = stmt.where(SyncRun.status == status.value)

        stmt = stmt.order_by(desc(SyncRun.started_at)).limit(1)

        result = await self.session.execute(stmt)
        sync_run = result.scalar_one_or_none()

        if not sync_run:
            if raise_if_empty:
                raise SynchronizationNotFoundError("Sync run not found")
            return None

        return SyncRunSchema.model_validate(sync_run)

    async def create_sync_run(
        self,
        status: SyncStatus,
        started_at: datetime,
        finished_at: datetime | None = None,
        changed_at: datetime | None = None,
        describe: str | None = None,
    ) -> SyncRun:
        sync_id = uuid.uuid4()

        sync_run = SyncRun(
            id=sync_id,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            changed_at=changed_at,
            describe=describe,
        )

        self.session.add(sync_run)
        await self.session.commit()
        await self.session.refresh(sync_run)

        return sync_run

    async def update_sync_run(
        self,
        sync_id: uuid.UUID,
        status: SyncStatus | None,
        finished_at: datetime | None,
        changed_at: datetime | None,
        describe: str | None = None,
    ) -> SyncRun:
        sync_run = await self.session.get(SyncRun, sync_id)

        if not sync_run:
            raise SynchronizationNotFoundError(f"Sync run {sync_id} not found")
        
        sync_run.status = status
        sync_run.finished_at = finished_at
        sync_run.changed_at = changed_at
        sync_run.describe = describe

        await self.session.commit()
        await self.session.refresh(sync_run)

        return sync_run

    async def get_events(
        self,
        date_from: datetime | None,
        page: int,
        page_size: int,
    ) -> LocalRepoEventsSchema:
        offset = (page - 1) * page_size

        stmt = select(Event)
        if date_from is not None:
            stmt = stmt.where(Event.event_time >= date_from)
        total_stmt = select(func.count()).select_from(stmt.subquery())

        total_result = await self.session.execute(total_stmt)
        total = total_result.scalar_one()

        stmt = (
            stmt.order_by(Event.event_time.desc())
            .limit(page_size)
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        events = result.scalars().all()

        return LocalRepoEventsSchema(
            count=total,
            next=None,
            previous=None,
            results=[self._map_event_to_schema(event) for event in events],
        )

    async def get_event_by_id(
        self,
        event_id: uuid.UUID,
    ) -> LocalRepoEventDescribeSchema:
        stmt = select(Event).where(Event.id == event_id)
        result = await self.session.execute(stmt)
        event = result.scalar_one_or_none()

        if not event:
            raise EventNotFoundError(f"Event with id: {event_id} not found")
        
        return self._map_event_to_schema(event)

    async def upsert_events(
        self,
        events: list[LocalRepoEventDescribeSchema],
    ) -> int:
        saved_count = 0

        for event_describe in events:
            event_id = event_describe.id

            event = await self.session.get(Event, event_id)
            if not event:
                event = Event(id=event_id)
                self.session.add(event)

            event.place = event_describe.place.model_dump(mode="json")
            event.name = event_describe.name
            event.event_time = event_describe.event_time
            event.registration_deadline = event_describe.registration_deadline
            event.status = event_describe.status
            event.number_of_visitors = event_describe.number_of_visitors

            saved_count += 1

        await self.session.commit()

        return saved_count

    async def get_event_id_by_ticket(
        self,
        ticket_id: uuid.UUID,
    ) -> uuid.UUID:
        stmt = (
            select(Ticket.event_id)
            .where(Ticket.ticket_id == ticket_id)
        )

        result = await self.session.execute(stmt)
        event_id = result.scalar_one_or_none()

        if not event_id:
            raise TicketNotFoundError(f"Ticket with id {ticket_id} not found")
        
        return event_id

    async def create_ticket(
        self,
        event_id: uuid.UUID,
        ticket_id: uuid.UUID,
    ) -> None:
        ticket = Ticket(
            ticket_id=ticket_id,
            event_id=event_id,
        )

        self.session.add(ticket)
        await self.session.commit()

    async def delete_ticket(
        self,
        ticket_id: uuid.UUID,
    ) -> None:
        ticket = await self.session.get(
            Ticket,
            ticket_id,
        )

        if not ticket:
            raise TicketNotFoundError(f"Ticket with id: {ticket_id} not found")
        
        await self.session.delete(ticket)
        await self.session.commit()