"""Route-free authored-synthetic Microsoft federation admission runtime.

This module is intentionally incapable of calling Microsoft, parsing a token,
creating an application session, or reading product data. It consumes typed
synthetic evidence representing the output of a future maintained OIDC verifier
and returns at most a bounded internal principal candidate after required audit.
"""

from __future__ import annotations

import hashlib
import hmac
import re
import threading
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol, Sequence


AUTHORED_SYNTHETIC_DATA_CLASS = "authored_synthetic"
FEDERATION_PROVIDER = "microsoft_entra"
TENANT_SPECIFIC_AUTHORITY = "tenant_specific_v2"
SYNTHETIC_OIDC_VERIFIER = "synthetic_oidc_verifier"
PKCE_METHOD = "S256"
POLICY_VERSION = "microsoft-entra-single-tenant-prebound.v1"

_SYNTHETIC_REF = re.compile(r"^synthetic-[a-z0-9-]{1,64}$")


class FederationDecision(str, Enum):
    ADMIT = "admit"
    DENY = "deny"
    ERROR = "error"


class FederationAuditUnavailable(RuntimeError):
    """Raised by a required audit sink that cannot durably accept an event."""


@dataclass(frozen=True)
class FederationRuntimeConfig:
    tenant_id: str
    issuer: str
    audience: str
    enabled: bool = False
    policy_version: str = POLICY_VERSION

    def __post_init__(self) -> None:
        _require_synthetic_ref(self.tenant_id, "tenant_id")
        _require_synthetic_ref(self.audience, "audience")
        expected = (
            "https://login.microsoftonline.invalid/"
            f"{self.tenant_id}/v2.0"
        )
        if self.issuer != expected:
            raise ValueError("issuer must be the exact synthetic tenant-specific v2 issuer")
        if self.policy_version != POLICY_VERSION:
            raise ValueError("unsupported federation policy version")


@dataclass(frozen=True)
class SyntheticAuthorizationAttemptEvidence:
    exists: bool
    consumed: bool
    expires_at: datetime
    state_matches: bool
    nonce_matches: bool
    pkce_method: str
    pkce_matches: bool


@dataclass(frozen=True)
class SyntheticMicrosoftAssertionEvidence:
    data_class: str
    verifier: str
    provider: str
    authority_mode: str
    account_type: str
    signature_valid: bool
    algorithm_allowed: bool
    signing_key_trusted: bool
    issuer: str
    audience: str
    tenant_id: str
    object_id: str | None
    subject: str | None
    issued_at: datetime
    not_before: datetime
    expires_at: datetime
    display_email: str | None = None
    office_signed_in: bool = False


@dataclass(frozen=True)
class ExternalIdentityBinding:
    provider: str
    tenant_id: str
    object_id: str
    binding_ref: str
    user_ref: str
    practice_ref: str
    status: str = "active"
    version: int = 1
    data_class: str = AUTHORED_SYNTHETIC_DATA_CLASS

    def __post_init__(self) -> None:
        if self.provider != FEDERATION_PROVIDER:
            raise ValueError("unsupported federation provider")
        for field_name in (
            "tenant_id",
            "object_id",
            "binding_ref",
            "user_ref",
            "practice_ref",
        ):
            _require_synthetic_ref(getattr(self, field_name), field_name)
        if self.status not in {"active", "revoked"}:
            raise ValueError("unsupported binding status")
        if self.version < 1:
            raise ValueError("binding version must be positive")
        if self.data_class != AUTHORED_SYNTHETIC_DATA_CLASS:
            raise ValueError("only authored-synthetic bindings are accepted")


@dataclass(frozen=True)
class SyntheticInternalPrincipal:
    user_ref: str
    practice_ref: str
    user_active: bool
    practice_active: bool
    data_class: str = AUTHORED_SYNTHETIC_DATA_CLASS

    def __post_init__(self) -> None:
        _require_synthetic_ref(self.user_ref, "user_ref")
        _require_synthetic_ref(self.practice_ref, "practice_ref")
        if self.data_class != AUTHORED_SYNTHETIC_DATA_CLASS:
            raise ValueError("only authored-synthetic principals are accepted")


