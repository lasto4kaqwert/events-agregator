import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.clients.events_provider_client import EventsProviderClient
from app.core.exceptions import ExternalAPIError
from app.schemas.ticket import (
    ExternalAPICreateTicketSchema,
    ExternalAPIDeleteTicketSchema,
)


def make_response(
    status_code: int,
    payload: dict,
) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    response.text = str(payload)

    return response


def mock_async_client(client: MagicMock):
    patched_client = patch("app.clients.events_provider_client.httpx.AsyncClient")
    async_client = patched_client.start()

    async_client.return_value.__aenter__ = AsyncMock(
        return_value=client,
    )
    async_client.return_value.__aexit__ = AsyncMock(
        return_value=None,
    )

    return patched_client


@pytest.mark.asyncio
async def test_fetch_events_success() -> None:
    client = EventsProviderClient(
        base_url="http://eventsprovider",
        api_key="my-test-api",
    )

    response = make_response(
        status_code=200,
        payload={
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        },
    )

    http_client = MagicMock()
    http_client.get = AsyncMock(return_value=response)

    patched_client = mock_async_client(http_client)

    try:
        result = await client.fetch_events(
            changed_at=date(2000, 1, 1),
        )
    finally:
        patched_client.stop()

    assert result.results == []

    http_client.get.assert_awaited_once_with(
        "http://eventsprovider/api/events/",
        params={"changed_at": "2000-01-01"},
        headers={"x-api-key": "my-test-api"},
    )


@pytest.mark.asyncio
async def test_next_events_success() -> None:
    client = EventsProviderClient(
        base_url="http://eventsprovider",
        api_key="my-test-api",
    )

    next_url = "http://eventsprovider/api/events/?cursor=abc"

    response = make_response(
        status_code=200,
        payload={
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        },
    )

    http_client = MagicMock()
    http_client.get = AsyncMock(return_value=response)

    patched_client = mock_async_client(http_client)

    try:
        result = await client.next_events(next_url)
    finally:
        patched_client.stop()

    assert result.results == []

    http_client.get.assert_awaited_once_with(
        next_url,
        headers={"x-api-key": "my-test-api"},
    )


@pytest.mark.asyncio
async def test_seats_success() -> None:
    event_id = uuid.uuid4()

    client = EventsProviderClient(
        base_url="http://eventsprovider",
        api_key="my-test-api",
    )

    response = make_response(
        status_code=200,
        payload={
            "seats": ["A1", "A2", "A3"],
        },
    )

    http_client = MagicMock()
    http_client.get = AsyncMock(return_value=response)

    patched_client = mock_async_client(http_client)

    try:
        result = await client.seats(event_id=event_id)
    finally:
        patched_client.stop()

    assert result.seats == ["A1", "A2", "A3"]

    http_client.get.assert_awaited_once_with(
        f"http://eventsprovider/api/events/{event_id}/seats/",
        headers={"x-api-key": "my-test-api"},
    )


@pytest.mark.asyncio
async def test_register_success() -> None:
    event_id = uuid.uuid4()
    ticket_id = uuid.uuid4()

    client = EventsProviderClient(
        base_url="http://eventsprovider",
        api_key="my-test-api",
    )

    payload = ExternalAPICreateTicketSchema(
        first_name="Vladimir",
        last_name="Lyalin",
        email="vladimirlyalin@example.com",
        seat="A15",
    )

    response = make_response(
        status_code=201,
        payload={
            "ticket_id": str(ticket_id),
        },
    )

    http_client = MagicMock()
    http_client.post = AsyncMock(return_value=response)

    patched_client = mock_async_client(http_client)

    try:
        result = await client.register(
            event_id=event_id,
            payload=payload,
        )
    finally:
        patched_client.stop()

    assert result.ticket_id == ticket_id

    http_client.post.assert_awaited_once_with(
        f"http://eventsprovider/api/events/{event_id}/register/",
        headers={"x-api-key": "my-test-api"},
        json=payload.model_dump(mode="json"),
    )


@pytest.mark.asyncio
async def test_unregister_success() -> None:
    event_id = uuid.uuid4()
    ticket_id = uuid.uuid4()

    client = EventsProviderClient(
        base_url="http://eventsprovider",
        api_key="my-test-api",
    )

    payload = ExternalAPIDeleteTicketSchema(
        ticket_id=ticket_id,
    )

    response = make_response(
        status_code=200,
        payload={
            "success": True,
        },
    )

    http_client = MagicMock()
    http_client.request = AsyncMock(return_value=response)

    patched_client = mock_async_client(http_client)

    try:
        result = await client.unregister(
            event_id=event_id,
            payload=payload,
        )
    finally:
        patched_client.stop()

    assert result.success is True

    http_client.request.assert_awaited_once_with(
        "DELETE",
        f"http://eventsprovider/api/events/{event_id}/unregister/",
        headers={"x-api-key": "my-test-api"},
        json=payload.model_dump(mode="json"),
    )


@pytest.mark.asyncio
async def test_register_raises_on_bad_response() -> None:
    event_id = uuid.uuid4()

    client = EventsProviderClient(
        base_url="http://eventsprovider",
        api_key="my-test-api",
    )

    payload = ExternalAPICreateTicketSchema(
        first_name="Vladimir",
        last_name="Lyalin",
        email="vladimirlyalin@example.com",
        seat="A15",
    )

    response = make_response(
        status_code=400,
        payload={
            "detail": "bad request",
        },
    )

    http_client = MagicMock()
    http_client.post = AsyncMock(return_value=response)

    patched_client = mock_async_client(http_client)

    try:
        with pytest.raises(ExternalAPIError):
            await client.register(
                event_id=event_id,
                payload=payload,
            )
    finally:
        patched_client.stop()
