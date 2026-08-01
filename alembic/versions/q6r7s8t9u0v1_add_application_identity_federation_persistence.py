"""Add authored-synthetic external identity binding persistence.

Revision ID: q6r7s8t9u0v1
Revises: p5q6r7s8t9u0
Create Date: 2026-08-01
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "q6r7s8t9u0v1"
down_revision: Union[str, Sequence[str], None] = "p5q6r7s8t9u0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_BINDINGS = "application_identity_federation_bindings"
_AUDIT = "application_identity_federation_audit_events"


def upgrade() -> None:
    op.create_table(
        _BINDINGS,
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("binding_ref", sa.String(length=74), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("issuer_reference_hmac", sa.String(length=96), nullable=False),
        sa.Column("tenant_reference_hmac", sa.String(length=96), nullable=False),
        sa.Column("object_reference_hmac", sa.String(length=96), nullable=False),
        sa.Column("subject_reference_hmac", sa.String(length=96), nullable=False),
        sa.Column("user_ref", sa.String(length=74), nullable=False),
        sa.Column("practice_ref", sa.String(length=74), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("version", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("data_class", sa.String(length=32), nullable=False),
        sa.CheckConstraint(
            "binding_ref ~ '^synthetic-[a-z0-9-]{1,64}$'",
            name="ck_app_id_fed_binding_ref_synthetic",
        ),
        sa.CheckConstraint(
            "provider = 'microsoft_entra'",
            name="ck_app_id_fed_binding_provider",
        ),
        sa.CheckConstraint(
            "issuer_reference_hmac ~ "
            "'^hmac-sha256:synthetic-v1:[0-9a-f]{64}$'",
            name="ck_app_id_fed_binding_issuer_hmac",
        ),
        sa.CheckConstraint(
            "tenant_reference_hmac ~ "
            "'^hmac-sha256:synthetic-v1:[0-9a-f]{64}$'",
            name="ck_app_id_fed_binding_tenant_hmac",
        ),
        sa.CheckConstraint(
            "object_reference_hmac ~ "
            "'^hmac-sha256:synthetic-v1:[0-9a-f]{64}$'",
            name="ck_app_id_fed_binding_object_hmac",
        ),
        sa.CheckConstraint(
            "subject_reference_hmac ~ "
            "'^hmac-sha256:synthetic-v1:[0-9a-f]{64}$'",
            name="ck_app_id_fed_binding_subject_hmac",
        ),
        sa.CheckConstraint(
            "user_ref ~ '^synthetic-[a-z0-9-]{1,64}$'",
            name="ck_app_id_fed_binding_user_synthetic",
        ),
        sa.CheckConstraint(
            "practice_ref ~ '^synthetic-[a-z0-9-]{1,64}$'",
            name="ck_app_id_fed_binding_practice_synthetic",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'revoked')",
            name="ck_app_id_fed_binding_status",
        ),
        sa.CheckConstraint(
            "version > 0",
            name="ck_app_id_fed_binding_version",
        ),
        sa.CheckConstraint(
            "updated_at >= created_at AND "
            "((status = 'active' AND revoked_at IS NULL) OR "
            "(status = 'revoked' AND revoked_at IS NOT NULL "
            "AND revoked_at >= created_at AND updated_at = revoked_at))",
            name="ck_app_id_fed_binding_time_status",
        ),
        sa.CheckConstraint(
            "data_class = 'authored_synthetic'",
            name="ck_app_id_fed_binding_data_class",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("binding_ref", name="uq_app_id_fed_binding_ref"),
        sa.UniqueConstraint(
            "provider",
            "issuer_reference_hmac",
            "tenant_reference_hmac",
            "object_reference_hmac",
            name="uq_app_id_fed_external_key",
        ),
    )
    op.create_index(
        "ix_app_id_fed_binding_practice_user",
        _BINDINGS,
        ["practice_ref", "user_ref"],
    )
    op.create_index(
        "ix_app_id_fed_binding_practice_status",
        _BINDINGS,
        ["practice_ref", "status"],
    )

    op.create_table(
        _AUDIT,
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("operation_ref", sa.String(length=74), nullable=False),
        sa.Column("correlation_reference_hmac", sa.String(length=96), nullable=False),
        sa.Column("external_reference_hmac", sa.String(length=96), nullable=False),
        sa.Column("binding_ref", sa.String(length=74), nullable=True),
        sa.Column("user_ref", sa.String(length=74), nullable=True),
        sa.Column("practice_ref", sa.String(length=74), nullable=True),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("decision", sa.String(length=16), nullable=False),
        sa.Column("reason_code", sa.String(length=64), nullable=False),
        sa.Column("policy_version", sa.String(length=64), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_class", sa.String(length=32), nullable=False),
        sa.CheckConstraint(
            "operation_ref ~ '^synthetic-[a-z0-9-]{1,64}$'",
            name="ck_app_id_fed_audit_operation_synthetic",
        ),
        sa.CheckConstraint(
            "correlation_reference_hmac ~ "
            "'^hmac-sha256:synthetic-v1:[0-9a-f]{64}$'",
            name="ck_app_id_fed_audit_correlation_hmac",
        ),
        sa.CheckConstraint(
            "external_reference_hmac ~ "
            "'^hmac-sha256:synthetic-v1:[0-9a-f]{64}$'",
            name="ck_app_id_fed_audit_external_hmac",
        ),
        sa.CheckConstraint(
            "binding_ref IS NULL OR "
            "binding_ref ~ '^synthetic-[a-z0-9-]{1,64}$'",
            name="ck_app_id_fed_audit_binding_synthetic",
        ),
        sa.CheckConstraint(
            "user_ref IS NULL OR user_ref ~ '^synthetic-[a-z0-9-]{1,64}$'",
            name="ck_app_id_fed_audit_user_synthetic",
        ),
        sa.CheckConstraint(
            "practice_ref IS NULL OR "
            "practice_ref ~ '^synthetic-[a-z0-9-]{1,64}$'",
            name="ck_app_id_fed_audit_practice_synthetic",
        ),
        sa.CheckConstraint(
            "(user_ref IS NULL) = (practice_ref IS NULL)",
            name="ck_app_id_fed_audit_principal_pair",
        ),
        sa.CheckConstraint(
            "provider = 'microsoft_entra'",
            name="ck_app_id_fed_audit_provider",
        ),
        sa.CheckConstraint(
            "event_type IN ("
            "'federation.binding_created', "
            "'federation.binding_revoked', "
            "'federation.binding_resolved', "
            "'federation.binding_rejected')",
            name="ck_app_id_fed_audit_event_type",
        ),
        sa.CheckConstraint(
            "decision IN ('allowed', 'denied', 'recorded')",
            name="ck_app_id_fed_audit_decision",
        ),
        sa.CheckConstraint(
            "reason_code ~ '^[a-z0-9_]{1,64}$'",
            name="ck_app_id_fed_audit_reason",
        ),
        sa.CheckConstraint(
            "policy_version = 'microsoft-entra-single-tenant-prebound.v1'",
            name="ck_app_id_fed_audit_policy",
        ),
        sa.CheckConstraint(
            "data_class = 'authored_synthetic'",
            name="ck_app_id_fed_audit_data_class",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("operation_ref", name="uq_app_id_fed_audit_operation"),
    )
    op.create_index(
        "ix_app_id_fed_audit_practice_time",
        _AUDIT,
        ["practice_ref", "occurred_at"],
    )
    op.create_index(
        "ix_app_id_fed_audit_external_time",
        _AUDIT,
        ["external_reference_hmac", "occurred_at"],
    )

    op.execute(
        "ALTER TABLE application_identity_federation_bindings "
        "ENABLE ROW LEVEL SECURITY"
    )
    op.execute(
        "ALTER TABLE application_identity_federation_bindings "
        "FORCE ROW LEVEL SECURITY"
    )
    op.execute(
        "ALTER TABLE application_identity_federation_audit_events "
        "ENABLE ROW LEVEL SECURITY"
    )
    op.execute(
        "ALTER TABLE application_identity_federation_audit_events "
        "FORCE ROW LEVEL SECURITY"
    )
    op.execute(
        """
        CREATE POLICY app_id_fed_binding_practice_all
        ON application_identity_federation_bindings
        FOR ALL
        USING (
          practice_ref = NULLIF(current_setting('emr4.practice_ref', true), '')
        )
        WITH CHECK (
          practice_ref = NULLIF(current_setting('emr4.practice_ref', true), '')
        )
        """
    )
    op.execute(
        """
        CREATE POLICY app_id_fed_audit_practice_select
        ON application_identity_federation_audit_events
        FOR SELECT
        USING (
          practice_ref = NULLIF(current_setting('emr4.practice_ref', true), '')
        )
        """
    )
    op.execute(
        """
        CREATE POLICY app_id_fed_audit_practice_insert
        ON application_identity_federation_audit_events
        FOR INSERT
        WITH CHECK (
          practice_ref = NULLIF(current_setting('emr4.practice_ref', true), '')
        )
        """
    )

    op.execute(
        """
        CREATE FUNCTION public.emr4_app_id_fed_audit_append_only()
        RETURNS trigger
        LANGUAGE plpgsql
        SET search_path = ''
        AS $$
        BEGIN
          RAISE EXCEPTION 'federation audit is append-only'
            USING ERRCODE = '55000';
        END;
        $$
        """
    )
    op.execute(
        "REVOKE ALL ON FUNCTION public.emr4_app_id_fed_audit_append_only() "
        "FROM PUBLIC"
    )
    op.execute(
        """
        CREATE TRIGGER trg_app_id_fed_audit_append_only
        BEFORE UPDATE OR DELETE
        ON application_identity_federation_audit_events
        FOR EACH ROW
        EXECUTE FUNCTION public.emr4_app_id_fed_audit_append_only()
        """
    )

    op.execute(
        """
        CREATE FUNCTION public.emr4_app_id_fed_binding_terminal()
        RETURNS trigger
        LANGUAGE plpgsql
        SET search_path = ''
        AS $$
        BEGIN
          IF OLD.status = 'revoked'
             OR NEW.status <> 'revoked'
             OR NEW.version <> OLD.version + 1
             OR NEW.revoked_at IS NULL
             OR NEW.updated_at <> NEW.revoked_at
             OR NEW.binding_ref IS DISTINCT FROM OLD.binding_ref
             OR NEW.provider IS DISTINCT FROM OLD.provider
             OR NEW.issuer_reference_hmac IS DISTINCT FROM OLD.issuer_reference_hmac
             OR NEW.tenant_reference_hmac IS DISTINCT FROM OLD.tenant_reference_hmac
             OR NEW.object_reference_hmac IS DISTINCT FROM OLD.object_reference_hmac
             OR NEW.subject_reference_hmac IS DISTINCT FROM OLD.subject_reference_hmac
             OR NEW.user_ref IS DISTINCT FROM OLD.user_ref
             OR NEW.practice_ref IS DISTINCT FROM OLD.practice_ref
             OR NEW.created_at IS DISTINCT FROM OLD.created_at
             OR NEW.data_class IS DISTINCT FROM OLD.data_class THEN
            RAISE EXCEPTION 'federation binding transition is invalid'
              USING ERRCODE = '55000';
          END IF;
          RETURN NEW;
        END;
        $$
        """
    )
    op.execute(
        "REVOKE ALL ON FUNCTION public.emr4_app_id_fed_binding_terminal() "
        "FROM PUBLIC"
    )
    op.execute(
        """
        CREATE TRIGGER trg_app_id_fed_binding_terminal
        BEFORE UPDATE
        ON application_identity_federation_bindings
        FOR EACH ROW
        EXECUTE FUNCTION public.emr4_app_id_fed_binding_terminal()
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_app_id_fed_binding_terminal "
        "ON application_identity_federation_bindings"
    )
    op.execute("DROP FUNCTION IF EXISTS public.emr4_app_id_fed_binding_terminal()")
    op.execute(
        "DROP TRIGGER IF EXISTS trg_app_id_fed_audit_append_only "
        "ON application_identity_federation_audit_events"
    )
    op.execute("DROP FUNCTION IF EXISTS public.emr4_app_id_fed_audit_append_only()")
    op.execute(
        "DROP POLICY IF EXISTS app_id_fed_audit_practice_insert "
        "ON application_identity_federation_audit_events"
    )
    op.execute(
        "DROP POLICY IF EXISTS app_id_fed_audit_practice_select "
        "ON application_identity_federation_audit_events"
    )
    op.execute(
        "DROP POLICY IF EXISTS app_id_fed_binding_practice_all "
        "ON application_identity_federation_bindings"
    )
    op.execute(
        "ALTER TABLE application_identity_federation_audit_events "
        "NO FORCE ROW LEVEL SECURITY"
    )
    op.execute(
        "ALTER TABLE application_identity_federation_bindings "
        "NO FORCE ROW LEVEL SECURITY"
    )
    op.drop_index("ix_app_id_fed_audit_external_time", table_name=_AUDIT)
    op.drop_index("ix_app_id_fed_audit_practice_time", table_name=_AUDIT)
    op.drop_table(_AUDIT)
    op.drop_index("ix_app_id_fed_binding_practice_status", table_name=_BINDINGS)
    op.drop_index("ix_app_id_fed_binding_practice_user", table_name=_BINDINGS)
    op.drop_table(_BINDINGS)
