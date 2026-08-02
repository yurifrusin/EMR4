"""Provider-free HMAC-only binding resolution and admission-grant issuance.

This service accepts only the typed output of the maintained-verifier port. It
cannot call a provider, redeem a grant, create a session, or read product data.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import re
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, Protocol

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.services.application_identity_federation import (
    FEDERATION_PROVIDER,
    POLICY_VERSION,
    FederationReferenceHasher,
)
from app.services.application_identity_oidc_adapter import (
    CompletedAuthorization,
    MicrosoftOIDCAdapterConfig,
    OIDCAuthenticationFailed,
    OIDCTemporarilyUnavailable,
    ReturnTarget,
    Surface,
    VerifiedMicrosoftPrincipal,
)
from app.services.application_identity_oidc_binding_database_role import (
    require_binding_login_role,
    require_binding_resolver_call_role,
    require_grant_issuer_role,
)


ADMISSION_GRANT_TTL_SECONDS = 60
MAX_ACTIVE_ADMISSION_GRANTS = 128

_OPAQUE_GRANT = re.compile(r"^[A-Za-z0-9_-]{43}$")
_KEY_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,31}$")
_SYNTHETIC_REF = re.compile(r"^synthetic-[a-z0-9-]{1,64}$")
_HMAC_REF = re.compile(r"^hmac-sha256:synthetic-v1:[0-9a-f]{64}$")


@dataclass(frozen=True)
class OIDCAdmissionGrant:
    raw_grant: str
    expires_at: datetime
    surface: Surface
    origin: str
    return_target: ReturnTarget
    authorization_granted: bool = False
    session_created: bool = False
    product_data_released: bool = False

    def __post_init__(self) -> None:
        _decode_grant(self.raw_grant)
        if not isinstance(self.expires_at, datetime) or self.expires_at.tzinfo is None:
            raise ValueError("admission-grant expiry must be timezone-aware")
        if not isinstance(self.surface, Surface):
            raise TypeError("admission grant requires a typed surface")
        if not isinstance(self.origin, str) or not self.origin:
            raise ValueError("admission grant requires an exact origin")
        if not isinstance(self.return_target, ReturnTarget):
            raise TypeError("admission grant requires a typed return target")


class OIDCAdmissionGrantPort(Protocol):
    def issue(
        self,
        *,
        completed: CompletedAuthorization,
        now: datetime,
    ) -> OIDCAdmissionGrant:
        raise NotImplementedError


class AdmissionGrantDigestKey:
    """Versioned keyed digest that never retains a raw bearer reference."""

    def __init__(self, *, key_id: str, key: bytes) -> None:
        if not isinstance(key_id, str) or not _KEY_ID.fullmatch(key_id):
            raise ValueError("admission-grant digest key identifier is invalid")
        if not isinstance(key, bytes) or len(key) < 32:
            raise ValueError("admission-grant digest key must be at least 32 bytes")
        self.key_id = key_id
        self._key = bytes(key)

    def reference(self, raw_grant: str) -> str:
        _decode_grant(raw_grant)
        digest = hmac.new(
            self._key,
            raw_grant.encode("ascii"),
            hashlib.sha256,
        ).hexdigest()
        return f"hmac-sha256:{self.key_id}:{digest}"


@dataclass(frozen=True)
class OIDCBindingAdmissionConfiguration:
    adapter: MicrosoftOIDCAdapterConfig
    login_role: str
    resolver_call_role: str
    grant_issuer_role: str
    enabled: bool = False
    policy_version: str = POLICY_VERSION
    max_active_grants: int = MAX_ACTIVE_ADMISSION_GRANTS
    grant_ttl_seconds: int = ADMISSION_GRANT_TTL_SECONDS

    def __post_init__(self) -> None:
        if not isinstance(self.adapter, MicrosoftOIDCAdapterConfig):
            raise TypeError("binding admission requires the accepted adapter config")
        require_binding_login_role(self.login_role)
        require_binding_resolver_call_role(self.resolver_call_role)
        require_grant_issuer_role(self.grant_issuer_role)
        if self.policy_version != POLICY_VERSION:
            raise ValueError("binding admission policy version is invalid")
        if self.grant_ttl_seconds != ADMISSION_GRANT_TTL_SECONDS:
            raise ValueError("admission-grant lifetime must be exactly 60 seconds")
        if not 1 <= self.max_active_grants <= MAX_ACTIVE_ADMISSION_GRANTS:
            raise ValueError("active admission-grant capacity is outside 1..128")


class PostgresOIDCBindingAdmissionService:
    """Resolve one HMAC-only binding and atomically issue one bearer grant."""

    def __init__(
        self,
        *,
        configuration: OIDCBindingAdmissionConfiguration,
        session_factory: Callable[[], Session],
        reference_hasher: FederationReferenceHasher,
        grant_digest_key: AdmissionGrantDigestKey,
        grant_source: Callable[[], str] | None = None,
        reference_source: Callable[[str], str] | None = None,
    ) -> None:
        if not isinstance(configuration, OIDCBindingAdmissionConfiguration):
            raise TypeError("binding admission configuration is required")
        if not callable(session_factory):
            raise TypeError("binding admission session factory is required")
        if not isinstance(reference_hasher, FederationReferenceHasher):
            raise TypeError("binding admission reference hasher is required")
        if not isinstance(grant_digest_key, AdmissionGrantDigestKey):
            raise TypeError("binding admission grant digest key is required")
        self._configuration = configuration
        self._session_factory = session_factory
        self._reference_hasher = reference_hasher
        self._grant_digest_key = grant_digest_key
        self._grant_source = grant_source or _new_raw_grant
        self._reference_source = reference_source or _new_synthetic_reference

    def issue(
        self,
        *,
        completed: CompletedAuthorization,
        now: datetime,
    ) -> OIDCAdmissionGrant:
        current = _aware_utc(now)
        self._require_completed(completed)
        if self._configuration.enabled is not True:
            raise OIDCTemporarilyUnavailable("binding_admission_disabled")

        principal = completed.principal
        issuer = self._configuration.adapter.issuer
        audience = self._configuration.adapter.client_id
        issuer_hmac = self._component("issuer", issuer)
        tenant_hmac = self._component("tenant", principal.tenant_id)
        object_hmac = self._component("object", principal.object_id)
        subject_hmac = self._component("subject", principal.subject)
        audience_hmac = self._component("audience", audience)
        external_hmac = self._reference_hasher.reference(
            provider=FEDERATION_PROVIDER,
            tenant_id=principal.tenant_id,
            object_id=principal.object_id,
        )
        correlation_ref = self._new_reference("correlation")
        correlation_hmac = self._component("correlation", correlation_ref)
        resolver_operation = self._new_reference("resolve")
        grant_operation = self._new_reference("grant")
        raw_grant = self._grant_source()
        _decode_grant(raw_grant)
        grant_hmac = self._grant_digest_key.reference(raw_grant)
        expires_at = current + timedelta(seconds=ADMISSION_GRANT_TTL_SECONDS)

        resolved: dict[str, object] | None = None
        denied = False
        try:
            with self._session_factory() as session:
                with session.begin():
                    self._require_login_identity(session)
                    self._set_role(session, self._configuration.resolver_call_role)
                    resolved = session.execute(
                        text(
                            "SELECT * FROM "
                            "public.emr4_resolve_application_identity_federation_binding("
                            ":provider, :issuer_hmac, :tenant_hmac, :object_hmac, "
                            ":subject_hmac, :external_hmac, :correlation_hmac, "
                            ":operation_ref, :policy_version)"
                        ),
                        {
                            "provider": FEDERATION_PROVIDER,
                            "issuer_hmac": issuer_hmac,
                            "tenant_hmac": tenant_hmac,
                            "object_hmac": object_hmac,
                            "subject_hmac": subject_hmac,
                            "external_hmac": external_hmac,
                            "correlation_hmac": correlation_hmac,
                            "operation_ref": resolver_operation,
                            "policy_version": self._configuration.policy_version,
                        },
                    ).mappings().one_or_none()
                    if resolved is None:
                        denied = True
                    else:
                        self._set_role(session, self._configuration.grant_issuer_role)
                        self._set_grant_context(
                            session,
                            practice_ref=str(resolved["practice_ref"]),
                            external_hmac=external_hmac,
                            audience_hmac=audience_hmac,
                            correlation_hmac=correlation_hmac,
                        )
                        session.execute(
                            text(
                                "SELECT pg_catalog.pg_advisory_xact_lock("
                                "pg_catalog.hashtextextended(:practice_ref, 724661))"
                            ),
                            {"practice_ref": str(resolved["practice_ref"])},
                        )
                        active_count = int(
                            session.execute(
                                text(
                                    "SELECT count(*) FROM "
                                    "public.application_identity_federation_admission_grants "
                                    "WHERE practice_ref = :practice_ref "
                                    "AND status = 'active' AND expires_at > :now"
                                ),
                                {
                                    "practice_ref": str(resolved["practice_ref"]),
                                    "now": current,
                                },
                            ).scalar_one()
                        )
                        if active_count >= self._configuration.max_active_grants:
                            raise OIDCTemporarilyUnavailable(
                                "admission_grant_capacity_exhausted"
                            )
                        session.execute(
                            text(
                                "INSERT INTO "
                                "public.application_identity_federation_admission_grants ("
                                "grant_reference_hmac, operation_ref, binding_ref, binding_version, "
                                "user_ref, practice_ref, provider, external_reference_hmac, "
                                "audience_reference_hmac, correlation_reference_hmac, "
                                "surface, origin, return_target, policy_version, issued_at, "
                                "expires_at, status, version, consumed_at, data_class"
                                ") VALUES ("
                                ":grant_hmac, :operation_ref, :binding_ref, :binding_version, :user_ref, "
                                ":practice_ref, :provider, :external_hmac, :audience_hmac, "
                                ":correlation_hmac, :surface, :origin, :return_target, "
                                ":policy_version, :issued_at, :expires_at, 'active', 1, "
                                "NULL, 'authored_synthetic')"
                            ),
                            {
                                "grant_hmac": grant_hmac,
                                "operation_ref": grant_operation,
                                "binding_ref": str(resolved["binding_ref"]),
                                "binding_version": int(resolved["binding_version"]),
                                "user_ref": str(resolved["user_ref"]),
                                "practice_ref": str(resolved["practice_ref"]),
                                "provider": FEDERATION_PROVIDER,
                                "external_hmac": external_hmac,
                                "audience_hmac": audience_hmac,
                                "correlation_hmac": correlation_hmac,
                                "surface": completed.surface.value,
                                "origin": completed.origin,
                                "return_target": completed.return_target.value,
                                "policy_version": self._configuration.policy_version,
                                "issued_at": current,
                                "expires_at": expires_at,
                            },
                        )
        except OIDCTemporarilyUnavailable:
            raise
        except (SQLAlchemyError, KeyError, TypeError, ValueError):
            raise OIDCTemporarilyUnavailable("binding_admission_unavailable") from None

        if denied:
            raise OIDCAuthenticationFailed("active_binding_required")
        if resolved is None:
            raise OIDCTemporarilyUnavailable("binding_admission_unavailable")
        return OIDCAdmissionGrant(
            raw_grant=raw_grant,
            expires_at=expires_at,
            surface=completed.surface,
            origin=completed.origin,
            return_target=completed.return_target,
        )

    def _require_completed(self, completed: CompletedAuthorization) -> None:
        if not isinstance(completed, CompletedAuthorization):
            raise OIDCAuthenticationFailed("verified_authorization_required")
        if (
            completed.authorization_granted
            or completed.session_created
            or completed.product_data_released
        ):
            raise OIDCTemporarilyUnavailable("unexpected_downstream_authority")
        principal = completed.principal
        if not isinstance(principal, VerifiedMicrosoftPrincipal):
            raise OIDCAuthenticationFailed("verified_principal_required")
        if (
            principal.provider != FEDERATION_PROVIDER
            or principal.authorization_granted
            or principal.session_created
            or principal.tenant_id != self._configuration.adapter.tenant_id
            or not _is_canonical_guid(principal.tenant_id)
            or not _bounded_identifier(principal.object_id)
            or not _bounded_identifier(principal.subject)
        ):
            raise OIDCAuthenticationFailed("verified_principal_invalid")
        expected_origin = self._configuration.adapter.surface_origins.get(
            completed.surface
        )
        if expected_origin is None or not hmac.compare_digest(
            expected_origin,
            completed.origin,
        ):
            raise OIDCAuthenticationFailed("verified_origin_invalid")

    def _component(self, label: str, value: str) -> str:
        reference = self._reference_hasher.component_reference(
            label=label,
            value=value,
        )
        if not _HMAC_REF.fullmatch(reference):
            raise OIDCTemporarilyUnavailable("binding_reference_invalid")
        return reference

    def _new_reference(self, label: str) -> str:
        reference = self._reference_source(label)
        if not isinstance(reference, str) or not _SYNTHETIC_REF.fullmatch(reference):
            raise OIDCTemporarilyUnavailable("binding_reference_source_invalid")
        return reference

    def _require_login_identity(self, session: Session) -> None:
        observed = session.execute(
            text("SELECT session_user, current_user")
        ).one()
        expected = self._configuration.login_role
        if tuple(observed) != (expected, expected):
            raise OIDCTemporarilyUnavailable("binding_login_identity_invalid")

    @staticmethod
    def _set_role(session: Session, role_name: str) -> None:
        session.execute(text("RESET ROLE"))
        session.execute(text(f'SET LOCAL ROLE "{role_name}"'))
        observed = session.execute(text("SELECT current_user")).scalar_one()
        if observed != role_name:
            raise OIDCTemporarilyUnavailable("binding_capability_entry_failed")

    @staticmethod
    def _set_grant_context(
        session: Session,
        *,
        practice_ref: str,
        external_hmac: str,
        audience_hmac: str,
        correlation_hmac: str,
    ) -> None:
        for name, value in (
            ("emr4.practice_ref", practice_ref),
            ("emr4.federation_external_hmac", external_hmac),
            ("emr4.federation_audience_hmac", audience_hmac),
            ("emr4.federation_correlation_hmac", correlation_hmac),
        ):
            session.execute(
                text("SELECT pg_catalog.set_config(:name, :value, true)"),
                {"name": name, "value": value},
            )


def _new_raw_grant() -> str:
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode("ascii")


def _decode_grant(value: str) -> bytes:
    if not isinstance(value, str) or not _OPAQUE_GRANT.fullmatch(value):
        raise ValueError("admission grant bearer is invalid")
    try:
        decoded = base64.urlsafe_b64decode(value + "=")
    except ValueError:
        raise ValueError("admission grant bearer is invalid") from None
    if len(decoded) != 32:
        raise ValueError("admission grant bearer must contain exactly 256 bits")
    return decoded


def _new_synthetic_reference(label: str) -> str:
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,15}", label):
        raise ValueError("synthetic reference label is invalid")
    return f"synthetic-{label}-{secrets.token_hex(12)}"


def _is_canonical_guid(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return str(uuid.UUID(value)) == value
    except (ValueError, AttributeError):
        return False


def _bounded_identifier(value: object) -> bool:
    return isinstance(value, str) and 1 <= len(value.encode("utf-8")) <= 256


def _aware_utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError("binding admission clock must be timezone-aware")
    return value.astimezone(timezone.utc)


__all__ = [
    "ADMISSION_GRANT_TTL_SECONDS",
    "MAX_ACTIVE_ADMISSION_GRANTS",
    "AdmissionGrantDigestKey",
    "OIDCAdmissionGrant",
    "OIDCAdmissionGrantPort",
    "OIDCBindingAdmissionConfiguration",
    "PostgresOIDCBindingAdmissionService",
]
