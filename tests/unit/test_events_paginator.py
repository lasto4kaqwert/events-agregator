from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.paginators.events_paginator import EventsPaginator


@pytest.mark.asyncio
async def test_events_paginator_fetches_first_page() -> None:
    event = MagicMock()

    page = MagicMock()
    page.results = [event]
    page.next = None

    client = MagicMock()
    client.fetch_events = AsyncMock(return_value=page)
    client.next_events = AsyncMock()

    paginator = EventsPaginator(
        client=client,
        changed_at=date(2000, 1, 1),
    )

    result = [item async for item in paginator]

    assert result == [event]

    client.fetch_events.assert_awaited_once_with(
        changed_at=date(2000, 1, 1),
    )
    client.next_events.assert_not_awaited()


@pytest.mark.asyncio
async def test_events_paginator_loads_next_page() -> None:
    first_event = MagicMock()
    second_event = MagicMock()

    next_url = "http://eventsprovider/api/events/?cursor=next-page"

    first_page = MagicMock()
    first_page.results = [first_event]
    first_page.next = next_url

    second_page = MagicMock()
    second_page.results = [second_event]
    second_page.next = None

    client = MagicMock()
    client.fetch_events = AsyncMock(return_value=first_page)
    client.next_events = AsyncMock(return_value=second_page)

    paginator = EventsPaginator(
        client=client,
        changed_at=date(2000, 1, 1),
    )

    result = [item async for item in paginator]

    assert result == [first_event, second_event]

    client.fetch_events.assert_awaited_once_with(
        changed_at=date(2000, 1, 1),
    )
    client.next_events.assert_awaited_once_with(next_url)


@pytest.mark.asyncio
async def test_events_paginator_returns_empty_list() -> None:
    page = MagicMock()
    page.results = []
    page.next = None

    client = MagicMock()
    client.fetch_events = AsyncMock(return_value=page)
    client.next_events = AsyncMock()

    paginator = EventsPaginator(
        client=client,
        changed_at=date(2000, 1, 1),
    )

    result = [item async for item in paginator]

    assert result == []

    client.fetch_events.assert_awaited_once_with(
        changed_at=date(2000, 1, 1),
    )
    client.next_events.assert_not_awaited()


@pytest.mark.asyncio
async def test_events_paginator_loads_next_page_even() -> None:
    event = MagicMock()

    next_url = "http://eventsprovider/api/events/?cursor=next-page"

    first_page = MagicMock()
    first_page.results = []
    first_page.next = next_url

    second_page = MagicMock()
    second_page.results = [event]
    second_page.next = None

    client = MagicMock()
    client.fetch_events = AsyncMock(return_value=first_page)
    client.next_events = AsyncMock(return_value=second_page)

    paginator = EventsPaginator(
        client=client,
        changed_at=date(2000, 1, 1),
    )

    result = [item async for item in paginator]

    assert result == [event]

    client.fetch_events.assert_awaited_once_with(
        changed_at=date(2000, 1, 1),
    )
    client.next_events.assert_awaited_once_with(next_url)
