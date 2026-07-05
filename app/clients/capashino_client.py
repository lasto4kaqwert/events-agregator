import httpx

from app.clients.base_client import BaseClient
from app.core.exceptions import (
    CapashinoEmptyMessageError,
    CapashinoIdempotencyParsedError,
    CapashinoInvalidApiKeyError,
    CapashinoInvalidBodyError,
    CapashinoRepeatEncounterError,
)
from app.schemas.capashino import CapashinoRequestSchema, CapashinoResponseSchema


class CapashinoClient(BaseClient):
    async def send_message(
        self,
        payload: CapashinoRequestSchema,
    ) -> CapashinoResponseSchema:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._build_url("/api/notifications"),
                headers=self.headers,
                json=payload.model_dump(mode="json"),
            )

        if response.status_code == 400:
            raise CapashinoInvalidBodyError(
                "Capashino message failed with incorrect reference_id or invalid body."
                f"status={response.status_code}"
                f"body={response.text}"
            )
        elif response.status_code == 401:
            raise CapashinoInvalidApiKeyError(
                "Capashino message failed with invalid api-key."
                f"status={response.status_code}"
                f"body={response.text}"
            )
        elif response.status_code == 409:
            raise CapashinoIdempotencyParsedError(
                "Already parsed capashino with this idempotency key."
                f"status={response.status_code}"
                f"body={response.text}"
            )
        elif response.status_code == 422:
            raise CapashinoEmptyMessageError(
                "Capashino message failed with empty message."
                f"status={response.status_code}"
                f"body={response.text}"
            )
        elif response.status_code >= 500:
            raise CapashinoRepeatEncounterError(
                "Capashino message failed with repeat workers message."
                f"status={response.status_code}"
                f"body={response.text}"
            )

        return CapashinoResponseSchema.model_validate(response.json())
