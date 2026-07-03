import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import TicketStatus
from app.models.base import Base


class TicketModel(Base):
    __tablename__ = "tickets"

    ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    external_ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[TicketStatus] = mapped_column(
        Enum(
            TicketStatus,
            values_callable=lambda enum: [item.value for item in enum],
            native_enum=False,
        ),
        nullable=False,
        default=TicketStatus.PENDING,
    )

    seat: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index(
            "uq_ticket_active_event_seat",
            "event_id", "seat",
            unique=True,
            postgresql_where=status.in_([
                TicketStatus.PENDING,
                TicketStatus.CONFIRMED,
            ]),
        ),
        Index(
            "uq_ticket_active_event_email",
            "event_id", "email",
            unique=True,
            postgresql_where=status.in_([
                TicketStatus.PENDING,
                TicketStatus.CONFIRMED,
            ]),
        ),
    )
