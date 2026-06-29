"""Add access_ai_audit_log table.

Revision ID: j0k1l2m3n4o5
Revises: i9j0k1l2m3n4
Create Date: 2026-06-29
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from alembic import op

revision: str = "j0k1l2m3n4o5"
down_revision: Union[str, Sequence[str], None] = "i9j0k1l2m3n4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "access_ai_audit_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("event_id", UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("practice_id", UUID(as_uuid=True), sa.ForeignKey("practices.id"), nullable=True),
        sa.Column("actor_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("capability", sa.String(100), nullable=True),
        sa.Column("method", sa.String(50), nullable=True),
        sa.Column("decision", sa.String(50), nullable=False),
        sa.Column("reason_code", sa.String(100), nullable=True),
        sa.Column("source_surface", sa.String(50), nullable=False),
        sa.Column("target_resource_type", sa.String(100), nullable=True),
        sa.Column("target_resource_id", sa.String(100), nullable=True),
        sa.Column("correlation_id", UUID(as_uuid=True), nullable=False),
        sa.Column("actor_roles", JSONB, nullable=True),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("event_timestamp", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_access_ai_audit_log_practice_created",
        "access_ai_audit_log",
        ["practice_id", "created_at"],
    )
    op.create_index(
        "ix_access_ai_audit_log_correlation_id",
        "access_ai_audit_log",
        ["correlation_id"],
    )
    op.create_index(
        "ix_access_ai_audit_log_event_type",
        "access_ai_audit_log",
        ["event_type"],
    )


def downgrade() -> None:
    op.drop_index("ix_access_ai_audit_log_event_type", table_name="access_ai_audit_log")
    op.drop_index("ix_access_ai_audit_log_correlation_id", table_name="access_ai_audit_log")
    op.drop_index("ix_access_ai_audit_log_practice_created", table_name="access_ai_audit_log")
    op.drop_table("access_ai_audit_log")
