"""Add encrypted authored-synthetic OIDC authorization attempts.

Revision ID: r7s8t9u0v1w2
Revises: q6r7s8t9u0v1
Create Date: 2026-08-02
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "r7s8t9u0v1w2"
down_revision: Union[str, Sequence[str], None] = "q6r7s8t9u0v1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_ATTEMPTS = "application_identity_oidc_authorization_attempts"
_ROLE_PATTERN = "^emr4_oidc_attempt_runtime_[a-z0-9_]{8,40}$"


def upgrade() -> None:
    op.create_table(
        _ATTEMPTS,
        sa.Column("state_reference_hmac", sa.String(length=128), nullable=False),
        sa.Column("nonce_reference_hmac", sa.String(length=128), nullable=False),
        sa.Column("cipher_key_id", sa.String(length=64), nullable=False),
        sa.Column("ciphertext", sa.LargeBinary(), nullable=False),
        sa.Column("envelope_version", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data_class", sa.String(length=32), nullable=False),
        sa.CheckConstraint(
            "state_reference_hmac ~ "
            "'^hmac-sha256:[a-z0-9][a-z0-9_-]{0,31}:[0-9a-f]{64}$'",
            name="ck_app_id_oidc_attempt_state_hmac",
        ),
        sa.CheckConstraint(
            "nonce_reference_hmac ~ "
            "'^hmac-sha256:[a-z0-9][a-z0-9_-]{0,31}:[0-9a-f]{64}$'",
            name="ck_app_id_oidc_attempt_nonce_hmac",
        ),
        sa.CheckConstraint(
            "cipher_key_id ~ '^[a-z0-9][a-z0-9_-]{0,31}$'",
            name="ck_app_id_oidc_attempt_cipher_key_id",
        ),
        sa.CheckConstraint(
            "octet_length(ciphertext) BETWEEN 1 AND 131072",
            name="ck_app_id_oidc_attempt_ciphertext_size",
        ),
        sa.CheckConstraint(
            "envelope_version = 'oidc-authorization-attempt-envelope.v1'",
            name="ck_app_id_oidc_attempt_envelope_version",
        ),
        sa.CheckConstraint(
            "expires_at = created_at + INTERVAL '5 minutes'",
            name="ck_app_id_oidc_attempt_exact_expiry",
        ),
        sa.CheckConstraint(
            "data_class = 'authored_synthetic'",
            name="ck_app_id_oidc_attempt_data_class",
        ),
        sa.PrimaryKeyConstraint("state_reference_hmac"),
        sa.UniqueConstraint(
            "nonce_reference_hmac",
            name="uq_app_id_oidc_attempt_nonce_hmac",
        ),
    )
    op.create_index(
        "ix_app_id_oidc_attempt_expiry",
        _ATTEMPTS,
        ["expires_at"],
    )
    op.execute(
        "REVOKE ALL ON TABLE "
        "public.application_identity_oidc_authorization_attempts FROM PUBLIC"
    )
    op.execute(
        "ALTER TABLE application_identity_oidc_authorization_attempts "
        "ENABLE ROW LEVEL SECURITY"
    )
    op.execute(
        "ALTER TABLE application_identity_oidc_authorization_attempts "
        "FORCE ROW LEVEL SECURITY"
    )
    op.execute(
        f"""
        CREATE POLICY app_id_oidc_attempt_runtime_select
        ON application_identity_oidc_authorization_attempts
        FOR SELECT
        USING (current_user ~ '{_ROLE_PATTERN}')
        """
    )
    op.execute(
        f"""
        CREATE POLICY app_id_oidc_attempt_runtime_insert
        ON application_identity_oidc_authorization_attempts
        FOR INSERT
        WITH CHECK (current_user ~ '{_ROLE_PATTERN}')
        """
    )
    op.execute(
        f"""
        CREATE POLICY app_id_oidc_attempt_runtime_delete
        ON application_identity_oidc_authorization_attempts
        FOR DELETE
        USING (current_user ~ '{_ROLE_PATTERN}')
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP POLICY IF EXISTS app_id_oidc_attempt_runtime_delete "
        "ON application_identity_oidc_authorization_attempts"
    )
    op.execute(
        "DROP POLICY IF EXISTS app_id_oidc_attempt_runtime_insert "
        "ON application_identity_oidc_authorization_attempts"
    )
    op.execute(
        "DROP POLICY IF EXISTS app_id_oidc_attempt_runtime_select "
        "ON application_identity_oidc_authorization_attempts"
    )
    op.execute(
        "ALTER TABLE application_identity_oidc_authorization_attempts "
        "NO FORCE ROW LEVEL SECURITY"
    )
    op.drop_index("ix_app_id_oidc_attempt_expiry", table_name=_ATTEMPTS)
    op.drop_table(_ATTEMPTS)
