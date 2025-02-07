"""add count items

Revision ID: 05f99f8a32a8
Revises: c6e9f2673bbd
Create Date: 2025-02-04 13:55:19.085794

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '05f99f8a32a8'
down_revision: Union[str, None] = 'c6e9f2673bbd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('inventories', sa.Column('count', sa.Integer(), nullable=False))
    op.add_column('players_items_storage', sa.Column('count', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('players_items_storage', 'count')
    op.drop_column('inventories', 'count')
    # ### end Alembic commands ###
