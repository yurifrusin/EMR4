"""Add a scoped synthetic patient request and exact staff create linkage.

Revision ID: b7c8d9e0f1a2
Revises: a6b7c8d9e0f1 (selected 32-file source map only)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'b7c8d9e0f1a2'
down_revision = 'a6b7c8d9e0f1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        "uq_appt_cmd_idem_practice_id_target", "appointment_command_idempotency",
        ["practice_id", "id", "target_appointment_id"], schema="public",
    )
    op.create_table(
        "patient_booking_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("practice_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("public.practices.id"), nullable=False),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("practitioner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("appointment_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=True)),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("practice_timezone", sa.String(64), nullable=False),
        sa.Column("capability_digest", sa.String(64), nullable=False),
        sa.Column("capability_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("state", sa.String(16), nullable=False, server_default="draft"),
        sa.Column("request_version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.Column("preference_date", sa.Date()),
        sa.Column("earliest_local", sa.Time()),
        sa.Column("latest_local", sa.Time()),
        sa.Column("reason_code", sa.String(32)),
        sa.Column("submission_key_digest", sa.String(64)),
        sa.Column("submission_body_digest", sa.String(64)),
        sa.Column("submission_receipt", postgresql.JSONB()),
        sa.Column("booked_appointment_id", postgresql.UUID(as_uuid=True)),
        sa.Column("booked_command_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("submitted_at", sa.DateTime(timezone=True)),
        sa.Column("cancelled_at", sa.DateTime(timezone=True)),
        sa.Column("booked_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("practice_id", "id", name="uq_patient_request_practice_id_id"),
        sa.UniqueConstraint("practice_id", "booked_appointment_id", name="uq_patient_request_booked_appointment"),
        sa.UniqueConstraint("practice_id", "booked_command_id", name="uq_patient_request_booked_command"),
        sa.ForeignKeyConstraint(["practice_id", "patient_id"], ["public.patients.practice_id", "public.patients.id"], name="fk_patient_request_patient"),
        sa.ForeignKeyConstraint(["practice_id", "practitioner_id"], ["public.practitioners.practice_id", "public.practitioners.id"], name="fk_patient_request_practitioner"),
        sa.ForeignKeyConstraint(["practice_id", "appointment_type_id"], ["public.appointment_types.practice_id", "public.appointment_types.id"], name="fk_patient_request_type"),
        sa.ForeignKeyConstraint(["practice_id", "location_id"], ["public.practice_locations.practice_id", "public.practice_locations.id"], name="fk_patient_request_location"),
        sa.ForeignKeyConstraint(["practice_id", "booked_appointment_id"], ["public.appointments.practice_id", "public.appointments.id"], name="fk_patient_request_appointment"),
        sa.CheckConstraint("state IN ('draft', 'submitted', 'booked', 'cancelled', 'expired')", name="ck_patient_request_state"),
        sa.CheckConstraint("request_version >= 1 AND duration_minutes BETWEEN 1 AND 480", name="ck_patient_request_version_duration"),
        sa.CheckConstraint("(state = 'booked' AND booked_appointment_id IS NOT NULL AND booked_command_id IS NOT NULL AND booked_at IS NOT NULL) OR (state != 'booked' AND booked_appointment_id IS NULL AND booked_command_id IS NULL AND booked_at IS NULL)", name="ck_patient_request_booked_links"),
        sa.CheckConstraint("state NOT IN ('submitted', 'booked') OR (preference_date IS NOT NULL AND earliest_local IS NOT NULL AND latest_local IS NOT NULL AND earliest_local < latest_local AND reason_code = 'follow_up' AND submitted_at IS NOT NULL)", name="ck_patient_request_submitted_preference"),
        schema="public",
    )
    op.create_foreign_key(
        "fk_patient_request_command_target", "patient_booking_requests",
        "appointment_command_idempotency",
        ["practice_id", "booked_command_id", "booked_appointment_id"],
        ["practice_id", "id", "target_appointment_id"],
        source_schema="public", referent_schema="public",
    )
    op.create_index("ix_patient_request_practice_state", "patient_booking_requests", ["practice_id", "state"], schema="public")
    op.execute("ALTER TABLE public.patient_booking_requests ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE public.patient_booking_requests FORCE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY tenant_isolation ON public.patient_booking_requests "
        "FOR ALL TO PUBLIC USING (practice_id = "
        "NULLIF(pg_catalog.current_setting('app.current_practice_id', true), '')::uuid) "
        "WITH CHECK (practice_id = "
        "NULLIF(pg_catalog.current_setting('app.current_practice_id', true), '')::uuid)"
    )


def downgrade():
    op.execute("DROP POLICY tenant_isolation ON public.patient_booking_requests")
    op.drop_index("ix_patient_request_practice_state", table_name="patient_booking_requests", schema="public")
    op.drop_table("patient_booking_requests", schema="public")
    op.drop_constraint("uq_appt_cmd_idem_practice_id_target", "appointment_command_idempotency", type_="unique", schema="public")
