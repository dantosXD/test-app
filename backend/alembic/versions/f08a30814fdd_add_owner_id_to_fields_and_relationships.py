"""add_owner_id_to_fields_and_relationships

Revision ID: f08a30814fdd
Revises: c08568358f6b
Create Date: 2025-05-29 19:06:26.779149

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f08a30814fdd'
down_revision: Union[str, None] = 'c08568358f6b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands manually adjusted ###
    op.add_column('fields', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key('fk_fields_owner_id_users', 'fields', 'users', ['owner_id'], ['id'])
    op.create_index(op.f('ix_fields_owner_id'), 'fields', ['owner_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands manually adjusted ###
    op.drop_index(op.f('ix_fields_owner_id'), table_name='fields')
    op.drop_constraint('fk_fields_owner_id_users', 'fields', type_='foreignkey')
    op.drop_column('fields', 'owner_id')
    # ### end Alembic commands ###
