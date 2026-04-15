"""rename_timeline_metadata_to_extra_metadata

Revision ID: eb56b97d642c
Revises: 185228b2c6f7
Create Date: 2026-04-14 00:09:42.289371

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'eb56b97d642c'
down_revision: Union[str, None] = '185228b2c6f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use alter_column for renaming
    op.alter_column('ticket_timeline', 'metadata', new_column_name='extra_metadata')


def downgrade() -> None:
    # Use alter_column for reverting
    op.alter_column('ticket_timeline', 'extra_metadata', new_column_name='metadata')
