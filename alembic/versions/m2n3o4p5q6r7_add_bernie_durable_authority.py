"""Add durable Bernie sessions, correlation, RLS, and immutable audit.

Revision ID: m2n3o4p5q6r7
Revises: l1m2n3o4p5q6
Create Date: 2026-07-19
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID


revision: str = "m2n3o4p5q6r7"
down_revision: Union[str, Sequence[str], None] = "l1m2n3o4p5q6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_PRACTICE_CONTEXT = (
    "practice_id = nullif(current_setting('app.current_practice_id', true), '')::uuid"
)


def _enable_all_practice_policy(table_name: str, policy_name: str) -> None:
    op.execute(f'ALTER TABLE "{table_name}" ENABLE ROW LEVEL SECURITY')
    op.execute(f'ALTER TABLE "{table_name}" FORCE ROW LEVEL SECURITY')
    op.execute(
        f'CREATE POLICY "{policy_name}" ON "{table_name}" '
        f"USING ({_PRACTICE_CONTEXT}) WITH CHECK ({_PRACTICE_CONTEXT})"
    )


def _disable_policy(table_name: str, policy_name: str) -> None:
    op.execute(f'DROP POLICY IF EXISTS "{policy_name}" ON "{table_name}"')
    op.execute(f'ALTER TABLE "{table_name}" NO FORCE ROW LEVEL SECURITY')
    op.execute(f'ALTER TABLE "{table_name}" DISABLE ROW LEVEL SECURITY')


def upgrade() -> None:
    op.create_table(
        "bernie_booking_sessions",
        sa.Column("session_id", sa.String(length=64), primary_key=True),
        sa.Column("practice_id", UUID(as_uuid=True), sa.ForeignKey("practices.id"), nullable=False),
        sa.Column("staff_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("surface_id", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=64), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("request_reference_date", sa.Date(), nullable=True),
        sa.Column("patient_id", UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=True),
        sa.Column("patient_band", sa.String(length=64), nullable=True),
        sa.Column("practitioner_id", UUID(as_uuid=True), sa.ForeignKey("practitioners.id"), nullable=True),
        sa.Column("practitioner_band", sa.String(length=64), nullable=True),
        sa.Column("candidate_freshness_ids", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("staged_proposal_freshness_id", sa.String(length=128), nullable=True),
        sa.Column("turn_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_event_id", sa.String(length=100), nullable=True),
        sa.Column("stale_reason_code", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("revision >= 0", name="ck_bernie_booking_sessions_revision"),
        sa.CheckConstraint("turn_count >= 0", name="ck_bernie_booking_sessions_turn_count"),
        sa.CheckConstraint(
            "state in ("
            "'instruction_entry', 'recognition', 'clarification', "
            "'context_enrichment', 'slot_search', 'candidate_selection', "
            "'proposal_preview', 'confirmation', 'confirmed', 'no_slot', "
            "'clinic_day_exhausted', 'handed_off'"
            ")",
            name="ck_bernie_booking_sessions_state",
        ),
        sa.UniqueConstraint(
            "practice_id",
            "session_id",
            name="uq_bernie_booking_sessions_practice_session",
        ),
    )
    op.create_index(
        "uq_bernie_booking_sessions_active_surface",
        "bernie_booking_sessions",
        ["practice_id", "staff_user_id", "surface_id"],
        unique=True,
        postgresql_where=sa.text("is_active"),
    )
    op.create_index(
        "ix_bernie_booking_sessions_owner_surface",
        "bernie_booking_sessions",
        ["practice_id", "staff_user_id", "surface_id"],
    )
    op.create_index(
        "ix_bernie_booking_sessions_practice_expiry",
        "bernie_booking_sessions",
        ["practice_id", "expires_at"],
    )
    op.create_index("ix_bernie_booking_sessions_patient_id", "bernie_booking_sessions", ["patient_id"])
    op.create_index(
        "ix_bernie_booking_sessions_practitioner_id",
        "bernie_booking_sessions",
        ["practitioner_id"],
    )

    op.create_table(
        "bernie_session_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("practice_id", UUID(as_uuid=True), sa.ForeignKey("practices.id"), nullable=False),
        sa.Column(
            "session_id",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column("event_id", sa.String(length=100), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("session_revision", sa.Integer(), nullable=False),
        sa.Column("turn_index", sa.Integer(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expected_revision", sa.Integer(), nullable=True),
        sa.Column("idempotency_key_hash", sa.String(length=64), nullable=True),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("payload", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("session_revision > 0", name="ck_bernie_session_events_revision"),
        sa.CheckConstraint("turn_index >= 0", name="ck_bernie_session_events_turn_index"),
        sa.UniqueConstraint("session_id", "event_id", name="uq_bernie_session_events_event_id"),
        sa.UniqueConstraint(
            "session_id",
            "session_revision",
            name="uq_bernie_session_events_revision",
        ),
        sa.UniqueConstraint(
            "session_id",
            "idempotency_key_hash",
            name="uq_bernie_session_events_idempotency_hash",
        ),
        sa.ForeignKeyConstraint(
            ["practice_id", "session_id"],
            [
                "bernie_booking_sessions.practice_id",
                "bernie_booking_sessions.session_id",
            ],
            name="fk_bernie_session_events_practice_session",
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_bernie_session_events_practice_session",
        "bernie_session_events",
        ["practice_id", "session_id"],
    )
    op.create_index(
        "ix_bernie_session_events_session_created",
        "bernie_session_events",
        ["session_id", "created_at"],
    )

    op.create_unique_constraint(
        "uq_appointments_practice_id_id",
        "appointments",
        ["practice_id", "id"],
    )
    op.create_unique_constraint(
        "uq_appt_audit_log_practice_id_id",
        "appointment_audit_log",
        ["practice_id", "id"],
    )
    op.create_unique_constraint(
        "uq_appt_cmd_idem_practice_id_id",
        "appointment_command_idempotency",
        ["practice_id", "id"],
    )

    op.add_column(
        "appointment_command_idempotency",
        sa.Column("bernie_session_id", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "ix_appt_cmd_idem_practice_session",
        "appointment_command_idempotency",
        ["practice_id", "bernie_session_id"],
    )
    op.create_index(
        "uq_appt_cmd_idem_audit_log_id",
        "appointment_command_idempotency",
        ["audit_log_id"],
        unique=True,
        postgresql_where=sa.text("audit_log_id IS NOT NULL"),
    )

    op.add_column(
        "appointment_audit_log",
        sa.Column("command_id", UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "appointment_audit_log",
        sa.Column("bernie_session_id", sa.String(length=64), nullable=True),
    )
    op.create_foreign_key(
        "fk_appt_audit_log_command_id",
        "appointment_audit_log",
        "appointment_command_idempotency",
        ["command_id"],
        ["id"],
    )
    op.create_index(
        "uq_appt_audit_log_command_id",
        "appointment_audit_log",
        ["command_id"],
        unique=True,
        postgresql_where=sa.text("command_id IS NOT NULL"),
    )
    op.create_index(
        "ix_appt_audit_log_practice_session",
        "appointment_audit_log",
        ["practice_id", "bernie_session_id"],
    )

    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1
            FROM appointment_command_idempotency AS i
            LEFT JOIN appointment_audit_log AS a
              ON a.practice_id = i.practice_id
             AND a.appointment_id = i.target_appointment_id
             AND a.action::text = 'create'
            WHERE i.state = 'completed'
              AND i.operation_id = 'confirmAppointmentCreateProposal'
              AND i.result_kind = 'confirmed_write'
              AND i.audit_log_id IS NULL
            GROUP BY i.id
            HAVING count(a.id) <> 1
          ) THEN
            RAISE EXCEPTION 'completed create command does not have exactly one matching create audit';
          END IF;
        END
        $$
        """
    )
    op.execute(
        """
        UPDATE appointment_command_idempotency AS i
        SET audit_log_id = a.id
        FROM appointment_audit_log AS a
        WHERE i.state = 'completed'
          AND i.operation_id = 'confirmAppointmentCreateProposal'
          AND i.result_kind = 'confirmed_write'
          AND i.audit_log_id IS NULL
          AND a.practice_id = i.practice_id
          AND a.appointment_id = i.target_appointment_id
          AND a.action::text = 'create'
        """
    )
    op.execute(
        """
        UPDATE appointment_audit_log AS a
        SET command_id = i.id
        FROM appointment_command_idempotency AS i
        WHERE i.audit_log_id = a.id
          AND a.command_id IS NULL
        """
    )
    op.create_check_constraint(
        "ck_appt_cmd_idem_completed_create_correlation",
        "appointment_command_idempotency",
        "NOT (state = 'completed' AND "
        "operation_id = 'confirmAppointmentCreateProposal' AND "
        "result_kind = 'confirmed_write') OR "
        "(target_appointment_id IS NOT NULL AND audit_log_id IS NOT NULL)",
    )
    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1
            FROM appointment_audit_log AS a
            JOIN appointments AS p ON p.id = a.appointment_id
            WHERE p.practice_id <> a.practice_id
          ) THEN
            RAISE EXCEPTION 'appointment audit practice does not match appointment practice';
          END IF;
          IF EXISTS (
            SELECT 1
            FROM appointment_command_idempotency AS i
            JOIN appointments AS p ON p.id = i.target_appointment_id
            WHERE p.practice_id <> i.practice_id
          ) THEN
            RAISE EXCEPTION 'appointment command practice does not match target appointment practice';
          END IF;
          IF EXISTS (
            SELECT 1
            FROM appointment_command_idempotency AS i
            JOIN appointment_audit_log AS a ON a.id = i.audit_log_id
            WHERE a.practice_id <> i.practice_id
          ) THEN
            RAISE EXCEPTION 'appointment command practice does not match audit practice';
          END IF;
          IF EXISTS (
            SELECT 1
            FROM appointment_audit_log AS a
            JOIN appointment_command_idempotency AS i ON i.id = a.command_id
            WHERE i.practice_id <> a.practice_id
          ) THEN
            RAISE EXCEPTION 'appointment audit practice does not match command practice';
          END IF;
        END
        $$
        """
    )
    op.create_foreign_key(
        "fk_appt_audit_log_practice_appointment",
        "appointment_audit_log",
        "appointments",
        ["practice_id", "appointment_id"],
        ["practice_id", "id"],
    )
    op.create_foreign_key(
        "fk_appt_cmd_idem_practice_target",
        "appointment_command_idempotency",
        "appointments",
        ["practice_id", "target_appointment_id"],
        ["practice_id", "id"],
    )
    op.create_foreign_key(
        "fk_appt_audit_log_practice_command",
        "appointment_audit_log",
        "appointment_command_idempotency",
        ["practice_id", "command_id"],
        ["practice_id", "id"],
    )
    op.create_foreign_key(
        "fk_appt_cmd_idem_practice_audit",
        "appointment_command_idempotency",
        "appointment_audit_log",
        ["practice_id", "audit_log_id"],
        ["practice_id", "id"],
    )

    _enable_all_practice_policy("bernie_booking_sessions", "bernie_booking_sessions_practice_all")
    op.execute('ALTER TABLE "bernie_session_events" ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE "bernie_session_events" FORCE ROW LEVEL SECURITY')
    op.execute(
        'CREATE POLICY "bernie_session_events_practice_select" ON "bernie_session_events" '
        f"FOR SELECT USING ({_PRACTICE_CONTEXT})"
    )
    op.execute(
        'CREATE POLICY "bernie_session_events_practice_insert" ON "bernie_session_events" '
        f"FOR INSERT WITH CHECK ({_PRACTICE_CONTEXT})"
    )
    _enable_all_practice_policy("appointments", "appointments_practice_all")
    _enable_all_practice_policy(
        "appointment_command_idempotency",
        "appointment_command_idempotency_practice_all",
    )
    op.execute('ALTER TABLE "appointment_audit_log" ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE "appointment_audit_log" FORCE ROW LEVEL SECURITY')
    op.execute(
        'CREATE POLICY "appointment_audit_log_practice_select" ON "appointment_audit_log" '
        f"FOR SELECT USING ({_PRACTICE_CONTEXT})"
    )
    op.execute(
        'CREATE POLICY "appointment_audit_log_practice_insert" ON "appointment_audit_log" '
        f"FOR INSERT WITH CHECK ({_PRACTICE_CONTEXT})"
    )

    op.execute(
        """
        CREATE FUNCTION emr4_reject_appointment_audit_mutation()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
          RAISE EXCEPTION 'appointment audit evidence is append-only'
            USING ERRCODE = '55000';
        END
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_appointment_audit_log_append_only
        BEFORE UPDATE OR DELETE ON appointment_audit_log
        FOR EACH ROW
        EXECUTE FUNCTION emr4_reject_appointment_audit_mutation()
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_appointment_audit_log_append_only ON appointment_audit_log")
    op.execute("DROP FUNCTION IF EXISTS emr4_reject_appointment_audit_mutation()")

    op.execute(
        'DROP POLICY IF EXISTS "appointment_audit_log_practice_insert" ON "appointment_audit_log"'
    )
    op.execute(
        'DROP POLICY IF EXISTS "appointment_audit_log_practice_select" ON "appointment_audit_log"'
    )
    op.execute('ALTER TABLE "appointment_audit_log" NO FORCE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE "appointment_audit_log" DISABLE ROW LEVEL SECURITY')
    _disable_policy(
        "appointment_command_idempotency",
        "appointment_command_idempotency_practice_all",
    )
    _disable_policy("appointments", "appointments_practice_all")
    op.execute(
        'DROP POLICY IF EXISTS "bernie_session_events_practice_insert" ON "bernie_session_events"'
    )
    op.execute(
        'DROP POLICY IF EXISTS "bernie_session_events_practice_select" ON "bernie_session_events"'
    )
    op.execute('ALTER TABLE "bernie_session_events" NO FORCE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE "bernie_session_events" DISABLE ROW LEVEL SECURITY')
    _disable_policy("bernie_booking_sessions", "bernie_booking_sessions_practice_all")

    op.drop_constraint(
        "fk_appt_cmd_idem_practice_audit",
        "appointment_command_idempotency",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_appt_audit_log_practice_command",
        "appointment_audit_log",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_appt_cmd_idem_practice_target",
        "appointment_command_idempotency",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_appt_audit_log_practice_appointment",
        "appointment_audit_log",
        type_="foreignkey",
    )

    op.drop_constraint(
        "ck_appt_cmd_idem_completed_create_correlation",
        "appointment_command_idempotency",
        type_="check",
    )

    op.drop_index("ix_appt_audit_log_practice_session", table_name="appointment_audit_log")
    op.drop_index("uq_appt_audit_log_command_id", table_name="appointment_audit_log")
    op.drop_constraint(
        "fk_appt_audit_log_command_id",
        "appointment_audit_log",
        type_="foreignkey",
    )
    op.drop_column("appointment_audit_log", "bernie_session_id")
    op.drop_column("appointment_audit_log", "command_id")

    op.drop_index("uq_appt_cmd_idem_audit_log_id", table_name="appointment_command_idempotency")
    op.drop_index("ix_appt_cmd_idem_practice_session", table_name="appointment_command_idempotency")
    op.drop_column("appointment_command_idempotency", "bernie_session_id")

    op.drop_constraint(
        "uq_appt_cmd_idem_practice_id_id",
        "appointment_command_idempotency",
        type_="unique",
    )
    op.drop_constraint(
        "uq_appt_audit_log_practice_id_id",
        "appointment_audit_log",
        type_="unique",
    )
    op.drop_constraint(
        "uq_appointments_practice_id_id",
        "appointments",
        type_="unique",
    )

    op.drop_index("ix_bernie_session_events_session_created", table_name="bernie_session_events")
    op.drop_index("ix_bernie_session_events_practice_session", table_name="bernie_session_events")
    op.drop_table("bernie_session_events")

    op.drop_index("ix_bernie_booking_sessions_practitioner_id", table_name="bernie_booking_sessions")
    op.drop_index("ix_bernie_booking_sessions_patient_id", table_name="bernie_booking_sessions")
    op.drop_index("ix_bernie_booking_sessions_practice_expiry", table_name="bernie_booking_sessions")
    op.drop_index("ix_bernie_booking_sessions_owner_surface", table_name="bernie_booking_sessions")
    op.drop_index("uq_bernie_booking_sessions_active_surface", table_name="bernie_booking_sessions")
    op.drop_table("bernie_booking_sessions")
