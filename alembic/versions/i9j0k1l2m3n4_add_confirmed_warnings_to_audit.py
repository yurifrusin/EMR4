"""Add confirmed_warnings to appointment_audit_log.

Revision ID: i9j0k1l2m3n4
Revises: 274919209522, h8i9j0k1l2m3
Create Date: 2026-06-26
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from alembic import op

revision: str = "i9j0k1l2m3n4"
down_revision: Union[str, Sequence[str], None] = ("274919209522", "h8i9j0k1l2m3")
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "appointment_audit_log",
        sa.Column("confirmed_warnings", JSONB, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("appointment_audit_log", "confirmed_warnings")
