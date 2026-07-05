"""increase outbox type length

Revision ID: acada23fe1d1
Revises: 69011cdf2d22
Create Date: 2026-07-05 14:47:02.421800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'acada23fe1d1'
down_revision: Union[str, Sequence[str], None] = '69011cdf2d22'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "outbox",
        "type",
        existing_type=sa.String(length=21),
        type_=sa.String(length=64),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "outbox",
        "type",
        existing_type=sa.String(length=64),
        type_=sa.String(length=21),
        existing_nullable=False,
    )
