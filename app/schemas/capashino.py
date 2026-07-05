import uuid

from pydantic import BaseModel, ConfigDict


class CapashinoRequestSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message: str
    reference_id: uuid.UUID
    idempotency_key: str


class CapashinoResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    message: str
    reference_id: str
    created_at: str
    idempotency_key: str | None
