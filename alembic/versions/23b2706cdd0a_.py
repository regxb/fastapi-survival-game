"""empty message

Revision ID: 23b2706cdd0a
Revises: 88cb8691a2e2
Create Date: 2025-02-09 00:39:52.338017

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23b2706cdd0a'
down_revision: Union[str, None] = '88cb8691a2e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'item_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column('items', sa.Column('type_id', sa.Integer(), nullable=True))
    connection = op.get_bind()
    connection.execute(
        sa.text("INSERT INTO item_types (id, name) VALUES (1, 'Default') ON CONFLICT DO NOTHING")
    )
    connection.execute(
        sa.text("UPDATE items SET type_id = 1 WHERE type_id IS NULL")
    )
    op.alter_column('items', 'type_id', nullable=False)
    op.create_foreign_key('fk_items_type', 'items', 'item_types', ['type_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_items_type', 'items', type_='foreignkey')
    op.drop_column('items', 'type_id')
    op.drop_table('item_types')
