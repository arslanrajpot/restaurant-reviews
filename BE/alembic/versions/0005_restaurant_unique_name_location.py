"""restaurants unique on name + location

Revision ID: 0005_name_location
Revises: eeb0358d04a8
Create Date: 2026-10-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '0005_name_location'
down_revision: Union[str, None] = 'eeb0358d04a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('restaurants_restaurant_name_key', 'restaurants', type_='unique')
    op.create_unique_constraint('uq_restaurants_name_location', 'restaurants', ['restaurant_name', 'restaurant_location'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_restaurants_name_location', 'restaurants', type_='unique')
    op.create_unique_constraint('restaurants_restaurant_name_key', 'restaurants', ['restaurant_name'])
