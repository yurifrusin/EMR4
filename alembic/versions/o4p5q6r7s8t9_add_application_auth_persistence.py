"""Add authored-synthetic shared application-auth persistence.

Revision ID: o4p5q6r7s8t9
Revises: n3o4p5q6r7s8
Create Date: 2026-08-01
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY


revision: str = "o4p5q6r7s8t9"
down_revision: Union[str, Sequence[str], None] = "n3o4p5q6r7s8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_PRACTICE_CONTEXT = (
    "practice_ref = nullif(current_setting('app.current_practice_ref', true), '')"
)
_SYNTHETIC_REF = "^synthetic-[a-z0-9-]{1,64}$"
_HASH_REF = "^sha256:[0-9a-f]{64}$"
_ROLES = "'GP', 'Receptionist', 'Nurse', 'Admin', 'PracticeOwner'"
_STATUSES = "'active', 'revoked'"


def _enable_state_rls(table_name: str) -> None:
    op.execute(f'ALTER TABLE "{table_name}" ENABLE ROW LEVEL SECURITY')
    op.execute(f'ALTER TABLE "{table_name}" FORCE ROW LEVEL SECURITY')
    op.execute(
        f'CREATE POLICY "{table_name}_practice_all" ON "{table_name}" '
        f"USING ({_PRACTICE_CONTEXT}) WITH CHECK ({_PRACTICE_CONTEXT})"
    )


def _disable_state_rls(table_name: str) -> None:
    op.execute(
        f'DROP POLICY IF EXISTS "{table_name}_practice_all" ON "{table_name}"'
    )
    op.execute(f'ALTER TABLE "{table_name}" NO FORCE ROW LEVEL SECURITY')
    op.execute(f'ALTER TABLE "{table_name}" DISABLE ROW LEVEL SECURITY')


def upgrade() -> None:
    op.create_table(
        "application_auth_principal_generations",
        sa.Column("practice_ref", sa.String(length=74), primary_key=True),
        sa.Column("user_ref", sa.String(length=74), primary_key=True),
        sa.Column("generation", sa.BigInteger(), nullable=False),
        sa.Column("data_class", sa.String(length=32), nullable=False),
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
        sa.CheckConstraint(
            f"practice_ref ~ '{_SYNTHETIC_REF}'",
            name="ck_app_auth_principal_practice_synthetic",
        ),
        sa.CheckConstraint(
            f"user_ref ~ '{_SYNTHETIC_REF}'",
            name="ck_app_auth_principal_user_synthetic",
        ),
        sa.CheckConstraint(
            "generation > 0",
            name="ck_app_auth_principal_generation",
        ),
        sa.CheckConstraint(
            "data_class = 'authored_synthetic'",
            name="ck_app_auth_principal_data_class",
        ),
    )
    op.create_index(
        "ix_app_auth_principal_user_practice",
        "application_auth_principal_generations",
        ["user_ref", "practice_ref"],
    )

    op.create_table(
        "application_auth_parent_sessions",
        sa.Column("session_reference_hash", sa.String(length=71), primary_key=True),
        sa.Column("practice_ref", sa.String(length=74), nullable=False),
        sa.Column("user_ref", sa.String(length=74), nullable=False),
        sa.Column("current_backend_role", sa.String(length=32), nullable=False),
        sa.Column("practitioner_ref", sa.String(length=74), nullable=True),
        sa.Column("generation", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("data_class", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("idle_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            f"session_reference_hash ~ '{_HASH_REF}'",
            name="ck_app_auth_parent_hash",
        ),
        sa.CheckConstraint(
            f"practice_ref ~ '{_SYNTHETIC_REF}'",
            name="ck_app_auth_parent_practice_synthetic",
        ),
        sa.CheckConstraint(
            f"user_ref ~ '{_SYNTHETIC_REF}'",
            name="ck_app_auth_parent_user_synthetic",
        ),
        sa.CheckConstraint(
            f"practitioner_ref IS NULL OR practitioner_ref ~ '{_SYNTHETIC_REF}'",
            name="ck_app_auth_parent_practitioner_synthetic",
        ),
        sa.CheckConstraint(
            f"current_backend_role IN ({_ROLES})",
            name="ck_app_auth_parent_role",
        ),
        sa.CheckConstraint("generation > 0", name="ck_app_auth_parent_generation"),
        sa.CheckConstraint(
            f"status IN ({_STATUSES})",
            name="ck_app_auth_parent_status",
        ),
        sa.CheckConstraint(
            "data_class = 'authored_synthetic'",
            name="ck_app_auth_parent_data_class",
        ),
        sa.CheckConstraint(
            "last_observed_at >= created_at AND "
            "expires_at > created_at AND idle_expires_at <= expires_at AND "
            "(status = 'revoked' OR idle_expires_at > last_observed_at)",
            name="ck_app_auth_parent_time_bounds",
        ),
        sa.UniqueConstraint(
            "practice_ref",
            "session_reference_hash",
            name="uq_app_auth_parent_practice_hash",
        ),
        sa.ForeignKeyConstraint(
            ["practice_ref", "user_ref"],
            [
                "application_auth_principal_generations.practice_ref",
                "application_auth_principal_generations.user_ref",
            ],
            name="fk_app_auth_parent_principal",
        ),
    )
    op.create_index(
        "ix_app_auth_parent_principal",
        "application_auth_parent_sessions",
        ["practice_ref", "user_ref"],
    )
    op.create_index(
        "ix_app_auth_parent_active_expiry",
        "application_auth_parent_sessions",
        ["practice_ref", "expires_at"],
        postgresql_where=sa.text("status = 'active'"),
    )

    op.create_table(
        "application_auth_surface_sessions",
        sa.Column("surface_reference_hash", sa.String(length=71), primary_key=True),
        sa.Column("practice_ref", sa.String(length=74), nullable=False),
        sa.Column(
            "parent_session_reference_hash",
            sa.String(length=71),
            nullable=False,
        ),
        sa.Column("surface", sa.String(length=32), nullable=False),
        sa.Column("origin", sa.String(length=255), nullable=False),
        sa.Column("audience", sa.String(length=64), nullable=False),
        sa.Column("parent_generation", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("data_class", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("idle_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            f"surface_reference_hash ~ '{_HASH_REF}'",
            name="ck_app_auth_surface_hash",
        ),
        sa.CheckConstraint(
            f"parent_session_reference_hash ~ '{_HASH_REF}'",
            name="ck_app_auth_surface_parent_hash",
        ),
        sa.CheckConstraint(
            f"practice_ref ~ '{_SYNTHETIC_REF}'",
            name="ck_app_auth_surface_practice_synthetic",
        ),
        sa.CheckConstraint(
            "surface IN ('word_desktop', 'word_online', 'native_diary')",
            name="ck_app_auth_surface_surface",
        ),
        sa.CheckConstraint(
            "origin ~ '^https://[^/]+$'",
            name="ck_app_auth_surface_origin",
        ),
        sa.CheckConstraint(
            "audience = 'emr4-api'",
            name="ck_app_auth_surface_audience",
        ),
        sa.CheckConstraint(
            "parent_generation > 0",
            name="ck_app_auth_surface_generation",
        ),
        sa.CheckConstraint(
            f"status IN ({_STATUSES})",
            name="ck_app_auth_surface_status",
        ),
        sa.CheckConstraint(
            "data_class = 'authored_synthetic'",
            name="ck_app_auth_surface_data_class",
        ),
        sa.CheckConstraint(
            "last_observed_at >= created_at AND "
            "expires_at = idle_expires_at AND "
            "(status = 'revoked' OR idle_expires_at > last_observed_at)",
            name="ck_app_auth_surface_time_bounds",
        ),
        sa.UniqueConstraint(
            "practice_ref",
            "surface_reference_hash",
            name="uq_app_auth_surface_practice_hash",
        ),
        sa.ForeignKeyConstraint(
            ["practice_ref", "parent_session_reference_hash"],
            [
                "application_auth_parent_sessions.practice_ref",
                "application_auth_parent_sessions.session_reference_hash",
            ],
            name="fk_app_auth_surface_parent",
        ),
    )
    op.create_index(
        "ix_app_auth_surface_parent",
        "application_auth_surface_sessions",
        ["practice_ref", "parent_session_reference_hash"],
    )
    op.create_index(
        "ix_app_auth_surface_active_expiry",
        "application_auth_surface_sessions",
        ["practice_ref", "surface", "expires_at"],
        postgresql_where=sa.text("status = 'active'"),
    )

    op.create_table(
        "application_auth_exchange_grants",
        sa.Column("grant_reference_hash", sa.String(length=71), primary_key=True),
        sa.Column("practice_ref", sa.String(length=74), nullable=False),
        sa.Column(
            "parent_session_reference_hash",
            sa.String(length=71),
            nullable=False,
        ),
        sa.Column(
            "source_surface_reference_hash",
            sa.String(length=71),
            nullable=False,
        ),
        sa.Column("parent_generation", sa.BigInteger(), nullable=False),
        sa.Column("source_surface", sa.String(length=32), nullable=False),
        sa.Column("target_surface", sa.String(length=32), nullable=False),
        sa.Column("source_origin", sa.String(length=255), nullable=False),
        sa.Column("target_origin", sa.String(length=255), nullable=False),
        sa.Column("audience", sa.String(length=64), nullable=False),
        sa.Column("state_hash", sa.String(length=71), nullable=False),
        sa.Column("nonce_hash", sa.String(length=71), nullable=False),
        sa.Column("pkce_challenge", sa.String(length=43), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("data_class", sa.String(length=32), nullable=False),
        sa.CheckConstraint(
            f"grant_reference_hash ~ '{_HASH_REF}'",
            name="ck_app_auth_exchange_hash",
        ),
        sa.CheckConstraint(
            f"parent_session_reference_hash ~ '{_HASH_REF}'",
            name="ck_app_auth_exchange_parent_hash",
        ),
        sa.CheckConstraint(
            f"source_surface_reference_hash ~ '{_HASH_REF}'",
            name="ck_app_auth_exchange_source_hash",
        ),
        sa.CheckConstraint(
            f"state_hash ~ '{_HASH_REF}'",
            name="ck_app_auth_exchange_state_hash",
        ),
        sa.CheckConstraint(
            f"nonce_hash ~ '{_HASH_REF}'",
            name="ck_app_auth_exchange_nonce_hash",
        ),
        sa.CheckConstraint(
            f"practice_ref ~ '{_SYNTHETIC_REF}'",
            name="ck_app_auth_exchange_practice_synthetic",
        ),
        sa.CheckConstraint(
            "parent_generation > 0",
            name="ck_app_auth_exchange_generation",
        ),
        sa.CheckConstraint(
            "source_surface IN ('word_desktop', 'word_online') AND "
            "target_surface = 'native_diary'",
            name="ck_app_auth_exchange_flow",
        ),
        sa.CheckConstraint(
            "source_origin ~ '^https://[^/]+$' AND "
            "target_origin ~ '^https://[^/]+$'",
            name="ck_app_auth_exchange_origins",
        ),
        sa.CheckConstraint(
            "audience = 'emr4-session-exchange'",
            name="ck_app_auth_exchange_audience",
        ),
        sa.CheckConstraint(
            "pkce_challenge ~ '^[A-Za-z0-9_-]{43}$'",
            name="ck_app_auth_exchange_pkce",
        ),
        sa.CheckConstraint(
            "expires_at > issued_at AND "
            "(consumed_at IS NULL OR "
            "(consumed_at >= issued_at AND consumed_at < expires_at))",
            name="ck_app_auth_exchange_time_bounds",
        ),
        sa.CheckConstraint(
            "data_class = 'authored_synthetic'",
            name="ck_app_auth_exchange_data_class",
        ),
        sa.UniqueConstraint(
            "practice_ref",
            "grant_reference_hash",
            name="uq_app_auth_exchange_practice_hash",
        ),
        sa.ForeignKeyConstraint(
            ["practice_ref", "parent_session_reference_hash"],
            [
                "application_auth_parent_sessions.practice_ref",
                "application_auth_parent_sessions.session_reference_hash",
            ],
            name="fk_app_auth_exchange_parent",
        ),
        sa.ForeignKeyConstraint(
            ["practice_ref", "source_surface_reference_hash"],
            [
                "application_auth_surface_sessions.practice_ref",
                "application_auth_surface_sessions.surface_reference_hash",
            ],
            name="fk_app_auth_exchange_source_surface",
        ),
    )
    op.create_index(
        "ix_app_auth_exchange_parent",
        "application_auth_exchange_grants",
        ["practice_ref", "parent_session_reference_hash"],
    )
    op.create_index(
        "ix_app_auth_exchange_source_surface",
        "application_auth_exchange_grants",
        ["practice_ref", "source_surface_reference_hash"],
    )
    op.create_index(
        "ix_app_auth_exchange_unconsumed_expiry",
        "application_auth_exchange_grants",
        ["practice_ref", "expires_at"],
        postgresql_where=sa.text("consumed_at IS NULL"),
    )

    op.create_table(
        "application_auth_audit_events",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(),
            primary_key=True,
        ),
        sa.Column("practice_ref", sa.String(length=74), nullable=True),
        sa.Column("user_ref", sa.String(length=74), nullable=True),
        sa.Column("current_backend_role", sa.String(length=32), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("correlation_id", sa.String(length=76), nullable=False),
        sa.Column("session_reference_hash", sa.String(length=71), nullable=False),
        sa.Column("surface", sa.String(length=32), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("resource_type", sa.String(length=64), nullable=False),
        sa.Column("policy_version", sa.String(length=64), nullable=False),
        sa.Column("decision", sa.String(length=16), nullable=False),
        sa.Column("reason_codes", ARRAY(sa.String(length=100)), nullable=False),
        sa.Column("grant_reference_hash", sa.String(length=71), nullable=True),
        sa.Column("target_surface", sa.String(length=32), nullable=True),
        sa.Column("data_class", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            f"practice_ref IS NULL OR practice_ref ~ '{_SYNTHETIC_REF}'",
            name="ck_app_auth_audit_practice_synthetic",
        ),
        sa.CheckConstraint(
            f"user_ref IS NULL OR user_ref ~ '{_SYNTHETIC_REF}'",
            name="ck_app_auth_audit_user_synthetic",
        ),
        sa.CheckConstraint(
            f"current_backend_role IS NULL OR current_backend_role IN ({_ROLES})",
            name="ck_app_auth_audit_role",
        ),
        sa.CheckConstraint(
            "event_type IN ("
            "'auth.session_created', 'auth.session_refreshed', "
            "'auth.session_revoked', 'auth.surface_bound', "
            "'auth.exchange_issued', 'auth.exchange_redeemed', "
            "'auth.exchange_rejected', 'auth.authorization_denied'"
            ")",
            name="ck_app_auth_audit_event_type",
        ),
        sa.CheckConstraint(
            "correlation_id ~ '^correlation-[a-z0-9-]{1,64}$'",
            name="ck_app_auth_audit_correlation",
        ),
        sa.CheckConstraint(
            f"session_reference_hash ~ '{_HASH_REF}'",
            name="ck_app_auth_audit_session_hash",
        ),
        sa.CheckConstraint(
            f"grant_reference_hash IS NULL OR grant_reference_hash ~ '{_HASH_REF}'",
            name="ck_app_auth_audit_grant_hash",
        ),
        sa.CheckConstraint(
            "surface IN ('word_desktop', 'word_online', 'native_diary', 'all')",
            name="ck_app_auth_audit_surface",
        ),
        sa.CheckConstraint(
            "target_surface IS NULL OR target_surface = 'native_diary'",
            name="ck_app_auth_audit_target_surface",
        ),
        sa.CheckConstraint(
            "policy_version = 'clinician-workspace-read.v1'",
            name="ck_app_auth_audit_policy",
        ),
        sa.CheckConstraint(
            "decision IN ('allowed', 'denied', 'recorded')",
            name="ck_app_auth_audit_decision",
        ),
        sa.CheckConstraint(
            "cardinality(reason_codes) BETWEEN 1 AND 4",
            name="ck_app_auth_audit_reason_count",
        ),
        sa.CheckConstraint(
            "data_class = 'authored_synthetic'",
            name="ck_app_auth_audit_data_class",
        ),
    )
    op.create_index(
        "ix_app_auth_audit_practice_order",
        "application_auth_audit_events",
        ["practice_ref", "occurred_at", "id"],
    )
    op.create_index(
        "ix_app_auth_audit_correlation",
        "application_auth_audit_events",
        ["correlation_id"],
    )
    op.create_index(
        "ix_app_auth_audit_session",
        "application_auth_audit_events",
        ["session_reference_hash", "occurred_at"],
    )
    op.create_index(
        "ix_app_auth_audit_grant",
        "application_auth_audit_events",
        ["grant_reference_hash"],
        postgresql_where=sa.text("grant_reference_hash IS NOT NULL"),
    )

    for table_name in (
        "application_auth_principal_generations",
        "application_auth_parent_sessions",
        "application_auth_surface_sessions",
        "application_auth_exchange_grants",
    ):
        _enable_state_rls(table_name)

    op.execute('ALTER TABLE "application_auth_audit_events" ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE "application_auth_audit_events" FORCE ROW LEVEL SECURITY')
    op.execute(
        'CREATE POLICY "application_auth_audit_events_practice_select" '
        'ON "application_auth_audit_events" FOR SELECT '
        f"USING ({_PRACTICE_CONTEXT})"
    )
    op.execute(
        'CREATE POLICY "application_auth_audit_events_practice_insert" '
        'ON "application_auth_audit_events" FOR INSERT '
        f"WITH CHECK ({_PRACTICE_CONTEXT})"
    )

    op.execute(
        """
        CREATE FUNCTION emr4_reject_application_auth_audit_mutation()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
          RAISE EXCEPTION 'application auth audit evidence is append-only'
            USING ERRCODE = '55000';
        END
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_application_auth_audit_append_only
        BEFORE UPDATE OR DELETE ON application_auth_audit_events
        FOR EACH ROW
        EXECUTE FUNCTION emr4_reject_application_auth_audit_mutation()
        """
    )

    op.execute(
        """
        CREATE FUNCTION emr4_guard_application_auth_generation()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
          IF NEW.generation < OLD.generation
             OR NEW.generation > OLD.generation + 1 THEN
            RAISE EXCEPTION 'application auth generation must be monotonic'
              USING ERRCODE = '55000';
          END IF;
          RETURN NEW;
        END
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_application_auth_generation_monotonic
        BEFORE UPDATE ON application_auth_principal_generations
        FOR EACH ROW
        EXECUTE FUNCTION emr4_guard_application_auth_generation()
        """
    )

    op.execute(
        """
        CREATE FUNCTION emr4_guard_application_auth_exchange_consumption()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
          IF OLD.consumed_at IS NOT NULL
             AND NEW.consumed_at IS DISTINCT FROM OLD.consumed_at THEN
            RAISE EXCEPTION 'application auth exchange consumption is terminal'
              USING ERRCODE = '55000';
          END IF;
          RETURN NEW;
        END
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_application_auth_exchange_consumption_terminal
        BEFORE UPDATE ON application_auth_exchange_grants
        FOR EACH ROW
        EXECUTE FUNCTION emr4_guard_application_auth_exchange_consumption()
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_application_auth_exchange_consumption_terminal "
        "ON application_auth_exchange_grants"
    )
    op.execute("DROP FUNCTION IF EXISTS emr4_guard_application_auth_exchange_consumption()")
    op.execute(
        "DROP TRIGGER IF EXISTS trg_application_auth_generation_monotonic "
        "ON application_auth_principal_generations"
    )
    op.execute("DROP FUNCTION IF EXISTS emr4_guard_application_auth_generation()")
    op.execute(
        "DROP TRIGGER IF EXISTS trg_application_auth_audit_append_only "
        "ON application_auth_audit_events"
    )
    op.execute("DROP FUNCTION IF EXISTS emr4_reject_application_auth_audit_mutation()")

    op.execute(
        'DROP POLICY IF EXISTS "application_auth_audit_events_practice_insert" '
        'ON "application_auth_audit_events"'
    )
    op.execute(
        'DROP POLICY IF EXISTS "application_auth_audit_events_practice_select" '
        'ON "application_auth_audit_events"'
    )
    op.execute('ALTER TABLE "application_auth_audit_events" NO FORCE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE "application_auth_audit_events" DISABLE ROW LEVEL SECURITY')

    for table_name in (
        "application_auth_exchange_grants",
        "application_auth_surface_sessions",
        "application_auth_parent_sessions",
        "application_auth_principal_generations",
    ):
        _disable_state_rls(table_name)

    op.drop_index("ix_app_auth_audit_grant", table_name="application_auth_audit_events")
    op.drop_index("ix_app_auth_audit_session", table_name="application_auth_audit_events")
    op.drop_index("ix_app_auth_audit_correlation", table_name="application_auth_audit_events")
    op.drop_index("ix_app_auth_audit_practice_order", table_name="application_auth_audit_events")
    op.drop_table("application_auth_audit_events")

    op.drop_index(
        "ix_app_auth_exchange_unconsumed_expiry",
        table_name="application_auth_exchange_grants",
    )
    op.drop_index(
        "ix_app_auth_exchange_source_surface",
        table_name="application_auth_exchange_grants",
    )
    op.drop_index(
        "ix_app_auth_exchange_parent",
        table_name="application_auth_exchange_grants",
    )
    op.drop_table("application_auth_exchange_grants")

    op.drop_index(
        "ix_app_auth_surface_active_expiry",
        table_name="application_auth_surface_sessions",
    )
    op.drop_index(
        "ix_app_auth_surface_parent",
        table_name="application_auth_surface_sessions",
    )
    op.drop_table("application_auth_surface_sessions")

    op.drop_index(
        "ix_app_auth_parent_active_expiry",
        table_name="application_auth_parent_sessions",
    )
    op.drop_index(
        "ix_app_auth_parent_principal",
        table_name="application_auth_parent_sessions",
    )
    op.drop_table("application_auth_parent_sessions")

    op.drop_index(
        "ix_app_auth_principal_user_practice",
        table_name="application_auth_principal_generations",
    )
    op.drop_table("application_auth_principal_generations")
