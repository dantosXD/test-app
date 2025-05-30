"""create_views_table

Revision ID: 22f0a0135ea6
Revises: 6199dde9b544
Create Date: 2025-05-29 20:15:51.402962

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql # For JSONB if needed by 'config'


# revision identifiers, used by Alembic.
revision: str = '22f0a0135ea6'
down_revision: Union[str, None] = '6199dde9b544' # Previous migration for record/recordvalue owner_id
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands manually created ###
    op.create_table('views',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('table_id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['table_id'], ['tables.id'], name=op.f('fk_views_table_id_tables')),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_views_owner_id_users'))
    )
    op.create_index(op.f('ix_views_id'), 'views', ['id'], unique=False)
    op.create_index(op.f('ix_views_table_id'), 'views', ['table_id'], unique=False)
    op.create_index(op.f('ix_views_owner_id'), 'views', ['owner_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands manually created ###
    op.drop_index(op.f('ix_views_owner_id'), table_name='views')
    op.drop_index(op.f('ix_views_table_id'), table_name='views')
    op.drop_index(op.f('ix_views_id'), table_name='views')
    op.drop_table('views')
    # ### end Alembic commands ###
