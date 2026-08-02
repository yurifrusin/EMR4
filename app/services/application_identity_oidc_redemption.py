"""Provider-free atomic OIDC admission-grant redemption.

This module can consume only an authored-synthetic grant and create only the
accepted authored-synthetic application session. It has no provider or product
client and is dormant until explicitly injected into the default-off router.
"""

from __future__ import annotations

import hmac
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Mapping

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.services.application_auth_role_runtime import (
    RoleScopedPostgresApplicationAuthRuntime,
)
from app.services.application_auth_runtime import (
    SURFACE_AUDIENCE,
    Surface as ApplicationSurface,
    SyntheticPrincipal,
)
from app.services.application_auth_transport import PREAUTH_CSRF_MAX_AGE_SECONDS
from app.services.application_identity_federation import (
    POLICY_VERSION,
    FederationReferenceHasher,
)
from app.services.application_identity_oidc_adapter import (
    MicrosoftOIDCAdapterConfig,
    OIDCAuthenticationFailed,
    OIDCTemporarilyUnavailable,
    Surface,
)
from app.services.application_identity_oidc_admission_grant import (
    AdmissionGrantDigestKey,
)
from app.services.application_identity_oidc_redemption_database_role import (
    REDEMPTION_FUNCTION,
    require_redemption_call_role,
    require_redemption_login_role,
)
from app.services.application_identity_oidc_transport import (
    OIDCTransportRequestDenied,
)


_CSRF = re.compile(r"^[A-Za-z0-9._~-]{43,128}$")
_HMAC_REF = re.compile(r"^hmac-sha256:synthetic-v1:[0-9a-f]{64}$")
_SYNTHETIC_REF = re.compile(r"^synthetic-[a-z0-9-]{1,64}$")


class OIDCAdmissionGrantConflict(RuntimeError):
    """The exact grant already committed its one allowed redemption."""


@dataclass(frozen=True)
class OIDCAdmissionRedemptionConfiguration:
    adapter: MicrosoftOIDCAdapterConfig
    login_role: str
    call_role: str
    enabled: bool = False
    policy_version: str = POLICY_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.adapter, MicrosoftOIDCAdapterConfig):
            raise TypeError("redemption requires the accepted adapter config")
        require_redemption_login_role(self.login_role)
        require_redemption_call_role(self.call_role)
        if self.policy_version != POLICY_VERSION:
            raise ValueError("redemption policy version is invalid")


@dataclass(frozen=True)
class RedeemedOIDCApplicationSession:
    surface_session_value: str
    surface: Surface
    parent_expires_at: datetime
    surface_idle_expires_at: datetime


@dataclass(frozen=True)
class OIDCAdmissionRedemptionTransportResult:
    surface_session_value: str
    csrf_token: str
    surface: Surface
    parent_expires_at: datetime
    surface_idle_expires_at: datetime


class PostgresOIDCAdmissionGrantRedemptionService:
    """Consume one grant and create one app session in the same transaction."""

    def __init__(
        self,
        *,
        configuration: OIDCAdmissionRedemptionConfiguration,
        session_factory: Callable[[], Session],
        reference_hasher: FederationReferenceHasher,
        grant_digest_key: AdmissionGrantDigestKey,
        application_auth_runtime: RoleScopedPostgresApplicationAuthRuntime,
        clock: Callable[[], datetime] | None = None,
        reference_source: Callable[[str], str] | None = None,
    ) -> None:
        if not isinstance(configuration, OIDCAdmissionRedemptionConfiguration):
            raise TypeError("redemption configuration is required")
        if not callable(session_factory):
            raise TypeError("redemption session factory is required")
        if not isinstance(reference_hasher, FederationReferenceHasher):
            raise TypeError("redemption reference hasher is required")
        if not isinstance(grant_digest_key, AdmissionGrantDigestKey):
            raise TypeError("redemption grant digest key is required")
        if not isinstance(
            application_auth_runtime,
            RoleScopedPostgresApplicationAuthRuntime,
        ):
            raise TypeError("accepted role-scoped application-auth runtime required")
        self._configuration = configuration
        self._session_factory = session_factory
        self._reference_hasher = reference_hasher
        self._grant_digest_key = grant_digest_key
        self._application_auth_runtime = application_auth_runtime
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._reference_source = reference_source or _new_synthetic_reference

    def redeem(
        self,
        *,
        raw_grant: str,
        surface: Surface,
        origin: str,
    ) -> RedeemedOIDCApplicationSession:
        if self._configuration.enabled is not True:
            raise OIDCTemporarilyUnavailable("admission_redemption_disabled")
        try:
            grant_hmac = self._grant_digest_key.reference(raw_grant)
        except ValueError:
            raise OIDCAuthenticationFailed("admission_grant_invalid") from None
        surface = Surface(surface)
        expected_origin = self._configuration.adapter.surface_origins[surface]
        if not hmac.compare_digest(expected_origin, origin):
            raise OIDCAuthenticationFailed("admission_grant_origin_invalid")
        audience_hmac = self._reference_hasher.component_reference(
            label="audience",
            value=self._configuration.adapter.client_id,
        )
        if not _HMAC_REF.fullmatch(audience_hmac):
            raise OIDCTemporarilyUnavailable("redemption_audience_reference_invalid")
        operation_ref = self._new_reference("redeem")
        correlation_id = f"correlation-{secrets.token_hex(12)}"
        now = _aware_utc(self._clock())

        rejected = False
        conflict = False
        created = None
        try:
            with self._session_factory() as db:
                with db.begin():
                    self._require_runtime_identity(db)
                    row = db.execute(
                        text(
                            "SELECT redemption_decision, user_ref, practice_ref, "
                            "current_backend_role, practitioner_ref, truth_version "
                            "FROM "
                            "public.emr4_redeem_application_identity_federation_grant("
                            ":grant_hmac, :surface, :origin, :audience_hmac, "
                            ":policy_version, :operation_ref, :occurred_at)"
                        ),
                        {
                            "grant_hmac": grant_hmac,
                            "surface": surface.value,
                            "origin": origin,
                            "audience_hmac": audience_hmac,
                            "policy_version": self._configuration.policy_version,
                            "operation_ref": operation_ref,
                            "occurred_at": now,
                        },
                    ).one_or_none()
                    if row is None or row.redemption_decision == "rejected":
                        rejected = True
                    elif row.redemption_decision == "already_consumed":
                        conflict = True
                    elif row.redemption_decision != "admitted":
                        raise OIDCTemporarilyUnavailable(
                            "admission_redemption_decision_invalid"
                        )
                    else:
                        principal = SyntheticPrincipal(
                            user_id=row.user_ref,
                            practice_id=row.practice_ref,
                            current_backend_role=row.current_backend_role,
                            practitioner_id=row.practitioner_ref,
                        )
                        created = self._application_auth_runtime.create_session_in_transaction(
                            db,
                            principal=principal,
                            surface=ApplicationSurface(surface.value),
                            origin=origin,
                            audience=SURFACE_AUDIENCE,
                            correlation_id=correlation_id,
                        )
        except OIDCTemporarilyUnavailable:
            raise
        except (SQLAlchemyError, RuntimeError, ValueError, TypeError):
            raise OIDCTemporarilyUnavailable(
                "admission_redemption_transaction_failed"
            ) from None

        if conflict:
            raise OIDCAdmissionGrantConflict()
        if rejected or created is None:
            raise OIDCAuthenticationFailed("admission_grant_rejected")
        return RedeemedOIDCApplicationSession(
            surface_session_value=created.surface_session_value,
            surface=surface,
            parent_expires_at=created.parent_expires_at,
            surface_idle_expires_at=created.surface_idle_expires_at,
        )

    def _require_runtime_identity(self, db: Session) -> None:
        observed = tuple(
            db.execute(text("SELECT session_user, current_user")).one()
        )
        expected = (
            self._configuration.login_role,
            self._configuration.call_role,
        )
        if observed != expected:
            raise OIDCTemporarilyUnavailable("redemption_runtime_identity_invalid")

    def _new_reference(self, label: str) -> str:
        reference = self._reference_source(label)
        if not isinstance(reference, str) or not _SYNTHETIC_REF.fullmatch(reference):
            raise OIDCTemporarilyUnavailable("redemption_reference_source_invalid")
        return reference


