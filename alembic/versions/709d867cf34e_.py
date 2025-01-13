"""empty message

Revision ID: 709d867cf34e
Revises: 67c54eec26ff
Create Date: 2025-01-08 23:34:22.330175

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '709d867cf34e'
down_revision: Union[str, None] = '67c54eec26ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('players', sa.Column('player_id', sa.Integer(), nullable=False))
    op.create_unique_constraint('idx_uniq_player_id', 'players', ['player_id', 'map_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('idx_uniq_player_id', 'players', type_='unique')
    op.drop_column('players', 'player_id')
    # ### end Alembic commands ###