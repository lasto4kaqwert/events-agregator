import uuid
from typing import Any

from pydantic import AwareDatetime, BaseModel, ConfigDict

from app.core.enums import (
    OutboxEventType,
    OutboxStatus,
)


class OutboxRepositorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: OutboxEventType
    payload: dict[str, Any]
    status: OutboxStatus
    created_at: AwareDatetime
    updated_at: AwareDatetime
