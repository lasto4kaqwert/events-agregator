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
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
