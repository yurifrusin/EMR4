"""Add the bounded Reception One committed reschedule event store.

Revision ID: n3o4p5q6r7s8
Revises: m2n3o4p5q6r7
Create Date: 2026-07-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID


revision: str = "n3o4p5q6r7s8"
down_revision: Union[str, Sequence[str], None] = "m2n3o4p5q6r7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_PRACTICE_CONTEXT = (
    "practice_id = nullif(current_setting('app.current_practice_id', true), '')::uuid"
)


def upgrade() -> None:
    op.create_table(
        "diary_committed_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "practice_id",
            UUID(as_uuid=True),
            sa.ForeignKey("practices.id"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("schema_version", sa.String(length=64), nullable=False),
        sa.Column("source_system", sa.String(length=64), nullable=False),
        sa.Column("appointment_id", UUID(as_uuid=True), nullable=False),
        sa.Column("aggregate_revision", sa.Integer(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "actor_user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("actor_role", sa.String(length=64), nullable=False),
        sa.Column("command_id", UUID(as_uuid=True), nullable=False),
        sa.Column("audit_log_id", UUID(as_uuid=True), nullable=False),
        sa.Column("correlation_id", UUID(as_uuid=True), nullable=False),
        sa.Column("evidence_mode", sa.String(length=64), nullable=False),
        sa.Column("payload", JSONB, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "event_type = 'diary.appointment_rescheduled'",
            name="ck_diary_committed_events_type",
        ),
        sa.CheckConstraint(
            "schema_version = 'diary.appointment_rescheduled.v1'",
            name="ck_diary_committed_events_schema",
        ),
        sa.CheckConstraint(
            "source_system = 'emr4-diary'",
            name="ck_diary_committed_events_source",
        ),
        sa.CheckConstraint(
            "evidence_mode = 'authored_synthetic_local'",
            name="ck_diary_committed_events_evidence",
        ),
        sa.CheckConstraint(
            "aggregate_revision > 0",
            name="ck_diary_committed_events_revision",
        ),
        sa.CheckConstraint(
            "expires_at > occurred_at",
            name="ck_diary_committed_events_expiry",
        ),
        sa.CheckConstraint(
            "correlation_id = command_id",
            name="ck_diary_committed_events_correlation",
        ),
        sa.CheckConstraint(
            "jsonb_typeof(payload) = 'object' AND "
            "payload ?& ARRAY['appointment_id', 'practitioner_id', 'location_id', "
            "'start_time', 'end_time', 'reason_codes'] AND "
            "payload - ARRAY['appointment_id', 'practitioner_id', 'location_id', "
            "'start_time', 'end_time', 'reason_codes'] = '{}'::jsonb AND "
            "payload->'reason_codes' = '[\"appointment_time_changed\"]'::jsonb",
            name="ck_diary_committed_events_payload_allowlist",
        ),
        sa.UniqueConstraint(
            "practice_id", "id", name="uq_diary_committed_events_practice_id_id"
        ),
        sa.UniqueConstraint(
            "practice_id",
            "appointment_id",
            "aggregate_revision",
            name="uq_diary_committed_events_aggregate_revision",
        ),
        sa.UniqueConstraint("command_id", name="uq_diary_committed_events_command"),
        sa.UniqueConstraint("audit_log_id", name="uq_diary_committed_events_audit"),
        sa.ForeignKeyConstraint(
            ["practice_id", "appointment_id"],
            ["appointments.practice_id", "appointments.id"],
            name="fk_diary_committed_events_practice_appointment",
        ),
        sa.ForeignKeyConstraint(
            ["practice_id", "command_id"],
            [
                "appointment_command_idempotency.practice_id",
                "appointment_command_idempotency.id",
            ],
            name="fk_diary_committed_events_practice_command",
        ),
        sa.ForeignKeyConstraint(
            ["practice_id", "audit_log_id"],
            ["appointment_audit_log.practice_id", "appointment_audit_log.id"],
            name="fk_diary_committed_events_practice_audit",
        ),
    )
    op.create_index(
        "ix_diary_committed_events_practice_order",
        "diary_committed_events",
        ["practice_id", "occurred_at", "id"],
    )
    op.create_index(
        "ix_diary_committed_events_practice_expiry",
        "diary_committed_events",
        ["practice_id", "expires_at"],
    )

    op.execute('ALTER TABLE "diary_committed_events" ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE "diary_committed_events" FORCE ROW LEVEL SECURITY')
    op.execute(
        'CREATE POLICY "diary_committed_events_practice_select" '
        'ON "diary_committed_events" FOR SELECT '
        f"USING ({_PRACTICE_CONTEXT})"
    )
    op.execute(
        'CREATE POLICY "diary_committed_events_practice_insert" '
        'ON "diary_committed_events" FOR INSERT '
        f"WITH CHECK ({_PRACTICE_CONTEXT})"
    )
    op.execute(
        """
        CREATE FUNCTION emr4_reject_diary_committed_event_mutation()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
          RAISE EXCEPTION 'diary committed-event evidence is append-only'
            USING ERRCODE = '55000';
        END
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_diary_committed_events_append_only
        BEFORE UPDATE OR DELETE ON diary_committed_events
        FOR EACH ROW
        EXECUTE FUNCTION emr4_reject_diary_committed_event_mutation()
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_diary_committed_events_append_only "
        "ON diary_committed_events"
    )
    op.execute("DROP FUNCTION IF EXISTS emr4_reject_diary_committed_event_mutation()")
    op.execute(
        'DROP POLICY IF EXISTS "diary_committed_events_practice_insert" '
        'ON "diary_committed_events"'
    )
    op.execute(
        'DROP POLICY IF EXISTS "diary_committed_events_practice_select" '
        'ON "diary_committed_events"'
    )
    op.execute('ALTER TABLE "diary_committed_events" NO FORCE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE "diary_committed_events" DISABLE ROW LEVEL SECURITY')
    op.drop_index(
        "ix_diary_committed_events_practice_expiry",
        table_name="diary_committed_events",
    )
    op.drop_index(
        "ix_diary_committed_events_practice_order",
        table_name="diary_committed_events",
    )
    op.drop_table("diary_committed_events")
