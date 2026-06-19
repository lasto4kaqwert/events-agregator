import uuid
from datetime import datetime

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    place: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    
    event_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    registration_deadline: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="new",
    )

    number_of_visitors: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )