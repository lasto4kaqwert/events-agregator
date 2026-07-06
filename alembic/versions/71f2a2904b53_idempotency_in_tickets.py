"""idempotency in tickets

Revision ID: 71f2a2904b53
Revises: bc65c52e605f
Create Date: 2026-07-06 14:33:17.367081

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71f2a2904b53'
down_revision: Union[str, Sequence[str], None] = 'bc65c52e605f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "tickets",
        sa.Column("idempotency_key", sa.String(length=128), nullable=True),
    )

    op.add_column(
        "tickets",
        sa.Column("request_hash", sa.String(length=64), nullable=True),
    )

    op.create_index(
        "uq_tickets_idempotency_key",
        "tickets",
        ["idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "uq_tickets_idempotency_key",
        table_name="tickets",
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )

    op.drop_column("tickets", "request_hash")
    op.drop_column("tickets", "idempotency_key")
