"""fill status rows in tickets table

Revision ID: bc65c52e605f
Revises: acada23fe1d1
Create Date: 2026-07-06 13:22:27.849956

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc65c52e605f'
down_revision: Union[str, Sequence[str], None] = 'acada23fe1d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        UPDATE tickets
        SET status = 'confirmed'
        WHERE status IS NULL
    """)
    op.execute("""
        UPDATE tickets
        SET created_at = now()
        WHERE created_at IS NULL
    """)
    op.execute("""
        UPDATE tickets
        SET updated_at = now()
        WHERE updated_at IS NULL
    """)

    op.alter_column(
        "tickets",
        "status",
        existing_type=sa.String(),
        nullable=False,
    )
    op.alter_column(
        "tickets",
        "seat",
        existing_type=sa.String(),
        nullable=True,
    )
    op.alter_column(
        "tickets",
        "email",
        existing_type=sa.String(),
        nullable=True,
    )
    op.alter_column(
        "tickets",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )
    op.alter_column(
        "tickets",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "tickets",
        "status",
        existing_type=sa.Stirng(),
        nullable=True,
    )
    op.alter_column(
        "tickets",
        "seat",
        existing_type=sa.String(),
        nullable=True,
    )
    op.alter_column(
        "tickets",
        "email",
        existing_type=sa.String(),
        nullable=True,
    )
    op.alter_column(
        "tickets",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=True,
    )
    op.alter_column(
        "tickets",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=True,
    )
