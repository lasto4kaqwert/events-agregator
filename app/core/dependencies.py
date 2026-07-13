
from datetime import date

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.capashino_client import CapashinoClient
from app.clients.events_provider_client import EventsProviderClient
from app.core.session import get_session
from app.core.settings import get_settings
from app.repositories.event_repository import EventRepository
from app.repositories.sync_repository import SyncRepository
from app.services import (
    SeatsCache,
    TicketService,
)
from app.services.repositories import (
    OutboxRepository,
    TicketRepository,
)
from app.services.workers import (
    CapashinoOutboxPorcessor,
    TicketOutboxProcessor,
)
from app.usecases import (
    GetEventsUseCase,
    GetEventUseCase,
    GetSeatsUseCase,
    GetSyncUseCase,
    LastSyncUseCase,
    RegisterTicketUsecase,
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
# CLIENTS
########################################

settings = get_settings()


def get_client() -> EventsProviderClient:
    return EventsProviderClient(
        api_key=settings.event_provider_api_key,
        base_url=settings.event_provider_host,
        env_client_type=settings.env_client_type,
    )


def get_client_capashino() -> CapashinoClient:
    return CapashinoClient(
        api_key=settings.event_provider_api_key,
        base_url=settings.capashino_host,
    )


########################################
# SYNCS
########################################


async def build_trigger_sync_usecase(
    session: AsyncSession,
) -> TriggerSyncUseCase:
    return TriggerSyncUseCase(
        sync_repo=SyncRepository(session=session),
        event_repo=EventRepository(session=session),
        client=get_client(),
        init_date=date(
            int(settings.sync_init_year),
            int(settings.sync_init_month),
            int(settings.sync_init_day),
        ),
    )


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
    return await build_trigger_sync_usecase(session=session)

########################################
# TICKETS
########################################


async def get_ticket_repository(
    session: AsyncSession = Depends(get_session),
) -> TicketRepository:
    return TicketRepository(session=session)


def _get_ticket_service(
    session: AsyncSession,
) -> TicketService:
    return TicketService(
        session=session,
        ticket_repo=TicketRepository(session=session),
        outbox_repo=OutboxRepository(session=session),
    )


async def build_ticket_outbox_processor(
    session: AsyncSession,
) -> TriggerSyncUseCase:
    return TicketOutboxProcessor(
        session=session,
        client=get_client(),
        service=_get_ticket_service(session=session),
        outbox_repo=OutboxRepository(session=session),
        event_repo=EventRepository(session=session),
    )


async def get_register_ticket_usecase(
    session: AsyncSession = Depends(get_session),
) -> RegisterTicketUsecase:
    return RegisterTicketUsecase(
        service=_get_ticket_service(session=session),
        cache=get_seats_cache(),
    )


async def get_unregister_ticket_usecase(
    session: AsyncSession = Depends(get_session),
) -> UnregisterTicketUseCase:
    return UnregisterTicketUseCase(
        service=_get_ticket_service(session=session),
        cache=get_seats_cache(),
    )

########################################
# EVENTS
########################################


async def get_event_repository(
    session: AsyncSession = Depends(get_session),
) -> EventRepository:
    return EventRepository(session=session)


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
        client=get_client(),
        cache=get_seats_cache(),
    )

########################################
# CAPASHINO
########################################


async def build_capashino_outbox_processor(
    session: AsyncSession,
) -> TriggerSyncUseCase:
    return CapashinoOutboxPorcessor(
        session=session,
        capashino=get_client_capashino(),
        outbox_repo=OutboxRepository(session=session),
    )
