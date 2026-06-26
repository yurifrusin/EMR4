"""Add appointment_audit_log table for confirmed mutation history.

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-06-26
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from alembic import op

revision: str = "h8i9j0k1l2m3"
down_revision: Union[str, Sequence[str], None] = "g7h8i9j0k1l2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "appointment_audit_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "practice_id", UUID(as_uuid=True),
            sa.ForeignKey("practices.id"), nullable=False,
        ),
        sa.Column(
            "appointment_id", UUID(as_uuid=True),
            sa.ForeignKey("appointments.id"), nullable=False,
        ),
        sa.Column(
            "confirmed_by_user_id", UUID(as_uuid=True),
            sa.ForeignKey("users.id"), nullable=False,
        ),
        sa.Column(
            "action",
            sa.Enum("create", "update", "status_change", "delete",
                    name="appointmentauditaction"),
            nullable=False,
        ),
        sa.Column(
            "status_before",
            sa.Enum(
                "Booked", "Confirmed", "Arrived", "InConsult",
                "Completed", "Cancelled", "NoShow", "DNA",
                name="appointmentstatus", create_type=False,
            ),
            nullable=True,
        ),
        sa.Column(
            "status_after",
            sa.Enum(
                "Booked", "Confirmed", "Arrived", "InConsult",
                "Completed", "Cancelled", "NoShow", "DNA",
                name="appointmentstatus", create_type=False,
            ),
            nullable=True,
        ),
        sa.Column("cancellation_reason", sa.String(500), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"), nullable=False,
        ),
    )
    op.create_index(
        "ix_appt_audit_log_practice_appt",
        "appointment_audit_log",
        ["practice_id", "appointment_id"],
    )
    op.create_index(
        "ix_appt_audit_log_appointment_id",
        "appointment_audit_log",
        ["appointment_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_appt_audit_log_appointment_id", table_name="appointment_audit_log")
    op.drop_index("ix_appt_audit_log_practice_appt", table_name="appointment_audit_log")
    op.drop_table("appointment_audit_log")
    op.execute("DROP TYPE IF EXISTS appointmentauditaction")
