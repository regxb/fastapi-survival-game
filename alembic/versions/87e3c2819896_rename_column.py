"""rename column

Revision ID: 87e3c2819896
Revises: b8415f6df174
Create Date: 2025-01-14 00:49:59.476889

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87e3c2819896'
down_revision: Union[str, None] = 'b8415f6df174'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('building_costs', 'quantity', new_column_name='resource_quantity')
    op.alter_column('players_bases_storage', 'count', new_column_name='resource_quantity')
    op.alter_column('players_resources', 'count', new_column_name='resource_quantity')
    op.alter_column('recipe_items', 'resource_count', new_column_name='resource_quantity')


def downgrade() -> None:
    op.alter_column('building_costs', 'resource_quantity', new_column_name='quantity')
    op.alter_column('players_bases_storage', 'resource_quantity', new_column_name='count')
    op.alter_column('players_resources', 'resource_quantity', new_column_name='count')
    op.alter_column('recipe_items', 'resource_quantity', new_column_name='resource_count')

