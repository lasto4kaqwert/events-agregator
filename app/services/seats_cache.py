import time
import uuid

from app.core.metrics import CACHE_HITS, CACHE_MISSES


class SeatsCache:
    def __init__(
        self,
        total_seconds: int = 30,
    ) -> None:
        self.total_seconds = total_seconds
        self._storage: dict[uuid.UUID, tuple[float, list[str]]] = {}

    def get(
        self,
        event_id: uuid.UUID,
    ) -> list[str] | None:
        cached = self._storage.get(event_id)

        if cached is None:
            CACHE_MISSES.inc()
            return None

        created_at, seats = cached

        if time.monotonic() - created_at > self.total_seconds:
            self._storage.pop(event_id, None)
            CACHE_MISSES.inc()
            return None

        CACHE_HITS.inc()
        return seats

    def set(
        self,
        event_id: uuid.UUID,
        seats: list[str],
    ) -> None:
        self._storage[event_id] = (
            time.monotonic(),
            seats,
        )

    def delete(self, event_id: uuid.UUID) -> None:
        self._storage.pop(event_id, None)