@dataclass(frozen=True)
class FederationPrincipalCandidate:
    binding_ref: str
    binding_version: int
    user_ref: str
    practice_ref: str
    authentication_method: str = "microsoft_entra_oidc"
    authorization_granted: bool = False
    session_created: bool = False


@dataclass(frozen=True)
class FederationAuditEvent:
    occurred_at: datetime
    correlation_ref: str
    policy_version: str
    provider: str
    decision: str
    reason_code: str
    external_reference_hmac: str
    binding_ref: str | None
    user_ref: str | None
    practice_ref: str | None
    principal_released: bool
    session_created: bool = False
    product_data_released: bool = False
    data_class: str = AUTHORED_SYNTHETIC_DATA_CLASS


@dataclass(frozen=True)
class FederationAdmissionResult:
    decision: FederationDecision
    http_status: int
    reason_code: str
    external_error: str | None
    audit_recorded: bool
    principal_candidate: FederationPrincipalCandidate | None
    provider_calls: int = 0
    session_created: bool = False
    product_data_released: bool = False


class ExternalIdentityBindingStore(Protocol):
    def find_bindings(
        self,
        *,
        provider: str,
        tenant_id: str,
        object_id: str,
    ) -> Sequence[ExternalIdentityBinding]: ...


class InternalPrincipalStore(Protocol):
    def find_principal(
        self,
        *,
        user_ref: str,
        practice_ref: str,
    ) -> SyntheticInternalPrincipal | None: ...


class FederationAuditSink(Protocol):
    def record(self, event: FederationAuditEvent) -> None: ...


class InMemoryExternalIdentityBindingStore:
    def __init__(self, bindings: Sequence[ExternalIdentityBinding] = ()) -> None:
        self._bindings = tuple(bindings)

    def find_bindings(
        self,
        *,
        provider: str,
        tenant_id: str,
        object_id: str,
    ) -> tuple[ExternalIdentityBinding, ...]:
        return tuple(
            binding
            for binding in self._bindings
            if binding.provider == provider
            and hmac.compare_digest(binding.tenant_id, tenant_id)
            and hmac.compare_digest(binding.object_id, object_id)
        )


class InMemoryInternalPrincipalStore:
    def __init__(self, principals: Sequence[SyntheticInternalPrincipal] = ()) -> None:
        self._principals = tuple(principals)

    def find_principal(
        self,
        *,
        user_ref: str,
        practice_ref: str,
    ) -> SyntheticInternalPrincipal | None:
        matches = [
            principal
            for principal in self._principals
            if principal.user_ref == user_ref
            and principal.practice_ref == practice_ref
        ]
        return matches[0] if len(matches) == 1 else None


class InMemoryFederationAuditSink:
    def __init__(self, *, available: bool = True) -> None:
        self._available = available
        self._events: list[FederationAuditEvent] = []
        self._lock = threading.Lock()

    def record(self, event: FederationAuditEvent) -> None:
        if not self._available:
            raise FederationAuditUnavailable("required federation audit unavailable")
        with self._lock:
            self._events.append(event)

    @property
    def events(self) -> tuple[FederationAuditEvent, ...]:
        with self._lock:
            return tuple(self._events)


class FederationReferenceHasher:
    def __init__(self, key: bytes, *, key_version: str = "synthetic-v1") -> None:
        if len(key) < 32:
            raise ValueError("federation reference HMAC key must be at least 32 bytes")
        _require_synthetic_ref(key_version, "key_version")
        self._key = bytes(key)
        self.key_version = key_version

    def reference(self, *, provider: str, tenant_id: str, object_id: str) -> str:
        canonical = "\x00".join((provider, tenant_id, object_id)).encode("utf-8")
        return self._digest(canonical)

    def component_reference(self, *, label: str, value: str) -> str:
        if not re.fullmatch(r"[a-z][a-z0-9_-]{0,31}", label):
            raise ValueError("HMAC component label is invalid")
        if not isinstance(value, str) or not value:
            raise ValueError("HMAC component value is required")
        canonical = "\x00".join((label, value)).encode("utf-8")
        return self._digest(canonical)

    def _digest(self, canonical: bytes) -> str:
        digest = hmac.new(self._key, canonical, hashlib.sha256).hexdigest()
        return f"hmac-sha256:{self.key_version}:{digest}"


