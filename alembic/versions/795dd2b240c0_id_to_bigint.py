"""id to bigint

Revision ID: 795dd2b240c0
Revises: 05f99f8a32a8
Create Date: 2025-02-05 18:31:50.309419

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '795dd2b240c0'
down_revision: Union[str, None] = '05f99f8a32a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('players', 'player_id',
               existing_type=sa.INTEGER(),
               type_=sa.BIGINT(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('players', 'player_id',
               existing_type=sa.BIGINT(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    # ### end Alembic commands ###
