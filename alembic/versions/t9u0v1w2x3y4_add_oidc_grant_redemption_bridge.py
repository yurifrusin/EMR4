"""Add atomic OIDC admission-grant redemption bridge.

Revision ID: t9u0v1w2x3y4
Revises: s8t9u0v1w2x3
Create Date: 2026-08-02
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "t9u0v1w2x3y4"
down_revision: Union[str, Sequence[str], None] = "s8t9u0v1w2x3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_TRUTH = "application_auth_synthetic_principal_truth"
_BINDINGS = "application_identity_federation_bindings"
_GRANTS = "application_identity_federation_admission_grants"
_FEDERATION_AUDIT = "application_identity_federation_audit_events"
_REDEEMER = (
    "public.emr4_redeem_application_identity_federation_grant("
    "text, text, text, text, text, text, timestamptz)"
)
_OWNER_PATTERN = "^emr4_oidc_redemption_owner_[a-z0-9_]{8,40}$"
_LOGIN_PATTERN = "^emr4_oidc_redemption_login_[a-z0-9_]{8,40}$"


def upgrade() -> None:
    op.create_table(
        _TRUTH,
        sa.Column("practice_ref", sa.String(length=74), nullable=False),
        sa.Column("user_ref", sa.String(length=74), nullable=False),
        sa.Column("current_backend_role", sa.String(length=32), nullable=False),
        sa.Column("practitioner_ref", sa.String(length=74), nullable=True),
        sa.Column("user_active", sa.Boolean(), nullable=False),
        sa.Column("practice_active", sa.Boolean(), nullable=False),
        sa.Column("membership_active", sa.Boolean(), nullable=False),
        sa.Column("practitioner_link_active", sa.Boolean(), nullable=False),
        sa.Column("truth_version", sa.BigInteger(), nullable=False),
        sa.Column("data_class", sa.String(length=32), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "practice_ref ~ '^synthetic-[a-z0-9-]{1,64}$'",
            name="ck_app_auth_truth_practice_synthetic",
        ),
        sa.CheckConstraint(
            "user_ref ~ '^synthetic-[a-z0-9-]{1,64}$'",
            name="ck_app_auth_truth_user_synthetic",
        ),
        sa.CheckConstraint(
            "practitioner_ref IS NULL OR "
            "practitioner_ref ~ '^synthetic-[a-z0-9-]{1,64}$'",
            name="ck_app_auth_truth_practitioner_synthetic",
        ),
        sa.CheckConstraint(
            "current_backend_role IN "
            "('GP', 'Receptionist', 'Nurse', 'Admin', 'PracticeOwner')",
            name="ck_app_auth_truth_role",
        ),
        sa.CheckConstraint(
            "(practitioner_ref IS NOT NULL) OR NOT practitioner_link_active",
            name="ck_app_auth_truth_practitioner_link_shape",
        ),
        sa.CheckConstraint(
            "truth_version > 0",
            name="ck_app_auth_truth_version",
        ),
        sa.CheckConstraint(
            "data_class = 'authored_synthetic'",
            name="ck_app_auth_truth_data_class",
        ),
        sa.PrimaryKeyConstraint("practice_ref", "user_ref"),
    )
    op.create_index(
        "ix_app_auth_truth_user_practice",
        _TRUTH,
        ["user_ref", "practice_ref"],
    )
    op.execute(f"REVOKE ALL ON TABLE public.{_TRUTH} FROM PUBLIC")
    op.execute(f"ALTER TABLE {_TRUTH} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {_TRUTH} FORCE ROW LEVEL SECURITY")
    op.execute(
        f"""
        CREATE POLICY app_auth_truth_table_owner_all
        ON {_TRUTH}
        FOR ALL
        USING (current_user !~ '^emr4_oidc_redemption_[a-z0-9_]+$')
        WITH CHECK (current_user !~ '^emr4_oidc_redemption_[a-z0-9_]+$')
        """
    )

    op.drop_constraint(
        "ck_app_id_fed_audit_event_type",
        _FEDERATION_AUDIT,
        type_="check",
    )
    op.create_check_constraint(
        "ck_app_id_fed_audit_event_type",
        _FEDERATION_AUDIT,
        "event_type IN ("
        "'federation.binding_created', "
        "'federation.binding_revoked', "
        "'federation.binding_resolved', "
        "'federation.binding_rejected', "
        "'federation.admission_grant_issued', "
        "'federation.admission_grant_consumed', "
        "'federation.admission_grant_rejected')",
    )

    op.execute(
        f"""
        CREATE POLICY app_id_fed_grant_redemption_owner_select
        ON {_GRANTS}
        FOR SELECT
        USING (
          current_user ~ '{_OWNER_PATTERN}'
          AND grant_reference_hmac = NULLIF(
            current_setting('emr4.redemption_grant_hmac', true), ''
          )
        )
        """
    )
    op.execute(
        f"""
        CREATE POLICY app_id_fed_grant_redemption_owner_update
        ON {_GRANTS}
        FOR UPDATE
        USING (
          current_user ~ '{_OWNER_PATTERN}'
          AND grant_reference_hmac = NULLIF(
            current_setting('emr4.redemption_grant_hmac', true), ''
          )
        )
        WITH CHECK (
          current_user ~ '{_OWNER_PATTERN}'
          AND grant_reference_hmac = NULLIF(
            current_setting('emr4.redemption_grant_hmac', true), ''
          )
          AND status = 'consumed'
          AND version = 2
          AND consumed_at IS NOT NULL
        )
        """
    )
    op.execute(
        f"""
        CREATE POLICY app_id_fed_binding_redemption_owner_select
        ON {_BINDINGS}
        FOR SELECT
        USING (
          current_user ~ '{_OWNER_PATTERN}'
          AND binding_ref = NULLIF(
            current_setting('emr4.redemption_binding_ref', true), ''
          )
          AND version::text = NULLIF(
            current_setting('emr4.redemption_binding_version', true), ''
          )
          AND user_ref = NULLIF(
            current_setting('emr4.redemption_user_ref', true), ''
          )
          AND practice_ref = NULLIF(
            current_setting('emr4.redemption_practice_ref', true), ''
          )
        )
        """
    )
    op.execute(
        f"""
        CREATE POLICY app_id_fed_binding_redemption_owner_lock
        ON {_BINDINGS}
        FOR UPDATE
        USING (
          current_user ~ '{_OWNER_PATTERN}'
          AND binding_ref = NULLIF(
            current_setting('emr4.redemption_binding_ref', true), ''
          )
          AND version::text = NULLIF(
            current_setting('emr4.redemption_binding_version', true), ''
          )
          AND user_ref = NULLIF(
            current_setting('emr4.redemption_user_ref', true), ''
          )
          AND practice_ref = NULLIF(
            current_setting('emr4.redemption_practice_ref', true), ''
          )
        )
        WITH CHECK (false)
        """
    )
    op.execute(
        f"""
        CREATE POLICY app_auth_truth_redemption_owner_select
        ON {_TRUTH}
        FOR SELECT
        USING (
          current_user ~ '{_OWNER_PATTERN}'
          AND user_ref = NULLIF(
            current_setting('emr4.redemption_user_ref', true), ''
          )
          AND practice_ref = NULLIF(
            current_setting('emr4.redemption_practice_ref', true), ''
          )
        )
        """
    )
    op.execute(
        f"""
        CREATE POLICY app_auth_truth_redemption_owner_lock
        ON {_TRUTH}
        FOR UPDATE
        USING (
          current_user ~ '{_OWNER_PATTERN}'
          AND user_ref = NULLIF(
            current_setting('emr4.redemption_user_ref', true), ''
          )
          AND practice_ref = NULLIF(
            current_setting('emr4.redemption_practice_ref', true), ''
          )
        )
        WITH CHECK (false)
        """
    )
    op.execute(
        f"""
        CREATE POLICY app_id_fed_audit_redemption_owner_insert
        ON {_FEDERATION_AUDIT}
        FOR INSERT
        WITH CHECK (
          current_user ~ '{_OWNER_PATTERN}'
          AND operation_ref = NULLIF(
            current_setting('emr4.redemption_operation_ref', true), ''
          )
          AND external_reference_hmac = NULLIF(
            current_setting('emr4.federation_external_hmac', true), ''
          )
          AND correlation_reference_hmac = NULLIF(
            current_setting('emr4.federation_correlation_hmac', true), ''
          )
          AND binding_ref = NULLIF(
            current_setting('emr4.redemption_binding_ref', true), ''
          )
          AND user_ref = NULLIF(
            current_setting('emr4.redemption_user_ref', true), ''
          )
          AND practice_ref = NULLIF(
            current_setting('emr4.redemption_practice_ref', true), ''
          )
          AND provider = 'microsoft_entra'
          AND policy_version = 'microsoft-entra-single-tenant-prebound.v1'
          AND (
            (
              event_type = 'federation.admission_grant_consumed'
              AND decision = 'recorded'
              AND reason_code = 'admission_grant_consumed'
            )
            OR (
              event_type = 'federation.admission_grant_rejected'
              AND decision = 'denied'
              AND reason_code IN (
                'admission_grant_expired',
                'admission_grant_context_mismatch',
                'federation_binding_changed',
                'internal_principal_not_current'
              )
            )
          )
        )
        """
    )

    op.execute(
        f"""
        CREATE FUNCTION public.emr4_redeem_application_identity_federation_grant(
          p_grant_reference_hmac text,
          p_surface text,
          p_origin text,
          p_audience_reference_hmac text,
          p_policy_version text,
          p_operation_ref text,
          p_occurred_at timestamptz
        )
        RETURNS TABLE(
          redemption_decision text,
          user_ref text,
          practice_ref text,
          current_backend_role text,
          practitioner_ref text,
          truth_version bigint
        )
        LANGUAGE plpgsql
        SECURITY DEFINER
        VOLATILE
        PARALLEL UNSAFE
        ROWS 1
        SET search_path = ''
        AS $$
        DECLARE
          v_grant public.application_identity_federation_admission_grants%ROWTYPE;
          v_role text;
          v_practitioner_ref text;
          v_truth_version bigint;
          v_user_active boolean;
          v_practice_active boolean;
          v_membership_active boolean;
          v_practitioner_link_active boolean;
          v_rejection_reason text;
        BEGIN
          IF current_user !~ '{_OWNER_PATTERN}'
             OR session_user !~ '{_LOGIN_PATTERN}' THEN
            RAISE EXCEPTION 'federation redemption execution identity is invalid'
              USING ERRCODE = '42501';
          END IF;
          IF p_grant_reference_hmac !~
               '^hmac-sha256:[a-z0-9][a-z0-9_-]{{0,31}}:[0-9a-f]{{64}}$'
             OR p_surface NOT IN ('word_desktop', 'word_online', 'native_diary')
             OR p_origin !~ '^https://[a-z0-9.-]+(:[0-9]{{1,5}})?$'
             OR p_audience_reference_hmac !~
               '^hmac-sha256:synthetic-v1:[0-9a-f]{{64}}$'
             OR p_policy_version <> 'microsoft-entra-single-tenant-prebound.v1'
             OR p_operation_ref !~ '^synthetic-[a-z0-9-]{{1,64}}$'
             OR p_occurred_at IS NULL THEN
            RAISE EXCEPTION 'federation redemption input is invalid'
              USING ERRCODE = '22023';
          END IF;

          PERFORM pg_catalog.set_config(
            'emr4.redemption_grant_hmac', p_grant_reference_hmac, true
          );
          SELECT admission.* INTO v_grant
          FROM public.application_identity_federation_admission_grants AS admission
          WHERE admission.grant_reference_hmac = p_grant_reference_hmac
          FOR UPDATE;

          IF NOT FOUND THEN
            RETURN;
          END IF;
          IF v_grant.status = 'consumed' THEN
            RETURN QUERY SELECT 'already_consumed'::text, NULL::text, NULL::text,
              NULL::text, NULL::text, NULL::bigint;
            RETURN;
          END IF;

          PERFORM pg_catalog.set_config(
            'emr4.redemption_operation_ref', p_operation_ref, true
          );
          PERFORM pg_catalog.set_config(
            'emr4.redemption_binding_ref', v_grant.binding_ref, true
          );
          PERFORM pg_catalog.set_config(
            'emr4.redemption_binding_version', v_grant.binding_version::text, true
          );
          PERFORM pg_catalog.set_config(
            'emr4.redemption_user_ref', v_grant.user_ref, true
          );
          PERFORM pg_catalog.set_config(
            'emr4.redemption_practice_ref', v_grant.practice_ref, true
          );
          PERFORM pg_catalog.set_config(
            'emr4.federation_external_hmac', v_grant.external_reference_hmac, true
          );
          PERFORM pg_catalog.set_config(
            'emr4.federation_correlation_hmac',
            v_grant.correlation_reference_hmac,
            true
          );

          IF v_grant.version <> 1
             OR p_occurred_at < v_grant.issued_at
             OR p_occurred_at >= v_grant.expires_at THEN
            v_rejection_reason := 'admission_grant_expired';
          ELSIF v_grant.surface <> p_surface
             OR v_grant.origin <> p_origin
             OR v_grant.audience_reference_hmac <> p_audience_reference_hmac
             OR v_grant.policy_version <> p_policy_version THEN
            v_rejection_reason := 'admission_grant_context_mismatch';
          END IF;

          IF v_rejection_reason IS NULL THEN
            PERFORM 1
            FROM public.application_identity_federation_bindings AS binding
            WHERE binding.binding_ref = v_grant.binding_ref
              AND binding.version = v_grant.binding_version
              AND binding.user_ref = v_grant.user_ref
              AND binding.practice_ref = v_grant.practice_ref
              AND binding.provider = v_grant.provider
              AND binding.status = 'active'
            FOR KEY SHARE;
            IF NOT FOUND THEN
              v_rejection_reason := 'federation_binding_changed';
            END IF;
          END IF;

          IF v_rejection_reason IS NULL THEN
            SELECT truth.current_backend_role,
                   truth.practitioner_ref,
                   truth.truth_version,
                   truth.user_active,
                   truth.practice_active,
                   truth.membership_active,
                   truth.practitioner_link_active
            INTO v_role,
                 v_practitioner_ref,
                 v_truth_version,
                 v_user_active,
                 v_practice_active,
                 v_membership_active,
                 v_practitioner_link_active
            FROM public.application_auth_synthetic_principal_truth AS truth
            WHERE truth.practice_ref = v_grant.practice_ref
              AND truth.user_ref = v_grant.user_ref
            FOR KEY SHARE;
            IF NOT FOUND
               OR NOT v_user_active
               OR NOT v_practice_active
               OR NOT v_membership_active
               OR (v_practitioner_ref IS NOT NULL AND NOT v_practitioner_link_active)
               OR v_truth_version < 1 THEN
              v_rejection_reason := 'internal_principal_not_current';
            END IF;
          END IF;

          IF v_rejection_reason IS NOT NULL THEN
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
              v_grant.correlation_reference_hmac,
              v_grant.external_reference_hmac,
              v_grant.binding_ref,
              v_grant.user_ref,
              v_grant.practice_ref,
              v_grant.provider,
              'federation.admission_grant_rejected',
              'denied',
              v_rejection_reason,
              v_grant.policy_version,
              p_occurred_at,
              'authored_synthetic'
            );
            RETURN QUERY SELECT 'rejected'::text, NULL::text, NULL::text,
              NULL::text, NULL::text, NULL::bigint;
            RETURN;
          END IF;

          UPDATE public.application_identity_federation_admission_grants
          SET status = 'consumed', version = 2, consumed_at = p_occurred_at
          WHERE grant_reference_hmac = p_grant_reference_hmac;
          IF NOT FOUND THEN
            RAISE EXCEPTION 'federation admission grant consume failed'
              USING ERRCODE = '40001';
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
            p_operation_ref,
            v_grant.correlation_reference_hmac,
            v_grant.external_reference_hmac,
            v_grant.binding_ref,
            v_grant.user_ref,
            v_grant.practice_ref,
            v_grant.provider,
            'federation.admission_grant_consumed',
            'recorded',
            'admission_grant_consumed',
            v_grant.policy_version,
            p_occurred_at,
            'authored_synthetic'
          );

          RETURN QUERY SELECT 'admitted'::text,
            v_grant.user_ref::text,
            v_grant.practice_ref::text,
            v_role,
            v_practitioner_ref,
            v_truth_version;
        END;
        $$
        """
    )
    op.execute(f"REVOKE ALL ON FUNCTION {_REDEEMER} FROM PUBLIC")


def downgrade() -> None:
    op.execute(f"DROP FUNCTION IF EXISTS {_REDEEMER}")
    op.execute(
        "DROP POLICY IF EXISTS app_id_fed_audit_redemption_owner_insert "
        f"ON {_FEDERATION_AUDIT}"
    )
    op.execute(
        "DROP POLICY IF EXISTS app_auth_truth_redemption_owner_select "
        f"ON {_TRUTH}"
    )
    op.execute(
        "DROP POLICY IF EXISTS app_auth_truth_redemption_owner_lock "
        f"ON {_TRUTH}"
    )
    op.execute(
        "DROP POLICY IF EXISTS app_auth_truth_table_owner_all "
        f"ON {_TRUTH}"
    )
    op.execute(
        "DROP POLICY IF EXISTS app_id_fed_binding_redemption_owner_select "
        f"ON {_BINDINGS}"
    )
    op.execute(
        "DROP POLICY IF EXISTS app_id_fed_binding_redemption_owner_lock "
        f"ON {_BINDINGS}"
    )
    op.execute(
        "DROP POLICY IF EXISTS app_id_fed_grant_redemption_owner_update "
        f"ON {_GRANTS}"
    )
    op.execute(
        "DROP POLICY IF EXISTS app_id_fed_grant_redemption_owner_select "
        f"ON {_GRANTS}"
    )
    op.drop_constraint(
        "ck_app_id_fed_audit_event_type",
        _FEDERATION_AUDIT,
        type_="check",
    )
    op.create_check_constraint(
        "ck_app_id_fed_audit_event_type",
        _FEDERATION_AUDIT,
        "event_type IN ("
        "'federation.binding_created', "
        "'federation.binding_revoked', "
        "'federation.binding_resolved', "
        "'federation.binding_rejected', "
        "'federation.admission_grant_issued')",
    )
    op.execute(f"ALTER TABLE {_TRUTH} NO FORCE ROW LEVEL SECURITY")
    op.drop_index("ix_app_auth_truth_user_practice", table_name=_TRUTH)
    op.drop_table(_TRUTH)
