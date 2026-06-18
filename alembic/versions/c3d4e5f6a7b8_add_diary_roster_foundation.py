"""Add Room and DiaryRoster tables for date-specific diary room assignment.

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-18
"""

from typing import Union, Sequence
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rooms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("practice_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("practices.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("display_order", sa.Integer, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
    )
    op.create_index("ix_rooms_practice_id", "rooms", ["practice_id"])
    op.create_unique_constraint("uq_rooms_practice_order", "rooms",
                                ["practice_id", "display_order"])

    op.create_table(
        "diary_roster",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("practice_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("practices.id"), nullable=False),
        sa.Column("room_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("rooms.id"), nullable=False),
        sa.Column("roster_date", sa.Date, nullable=False),
        sa.Column("practitioner_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("practitioners.id"), nullable=True),
        sa.Column("practitioner_ahpra", sa.String(50), nullable=True),
        sa.Column("label", sa.String(255), nullable=True),
    )
    op.create_index("ix_diary_roster_practice_date", "diary_roster",
                    ["practice_id", "roster_date"])
    op.create_unique_constraint("uq_diary_roster_practice_room_date", "diary_roster",
                                ["practice_id", "room_id", "roster_date"])


def downgrade() -> None:
    op.drop_constraint("uq_diary_roster_practice_room_date", "diary_roster", type_="unique")
    op.drop_index("ix_diary_roster_practice_date", table_name="diary_roster")
    op.drop_table("diary_roster")

    op.drop_constraint("uq_rooms_practice_order", "rooms", type_="unique")
    op.drop_index("ix_rooms_practice_id", table_name="rooms")
    op.drop_table("rooms")
