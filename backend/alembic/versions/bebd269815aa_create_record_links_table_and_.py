"""create_record_links_table_and_relationships

Revision ID: bebd269815aa
Revises: 22f0a0135ea6 
Create Date: 2025-05-29 20:23:32.291344

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
# Import postgresql if using JSONB or other PostgreSQL specific types, not needed for this table

# revision identifiers, used by Alembic.
revision: str = 'bebd269815aa'
down_revision: Union[str, None] = '22f0a0135ea6' # Previous migration for views table
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands manually created ###
    op.create_table('record_links',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source_record_id', sa.Integer(), nullable=False),
        sa.Column('source_field_id', sa.Integer(), nullable=False),
        sa.Column('linked_record_id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['source_record_id'], ['records.id'], name=op.f('fk_record_links_source_record_id_records')),
        sa.ForeignKeyConstraint(['source_field_id'], ['fields.id'], name=op.f('fk_record_links_source_field_id_fields')),
        sa.ForeignKeyConstraint(['linked_record_id'], ['records.id'], name=op.f('fk_record_links_linked_record_id_records')),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_record_links_owner_id_users')),
        sa.UniqueConstraint('source_record_id', 'source_field_id', 'linked_record_id', name='uq_record_link_constraint')
    )
    op.create_index(op.f('ix_record_links_id'), 'record_links', ['id'], unique=False)
    op.create_index(op.f('ix_record_links_source_record_id'), 'record_links', ['source_record_id'], unique=False)
    op.create_index(op.f('ix_record_links_source_field_id'), 'record_links', ['source_field_id'], unique=False)
    op.create_index(op.f('ix_record_links_linked_record_id'), 'record_links', ['linked_record_id'], unique=False)
    op.create_index(op.f('ix_record_links_owner_id'), 'record_links', ['owner_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands manually created ###
    op.drop_index(op.f('ix_record_links_owner_id'), table_name='record_links')
    op.drop_index(op.f('ix_record_links_linked_record_id'), table_name='record_links')
    op.drop_index(op.f('ix_record_links_source_field_id'), table_name='record_links')
    op.drop_index(op.f('ix_record_links_source_record_id'), table_name='record_links')
    op.drop_index(op.f('ix_record_links_id'), table_name='record_links')
    op.drop_table('record_links')
    # ### end Alembic commands ###
