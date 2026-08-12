"""Add the unmounted status-confirm physical scaffold.

Revision ID: w2x3y4z5a6b7
Revises: v1w2x3y4z5b6
Create Date: 2026-08-12

This migration is inert until separately admitted and executed. The appointment
trigger is a synchronous row invariant, not an event watcher or cue producer.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "w2x3y4z5a6b7"
down_revision: Union[str, Sequence[str], None] = "v1w2x3y4z5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


APPOINTMENT_VERSION_MAX = 9223372036854775807


def upgrade() -> None:
    # 1. Nullable, no default: avoid a table-rewriting semantic claim.
    op.add_column(
        "appointments",
        sa.Column("appointment_state_version", sa.BigInteger(), nullable=True),
    )
    # 2. New inserts begin at the cutover baseline.
    op.alter_column(
        "appointments",
        "appointment_state_version",
        server_default=sa.text("1"),
    )
    # 3. Existing rows receive a baseline, never fabricated chronology.
    op.execute(
        "UPDATE appointments SET appointment_state_version = 1 "
        "WHERE appointment_state_version IS NULL"
    )
    # 4. Validate the positive BIGINT domain before setting NOT NULL.
    op.execute(
        "ALTER TABLE appointments ADD CONSTRAINT "
        "ck_appointments_state_version_positive "
        "CHECK (appointment_state_version >= 1) NOT VALID"
    )
    op.execute(
        "ALTER TABLE appointments VALIDATE CONSTRAINT "
        "ck_appointments_state_version_positive"
    )
    op.alter_column("appointments", "appointment_state_version", nullable=False)

    # 5. PostgreSQL owns every increment and rejects overflow.
    op.execute(
        f"""
        CREATE FUNCTION emr4_advance_appointment_state_version()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF OLD.appointment_state_version >= {APPOINTMENT_VERSION_MAX} THEN
                RAISE EXCEPTION 'appointment_state_version overflow'
                    USING ERRCODE = '22003';
            END IF;
            NEW.appointment_state_version := OLD.appointment_state_version + 1;
            RETURN NEW;
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_appointments_advance_state_version
        BEFORE UPDATE ON appointments
        FOR EACH ROW
        EXECUTE FUNCTION emr4_advance_appointment_state_version()
        """
    )
    # 6. Fail the migration if any row escaped the cutover invariant.
    op.execute(
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM appointments
                WHERE appointment_state_version IS NULL
                   OR appointment_state_version < 1
                   OR appointment_state_version > {APPOINTMENT_VERSION_MAX}
            ) THEN
                RAISE EXCEPTION 'invalid appointment_state_version after cutover';
            END IF;
        END;
        $$
        """
    )
    # 7. The server default remains one for every later insert.

    for column in (
        sa.Column("completed_receipt_version", sa.SmallInteger(), nullable=True),
        sa.Column("session_binding_digest", sa.LargeBinary(), nullable=True),
        sa.Column("pre_state_version", sa.BigInteger(), nullable=True),
        sa.Column("post_state_version", sa.BigInteger(), nullable=True),
        sa.Column("response_body_canonical_bytes", sa.LargeBinary(), nullable=True),
    ):
        op.add_column("appointment_command_idempotency", column)

    op.create_check_constraint(
        "ck_appt_cmd_idem_receipt_version",
        "appointment_command_idempotency",
        "completed_receipt_version IS NULL OR completed_receipt_version = 1",
    )
    op.create_check_constraint(
        "ck_appt_cmd_idem_status_receipt_v1_complete",
        "appointment_command_idempotency",
        "completed_receipt_version IS NULL OR "
        "(state = 'completed' AND "
        "operation_id = 'confirmAppointmentStatusProposal' AND "
        "route_family = 'status-confirm' AND "
        "result_kind = 'confirmed_write' AND "
        "session_binding_digest IS NOT NULL AND "
        "octet_length(session_binding_digest) = 32 AND "
        "pre_state_version IS NOT NULL AND pre_state_version >= 1 AND "
        "post_state_version IS NOT NULL AND "
        "post_state_version = pre_state_version + 1 AND "
        "response_body_canonical_bytes IS NOT NULL AND "
        "octet_length(response_body_canonical_bytes) > 0 AND "
        "target_appointment_id IS NOT NULL AND audit_log_id IS NOT NULL AND "
        "response_status_code IS NOT NULL AND response_body_hash IS NOT NULL AND "
        "response_body_json IS NOT NULL)",
    )


def downgrade() -> None:
    # Once a v1 receipt exists its byte/version meaning is forward-only.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM appointment_command_idempotency
                WHERE completed_receipt_version = 1
            ) THEN
                RAISE EXCEPTION
                    'status-confirm receipt v1 exists; forward recovery required';
            END IF;
        END;
        $$
        """
    )
    op.drop_constraint(
        "ck_appt_cmd_idem_status_receipt_v1_complete",
        "appointment_command_idempotency",
        type_="check",
    )
    op.drop_constraint(
        "ck_appt_cmd_idem_receipt_version",
        "appointment_command_idempotency",
        type_="check",
    )
    for column_name in (
        "response_body_canonical_bytes",
        "post_state_version",
        "pre_state_version",
        "session_binding_digest",
        "completed_receipt_version",
    ):
        op.drop_column("appointment_command_idempotency", column_name)
    op.execute(
        "DROP TRIGGER trg_appointments_advance_state_version ON appointments"
    )
    op.execute("DROP FUNCTION emr4_advance_appointment_state_version()")
    op.drop_constraint(
        "ck_appointments_state_version_positive",
        "appointments",
        type_="check",
    )
    op.drop_column("appointments", "appointment_state_version")
