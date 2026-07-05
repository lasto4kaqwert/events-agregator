import uuid
from typing import Any

from pydantic import AwareDatetime, BaseModel, ConfigDict

from app.core.enums import (
    OutboxEventType,
    OutboxStatus,
    TicketStatus,
)


class OutboxRepositorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: OutboxEventType
    payload: dict[str, Any]
    status: OutboxStatus
    created_at: AwareDatetime
    updated_at: AwareDatetime


class TicketProcessingOutbox(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    outbox_status: OutboxStatus
    ticket_status: TicketStatus | None = None
    external_ticket_id: uuid.UUID | None = None
    create_capashino_outbox: bool = False
    capashino_message: str | None = None


class CapashinoProcessingOutbox(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    outbox_status: OutboxStatus
