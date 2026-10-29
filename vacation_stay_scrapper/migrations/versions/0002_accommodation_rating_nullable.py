"""accommodation rating nullable

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-18 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("accommodations", "rating", existing_type=sa.Float(), nullable=True)


def downgrade() -> None:
    op.execute("UPDATE accommodations SET rating = 0 WHERE rating IS NULL")
    op.alter_column("accommodations", "rating", existing_type=sa.Float(), nullable=False)