class OIDCAdmissionGrantRedemptionTransport:
    """Exact-origin and pre-auth CSRF wrapper around the redemption service."""

    def __init__(
        self,
        *,
        service: PostgresOIDCAdmissionGrantRedemptionService,
        surface_origins: Mapping[Surface, str],
        csrf_token_source: Callable[[], str] | None = None,
    ) -> None:
        if not isinstance(service, PostgresOIDCAdmissionGrantRedemptionService):
            raise TypeError("redemption service is required")
        origins = {Surface(key): value for key, value in surface_origins.items()}
        if set(origins) != set(Surface):
            raise ValueError("all three redemption origins are required")
        self._service = service
        self._surface_origins = origins
        self._csrf_token_source = csrf_token_source or (
            lambda: f"csrf.{secrets.token_urlsafe(32)}"
        )

    def require_origin(self, surface: Surface, origin: str | None) -> str:
        expected = self._surface_origins.get(Surface(surface))
        if not isinstance(origin, str) or expected is None or not hmac.compare_digest(
            origin,
            expected,
        ):
            raise OIDCTransportRequestDenied()
        return origin

    @staticmethod
    def require_csrf(cookie_value: str | None, header_value: str | None) -> None:
        cookie = cookie_value if isinstance(cookie_value, str) else ""
        header = header_value if isinstance(header_value, str) else ""
        if not (
            _CSRF.fullmatch(cookie)
            and _CSRF.fullmatch(header)
            and hmac.compare_digest(cookie, header)
        ):
            raise OIDCTransportRequestDenied()

    def redeem(
        self,
        *,
        raw_grant: str,
        surface: Surface,
        origin: str,
    ) -> OIDCAdmissionRedemptionTransportResult:
        csrf_token = self._csrf_token_source()
        if not isinstance(csrf_token, str) or not _CSRF.fullmatch(csrf_token):
            raise OIDCTemporarilyUnavailable("redemption_csrf_source_invalid")
        redeemed = self._service.redeem(
            raw_grant=raw_grant,
            surface=surface,
            origin=origin,
        )
        return OIDCAdmissionRedemptionTransportResult(
            surface_session_value=redeemed.surface_session_value,
            csrf_token=csrf_token,
            surface=redeemed.surface,
            parent_expires_at=redeemed.parent_expires_at,
            surface_idle_expires_at=redeemed.surface_idle_expires_at,
        )


def _aware_utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise OIDCTemporarilyUnavailable("redemption_clock_invalid")
    return value.astimezone(timezone.utc)


def _new_synthetic_reference(label: str) -> str:
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,15}", label):
        raise ValueError("synthetic reference label is invalid")
    return f"synthetic-{label}-{secrets.token_hex(12)}"


__all__ = [
    "OIDCAdmissionGrantConflict",
    "OIDCAdmissionGrantRedemptionTransport",
    "OIDCAdmissionRedemptionConfiguration",
    "OIDCAdmissionRedemptionTransportResult",
    "PREAUTH_CSRF_MAX_AGE_SECONDS",
    "PostgresOIDCAdmissionGrantRedemptionService",
    "RedeemedOIDCApplicationSession",
    "REDEMPTION_FUNCTION",
]
