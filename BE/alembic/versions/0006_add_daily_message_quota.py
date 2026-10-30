"""add daily message quota columns for free-tier users

Revision ID: 0006_daily_quota
Revises: 0005_name_location
Create Date: 2026-10-30 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '0006_daily_quota'
down_revision: Union[str, None] = '0005_name_location'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('daily_message_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('daily_message_reset_date', sa.Date(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'daily_message_reset_date')
    op.drop_column('users', 'daily_message_count')
