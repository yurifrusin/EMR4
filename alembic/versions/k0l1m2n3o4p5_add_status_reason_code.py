"""Add nullable appointment status reason code fields.

Revision ID: k0l1m2n3o4p5
Revises: j0k1l2m3n4o5
Create Date: 2026-07-05
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "k0l1m2n3o4p5"
down_revision: Union[str, Sequence[str], None] = "j0k1l2m3n4o5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "appointments",
        sa.Column("status_reason_code", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "appointment_audit_log",
        sa.Column("status_reason_code", sa.String(length=50), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("appointment_audit_log", "status_reason_code")
    op.drop_column("appointments", "status_reason_code")
