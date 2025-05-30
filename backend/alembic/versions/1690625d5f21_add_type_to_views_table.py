"""add_type_to_views_table

Revision ID: 1690625d5f21
Revises: bebd269815aa
Create Date: 2025-05-29 21:12:52.113944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1690625d5f21'
down_revision: Union[str, None] = 'bebd269815aa' # Previous migration for record_links table
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands manually created ###
    op.add_column('views',
        sa.Column('type', sa.String(), nullable=False, server_default='grid')
    )
    # If we want to ensure existing rows (if any) get this default,
    # sometimes an explicit update is needed if server_default only applies to new rows
    # For PostgreSQL, server_default should handle this for new rows,
    # and for existing rows, they would be NULL without an update.
    # To ensure non-nullability on existing rows:
    op.execute("UPDATE views SET type = 'grid' WHERE type IS NULL")
    # Then, if the column was created as nullable and needs to be altered to nullable=False after update:
    # op.alter_column('views', 'type', nullable=False)
    # However, by defining nullable=False with server_default from start, it should be fine for new tables
    # For existing tables, the above UPDATE + ALTER might be safer.
    # For this case, assuming the nullable=False and server_default='grid' is sufficient for new tables,
    # and if there was data, an update ensures non-nullability.
    # The column definition itself with nullable=False is the main thing.
    # The op.execute is a good measure if there could be pre-existing data.
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands manually created ###
    op.drop_column('views', 'type')
    # ### end Alembic commands ###
