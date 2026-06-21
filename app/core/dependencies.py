import os

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.events_provider_client import EventsProviderClient
from app.core.session import get_session
from app.repositories.event_repository import EventRepository
from app.repositories.sync_repository import SyncRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.seats_cache import SeatsCache
from app.usecases import (
    GetEventsUseCase,
    GetEventUseCase,
    GetSeatsUseCase,
    GetSyncUseCase,
    LastSyncUseCase,
    RegisterTicketUseCase,
    TriggerSyncUseCase,
    UnregisterTicketUseCase,
)

########################################
# CACHE
########################################

seats_cache = SeatsCache(total_seconds=30)


def get_seats_cache() -> SeatsCache:
    return seats_cache


########################################
# SYNCS
########################################


async def get_getter_sync_usesace(
    session: AsyncSession = Depends(get_session),
) -> GetSyncUseCase:
    return GetSyncUseCase(
        sync_repo=SyncRepository(session=session),
    )


async def get_last_sync_usecase(
    session: AsyncSession = Depends(get_session),
) -> LastSyncUseCase:
    return LastSyncUseCase(
        sync_repo=SyncRepository(session=session),
    )


async def get_trigger_sync_usecase(
    session: AsyncSession = Depends(get_session),
) -> TriggerSyncUseCase:
    return TriggerSyncUseCase(
        sync_repo=SyncRepository(session=session),
        event_repo=EventRepository(session=session),
        client=EventsProviderClient(
            api_key=os.getenv("EVENT_PROVIDER_API_KEY"),
            base_url=os.getenv("EVENT_PROVIDER_HOST"),
        ),
    )


########################################
# TICKETS
########################################


async def get_register_ticket_usecase(
    session: AsyncSession = Depends(get_session),
) -> RegisterTicketUseCase:
    return RegisterTicketUseCase(
        repo=TicketRepository(session=session),
        client=EventsProviderClient(
            api_key=os.getenv("EVENT_PROVIDER_API_KEY"),
            base_url=os.getenv("EVENT_PROVIDER_HOST"),
        ),
        cache=get_seats_cache(),
    )


async def get_unregister_ticket_usecase(
    session: AsyncSession = Depends(get_session),
) -> UnregisterTicketUseCase:
    return UnregisterTicketUseCase(
        repo=TicketRepository(session=session),
        client=EventsProviderClient(
            api_key=os.getenv("EVENT_PROVIDER_API_KEY"),
            base_url=os.getenv("EVENT_PROVIDER_HOST"),
        ),
        cache=get_seats_cache(),
    )


########################################
# EVENTS
########################################


async def get_getter_events_usecase(
    session: AsyncSession = Depends(get_session),
) -> GetEventsUseCase:
    return GetEventsUseCase(
        repo=EventRepository(session=session),
    )


async def get_getter_event_usecase(
    session: AsyncSession = Depends(get_session),
) -> GetEventUseCase:
    return GetEventUseCase(
        repo=EventRepository(session=session),
    )


async def get_getter_seats_usecase(
    session: AsyncSession = Depends(get_session),
) -> GetSeatsUseCase:
    return GetSeatsUseCase(
        repo=EventRepository(session=session),
        client=EventsProviderClient(
            api_key=os.getenv("EVENT_PROVIDER_API_KEY"),
            base_url=os.getenv("EVENT_PROVIDER_HOST"),
        ),
        cache=get_seats_cache(),
    )
