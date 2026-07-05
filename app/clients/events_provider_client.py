from datetime import date
from typing import AsyncIterator
from uuid import UUID

import httpx

from app.clients.base_client import BaseClient
from app.core.enums import EventProviderClientType
from app.core.exceptions import (
    EventNotFoundError,
    ExternalAPIError,
    ExternalAPIUnauthorizedError,
    TicketOccupiedError,
)
from app.paginators.events_paginator import EventsPaginator
from app.schemas.event import ExternalAPIEventDescribeSchema, ExternalAPIEventsSchema
from app.schemas.seat import ExternalAPIAvaiableSeatsSchema
from app.schemas.ticket import (
    RegisteredTicketSchema,
    RegisterTicketSchema,
    UnregisteredTicketSchema,
    UnregisterTicketSchema,
)


class EventsProviderClient(BaseClient):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        env_client_type: str = "HTTP",
    ) -> None:
        super().__init__(base_url, api_key)
        self.env_client_type = env_client_type

    def _url_http_to_https(self, url: str | None) -> str | None:
        if not url:
            return None
        return url.replace("http://", "https://")

    def iter_events(
        self,
        changed_at: date,
    ) -> AsyncIterator[ExternalAPIEventDescribeSchema]:
        return EventsPaginator(
            client=self,
            changed_at=changed_at,
        )

    async def fetch_events(
        self,
        changed_at: date,
    ) -> ExternalAPIEventsSchema:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self._build_url("/api/events/"),
                params={
                    "changed_at": changed_at.strftime("%Y-%m-%d"),
                },
                headers=self.headers,
            )

        if response.status_code >= 400:
            raise ExternalAPIError(
                f"Provider register failed: "
                f"status={response.status_code}, "
                f"body={response.text}"
            )

        return ExternalAPIEventsSchema.model_validate(response.json())

    async def next_events(
        self,
        next: str,
    ) -> ExternalAPIEventsSchema:
        async with httpx.AsyncClient() as client:
            if self.env_client_type is EventProviderClientType.HTTPS:
                next = self._url_http_to_https(next)

            response = await client.get(
                next,
                headers=self.headers,
            )

        if response.status_code >= 400:
            raise ExternalAPIError(
                f"Provider register failed: "
                f"status={response.status_code}, "
                f"body={response.text}"
            )

        return ExternalAPIEventsSchema.model_validate(response.json())

    async def seats(
        self,
        event_id: UUID,
    ) -> ExternalAPIAvaiableSeatsSchema:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self._build_url(f"/api/events/{event_id}/seats/"),
                headers=self.headers,
            )

        if response.status_code >= 400:
            raise ExternalAPIError(
                f"Provider register failed: "
                f"status={response.status_code}, "
                f"body={response.text}"
            )

        return ExternalAPIAvaiableSeatsSchema.model_validate(response.json())

    async def register(
        self,
        event_id: UUID,
        payload: RegisterTicketSchema,
    ) -> RegisteredTicketSchema:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._build_url(f"/api/events/{event_id}/register/"),
                headers=self.headers,
                json=payload.model_dump(mode="json"),
            )

        if response.status_code == 400:
            raise TicketOccupiedError(
                f"This ticket is not available (already sold). "
                f"status={response.status_code}, "
                f"body={response.text}"
            )
        elif response.status_code == 404:
            raise EventNotFoundError(
                f"Event {event_id} not found. "
                f"status={response.status_code}, "
                f"body={response.text}"
            )
        elif response.status_code == 401:
            raise ExternalAPIUnauthorizedError(
                f"Invalid API-KEY. "
                f"status={response.status_code}, "
                f"body={response.text}"
            )

        return RegisteredTicketSchema.model_validate(response.json())

    async def unregister(
        self,
        event_id: UUID,
        payload: UnregisterTicketSchema,
    ) -> UnregisteredTicketSchema:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                "DELETE",
                self._build_url(f"/api/events/{event_id}/unregister/"),
                headers=self.headers,
                json=payload.model_dump(mode="json"),
            )

        if response.status_code >= 400:
            raise ExternalAPIError(
                f"Provider register failed: "
                f"status={response.status_code}, "
                f"body={response.text}"
            )

        return UnregisteredTicketSchema.model_validate(response.json())
