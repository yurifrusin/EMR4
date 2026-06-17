"""add_diary_template_models

Revision ID: a1b2c3d4e5f6
Revises: 9f5d2d8c7b31
Create Date: 2026-06-17 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "9f5d2d8c7b31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "diary_templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("practice_id", UUID(as_uuid=True), sa.ForeignKey("practices.id"), nullable=False, unique=True),
        sa.Column("practice_name", sa.String(255), nullable=True),
        sa.Column("slot_start", sa.Time(), nullable=False),
        sa.Column("slot_end", sa.Time(), nullable=False),
        sa.Column("slot_interval_minutes", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("footer", JSONB(), nullable=True),
    )
    op.create_index("ix_diary_templates_practice_id", "diary_templates", ["practice_id"])

    op.create_table(
        "diary_columns",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("template_id", UUID(as_uuid=True), sa.ForeignKey("diary_templates.id"), nullable=False),
        sa.Column("practice_id", UUID(as_uuid=True), sa.ForeignKey("practices.id"), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("room_label", sa.String(100), nullable=False),
        sa.Column("assignment", sa.String(255), nullable=True),
        sa.Column("practitioner_id", UUID(as_uuid=True), sa.ForeignKey("practitioners.id"), nullable=True),
        sa.Column("practitioner_ahpra", sa.String(50), nullable=True),
        sa.Column("tint_hex", sa.String(7), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.UniqueConstraint("template_id", "display_order", name="uq_diary_columns_template_order"),
    )
    op.create_index("ix_diary_columns_template_id", "diary_columns", ["template_id"])
    op.create_index("ix_diary_columns_practice_id", "diary_columns", ["practice_id"])

    op.create_table(
        "diary_breaks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("column_id", UUID(as_uuid=True), sa.ForeignKey("diary_columns.id"), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("from_time", sa.Time(), nullable=False),
        sa.Column("to_time", sa.Time(), nullable=False),
    )
    op.create_index("ix_diary_breaks_column_id", "diary_breaks", ["column_id"])


def downgrade() -> None:
    op.drop_index("ix_diary_breaks_column_id", table_name="diary_breaks")
    op.drop_table("diary_breaks")
    op.drop_index("ix_diary_columns_practice_id", table_name="diary_columns")
    op.drop_index("ix_diary_columns_template_id", table_name="diary_columns")
    op.drop_table("diary_columns")
    op.drop_index("ix_diary_templates_practice_id", table_name="diary_templates")
    op.drop_table("diary_templates")
