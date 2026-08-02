"""Add HMAC-only binding resolver and authored-synthetic admission grants.

Revision ID: s8t9u0v1w2x3
Revises: r7s8t9u0v1w2
Create Date: 2026-08-02
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "s8t9u0v1w2x3"
down_revision: Union[str, Sequence[str], None] = "r7s8t9u0v1w2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_BINDINGS = "application_identity_federation_bindings"
_AUDIT = "application_identity_federation_audit_events"
_GRANTS = "application_identity_federation_admission_grants"
_RESOLVER = (
    "public.emr4_resolve_application_identity_federation_binding("
    "text, text, text, text, text, text, text, text, text)"
)
_RESOLVER_OWNER_PATTERN = (
    "^emr4_oidc_binding_resolver_owner_[a-z0-9_]{8,40}$"
)
_LOGIN_PATTERN = "^emr4_oidc_binding_login_[a-z0-9_]{8,40}$"
_GRANT_ISSUER_PATTERN = "^emr4_oidc_grant_issuer_[a-z0-9_]{8,40}$"
_NEW_ROLE_PATTERN = (
    "^emr4_oidc_(binding_resolver_owner|grant_issuer)_[a-z0-9_]{8,40}$"
)


def upgrade() -> None:
    op.create_table(
        _GRANTS,
        sa.Column("grant_reference_hmac", sa.String(length=128), nullable=False),
        sa.Column("operation_ref", sa.String(length=74), nullable=False),
        sa.Column("binding_ref", sa.String(length=74), nullable=False),
        sa.Column("binding_version", sa.BigInteger(), nullable=False),
        sa.Column("user_ref", sa.String(length=74), nullable=False),
        sa.Column("practice_ref", sa.String(length=74), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("external_reference_hmac", sa.String(length=96), nullable=False),
        sa.Column("audience_reference_hmac", sa.String(length=96), nullable=False),
        sa.Column("correlation_reference_hmac", sa.String(length=96), nullable=False),
        sa.Column("surface", sa.String(length=32), nullable=False),
        sa.Column("origin", sa.String(length=512), nullable=False),
        sa.Column("return_target", sa.String(length=32), nullable=False),
        sa.Column("policy_version", sa.String(length=64), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("version", sa.BigInteger(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("data_class", sa.String(length=32), nullable=False),
        sa.CheckConstraint(
            "grant_reference_hmac ~ "
            "'^hmac-sha256:[a-z0-9][a-z0-9_-]{0,31}:[0-9a-f]{64}$'",
            name="ck_app_id_fed_grant_reference_hmac",
        ),
        sa.CheckConstraint(
            "operation_ref ~ '^synthetic-[a-z0-9-]{1,64}$'",
            name="ck_app_id_fed_grant_operation_synthetic",
        ),
        sa.CheckConstraint(
            "binding_ref ~ '^synthetic-[a-z0-9-]{1,64}$'",
            name="ck_app_id_fed_grant_binding_synthetic",
        ),
        sa.CheckConstraint(
            "binding_version > 0",
            name="ck_app_id_fed_grant_binding_version",
        ),
        sa.CheckConstraint(
            "user_ref ~ '^synthetic-[a-z0-9-]{1,64}$'",
            name="ck_app_id_fed_grant_user_synthetic",
        ),
        sa.CheckConstraint(
            "practice_ref ~ '^synthetic-[a-z0-9-]{1,64}$'",
            name="ck_app_id_fed_grant_practice_synthetic",
        ),
        sa.CheckConstraint(
            "provider = 'microsoft_entra'",
            name="ck_app_id_fed_grant_provider",
        ),
        sa.CheckConstraint(
            "external_reference_hmac ~ "
            "'^hmac-sha256:synthetic-v1:[0-9a-f]{64}$'",
            name="ck_app_id_fed_grant_external_hmac",
        ),
        sa.CheckConstraint(
            "audience_reference_hmac ~ "
            "'^hmac-sha256:synthetic-v1:[0-9a-f]{64}$'",
            name="ck_app_id_fed_grant_audience_hmac",
        ),
        sa.CheckConstraint(
            "correlation_reference_hmac ~ "
            "'^hmac-sha256:synthetic-v1:[0-9a-f]{64}$'",
            name="ck_app_id_fed_grant_correlation_hmac",
        ),
        sa.CheckConstraint(
            "surface IN ('word_desktop', 'word_online', 'native_diary')",
            name="ck_app_id_fed_grant_surface",
        ),
        sa.CheckConstraint(
            "origin ~ '^https://[a-z0-9.-]+(:[0-9]{1,5})?$'",
            name="ck_app_id_fed_grant_origin",
        ),
        sa.CheckConstraint(
            "return_target IN ('clinician_one', 'reception_one', 'diary')",
            name="ck_app_id_fed_grant_return_target",
        ),
        sa.CheckConstraint(
            "policy_version = 'microsoft-entra-single-tenant-prebound.v1'",
            name="ck_app_id_fed_grant_policy",
        ),
        sa.CheckConstraint(
            "expires_at = issued_at + INTERVAL '60 seconds'",
            name="ck_app_id_fed_grant_exact_expiry",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'consumed')",
            name="ck_app_id_fed_grant_status",
        ),
        sa.CheckConstraint(
            "version > 0 AND "
            "((status = 'active' AND version = 1 AND consumed_at IS NULL) OR "
            "(status = 'consumed' AND version = 2 AND consumed_at IS NOT NULL "
            "AND consumed_at >= issued_at))",
            name="ck_app_id_fed_grant_state",
        ),
        sa.CheckConstraint(
            "data_class = 'authored_synthetic'",
            name="ck_app_id_fed_grant_data_class",
        ),
        sa.PrimaryKeyConstraint("grant_reference_hmac"),
        sa.UniqueConstraint(
            "operation_ref",
            name="uq_app_id_fed_grant_operation",
        ),
    )
    op.create_index(
        "ix_app_id_fed_grant_practice_expiry",
        _GRANTS,
        ["practice_ref", "expires_at"],
    )
    op.create_index(
        "ix_app_id_fed_grant_binding_status",
        _GRANTS,
        ["binding_ref", "status"],
    )
    op.execute(f"REVOKE ALL ON TABLE public.{_GRANTS} FROM PUBLIC")
    op.execute(f"ALTER TABLE {_GRANTS} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {_GRANTS} FORCE ROW LEVEL SECURITY")

    op.drop_constraint("ck_app_id_fed_audit_event_type", _AUDIT, type_="check")
    op.create_check_constraint(
        "ck_app_id_fed_audit_event_type",
        _AUDIT,
        "event_type IN ("
        "'federation.binding_created', "
        "'federation.binding_revoked', "
        "'federation.binding_resolved', "
        "'federation.binding_rejected', "
        "'federation.admission_grant_issued')",
    )

    op.execute(
        "DROP POLICY app_id_fed_audit_practice_insert "
        "ON application_identity_federation_audit_events"
    )
    op.execute(
        f"""
        CREATE POLICY app_id_fed_audit_practice_insert
        ON application_identity_federation_audit_events
        FOR INSERT
        WITH CHECK (
          current_user !~ '{_NEW_ROLE_PATTERN}'
          AND practice_ref = NULLIF(current_setting('emr4.practice_ref', true), '')
        )
        """
    )
    op.execute(
        f"""
        CREATE POLICY app_id_fed_binding_resolver_select
        ON application_identity_federation_bindings
        FOR SELECT
        USING (
          current_user ~ '{_RESOLVER_OWNER_PATTERN}'
          AND provider = NULLIF(current_setting('emr4.federation_provider', true), '')
          AND issuer_reference_hmac = NULLIF(
            current_setting('emr4.federation_issuer_hmac', true), ''
          )
          AND tenant_reference_hmac = NULLIF(
            current_setting('emr4.federation_tenant_hmac', true), ''
          )
          AND object_reference_hmac = NULLIF(
            current_setting('emr4.federation_object_hmac', true), ''
          )
          AND subject_reference_hmac = NULLIF(
            current_setting('emr4.federation_subject_hmac', true), ''
          )
        )
        """
    )
    op.execute(
        f"""
        CREATE POLICY app_id_fed_audit_resolver_insert
        ON application_identity_federation_audit_events
        FOR INSERT
        WITH CHECK (
          current_user ~ '{_RESOLVER_OWNER_PATTERN}'
          AND provider = 'microsoft_entra'
          AND policy_version = 'microsoft-entra-single-tenant-prebound.v1'
          AND external_reference_hmac = NULLIF(
            current_setting('emr4.federation_external_hmac', true), ''
          )
          AND correlation_reference_hmac = NULLIF(
            current_setting('emr4.federation_correlation_hmac', true), ''
          )
          AND (
            (
              event_type = 'federation.binding_resolved'
              AND decision = 'allowed'
              AND reason_code = 'federation_binding_resolved'
              AND binding_ref IS NOT NULL
              AND user_ref IS NOT NULL
              AND practice_ref = NULLIF(
                current_setting('emr4.federation_practice_ref', true), ''
              )
            )
            OR (
              event_type = 'federation.binding_rejected'
              AND decision = 'denied'
              AND reason_code = 'active_binding_required'
              AND binding_ref IS NULL
              AND user_ref IS NULL
              AND practice_ref IS NULL
            )
            OR (
              event_type = 'federation.admission_grant_issued'
              AND decision = 'recorded'
              AND reason_code = 'admission_grant_issued'
              AND binding_ref IS NOT NULL
              AND user_ref IS NOT NULL
              AND practice_ref = NULLIF(
                current_setting('emr4.practice_ref', true), ''
              )
            )
          )
        )
        """
    )
    op.execute(
        f"""
        CREATE POLICY app_id_fed_grant_issuer_select
        ON application_identity_federation_admission_grants
        FOR SELECT
        USING (
          current_user ~ '{_GRANT_ISSUER_PATTERN}'
          AND practice_ref = NULLIF(current_setting('emr4.practice_ref', true), '')
        )
        """
    )
    op.execute(
        f"""
        CREATE POLICY app_id_fed_grant_issuer_insert
        ON application_identity_federation_admission_grants
        FOR INSERT
        WITH CHECK (
          current_user ~ '{_GRANT_ISSUER_PATTERN}'
          AND practice_ref = NULLIF(current_setting('emr4.practice_ref', true), '')
          AND external_reference_hmac = NULLIF(
            current_setting('emr4.federation_external_hmac', true), ''
          )
          AND audience_reference_hmac = NULLIF(
            current_setting('emr4.federation_audience_hmac', true), ''
          )
          AND correlation_reference_hmac = NULLIF(
            current_setting('emr4.federation_correlation_hmac', true), ''
          )
          AND status = 'active'
          AND version = 1
          AND consumed_at IS NULL
        )
        """
    )
    op.execute(
        f"""
        CREATE FUNCTION public.emr4_resolve_application_identity_federation_binding(
          p_provider text,
          p_issuer_reference_hmac text,
          p_tenant_reference_hmac text,
          p_object_reference_hmac text,
          p_subject_reference_hmac text,
          p_external_reference_hmac text,
          p_correlation_reference_hmac text,
          p_operation_ref text,
          p_policy_version text
        )
        RETURNS TABLE(
          binding_ref text,
          binding_version bigint,
          user_ref text,
          practice_ref text
        )
        LANGUAGE plpgsql
        SECURITY DEFINER
        VOLATILE
        PARALLEL UNSAFE
        ROWS 1
        SET search_path = ''
        AS $$
        DECLARE
          v_binding_ref text;
          v_binding_version bigint;
          v_user_ref text;
          v_practice_ref text;
          v_now timestamptz := clock_timestamp();
        BEGIN
          IF current_user !~ '{_RESOLVER_OWNER_PATTERN}'
             OR session_user !~ '{_LOGIN_PATTERN}' THEN
            RAISE EXCEPTION 'federation resolver execution identity is invalid'
              USING ERRCODE = '42501';
          END IF;
          IF p_provider <> 'microsoft_entra'
             OR p_policy_version <> 'microsoft-entra-single-tenant-prebound.v1'
             OR p_issuer_reference_hmac !~ '^hmac-sha256:synthetic-v1:[0-9a-f]{{64}}$'
             OR p_tenant_reference_hmac !~ '^hmac-sha256:synthetic-v1:[0-9a-f]{{64}}$'
             OR p_object_reference_hmac !~ '^hmac-sha256:synthetic-v1:[0-9a-f]{{64}}$'
             OR p_subject_reference_hmac !~ '^hmac-sha256:synthetic-v1:[0-9a-f]{{64}}$'
             OR p_external_reference_hmac !~ '^hmac-sha256:synthetic-v1:[0-9a-f]{{64}}$'
             OR p_correlation_reference_hmac !~ '^hmac-sha256:synthetic-v1:[0-9a-f]{{64}}$'
             OR p_operation_ref !~ '^synthetic-[a-z0-9-]{{1,64}}$' THEN
            RAISE EXCEPTION 'federation resolver input is invalid'
              USING ERRCODE = '22023';
          END IF;

          PERFORM pg_catalog.set_config('emr4.federation_provider', p_provider, true);
          PERFORM pg_catalog.set_config(
            'emr4.federation_issuer_hmac', p_issuer_reference_hmac, true
          );
          PERFORM pg_catalog.set_config(
            'emr4.federation_tenant_hmac', p_tenant_reference_hmac, true
          );
          PERFORM pg_catalog.set_config(
            'emr4.federation_object_hmac', p_object_reference_hmac, true
          );
          PERFORM pg_catalog.set_config(
            'emr4.federation_subject_hmac', p_subject_reference_hmac, true
          );
          PERFORM pg_catalog.set_config(
            'emr4.federation_external_hmac', p_external_reference_hmac, true
          );
          PERFORM pg_catalog.set_config(
            'emr4.federation_correlation_hmac', p_correlation_reference_hmac, true
          );

          SELECT binding.binding_ref,
                 binding.version,
                 binding.user_ref,
                 binding.practice_ref
          INTO v_binding_ref, v_binding_version, v_user_ref, v_practice_ref
          FROM public.application_identity_federation_bindings AS binding
          WHERE binding.provider = p_provider
            AND binding.issuer_reference_hmac = p_issuer_reference_hmac
            AND binding.tenant_reference_hmac = p_tenant_reference_hmac
            AND binding.object_reference_hmac = p_object_reference_hmac
            AND binding.subject_reference_hmac = p_subject_reference_hmac
            AND binding.status = 'active'
          LIMIT 1;

          IF NOT FOUND THEN
            INSERT INTO public.application_identity_federation_audit_events (
              operation_ref,
              correlation_reference_hmac,
              external_reference_hmac,
              binding_ref,
              user_ref,
              practice_ref,
              provider,
              event_type,
              decision,
              reason_code,
              policy_version,
              occurred_at,
              data_class
            ) VALUES (
              p_operation_ref,
              p_correlation_reference_hmac,
              p_external_reference_hmac,
              NULL,
              NULL,
              NULL,
              p_provider,
              'federation.binding_rejected',
              'denied',
              'active_binding_required',
              p_policy_version,
              v_now,
              'authored_synthetic'
            );
            RETURN;
          END IF;

          PERFORM pg_catalog.set_config(
            'emr4.federation_practice_ref', v_practice_ref, true
          );
          INSERT INTO public.application_identity_federation_audit_events (
            operation_ref,
            correlation_reference_hmac,
            external_reference_hmac,
            binding_ref,
            user_ref,
            practice_ref,
            provider,
            event_type,
            decision,
            reason_code,
            policy_version,
            occurred_at,
            data_class
          ) VALUES (
            p_operation_ref,
            p_correlation_reference_hmac,
            p_external_reference_hmac,
            v_binding_ref,
            v_user_ref,
            v_practice_ref,
            p_provider,
            'federation.binding_resolved',
            'allowed',
            'federation_binding_resolved',
            p_policy_version,
            v_now,
            'authored_synthetic'
          );

          RETURN QUERY
            SELECT v_binding_ref, v_binding_version, v_user_ref, v_practice_ref;
        END;
        $$
        """
    )
    op.execute(f"REVOKE ALL ON FUNCTION {_RESOLVER} FROM PUBLIC")

    op.execute(
        f"""
        CREATE FUNCTION public.emr4_app_id_fed_grant_required_audit()
        RETURNS trigger
        LANGUAGE plpgsql
        SECURITY DEFINER
        VOLATILE
        PARALLEL UNSAFE
        SET search_path = ''
        AS $$
        BEGIN
          IF current_user !~ '{_RESOLVER_OWNER_PATTERN}'
             OR session_user !~ '{_LOGIN_PATTERN}' THEN
            RAISE EXCEPTION 'federation admission grant audit identity is invalid'
              USING ERRCODE = '42501';
          END IF;
          INSERT INTO public.application_identity_federation_audit_events (
            operation_ref,
            correlation_reference_hmac,
            external_reference_hmac,
            binding_ref,
            user_ref,
            practice_ref,
            provider,
            event_type,
            decision,
            reason_code,
            policy_version,
            occurred_at,
            data_class
          ) VALUES (
            NEW.operation_ref,
            NEW.correlation_reference_hmac,
            NEW.external_reference_hmac,
            NEW.binding_ref,
            NEW.user_ref,
            NEW.practice_ref,
            NEW.provider,
            'federation.admission_grant_issued',
            'recorded',
            'admission_grant_issued',
            NEW.policy_version,
            NEW.issued_at,
            'authored_synthetic'
          );
          RETURN NEW;
        END;
        $$
        """
    )
    op.execute(
        "REVOKE ALL ON FUNCTION "
        "public.emr4_app_id_fed_grant_required_audit() FROM PUBLIC"
    )
    op.execute(
        """
        CREATE TRIGGER trg_app_id_fed_grant_required_audit
        AFTER INSERT
        ON application_identity_federation_admission_grants
        FOR EACH ROW
        EXECUTE FUNCTION public.emr4_app_id_fed_grant_required_audit()
        """
    )

    op.execute(
        """
        CREATE FUNCTION public.emr4_app_id_fed_grant_terminal()
        RETURNS trigger
        LANGUAGE plpgsql
        SET search_path = ''
        AS $$
        BEGIN
          IF OLD.status <> 'active'
             OR NEW.status <> 'consumed'
             OR NEW.version <> 2
             OR NEW.consumed_at IS NULL
             OR NEW.consumed_at < OLD.issued_at
             OR NEW.grant_reference_hmac IS DISTINCT FROM OLD.grant_reference_hmac
             OR NEW.operation_ref IS DISTINCT FROM OLD.operation_ref
             OR NEW.binding_ref IS DISTINCT FROM OLD.binding_ref
             OR NEW.binding_version IS DISTINCT FROM OLD.binding_version
             OR NEW.user_ref IS DISTINCT FROM OLD.user_ref
             OR NEW.practice_ref IS DISTINCT FROM OLD.practice_ref
             OR NEW.provider IS DISTINCT FROM OLD.provider
             OR NEW.external_reference_hmac IS DISTINCT FROM OLD.external_reference_hmac
             OR NEW.audience_reference_hmac IS DISTINCT FROM OLD.audience_reference_hmac
             OR NEW.correlation_reference_hmac IS DISTINCT FROM OLD.correlation_reference_hmac
             OR NEW.surface IS DISTINCT FROM OLD.surface
             OR NEW.origin IS DISTINCT FROM OLD.origin
             OR NEW.return_target IS DISTINCT FROM OLD.return_target
             OR NEW.policy_version IS DISTINCT FROM OLD.policy_version
             OR NEW.issued_at IS DISTINCT FROM OLD.issued_at
             OR NEW.expires_at IS DISTINCT FROM OLD.expires_at
             OR NEW.data_class IS DISTINCT FROM OLD.data_class THEN
            RAISE EXCEPTION 'federation admission grant transition is invalid'
              USING ERRCODE = '55000';
          END IF;
          RETURN NEW;
        END;
        $$
        """
    )
    op.execute(
        "REVOKE ALL ON FUNCTION public.emr4_app_id_fed_grant_terminal() FROM PUBLIC"
    )
    op.execute(
        """
        CREATE TRIGGER trg_app_id_fed_grant_terminal
        BEFORE UPDATE
        ON application_identity_federation_admission_grants
        FOR EACH ROW
        EXECUTE FUNCTION public.emr4_app_id_fed_grant_terminal()
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_app_id_fed_grant_required_audit "
        "ON application_identity_federation_admission_grants"
    )
    op.execute(
        "DROP FUNCTION IF EXISTS public.emr4_app_id_fed_grant_required_audit()"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS trg_app_id_fed_grant_terminal "
        "ON application_identity_federation_admission_grants"
    )
    op.execute("DROP FUNCTION IF EXISTS public.emr4_app_id_fed_grant_terminal()")
    op.execute(f"DROP FUNCTION IF EXISTS {_RESOLVER}")
    op.execute(
        "DROP POLICY IF EXISTS app_id_fed_grant_issuer_insert "
        "ON application_identity_federation_admission_grants"
    )
    op.execute(
        "DROP POLICY IF EXISTS app_id_fed_grant_issuer_select "
        "ON application_identity_federation_admission_grants"
    )
    op.execute(
        "DROP POLICY IF EXISTS app_id_fed_audit_resolver_insert "
        "ON application_identity_federation_audit_events"
    )
    op.execute(
        "DROP POLICY IF EXISTS app_id_fed_binding_resolver_select "
        "ON application_identity_federation_bindings"
    )
    op.execute(
        "DROP POLICY app_id_fed_audit_practice_insert "
        "ON application_identity_federation_audit_events"
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
    op.drop_constraint("ck_app_id_fed_audit_event_type", _AUDIT, type_="check")
    op.create_check_constraint(
        "ck_app_id_fed_audit_event_type",
        _AUDIT,
        "event_type IN ("
        "'federation.binding_created', "
        "'federation.binding_revoked', "
        "'federation.binding_resolved', "
        "'federation.binding_rejected')",
    )
    op.execute(f"ALTER TABLE {_GRANTS} NO FORCE ROW LEVEL SECURITY")
    op.drop_index("ix_app_id_fed_grant_binding_status", table_name=_GRANTS)
    op.drop_index("ix_app_id_fed_grant_practice_expiry", table_name=_GRANTS)
    op.drop_table(_GRANTS)
