from typing import TYPE_CHECKING

import uuid
from datetime import datetime

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .place import Place
    from .tickets import Ticket


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    place_id: Mapped[int] = mapped_column(
        ForeignKey("places.id"),
        nullable=False,
    )

    place: Mapped["Place"] = relationship(
        back_populates="events"
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

    seats: Mapped[list["Ticket"]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    status_changed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )