"""Add B4.1 Davida default-location command runtime persistence.

Revision ID: v1w2x3y4z5b6
Revises: u0v1w2x3y4z5
Create Date: 2026-08-05
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID


revision: str = "v1w2x3y4z5b6"
down_revision: Union[str, Sequence[str], None] = "u0v1w2x3y4z5"
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
    op.add_column(
        "practitioners",
        sa.Column("aggregate_version", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "practice_administration_confirmation_evidence",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "practice_id",
            UUID(as_uuid=True),
            sa.ForeignKey("practices.id"),
            nullable=False,
        ),
        sa.Column(
            "actor_user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("actor_role", sa.String(length=64), nullable=False),
        sa.Column("proposal_id", sa.String(length=1024), nullable=False),
        sa.Column("proposal_hash", sa.String(length=64), nullable=False),
        sa.Column("canonical_request_hash", sa.String(length=64), nullable=False),
        sa.Column("before_state_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "practitioner_id",
            UUID(as_uuid=True),
            sa.ForeignKey("practitioners.id"),
            nullable=False,
        ),
        sa.Column(
            "requested_location_id",
            UUID(as_uuid=True),
            sa.ForeignKey("practice_locations.id"),
            nullable=False,
        ),
        sa.Column("expected_aggregate_version", sa.Integer(), nullable=False),
        sa.Column("correlation_id", sa.String(length=128), nullable=False),
        sa.Column("idempotency_key_hash", sa.String(length=64), nullable=False),
        sa.Column("nonce", sa.String(length=128), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("consumed_by_command_id", UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "state in ('live', 'consumed')", name="ck_b4_evidence_state"
        ),
        sa.CheckConstraint(
            "expires_at > issued_at", name="ck_b4_evidence_expiry"
        ),
        sa.CheckConstraint(
            "expected_aggregate_version >= 0",
            name="ck_b4_evidence_expected_version",
        ),
        sa.UniqueConstraint(
            "practice_id", "id", name="uq_b4_evidence_practice_id_id"
        ),
        sa.UniqueConstraint(
            "practice_id",
            "actor_user_id",
            "proposal_hash",
            name="uq_b4_evidence_practice_actor_proposal",
        ),
        sa.UniqueConstraint("nonce", name="uq_b4_evidence_nonce"),
    )
    op.create_index(
        "ix_b4_evidence_practice_actor",
        "practice_administration_confirmation_evidence",
        ["practice_id", "actor_user_id"],
    )
    op.create_index(
        "ix_b4_evidence_practice_expiry",
        "practice_administration_confirmation_evidence",
        ["practice_id", "expires_at"],
    )

    op.create_table(
        "practice_administration_command_idempotency",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "practice_id",
            UUID(as_uuid=True),
            sa.ForeignKey("practices.id"),
            nullable=False,
        ),
        sa.Column(
            "actor_user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("actor_role", sa.String(length=64), nullable=False),
        sa.Column("operation_id", sa.String(length=100), nullable=False),
        sa.Column("route_family", sa.String(length=100), nullable=False),
        sa.Column("idempotency_key_hash", sa.String(length=64), nullable=False),
        sa.Column("request_body_hash", sa.String(length=64), nullable=False),
        sa.Column("canonical_request_hash", sa.String(length=64), nullable=False),
        sa.Column("proposal_hash", sa.String(length=64), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("response_status_code", sa.Integer(), nullable=True),
        sa.Column("response_body_hash", sa.String(length=64), nullable=True),
        sa.Column("response_body_json", JSONB, nullable=True),
        sa.Column("result_kind", sa.String(length=50), nullable=True),
        sa.Column("receipt_id", sa.String(length=128), nullable=True),
        sa.Column(
            "practitioner_id",
            UUID(as_uuid=True),
            sa.ForeignKey("practitioners.id"),
            nullable=True,
        ),
        sa.Column("confirmation_evidence_id", UUID(as_uuid=True), nullable=True),
        sa.Column("audit_event_id", UUID(as_uuid=True), nullable=True),
        sa.Column("outbox_event_id", UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "practice_id", "id", name="uq_b4_cmd_idem_practice_id_id"
        ),
        sa.UniqueConstraint(
            "practice_id",
            "actor_user_id",
            "operation_id",
            "idempotency_key_hash",
            name="uq_b4_cmd_idem_practice_actor_operation_key",
        ),
        sa.CheckConstraint(
            "state in ('in_progress', 'completed', 'failed_transient')",
            name="ck_b4_cmd_idem_state",
        ),
        sa.CheckConstraint(
            "state != 'completed' OR "
            "(response_status_code IS NOT NULL AND "
            "response_body_hash IS NOT NULL AND response_body_json IS NOT NULL)",
            name="ck_b4_cmd_idem_completed_response",
        ),
    )
    op.create_index(
        "ix_b4_cmd_idem_practice_created",
        "practice_administration_command_idempotency",
        ["practice_id", "created_at"],
    )
    op.create_index(
        "ix_b4_cmd_idem_practice_evidence",
        "practice_administration_command_idempotency",
        ["practice_id", "confirmation_evidence_id"],
    )

    op.create_table(
        "practice_administration_audit_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "practice_id",
            UUID(as_uuid=True),
            sa.ForeignKey("practices.id"),
            nullable=False,
        ),
        sa.Column(
            "actor_user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("actor_role", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("command_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "practitioner_id",
            UUID(as_uuid=True),
            sa.ForeignKey("practitioners.id"),
            nullable=False,
        ),
        sa.Column(
            "before_location_id",
            UUID(as_uuid=True),
            sa.ForeignKey("practice_locations.id"),
            nullable=True,
        ),
        sa.Column(
            "after_location_id",
            UUID(as_uuid=True),
            sa.ForeignKey("practice_locations.id"),
            nullable=False,
        ),
        sa.Column("expected_aggregate_version", sa.Integer(), nullable=False),
        sa.Column("resulting_aggregate_version", sa.Integer(), nullable=False),
        sa.Column("proposal_hash", sa.String(length=64), nullable=False),
        sa.Column("correlation_id", sa.String(length=128), nullable=False),
        sa.Column("committed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "action = 'practitioner_default_location_changed'",
            name="ck_b4_audit_action",
        ),
        sa.CheckConstraint(
            "resulting_aggregate_version = expected_aggregate_version + 1",
            name="ck_b4_audit_version_step",
        ),
        sa.UniqueConstraint(
            "practice_id", "id", name="uq_b4_audit_practice_id_id"
        ),
        sa.UniqueConstraint("command_id", name="uq_b4_audit_command"),
    )
    op.create_index(
        "ix_b4_audit_practice_practitioner",
        "practice_administration_audit_events",
        ["practice_id", "practitioner_id"],
    )

    op.create_table(
        "practice_administration_outbox_events",
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
        sa.Column(
            "actor_user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("actor_role", sa.String(length=64), nullable=False),
        sa.Column("command_id", UUID(as_uuid=True), nullable=False),
        sa.Column("audit_event_id", UUID(as_uuid=True), nullable=False),
        sa.Column("correlation_id", sa.String(length=128), nullable=False),
        sa.Column(
            "published",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("payload", JSONB, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "event_type = 'practice.practitioner_default_location_changed'",
            name="ck_b4_outbox_type",
        ),
        sa.CheckConstraint(
            "schema_version = 'practice.practitioner_default_location_changed.v1'",
            name="ck_b4_outbox_schema",
        ),
        sa.CheckConstraint(
            "source_system = 'emr4-practice-administration'",
            name="ck_b4_outbox_source",
        ),
        sa.CheckConstraint("published = false", name="ck_b4_outbox_unpublished"),
        sa.CheckConstraint(
            "jsonb_typeof(payload) = 'object' AND "
            "payload ?& ARRAY['practitioner_id', 'before_location_id', "
            "'after_location_id', 'aggregate_version', 'reason_codes'] AND "
            "payload - ARRAY['practitioner_id', 'before_location_id', "
            "'after_location_id', 'aggregate_version', 'reason_codes'] = '{}'::jsonb AND "
            "payload->'reason_codes' = '[\"practitioner_default_location_changed\"]'::jsonb",
            name="ck_b4_outbox_payload_allowlist",
        ),
        sa.UniqueConstraint(
            "practice_id", "id", name="uq_b4_outbox_practice_id_id"
        ),
        sa.UniqueConstraint("command_id", name="uq_b4_outbox_command"),
        sa.UniqueConstraint("audit_event_id", name="uq_b4_outbox_audit"),
    )
    op.create_index(
        "ix_b4_outbox_practice_order",
        "practice_administration_outbox_events",
        ["practice_id", "created_at", "id"],
    )

    _enable_all_practice_policy(
        "practice_administration_confirmation_evidence",
        "b4_evidence_practice_all",
    )
    _enable_all_practice_policy(
        "practice_administration_command_idempotency",
        "b4_cmd_idem_practice_all",
    )
    _enable_all_practice_policy(
        "practice_administration_audit_events",
        "b4_audit_practice_all",
    )
    _enable_all_practice_policy(
        "practice_administration_outbox_events",
        "b4_outbox_practice_all",
    )

    op.execute(
        """
        CREATE FUNCTION emr4_reject_b4_audit_mutation()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
          RAISE EXCEPTION 'practice-administration audit is append-only'
            USING ERRCODE = '55000';
        END
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_b4_audit_append_only
        BEFORE UPDATE OR DELETE ON practice_administration_audit_events
        FOR EACH ROW
        EXECUTE FUNCTION emr4_reject_b4_audit_mutation()
        """
    )
    op.execute(
        """
        CREATE FUNCTION emr4_reject_b4_outbox_mutation()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
          RAISE EXCEPTION 'practice-administration outbox is append-only'
            USING ERRCODE = '55000';
        END
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_b4_outbox_append_only
        BEFORE UPDATE OR DELETE ON practice_administration_outbox_events
        FOR EACH ROW
        EXECUTE FUNCTION emr4_reject_b4_outbox_mutation()
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_b4_outbox_append_only ON practice_administration_outbox_events")
    op.execute("DROP FUNCTION IF EXISTS emr4_reject_b4_outbox_mutation()")
    op.execute("DROP TRIGGER IF EXISTS trg_b4_audit_append_only ON practice_administration_audit_events")
    op.execute("DROP FUNCTION IF EXISTS emr4_reject_b4_audit_mutation()")

    _disable_policy(
        "practice_administration_outbox_events",
        "b4_outbox_practice_all",
    )
    _disable_policy(
        "practice_administration_audit_events",
        "b4_audit_practice_all",
    )
    _disable_policy(
        "practice_administration_command_idempotency",
        "b4_cmd_idem_practice_all",
    )
    _disable_policy(
        "practice_administration_confirmation_evidence",
        "b4_evidence_practice_all",
    )

    op.drop_index(
        "ix_b4_outbox_practice_order",
        table_name="practice_administration_outbox_events",
    )
    op.drop_table("practice_administration_outbox_events")

    op.drop_index(
        "ix_b4_audit_practice_practitioner",
        table_name="practice_administration_audit_events",
    )
    op.drop_table("practice_administration_audit_events")

    op.drop_index(
        "ix_b4_cmd_idem_practice_evidence",
        table_name="practice_administration_command_idempotency",
    )
    op.drop_index(
        "ix_b4_cmd_idem_practice_created",
        table_name="practice_administration_command_idempotency",
    )
    op.drop_table("practice_administration_command_idempotency")

    op.drop_index(
        "ix_b4_evidence_practice_expiry",
        table_name="practice_administration_confirmation_evidence",
    )
    op.drop_index(
        "ix_b4_evidence_practice_actor",
        table_name="practice_administration_confirmation_evidence",
    )
    op.drop_table("practice_administration_confirmation_evidence")

    op.drop_column("practitioners", "aggregate_version")