class MicrosoftFederationAdmissionRuntime:
    """Admit one authored-synthetic, already-verified Microsoft assertion."""

    def __init__(
        self,
        *,
        config: FederationRuntimeConfig,
        binding_store: ExternalIdentityBindingStore,
        principal_store: InternalPrincipalStore,
        audit_sink: FederationAuditSink,
        reference_hasher: FederationReferenceHasher,
    ) -> None:
        self._config = config
        self._binding_store = binding_store
        self._principal_store = principal_store
        self._audit_sink = audit_sink
        self._reference_hasher = reference_hasher

    def admit(
        self,
        *,
        assertion: SyntheticMicrosoftAssertionEvidence,
        attempt: SyntheticAuthorizationAttemptEvidence,
        now: datetime,
        correlation_ref: str,
    ) -> FederationAdmissionResult:
        _require_synthetic_ref(correlation_ref, "correlation_ref")

        binding: ExternalIdentityBinding | None = None
        principal: SyntheticInternalPrincipal | None = None

        reason = self._validate_protocol(assertion=assertion, attempt=attempt, now=now)
        if reason is None:
            assert assertion.object_id is not None
            bindings = tuple(
                self._binding_store.find_bindings(
                    provider=assertion.provider,
                    tenant_id=assertion.tenant_id,
                    object_id=assertion.object_id,
                )
            )
            if len(bindings) > 1:
                reason = "binding_ambiguous"
            elif len(bindings) == 0 or bindings[0].status != "active":
                reason = "active_binding_required"
            else:
                binding = bindings[0]
                principal = self._principal_store.find_principal(
                    user_ref=binding.user_ref,
                    practice_ref=binding.practice_ref,
                )
                if (
                    principal is None
                    or principal.user_active is not True
                    or principal.practice_active is not True
                ):
                    reason = "active_internal_principal_required"

        decision = FederationDecision.ADMIT if reason is None else FederationDecision.DENY
        reason = reason or "federation_admitted"
        external_reference = self._safe_external_reference(assertion)
        candidate = (
            FederationPrincipalCandidate(
                binding_ref=binding.binding_ref,
                binding_version=binding.version,
                user_ref=principal.user_ref,
                practice_ref=principal.practice_ref,
            )
            if decision is FederationDecision.ADMIT
            and binding is not None
            and principal is not None
            else None
        )
        event = FederationAuditEvent(
            occurred_at=now,
            correlation_ref=correlation_ref,
            policy_version=self._config.policy_version,
            provider=FEDERATION_PROVIDER,
            decision=decision.value,
            reason_code=reason,
            external_reference_hmac=external_reference,
            binding_ref=binding.binding_ref if binding else None,
            user_ref=principal.user_ref if candidate and principal else None,
            practice_ref=principal.practice_ref if candidate and principal else None,
            principal_released=candidate is not None,
        )
        try:
            self._audit_sink.record(event)
        except FederationAuditUnavailable:
            return FederationAdmissionResult(
                decision=FederationDecision.ERROR,
                http_status=503,
                reason_code="required_audit_unavailable",
                external_error="authentication_temporarily_unavailable",
                audit_recorded=False,
                principal_candidate=None,
            )
        return FederationAdmissionResult(
            decision=decision,
            http_status=200 if decision is FederationDecision.ADMIT else 401,
            reason_code=reason,
            external_error=(
                None
                if decision is FederationDecision.ADMIT
                else "authentication_failed"
            ),
            audit_recorded=True,
            principal_candidate=candidate,
        )

    def _validate_protocol(
        self,
        *,
        assertion: SyntheticMicrosoftAssertionEvidence,
        attempt: SyntheticAuthorizationAttemptEvidence,
        now: datetime,
    ) -> str | None:
        if self._config.enabled is not True:
            return "federation_disabled"
        if assertion.data_class != AUTHORED_SYNTHETIC_DATA_CLASS:
            return "authored_synthetic_assertion_required"
        if assertion.verifier != SYNTHETIC_OIDC_VERIFIER:
            return "synthetic_verifier_required"
        if assertion.provider != FEDERATION_PROVIDER:
            return "provider_mismatch"
        if assertion.authority_mode != TENANT_SPECIFIC_AUTHORITY:
            return "tenant_specific_authority_required"
        if assertion.account_type not in {"organisational", "prebound_tenant_guest"}:
            return "organisational_account_required"
        if attempt.exists is not True:
            return "authorization_attempt_required"
        if attempt.consumed is True:
            return "authorization_attempt_consumed"
        if now >= attempt.expires_at:
            return "authorization_attempt_expired"
        if attempt.state_matches is not True:
            return "state_mismatch"
        if attempt.nonce_matches is not True:
            return "nonce_mismatch"
        if attempt.pkce_method != PKCE_METHOD or attempt.pkce_matches is not True:
            return "pkce_mismatch"
        if assertion.signature_valid is not True:
            return "token_signature_invalid"
        if assertion.algorithm_allowed is not True:
            return "token_algorithm_invalid"
        if assertion.signing_key_trusted is not True:
            return "signing_key_untrusted"
        if not hmac.compare_digest(assertion.issuer, self._config.issuer):
            return "issuer_mismatch"
        if not hmac.compare_digest(assertion.audience, self._config.audience):
            return "audience_mismatch"
        if not hmac.compare_digest(assertion.tenant_id, self._config.tenant_id):
            return "tenant_mismatch"
        if not assertion.object_id or not assertion.subject:
            return "immutable_subject_required"
        if not _SYNTHETIC_REF.fullmatch(assertion.object_id):
            return "immutable_subject_required"
        if not _SYNTHETIC_REF.fullmatch(assertion.subject):
            return "immutable_subject_required"
        if now >= assertion.expires_at:
            return "token_expired"
        if now < assertion.not_before:
            return "token_not_yet_valid"
        if assertion.issued_at > now:
            return "token_issued_in_future"
        return None

    def _safe_external_reference(
        self,
        assertion: SyntheticMicrosoftAssertionEvidence,
    ) -> str:
        tenant = (
            assertion.tenant_id
            if _SYNTHETIC_REF.fullmatch(assertion.tenant_id)
            else "synthetic-invalid-tenant"
        )
        object_id = (
            assertion.object_id
            if assertion.object_id and _SYNTHETIC_REF.fullmatch(assertion.object_id)
            else "synthetic-missing-object"
        )
        return self._reference_hasher.reference(
            provider=FEDERATION_PROVIDER,
            tenant_id=tenant,
            object_id=object_id,
        )


def _require_synthetic_ref(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not _SYNTHETIC_REF.fullmatch(value):
        raise ValueError(f"{field_name} must be an authored-synthetic reference")


__all__ = [
    "AUTHORED_SYNTHETIC_DATA_CLASS",
    "FEDERATION_PROVIDER",
    "PKCE_METHOD",
    "POLICY_VERSION",
    "SYNTHETIC_OIDC_VERIFIER",
    "TENANT_SPECIFIC_AUTHORITY",
    "ExternalIdentityBinding",
    "FederationAdmissionResult",
    "FederationAuditEvent",
    "FederationAuditSink",
    "FederationAuditUnavailable",
    "FederationDecision",
    "FederationPrincipalCandidate",
    "FederationReferenceHasher",
    "FederationRuntimeConfig",
    "InMemoryExternalIdentityBindingStore",
    "InMemoryFederationAuditSink",
    "InMemoryInternalPrincipalStore",
    "MicrosoftFederationAdmissionRuntime",
    "SyntheticAuthorizationAttemptEvidence",
    "SyntheticInternalPrincipal",
    "SyntheticMicrosoftAssertionEvidence",
]
