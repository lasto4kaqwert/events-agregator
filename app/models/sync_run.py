import uuid
from datetime import datetime, date

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SyncRun(Base):
    __tablename__ = "sync_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    describe: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    finished_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
    )

    changed_at: Mapped[date] = mapped_column(
        DateTime,
        nullable=False,
    )