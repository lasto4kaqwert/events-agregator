import uuid

from pydantic import BaseModel


class ExternalAPIAvaiableSeatsSchema(BaseModel):
    seats: list[str]


class LocalRepoAvaiableSeatsSchema(BaseModel):
    event_id: uuid.UUID
    seats: list[str]