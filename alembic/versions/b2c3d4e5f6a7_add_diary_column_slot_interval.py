"""add_diary_column_slot_interval

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-18 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "diary_columns",
        sa.Column("slot_interval_minutes", sa.Integer(), nullable=True),
    )
    op.create_check_constraint(
        "ck_diary_columns_slot_interval_valid",
        "diary_columns",
        "slot_interval_minutes IS NULL OR (slot_interval_minutes >= 5 AND slot_interval_minutes % 5 = 0)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_diary_columns_slot_interval_valid", "diary_columns", type_="check")
    op.drop_column("diary_columns", "slot_interval_minutes")
