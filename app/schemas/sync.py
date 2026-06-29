import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import SyncStatus


class SyncRunSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: SyncStatus
    describe: str | None = None
    started_at: datetime
    finished_at: datetime | None
    changed_at: datetime | None
