from fastapi import APIRouter, Depends, Response
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest

from app.core.dependencies import (
    get_event_repository,
    get_ticket_repository,
)
from app.core.metrics import EVENTS_TOTAL, TICKETS_CANCELLED, TICKETS_CREATED
from app.repositories.event_repository import EventRepository
from app.services.repositories import TicketRepository

metrics_router = APIRouter(
    tags=["metrics"],
)


@metrics_router.get("", include_in_schema=False,response_class=Response)
async def metrics(
    events_repo: EventRepository = Depends(get_event_repository),
    ticket_repo: TicketRepository = Depends(get_ticket_repository),
) -> Response:
    EVENTS_TOTAL.set(await events_repo.count())
    TICKETS_CREATED.set(await ticket_repo.count_created())
    TICKETS_CANCELLED.set(await ticket_repo.count_cancelled())

    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST,
    )
