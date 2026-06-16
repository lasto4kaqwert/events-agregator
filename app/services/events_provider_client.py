import os
import httpx

from uuid import UUID
from datetime import date

from pydantic import BaseModel
from typing import Any


class EventsProviderClient:
    def __init__(self) -> None:
        self.base_url = os.environ.get("EVENT_PROVIDER_HOST")
        self.headers = {
            "x-api-key": os.environ.get("EVENT_PROVIDER_API_KEY"),
        }

    async def events(
        self, 
        changed_at: date
    ) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/events/",
                params={
                    "changed_at": changed_at.isoformat()
                },
                headers=self.headers,
            )

        response.raise_for_status()

        return response.json()

    async def seats(
        self,
        event_id: UUID,
    ) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/events/{event_id}/seats/",
                headers=self.headers,
            )

        response.raise_for_status()

        return response.json()

    async def register(
        self,
        event_id: UUID,
        payload: BaseModel,
    ) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/events/{event_id}/register/",
                headers=self.headers,
                json=payload.model_dump(mode="json"),
            )

        response.raise_for_status()

        return response.json()

    async def unregister(
        self, 
        event_id: UUID,
        payload: BaseModel,
    ) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/api/events/{event_id}/unregister/",
                headers=self.headers,
                json=payload.model_dump(mode="json"),
            )

        response.raise_for_status()

        return response.json()