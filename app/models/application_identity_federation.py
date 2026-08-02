"""Authored-synthetic PostgreSQL records for external identity bindings.

The schema stores only versioned keyed-HMAC references for external identity
material. It intentionally has no foreign key to live EMR4 identity or product
tables; replacing synthetic references requires a later migration and authority.
"""

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    Identity,
    Index,
    String,
    UniqueConstraint,
)

from app.models.base import Base


_SYNTHETIC_REF_CHECK = "VALUE ~ '^synthetic-[a-z0-9-]{1,64}$'"
_HMAC_REF_CHECK = (
    "VALUE ~ '^hmac-sha256:synthetic-v1:[0-9a-f]{64}$'"
)


class ApplicationIdentityFederationBinding(Base):
    __tablename__ = "application_identity_federation_bindings"

    id = Column(BigInteger, Identity(), primary_key=True)
    binding_ref = Column(String(74), nullable=False)
    provider = Column(String(32), nullable=False)
    issuer_reference_hmac = Column(String(96), nullable=False)
    tenant_reference_hmac = Column(String(96), nullable=False)
    object_reference_hmac = Column(String(96), nullable=False)
    subject_reference_hmac = Column(String(96), nullable=False)
    user_ref = Column(String(74), nullable=False)
    practice_ref = Column(String(74), nullable=False)
    status = Column(String(16), nullable=False)
    version = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    data_class = Column(String(32), nullable=False)

    __table_args__ = (
        CheckConstraint(
            _SYNTHETIC_REF_CHECK.replace("VALUE", "binding_ref"),
            name="ck_app_id_fed_binding_ref_synthetic",
        ),
        CheckConstraint(
            "provider = 'microsoft_entra'",
            name="ck_app_id_fed_binding_provider",
        ),
        CheckConstraint(
            _HMAC_REF_CHECK.replace("VALUE", "issuer_reference_hmac"),
            name="ck_app_id_fed_binding_issuer_hmac",
        ),
        CheckConstraint(
            _HMAC_REF_CHECK.replace("VALUE", "tenant_reference_hmac"),
            name="ck_app_id_fed_binding_tenant_hmac",
        ),
        CheckConstraint(
            _HMAC_REF_CHECK.replace("VALUE", "object_reference_hmac"),
            name="ck_app_id_fed_binding_object_hmac",
        ),
        CheckConstraint(
            _HMAC_REF_CHECK.replace("VALUE", "subject_reference_hmac"),
            name="ck_app_id_fed_binding_subject_hmac",
        ),
        CheckConstraint(
            _SYNTHETIC_REF_CHECK.replace("VALUE", "user_ref"),
            name="ck_app_id_fed_binding_user_synthetic",
        ),
        CheckConstraint(
            _SYNTHETIC_REF_CHECK.replace("VALUE", "practice_ref"),
            name="ck_app_id_fed_binding_practice_synthetic",
        ),
        CheckConstraint(
            "status IN ('active', 'revoked')",
            name="ck_app_id_fed_binding_status",
        ),
        CheckConstraint(
            "version > 0",
            name="ck_app_id_fed_binding_version",
        ),
        CheckConstraint(
            "updated_at >= created_at AND "
            "((status = 'active' AND revoked_at IS NULL) OR "
            "(status = 'revoked' AND revoked_at IS NOT NULL "
            "AND revoked_at >= created_at AND updated_at = revoked_at))",
            name="ck_app_id_fed_binding_time_status",
        ),
        CheckConstraint(
            "data_class = 'authored_synthetic'",
            name="ck_app_id_fed_binding_data_class",
        ),
        UniqueConstraint(
            "binding_ref",
            name="uq_app_id_fed_binding_ref",
        ),
        UniqueConstraint(
            "provider",
            "issuer_reference_hmac",
            "tenant_reference_hmac",
            "object_reference_hmac",
            name="uq_app_id_fed_external_key",
        ),
        Index(
            "ix_app_id_fed_binding_practice_user",
            "practice_ref",
            "user_ref",
        ),
        Index(
            "ix_app_id_fed_binding_practice_status",
            "practice_ref",
            "status",
        ),
    )


class ApplicationIdentityFederationAuditEvent(Base):
    __tablename__ = "application_identity_federation_audit_events"

    id = Column(BigInteger, Identity(), primary_key=True)
    operation_ref = Column(String(74), nullable=False)
    correlation_reference_hmac = Column(String(96), nullable=False)
    external_reference_hmac = Column(String(96), nullable=False)
    binding_ref = Column(String(74), nullable=True)
    user_ref = Column(String(74), nullable=True)
    practice_ref = Column(String(74), nullable=True)
    provider = Column(String(32), nullable=False)
    event_type = Column(String(64), nullable=False)
    decision = Column(String(16), nullable=False)
    reason_code = Column(String(64), nullable=False)
    policy_version = Column(String(64), nullable=False)
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    data_class = Column(String(32), nullable=False)

    __table_args__ = (
        CheckConstraint(
            _SYNTHETIC_REF_CHECK.replace("VALUE", "operation_ref"),
            name="ck_app_id_fed_audit_operation_synthetic",
        ),
        CheckConstraint(
            _HMAC_REF_CHECK.replace("VALUE", "correlation_reference_hmac"),
            name="ck_app_id_fed_audit_correlation_hmac",
        ),
        CheckConstraint(
            _HMAC_REF_CHECK.replace("VALUE", "external_reference_hmac"),
            name="ck_app_id_fed_audit_external_hmac",
        ),
        CheckConstraint(
            "binding_ref IS NULL OR "
            + _SYNTHETIC_REF_CHECK.replace("VALUE", "binding_ref"),
            name="ck_app_id_fed_audit_binding_synthetic",
        ),
        CheckConstraint(
            "user_ref IS NULL OR "
            + _SYNTHETIC_REF_CHECK.replace("VALUE", "user_ref"),
            name="ck_app_id_fed_audit_user_synthetic",
        ),
        CheckConstraint(
            "practice_ref IS NULL OR "
            + _SYNTHETIC_REF_CHECK.replace("VALUE", "practice_ref"),
            name="ck_app_id_fed_audit_practice_synthetic",
        ),
        CheckConstraint(
            "(user_ref IS NULL) = (practice_ref IS NULL)",
            name="ck_app_id_fed_audit_principal_pair",
        ),
        CheckConstraint(
            "provider = 'microsoft_entra'",
            name="ck_app_id_fed_audit_provider",
        ),
        CheckConstraint(
            "event_type IN ("
            "'federation.binding_created', "
            "'federation.binding_revoked', "
            "'federation.binding_resolved', "
            "'federation.binding_rejected', "
            "'federation.admission_grant_issued', "
            "'federation.admission_grant_consumed', "
            "'federation.admission_grant_rejected')",
            name="ck_app_id_fed_audit_event_type",
        ),
        CheckConstraint(
            "decision IN ('allowed', 'denied', 'recorded')",
            name="ck_app_id_fed_audit_decision",
        ),
        CheckConstraint(
            "reason_code ~ '^[a-z0-9_]{1,64}$'",
            name="ck_app_id_fed_audit_reason",
        ),
        CheckConstraint(
            "policy_version = 'microsoft-entra-single-tenant-prebound.v1'",
            name="ck_app_id_fed_audit_policy",
        ),
        CheckConstraint(
            "data_class = 'authored_synthetic'",
            name="ck_app_id_fed_audit_data_class",
        ),
        UniqueConstraint(
            "operation_ref",
            name="uq_app_id_fed_audit_operation",
        ),
        Index(
            "ix_app_id_fed_audit_practice_time",
            "practice_ref",
            "occurred_at",
        ),
        Index(
            "ix_app_id_fed_audit_external_time",
            "external_reference_hmac",
            "occurred_at",
        ),
    )


class ApplicationIdentityFederationAdmissionGrant(Base):
    __tablename__ = "application_identity_federation_admission_grants"

    grant_reference_hmac = Column(String(128), primary_key=True)
    operation_ref = Column(String(74), nullable=False)
    binding_ref = Column(String(74), nullable=False)
    binding_version = Column(BigInteger, nullable=False)
    user_ref = Column(String(74), nullable=False)
    practice_ref = Column(String(74), nullable=False)
    provider = Column(String(32), nullable=False)
    external_reference_hmac = Column(String(96), nullable=False)
    audience_reference_hmac = Column(String(96), nullable=False)
    correlation_reference_hmac = Column(String(96), nullable=False)
    surface = Column(String(32), nullable=False)
    origin = Column(String(512), nullable=False)
    return_target = Column(String(32), nullable=False)
    policy_version = Column(String(64), nullable=False)
    issued_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(16), nullable=False)
    version = Column(BigInteger, nullable=False)
    consumed_at = Column(DateTime(timezone=True), nullable=True)
    data_class = Column(String(32), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "grant_reference_hmac ~ "
            "'^hmac-sha256:[a-z0-9][a-z0-9_-]{0,31}:[0-9a-f]{64}$'",
            name="ck_app_id_fed_grant_reference_hmac",
        ),
        CheckConstraint(
            _SYNTHETIC_REF_CHECK.replace("VALUE", "operation_ref"),
            name="ck_app_id_fed_grant_operation_synthetic",
        ),
        CheckConstraint(
            _SYNTHETIC_REF_CHECK.replace("VALUE", "binding_ref"),
            name="ck_app_id_fed_grant_binding_synthetic",
        ),
        CheckConstraint(
            "binding_version > 0",
            name="ck_app_id_fed_grant_binding_version",
        ),
        CheckConstraint(
            _SYNTHETIC_REF_CHECK.replace("VALUE", "user_ref"),
            name="ck_app_id_fed_grant_user_synthetic",
        ),
        CheckConstraint(
            _SYNTHETIC_REF_CHECK.replace("VALUE", "practice_ref"),
            name="ck_app_id_fed_grant_practice_synthetic",
        ),
        CheckConstraint(
            "provider = 'microsoft_entra'",
            name="ck_app_id_fed_grant_provider",
        ),
        CheckConstraint(
            _HMAC_REF_CHECK.replace("VALUE", "external_reference_hmac"),
            name="ck_app_id_fed_grant_external_hmac",
        ),
        CheckConstraint(
            _HMAC_REF_CHECK.replace("VALUE", "audience_reference_hmac"),
            name="ck_app_id_fed_grant_audience_hmac",
        ),
        CheckConstraint(
            _HMAC_REF_CHECK.replace("VALUE", "correlation_reference_hmac"),
            name="ck_app_id_fed_grant_correlation_hmac",
        ),
        CheckConstraint(
            "surface IN ('word_desktop', 'word_online', 'native_diary')",
            name="ck_app_id_fed_grant_surface",
        ),
        CheckConstraint(
            "origin ~ '^https://[a-z0-9.-]+(:[0-9]{1,5})?$'",
            name="ck_app_id_fed_grant_origin",
        ),
        CheckConstraint(
            "return_target IN ('clinician_one', 'reception_one', 'diary')",
            name="ck_app_id_fed_grant_return_target",
        ),
        CheckConstraint(
            "policy_version = 'microsoft-entra-single-tenant-prebound.v1'",
            name="ck_app_id_fed_grant_policy",
        ),
        CheckConstraint(
            "expires_at = issued_at + INTERVAL '60 seconds'",
            name="ck_app_id_fed_grant_exact_expiry",
        ),
        CheckConstraint(
            "status IN ('active', 'consumed')",
            name="ck_app_id_fed_grant_status",
        ),
        CheckConstraint(
            "version > 0 AND "
            "((status = 'active' AND version = 1 AND consumed_at IS NULL) OR "
            "(status = 'consumed' AND version = 2 AND consumed_at IS NOT NULL "
            "AND consumed_at >= issued_at))",
            name="ck_app_id_fed_grant_state",
        ),
        CheckConstraint(
            "data_class = 'authored_synthetic'",
            name="ck_app_id_fed_grant_data_class",
        ),
        Index(
            "ix_app_id_fed_grant_practice_expiry",
            "practice_ref",
            "expires_at",
        ),
        Index(
            "ix_app_id_fed_grant_binding_status",
            "binding_ref",
            "status",
        ),
        UniqueConstraint(
            "operation_ref",
            name="uq_app_id_fed_grant_operation",
        ),
    )


__all__ = [
    "ApplicationIdentityFederationAdmissionGrant",
    "ApplicationIdentityFederationAuditEvent",
    "ApplicationIdentityFederationBinding",
]
