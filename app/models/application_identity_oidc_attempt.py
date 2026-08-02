"""Encrypted authored-synthetic OIDC authorization-attempt persistence."""

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Index,
    LargeBinary,
    String,
    UniqueConstraint,
)

from app.models.base import Base


_HMAC_REF_CHECK = (
    "VALUE ~ '^hmac-sha256:[a-z0-9][a-z0-9_-]{0,31}:[0-9a-f]{64}$'"
)


class ApplicationIdentityOIDCAuthorizationAttempt(Base):
    __tablename__ = "application_identity_oidc_authorization_attempts"

    state_reference_hmac = Column(String(128), primary_key=True)
    nonce_reference_hmac = Column(String(128), nullable=False)
    cipher_key_id = Column(String(64), nullable=False)
    ciphertext = Column(LargeBinary, nullable=False)
    envelope_version = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    data_class = Column(String(32), nullable=False)

    __table_args__ = (
        CheckConstraint(
            _HMAC_REF_CHECK.replace("VALUE", "state_reference_hmac"),
            name="ck_app_id_oidc_attempt_state_hmac",
        ),
        CheckConstraint(
            _HMAC_REF_CHECK.replace("VALUE", "nonce_reference_hmac"),
            name="ck_app_id_oidc_attempt_nonce_hmac",
        ),
        CheckConstraint(
            "cipher_key_id ~ '^[a-z0-9][a-z0-9_-]{0,31}$'",
            name="ck_app_id_oidc_attempt_cipher_key_id",
        ),
        CheckConstraint(
            "octet_length(ciphertext) BETWEEN 1 AND 131072",
            name="ck_app_id_oidc_attempt_ciphertext_size",
        ),
        CheckConstraint(
            "envelope_version = 'oidc-authorization-attempt-envelope.v1'",
            name="ck_app_id_oidc_attempt_envelope_version",
        ),
        CheckConstraint(
            "expires_at = created_at + INTERVAL '5 minutes'",
            name="ck_app_id_oidc_attempt_exact_expiry",
        ),
        CheckConstraint(
            "data_class = 'authored_synthetic'",
            name="ck_app_id_oidc_attempt_data_class",
        ),
        UniqueConstraint(
            "nonce_reference_hmac",
            name="uq_app_id_oidc_attempt_nonce_hmac",
        ),
        Index(
            "ix_app_id_oidc_attempt_expiry",
            "expires_at",
        ),
    )


__all__ = ["ApplicationIdentityOIDCAuthorizationAttempt"]
