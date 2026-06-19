import httpx

from uuid import UUID
from datetime import date

from app.schemas.event import ExternalAPIEventsSchema
from app.schemas.seat import ExternalAPIAvaiableSeatsSchema
from app.schemas.ticket import (
    ExternalAPICreateTicketSchema,
    ExternalAPIDeleteTicketSchema,
    CreatedTicketSchema,
    DeletedTicketSchema,
)


class ExternalAPIService:
    def __init__(
            self, 
            base_url: str,
            api_key: str,
        ) -> None:
        self.base_url = base_url
        self.headers = {
            "x-api-key": api_key,
        }

    async def _fetch_events(
        self,
        change_at: date,
    ) -> ExternalAPIEventsSchema:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/events/",
                params={
                    "change_at": change_at,
                },
                headers=self.headers,
            )
        
        response.raise_for_status()

        return ExternalAPIEventsSchema.model_validate(response.json())

    async def _next_events(
        self,
        next: str,
    ) -> ExternalAPIEventsSchema:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                next,
                headers=self.headers,
            )

        response.raise_for_status()

        return ExternalAPIEventsSchema.model_validate(response.json())

    async def events(
        self,
        change_at: date,
    ):
        page = await self._fetch_events(change_at)

        while True:

            yield (ExternalAPIEventsSchema.model_validate(page)).results

            if not page["next"]:
                break

            page = await self._next_events(page["next"])

    async def seats(
        self,
        event_id: UUID,
    ) -> ExternalAPIAvaiableSeatsSchema:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/events/{event_id}/seats/",
                headers=self.headers,
            )

        response.raise_for_status()

        return ExternalAPIAvaiableSeatsSchema.model_validate(response.json())

    async def register(
        self,
        event_id: UUID,
        payload: ExternalAPICreateTicketSchema,
    ) -> DeletedTicketSchema:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/events/{event_id}/register/",
                headers=self.headers,
                json=payload.model_dump(mode="json"),
            )

        response.raise_for_status()

        return CreatedTicketSchema.model_validate(response.json())

    async def unregister(
        self, 
        event_id: UUID,
        payload: ExternalAPIDeleteTicketSchema,
    ) -> DeletedTicketSchema:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/api/events/{event_id}/unregister/",
                headers=self.headers,
                json=payload.model_dump(mode="json"),
            )

        response.raise_for_status()

        return DeletedTicketSchema.model_validate(response.json())