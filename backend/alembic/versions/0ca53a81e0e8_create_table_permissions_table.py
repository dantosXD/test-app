"""create_table_permissions_table

Revision ID: 0ca53a81e0e8
Revises: 1690625d5f21
Create Date: 2025-05-30 11:54:08.025606

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0ca53a81e0e8'
down_revision: Union[str, None] = '1690625d5f21' # Previous migration for adding type to views
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands manually created ###
    op.create_table('table_permissions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('table_id', sa.Integer(), nullable=False),
        sa.Column('permission_level', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_table_permissions_user_id_users')),
        sa.ForeignKeyConstraint(['table_id'], ['tables.id'], name=op.f('fk_table_permissions_table_id_tables')),
        sa.UniqueConstraint('user_id', 'table_id', name='uq_user_table_permission')
    )
    op.create_index(op.f('ix_table_permissions_id'), 'table_permissions', ['id'], unique=False)
    op.create_index(op.f('ix_table_permissions_user_id'), 'table_permissions', ['user_id'], unique=False)
    op.create_index(op.f('ix_table_permissions_table_id'), 'table_permissions', ['table_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands manually created ###
    op.drop_index(op.f('ix_table_permissions_table_id'), table_name='table_permissions')
    op.drop_index(op.f('ix_table_permissions_user_id'), table_name='table_permissions')
    op.drop_index(op.f('ix_table_permissions_id'), table_name='table_permissions')
    op.drop_table('table_permissions')
    # ### end Alembic commands ###
