"""Add appointment command idempotency ledger.

Revision ID: l1m2n3o4p5q6
Revises: k0l1m2n3o4p5
Create Date: 2026-07-07
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from alembic import op


revision: str = "l1m2n3o4p5q6"
down_revision: Union[str, Sequence[str], None] = "k0l1m2n3o4p5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "appointment_command_idempotency",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("practice_id", UUID(as_uuid=True), sa.ForeignKey("practices.id"), nullable=False),
        sa.Column("actor_user_id", sa.String(length=64), nullable=False),
        sa.Column("actor_role", sa.String(length=64), nullable=False),
        sa.Column("operation_id", sa.String(length=100), nullable=False),
        sa.Column("route_family", sa.String(length=100), nullable=False),
        sa.Column("idempotency_key_hash", sa.String(length=128), nullable=False),
        sa.Column("request_body_hash", sa.String(length=128), nullable=False),
        sa.Column("request_body_canonicalization_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("response_status_code", sa.Integer(), nullable=True),
        sa.Column("response_body_hash", sa.String(length=128), nullable=True),
        sa.Column("response_body_json", JSONB, nullable=True),
        sa.Column("result_kind", sa.String(length=50), nullable=True),
        sa.Column("target_appointment_id", UUID(as_uuid=True), sa.ForeignKey("appointments.id"), nullable=True),
        sa.Column("audit_log_id", UUID(as_uuid=True), sa.ForeignKey("appointment_audit_log.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "practice_id",
            "actor_user_id",
            "operation_id",
            "idempotency_key_hash",
            name="uq_appt_cmd_idem_practice_actor_operation_key",
        ),
        sa.CheckConstraint(
            "state in ('in_progress', 'completed', 'failed_transient')",
            name="ck_appt_cmd_idem_state",
        ),
        sa.CheckConstraint(
            "state != 'completed' OR "
            "(response_status_code IS NOT NULL AND "
            "response_body_hash IS NOT NULL AND response_body_json IS NOT NULL)",
            name="ck_appt_cmd_idem_completed_response",
        ),
    )
    op.create_index(
        "ix_appt_cmd_idem_practice_target",
        "appointment_command_idempotency",
        ["practice_id", "target_appointment_id"],
    )
    op.create_index(
        "ix_appt_cmd_idem_practice_created",
        "appointment_command_idempotency",
        ["practice_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_appt_cmd_idem_practice_created", table_name="appointment_command_idempotency")
    op.drop_index("ix_appt_cmd_idem_practice_target", table_name="appointment_command_idempotency")
    op.drop_table("appointment_command_idempotency")
