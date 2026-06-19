import uuid
from datetime import datetime

from enum import StrEnum

from pydantic import BaseModel


class SyncStatus(StrEnum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class SyncRunSchema(BaseModel):
    id: uuid.UUID
    started_at: datetime
    finished_at: datetime | None
    changed_at: datetime | None