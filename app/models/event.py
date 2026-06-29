import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import EventStatus
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
        DateTime(timezone=True),
        nullable=False,
    )

    registration_deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    status: Mapped[EventStatus] = mapped_column(
        Enum(
            EventStatus,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=False,
        ),
        nullable=False,
        default=EventStatus.NEW,
    )

    number_of_visitors: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
