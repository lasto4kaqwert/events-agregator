from typing import TYPE_CHECKING

import uuid

from sqlalchemy import String, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .event import Event


class Ticket(Base):
    __tablename__ = "tickets"

    __table_args__ = (
        UniqueConstraint(
            "event_id",
            "seat",
            name="unique_event_seat",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"),
        index=True,
    )

    event: Mapped["Event"] = relationship(
        back_populates="seats",
    )

    first_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    seat: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )