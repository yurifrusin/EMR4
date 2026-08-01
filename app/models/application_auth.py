"""Authored-synthetic PostgreSQL records for the shared auth foundation.

These tables intentionally accept only the bounded synthetic references used by
the authorised persistence tranche. Live EMR4 identity mapping requires a later
schema and authority decision.
"""

from sqlalchemy import (
    ARRAY,
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKeyConstraint,
    Identity,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.sql import func

from app.models.base import Base


_SYNTHETIC_REF_CHECK = "VALUE ~ '^synthetic-[a-z0-9-]{1,64}$'"
_HASH_REF_CHECK = "VALUE ~ '^sha256:[0-9a-f]{64}$'"
_ROLES = "'GP', 'Receptionist', 'Nurse', 'Admin', 'PracticeOwner'"
_SURFACES = "'word_desktop', 'word_online', 'native_diary'"
_STATUSES = "'active', 'revoked'"
_EVENT_TYPES = (
    "'auth.session_created', 'auth.session_refreshed', "
    "'auth.session_revoked', 'auth.surface_bound', "
    "'auth.exchange_issued', 'auth.exchange_redeemed', "
    "'auth.exchange_rejected', 'auth.authorization_denied'"
)
_DECISIONS = "'allowed', 'denied', 'recorded'"


class ApplicationAuthPrincipalGeneration(Base):
    __tablename__ = "application_auth_principal_generations"

    practice_ref = Column(String(74), primary_key=True)
    user_ref = Column(String(74), primary_key=True)
    generation = Column(BigInteger, nullable=False)
    data_class = Column(String(32), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            _SYNTHETIC_REF_CHECK.replace("VALUE", "practice_ref"),
            name="ck_app_auth_principal_practice_synthetic",
        ),
        CheckConstraint(
            _SYNTHETIC_REF_CHECK.replace("VALUE", "user_ref"),
            name="ck_app_auth_principal_user_synthetic",
        ),
        CheckConstraint("generation > 0", name="ck_app_auth_principal_generation"),
        CheckConstraint(
            "data_class = 'authored_synthetic'",
            name="ck_app_auth_principal_data_class",
        ),
        Index(
            "ix_app_auth_principal_user_practice",
            "user_ref",
            "practice_ref",
        ),
    )


class ApplicationAuthParentSession(Base):
    __tablename__ = "application_auth_parent_sessions"

    session_reference_hash = Column(String(71), primary_key=True)
    practice_ref = Column(String(74), nullable=False)
    user_ref = Column(String(74), nullable=False)
    current_backend_role = Column(String(32), nullable=False)
    practitioner_ref = Column(String(74), nullable=True)
    generation = Column(BigInteger, nullable=False)
    status = Column(String(16), nullable=False)
    data_class = Column(String(32), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    last_observed_at = Column(DateTime(timezone=True), nullable=False)
    idle_expires_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        CheckConstraint(
            _HASH_REF_CHECK.replace("VALUE", "session_reference_hash"),
            name="ck_app_auth_parent_hash",
        ),
        CheckConstraint(
            _SYNTHETIC_REF_CHECK.replace("VALUE", "practice_ref"),
            name="ck_app_auth_parent_practice_synthetic",
        ),
        CheckConstraint(
            _SYNTHETIC_REF_CHECK.replace("VALUE", "user_ref"),
            name="ck_app_auth_parent_user_synthetic",
        ),
        CheckConstraint(
            "practitioner_ref IS NULL OR "
            + _SYNTHETIC_REF_CHECK.replace("VALUE", "practitioner_ref"),
            name="ck_app_auth_parent_practitioner_synthetic",
        ),
        CheckConstraint(
            f"current_backend_role IN ({_ROLES})",
            name="ck_app_auth_parent_role",
        ),
        CheckConstraint("generation > 0", name="ck_app_auth_parent_generation"),
        CheckConstraint(
            f"status IN ({_STATUSES})",
            name="ck_app_auth_parent_status",
        ),
        CheckConstraint(
            "data_class = 'authored_synthetic'",
            name="ck_app_auth_parent_data_class",
        ),
        CheckConstraint(
            "last_observed_at >= created_at AND "
            "expires_at > created_at AND idle_expires_at <= expires_at AND "
            "(status = 'revoked' OR idle_expires_at > last_observed_at)",
            name="ck_app_auth_parent_time_bounds",
        ),
        UniqueConstraint(
            "practice_ref",
            "session_reference_hash",
            name="uq_app_auth_parent_practice_hash",
        ),
        ForeignKeyConstraint(
            ["practice_ref", "user_ref"],
            [
                "application_auth_principal_generations.practice_ref",
                "application_auth_principal_generations.user_ref",
            ],
            name="fk_app_auth_parent_principal",
        ),
        Index(
            "ix_app_auth_parent_principal",
            "practice_ref",
            "user_ref",
        ),
        Index(
            "ix_app_auth_parent_active_expiry",
            "practice_ref",
            "expires_at",
            postgresql_where=text("status = 'active'"),
        ),
    )


class ApplicationAuthSurfaceSession(Base):
    __tablename__ = "application_auth_surface_sessions"

    surface_reference_hash = Column(String(71), primary_key=True)
    practice_ref = Column(String(74), nullable=False)
    parent_session_reference_hash = Column(String(71), nullable=False)
    surface = Column(String(32), nullable=False)
    origin = Column(String(255), nullable=False)
    audience = Column(String(64), nullable=False)
    parent_generation = Column(BigInteger, nullable=False)
    status = Column(String(16), nullable=False)
    data_class = Column(String(32), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    last_observed_at = Column(DateTime(timezone=True), nullable=False)
    idle_expires_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        CheckConstraint(
            _HASH_REF_CHECK.replace("VALUE", "surface_reference_hash"),
            name="ck_app_auth_surface_hash",
        ),
        CheckConstraint(
            _HASH_REF_CHECK.replace("VALUE", "parent_session_reference_hash"),
            name="ck_app_auth_surface_parent_hash",
        ),
        CheckConstraint(
            _SYNTHETIC_REF_CHECK.replace("VALUE", "practice_ref"),
            name="ck_app_auth_surface_practice_synthetic",
        ),
        CheckConstraint(
            f"surface IN ({_SURFACES})",
            name="ck_app_auth_surface_surface",
        ),
        CheckConstraint(
            "origin ~ '^https://[^/]+$'",
            name="ck_app_auth_surface_origin",
        ),
        CheckConstraint(
            "audience = 'emr4-api'",
            name="ck_app_auth_surface_audience",
        ),
        CheckConstraint(
            "parent_generation > 0",
            name="ck_app_auth_surface_generation",
        ),
        CheckConstraint(
            f"status IN ({_STATUSES})",
            name="ck_app_auth_surface_status",
        ),
        CheckConstraint(
            "data_class = 'authored_synthetic'",
            name="ck_app_auth_surface_data_class",
        ),
        CheckConstraint(
            "last_observed_at >= created_at AND "
            "expires_at = idle_expires_at AND "
            "(status = 'revoked' OR idle_expires_at > last_observed_at)",
            name="ck_app_auth_surface_time_bounds",
        ),
        UniqueConstraint(
            "practice_ref",
            "surface_reference_hash",
            name="uq_app_auth_surface_practice_hash",
        ),
        ForeignKeyConstraint(
            ["practice_ref", "parent_session_reference_hash"],
            [
                "application_auth_parent_sessions.practice_ref",
                "application_auth_parent_sessions.session_reference_hash",
            ],
            name="fk_app_auth_surface_parent",
        ),
        Index(
            "ix_app_auth_surface_parent",
            "practice_ref",
            "parent_session_reference_hash",
        ),
        Index(
            "ix_app_auth_surface_active_expiry",
            "practice_ref",
            "surface",
            "expires_at",
            postgresql_where=text("status = 'active'"),
        ),
    )


class ApplicationAuthExchangeGrant(Base):
    __tablename__ = "application_auth_exchange_grants"

    grant_reference_hash = Column(String(71), primary_key=True)
    practice_ref = Column(String(74), nullable=False)
    parent_session_reference_hash = Column(String(71), nullable=False)
    source_surface_reference_hash = Column(String(71), nullable=False)
    parent_generation = Column(BigInteger, nullable=False)
    source_surface = Column(String(32), nullable=False)
    target_surface = Column(String(32), nullable=False)
    source_origin = Column(String(255), nullable=False)
    target_origin = Column(String(255), nullable=False)
    audience = Column(String(64), nullable=False)
    state_hash = Column(String(71), nullable=False)
    nonce_hash = Column(String(71), nullable=False)
    pkce_challenge = Column(String(43), nullable=False)
    issued_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    consumed_at = Column(DateTime(timezone=True), nullable=True)
    data_class = Column(String(32), nullable=False)

    __table_args__ = (
        CheckConstraint(
            _HASH_REF_CHECK.replace("VALUE", "grant_reference_hash"),
            name="ck_app_auth_exchange_hash",
        ),
        CheckConstraint(
            _HASH_REF_CHECK.replace("VALUE", "parent_session_reference_hash"),
            name="ck_app_auth_exchange_parent_hash",
        ),
        CheckConstraint(
            _HASH_REF_CHECK.replace("VALUE", "source_surface_reference_hash"),
            name="ck_app_auth_exchange_source_hash",
        ),
        CheckConstraint(
            _HASH_REF_CHECK.replace("VALUE", "state_hash"),
            name="ck_app_auth_exchange_state_hash",
        ),
        CheckConstraint(
            _HASH_REF_CHECK.replace("VALUE", "nonce_hash"),
            name="ck_app_auth_exchange_nonce_hash",
        ),
        CheckConstraint(
            _SYNTHETIC_REF_CHECK.replace("VALUE", "practice_ref"),
            name="ck_app_auth_exchange_practice_synthetic",
        ),
        CheckConstraint(
            "parent_generation > 0",
            name="ck_app_auth_exchange_generation",
        ),
        CheckConstraint(
            "source_surface IN ('word_desktop', 'word_online') AND "
            "target_surface = 'native_diary'",
            name="ck_app_auth_exchange_flow",
        ),
        CheckConstraint(
            "source_origin ~ '^https://[^/]+$' AND "
            "target_origin ~ '^https://[^/]+$'",
            name="ck_app_auth_exchange_origins",
        ),
        CheckConstraint(
            "audience = 'emr4-session-exchange'",
            name="ck_app_auth_exchange_audience",
        ),
        CheckConstraint(
            "pkce_challenge ~ '^[A-Za-z0-9_-]{43}$'",
            name="ck_app_auth_exchange_pkce",
        ),
        CheckConstraint(
            "expires_at > issued_at AND "
            "(consumed_at IS NULL OR "
            "(consumed_at >= issued_at AND consumed_at < expires_at))",
            name="ck_app_auth_exchange_time_bounds",
        ),
        CheckConstraint(
            "data_class = 'authored_synthetic'",
            name="ck_app_auth_exchange_data_class",
        ),
        UniqueConstraint(
            "practice_ref",
            "grant_reference_hash",
            name="uq_app_auth_exchange_practice_hash",
        ),
        ForeignKeyConstraint(
            ["practice_ref", "parent_session_reference_hash"],
            [
                "application_auth_parent_sessions.practice_ref",
                "application_auth_parent_sessions.session_reference_hash",
            ],
            name="fk_app_auth_exchange_parent",
        ),
        ForeignKeyConstraint(
            ["practice_ref", "source_surface_reference_hash"],
            [
                "application_auth_surface_sessions.practice_ref",
                "application_auth_surface_sessions.surface_reference_hash",
            ],
            name="fk_app_auth_exchange_source_surface",
        ),
        Index(
            "ix_app_auth_exchange_parent",
            "practice_ref",
            "parent_session_reference_hash",
        ),
        Index(
            "ix_app_auth_exchange_source_surface",
            "practice_ref",
            "source_surface_reference_hash",
        ),
        Index(
            "ix_app_auth_exchange_unconsumed_expiry",
            "practice_ref",
            "expires_at",
            postgresql_where=text("consumed_at IS NULL"),
        ),
    )


class ApplicationAuthAuditEvent(Base):
    __tablename__ = "application_auth_audit_events"

    id = Column(BigInteger, Identity(), primary_key=True)
    practice_ref = Column(String(74), nullable=True)
    user_ref = Column(String(74), nullable=True)
    current_backend_role = Column(String(32), nullable=True)
    event_type = Column(String(64), nullable=False)
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    correlation_id = Column(String(76), nullable=False)
    session_reference_hash = Column(String(71), nullable=False)
    surface = Column(String(32), nullable=False)
    action = Column(String(64), nullable=False)
    resource_type = Column(String(64), nullable=False)
    policy_version = Column(String(64), nullable=False)
    decision = Column(String(16), nullable=False)
    reason_codes = Column(ARRAY(String(100)), nullable=False)
    grant_reference_hash = Column(String(71), nullable=True)
    target_surface = Column(String(32), nullable=True)
    data_class = Column(String(32), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "practice_ref IS NULL OR "
            + _SYNTHETIC_REF_CHECK.replace("VALUE", "practice_ref"),
            name="ck_app_auth_audit_practice_synthetic",
        ),
        CheckConstraint(
            "user_ref IS NULL OR "
            + _SYNTHETIC_REF_CHECK.replace("VALUE", "user_ref"),
            name="ck_app_auth_audit_user_synthetic",
        ),
        CheckConstraint(
            f"current_backend_role IS NULL OR current_backend_role IN ({_ROLES})",
            name="ck_app_auth_audit_role",
        ),
        CheckConstraint(
            f"event_type IN ({_EVENT_TYPES})",
            name="ck_app_auth_audit_event_type",
        ),
        CheckConstraint(
            "correlation_id ~ '^correlation-[a-z0-9-]{1,64}$'",
            name="ck_app_auth_audit_correlation",
        ),
        CheckConstraint(
            _HASH_REF_CHECK.replace("VALUE", "session_reference_hash"),
            name="ck_app_auth_audit_session_hash",
        ),
        CheckConstraint(
            "grant_reference_hash IS NULL OR "
            + _HASH_REF_CHECK.replace("VALUE", "grant_reference_hash"),
            name="ck_app_auth_audit_grant_hash",
        ),
        CheckConstraint(
            "surface IN ('word_desktop', 'word_online', 'native_diary', 'all')",
            name="ck_app_auth_audit_surface",
        ),
        CheckConstraint(
            "target_surface IS NULL OR target_surface = 'native_diary'",
            name="ck_app_auth_audit_target_surface",
        ),
        CheckConstraint(
            "policy_version = 'clinician-workspace-read.v1'",
            name="ck_app_auth_audit_policy",
        ),
        CheckConstraint(
            f"decision IN ({_DECISIONS})",
            name="ck_app_auth_audit_decision",
        ),
        CheckConstraint(
            "cardinality(reason_codes) BETWEEN 1 AND 4",
            name="ck_app_auth_audit_reason_count",
        ),
        CheckConstraint(
            "data_class = 'authored_synthetic'",
            name="ck_app_auth_audit_data_class",
        ),
        Index(
            "ix_app_auth_audit_practice_order",
            "practice_ref",
            "occurred_at",
            "id",
        ),
        Index(
            "ix_app_auth_audit_correlation",
            "correlation_id",
        ),
        Index(
            "ix_app_auth_audit_session",
            "session_reference_hash",
            "occurred_at",
        ),
        Index(
            "ix_app_auth_audit_grant",
            "grant_reference_hash",
            postgresql_where=text("grant_reference_hash IS NOT NULL"),
        ),
    )


__all__ = [
    "ApplicationAuthAuditEvent",
    "ApplicationAuthExchangeGrant",
    "ApplicationAuthParentSession",
    "ApplicationAuthPrincipalGeneration",
    "ApplicationAuthSurfaceSession",
]
