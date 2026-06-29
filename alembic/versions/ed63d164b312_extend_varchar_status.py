"""extend varchar status

Revision ID: ed63d164b312
Revises: db9ddc13cd57
Create Date: 2026-06-29 14:11:16.936860

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed63d164b312'
down_revision: Union[str, Sequence[str], None] = 'db9ddc13cd57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
