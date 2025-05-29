"""add_owner_id_to_records_recordvalues_and_relationships

Revision ID: 6199dde9b544
Revises: f08a30814fdd
Create Date: 2025-05-29 19:10:51.137995

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6199dde9b544'
down_revision: Union[str, None] = 'f08a30814fdd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands manually adjusted ###
    # Add owner_id to records table
    op.add_column('records', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key('fk_records_owner_id_users', 'records', 'users', ['owner_id'], ['id'])
    op.create_index(op.f('ix_records_owner_id'), 'records', ['owner_id'], unique=False)

    # Add owner_id to record_values table
    op.add_column('record_values', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key('fk_record_values_owner_id_users', 'record_values', 'users', ['owner_id'], ['id'])
    op.create_index(op.f('ix_record_values_owner_id'), 'record_values', ['owner_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands manually adjusted ###
    # Drop owner_id from record_values table
    op.drop_index(op.f('ix_record_values_owner_id'), table_name='record_values')
    op.drop_constraint('fk_record_values_owner_id_users', 'record_values', type_='foreignkey')
    op.drop_column('record_values', 'owner_id')

    # Drop owner_id from records table
    op.drop_index(op.f('ix_records_owner_id'), table_name='records')
    op.drop_constraint('fk_records_owner_id_users', 'records', type_='foreignkey')
    op.drop_column('records', 'owner_id')
    # ### end Alembic commands ###
