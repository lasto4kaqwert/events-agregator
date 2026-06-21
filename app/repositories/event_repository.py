import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EventNotFoundError
from app.models.event import Event
from app.schemas.event import (
    LocalRepoEventDescribeSchema,
    LocalRepoEventsSchema,
    LocalRepoPlaceDescribeSchema,
)


class EventRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    def _map_event(
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

    async def get(
        self,
        date_from: datetime | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> LocalRepoEventsSchema:
        offset = (page - 1) * page_size

        stmt = select(Event)
        if date_from is not None:
            stmt = stmt.where(Event.event_time >= date_from)

        count_stmt = select(func.count()).select_from(stmt.subquery())

        count_result = await self.session.execute(count_stmt)
        count = count_result.scalar_one()

        events_stmt = (
            stmt.order_by(Event.event_time.desc()).limit(page_size).offset(offset)
        )

        events_result = await self.session.execute(events_stmt)
        events = events_result.scalars().all()

        return LocalRepoEventsSchema(
            count=count,
            next=None,
            previous=None,
            results=[self._map_event(event=event) for event in events],
        )

    async def get_describe(
        self,
        event_id: uuid.UUID,
    ) -> LocalRepoEventDescribeSchema:
        stmt = select(Event).where(Event.id == event_id)

        result = await self.session.execute(stmt)
        event = result.scalar_one_or_none()

        if event is None:
            raise EventNotFoundError(f"Event {event_id} not found")

        return self._map_event(event=event)

    async def upsert(
        self,
        events: list[LocalRepoEventDescribeSchema],
    ) -> int:
        saved = 0

        for event_describe in events:
            event_id = event_describe.id

            event = await self.session.get(Event, event_id)
            if event is None:
                event = Event(id=event_id)
                self.session.add(event)

            event.name = event_describe.name
            event.place = event_describe.place.model_dump(mode="json")
            event.event_time = event_describe.event_time
            event.registration_deadline = event_describe.registration_deadline
            event.status = event_describe.status
            event.number_of_visitors = event_describe.number_of_visitors

            saved += 1

        await self.session.commit()

        return saved
