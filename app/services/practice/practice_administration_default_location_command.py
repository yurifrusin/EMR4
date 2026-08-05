"""B4.1 Davida default-location command runtime service.

Provider-free, backend-owned, human-confirmed command semantics for one
practitioner default-location change. Davida is proposal provenance only. The
authenticated human ``Admin``/``PracticeOwner`` is the sole confirmer; the
server maps ``UserRole.Admin -> practice_manager`` and
``UserRole.PracticeOwner -> practice_owner`` with no aliases before comparing
the non-authoritative body assertion. Every durable row stores hashes and
bounded codes only; raw idempotency keys, session credentials, provider output,
patient data and free text are never stored.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.orm import Session

from app.config import settings
from app.models.practice_administration_commands import (
    PracticeAdministrationAuditEvent,
    PracticeAdministrationCommandIdempotency,
    PracticeAdministrationConfirmationEvidence,
    PracticeAdministrationOutboxEvent,
)
from app.models.tenancy import PracticeLocation, Practitioner, User, UserRole
from app.schemas.practice_administration_default_location_command import (
    CHANGED_PATH,
    COMMIT_RECEIPT_SCHEMA_VERSION,
    CONFIRMATION_RESULT_SCHEMA_VERSION,
    ConfirmationEvidenceEnvelope,
    ConfirmationVerification,
    DefaultLocationChange,
    DefaultLocationCommitReceipt,
    DefaultLocationConfirmationCommand,
    DefaultLocationConfirmationResult,
    DefaultLocationEvidenceRequest,
    DefaultLocationProposalEnvelope,
    DefaultLocationProposalRequest,
    EVIDENCE_ENVELOPE_SCHEMA_VERSION,
    MAXIMUM_LIFETIME_SECONDS,
    OPERATION_RESULT,
    PROPOSAL_ENVELOPE_SCHEMA_VERSION,
    SHA256_PATTERN,
)

B4_ROUTE_FAMILY = "practice_administration_default_location"
B4_OPERATION_ID_PROPOSE = "proposePractitionerDefaultLocationChange"
B4_OPERATION_ID_EVIDENCE = "issuePractitionerDefaultLocationConfirmationEvidence"
B4_OPERATION_ID_CONFIRM = "confirmPractitionerDefaultLocationChange"
SIGNED_PROPOSAL_SCHEMA_VERSION = (
    "emr4.practice_administration.default_location.signed_proposal.v1"
)
SIGNED_PROPOSAL_PREFIX = "dlp1"
MIN_B4_SECRET_LENGTH = 16
PROPOSAL_LIFETIME = timedelta(seconds=MAXIMUM_LIFETIME_SECONDS)
EVIDENCE_LIFETIME = timedelta(seconds=MAXIMUM_LIFETIME_SECONDS)
EVENT_TYPE = "practice.practitioner_default_location_changed"
EVENT_SCHEMA_VERSION = "practice.practitioner_default_location_changed.v1"
EVENT_SOURCE_SYSTEM = "emr4-practice-administration"
REASON_CODES = ["practitioner_default_location_changed"]
PERMITTED_CONFIRMER_ROLES = ("practice_manager", "practice_owner")

SERVER_ROLE_TO_RUNTIME_ROLE = {
    UserRole.Admin: "practice_manager",
    UserRole.PracticeOwner: "practice_owner",
}


class B4CommandError(RuntimeError):
    """Closed-vocabulary command rejection carrying an HTTP status code."""

    def __init__(
        self,
        reason_code: str,
        *,
        status_code: int = 409,
        retryable: bool = False,
    ) -> None:
        super().__init__(reason_code)
        self.reason_code = reason_code
        self.status_code = status_code
        self.retryable = retryable


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def _parse_dt(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def hash_idempotency_key(raw_key: str, secret: bytes) -> str:
    return hmac.new(secret, raw_key.encode("utf-8"), hashlib.sha256).hexdigest()


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def _practice_ref(practice_id: UUID) -> str:
    return f"practice_{practice_id.hex}"


def _actor_ref(user_id: UUID) -> str:
    return f"user_{user_id.hex}"


def _resource_ref(
    *,
    kind: str,
    practice_id: UUID,
    resource_id: UUID,
    secret: bytes,
) -> str:
    """Return a stable, non-positional opaque reference for one resource."""
    digest = hmac.new(
        secret,
        f"b4-resource-ref:v1:{practice_id}:{kind}:{resource_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:24]
    prefix = "prac" if kind == "practitioner" else "loc"
    return f"{prefix}_synth_{digest}"


def _practice_allowlist() -> frozenset[str]:
    raw = settings.b4_default_location_command_synthetic_practice_ids or ""
    return frozenset(part.strip() for part in raw.split(",") if part.strip())


def _gate_allows_or_raise(practice_id: UUID) -> None:
    if not settings.b4_default_location_command_runtime_enabled:
        raise B4CommandError("not_authorized", status_code=403)
    if str(practice_id) not in _practice_allowlist():
        raise B4CommandError("not_authorized", status_code=403)
    secret = settings.b4_default_location_command_secret or ""
    if len(secret) < MIN_B4_SECRET_LENGTH:
        raise B4CommandError("not_authorized", status_code=403)


def _b4_secret() -> bytes:
    raw = settings.b4_default_location_command_secret or ""
    if len(raw) < MIN_B4_SECRET_LENGTH:
        raise B4CommandError("not_authorized", status_code=403)
    return raw.encode("utf-8")


def _runtime_role(user_role: UserRole) -> str | None:
    return SERVER_ROLE_TO_RUNTIME_ROLE.get(user_role)


def _assert_session_binding(
    *,
    current_user: User,
    binding: Any,
    correlation_id: str,
) -> str:
    """Return the server-mapped runtime role after exact session assertion."""
    runtime_role = _runtime_role(current_user.role)
    if runtime_role is None:
        raise B4CommandError("confirmer_not_authorized", status_code=403)
    expected_practice_ref = _practice_ref(current_user.practice_id)
    expected_actor_ref = _actor_ref(current_user.id)
    if (
        binding.practice_ref != expected_practice_ref
        or binding.actor.actor_type != "human_user"
        or binding.actor.actor_ref != expected_actor_ref
        or binding.actor.role != runtime_role
        or binding.correlation_id != correlation_id
    ):
        raise B4CommandError("practice_scope_mismatch", status_code=403)
    if binding.source_surface not in (
        "practice_administration_console",
        "command_centre",
    ):
        raise B4CommandError("invalid_envelope", status_code=422)
    if binding.delegated_agent is not None and binding.delegated_agent != "davida":
        raise B4CommandError("invalid_envelope", status_code=422)
    return runtime_role


@dataclass(frozen=True)
class _PracticeResourceRegistry:
    practice_ref: str
    practitioner_by_ref: dict[str, UUID]
    location_by_ref: dict[str, UUID]
    ref_by_practitioner: dict[UUID, str]
    ref_by_location: dict[UUID, str]


def _build_registry(
    db: Session,
    *,
    practice_id: UUID,
    practice_ref: str,
    secret: bytes,
) -> _PracticeResourceRegistry:
    practitioners = (
        db.query(Practitioner)
        .filter(
            Practitioner.practice_id == practice_id,
            Practitioner.is_active.is_(True),
        )
        .order_by(Practitioner.id.asc())
        .all()
    )
    locations = (
        db.query(PracticeLocation)
        .filter(
            PracticeLocation.practice_id == practice_id,
            PracticeLocation.is_active.is_(True),
        )
        .order_by(PracticeLocation.id.asc())
        .all()
    )
    practitioner_by_ref: dict[str, UUID] = {}
    ref_by_practitioner: dict[UUID, str] = {}
    for practitioner in practitioners:
        ref = _resource_ref(
            kind="practitioner",
            practice_id=practice_id,
            resource_id=practitioner.id,
            secret=secret,
        )
        practitioner_by_ref[ref] = practitioner.id
        ref_by_practitioner[practitioner.id] = ref
    location_by_ref: dict[str, UUID] = {}
    ref_by_location: dict[UUID, str] = {}
    for location in locations:
        ref = _resource_ref(
            kind="location",
            practice_id=practice_id,
            resource_id=location.id,
            secret=secret,
        )
        location_by_ref[ref] = location.id
        ref_by_location[location.id] = ref
    return _PracticeResourceRegistry(
        practice_ref,
        practitioner_by_ref,
        location_by_ref,
        ref_by_practitioner,
        ref_by_location,
    )


def _resolve_practitioner(reg: _PracticeResourceRegistry, ref: str) -> UUID:
    resolved = reg.practitioner_by_ref.get(ref)
    if resolved is None:
        raise B4CommandError("resource_scope_mismatch", status_code=403)
    return resolved


def _resolve_location(reg: _PracticeResourceRegistry, ref: str) -> UUID:
    resolved = reg.location_by_ref.get(ref)
    if resolved is None:
        raise B4CommandError("resource_scope_mismatch", status_code=403)
    return resolved


def _compute_before_state_hash(
    *,
    practice_ref: str,
    practitioner_ref: str,
    default_location_ref: str | None,
    aggregate_version: int,
) -> str:
    return _sha256(
        {
            "practice_ref": practice_ref,
            "practitioner_ref": practitioner_ref,
            "default_location_ref": default_location_ref,
            "aggregate_version": aggregate_version,
        }
    )


def _sign_proposal(payload: dict[str, Any], secret: bytes) -> str:
    canonical = _canonical(payload).encode("utf-8")
    signature = hmac.new(secret, canonical, hashlib.sha256).digest()
    return f"{SIGNED_PROPOSAL_PREFIX}.{_b64url(canonical)}.{_b64url(signature)}"


def _verify_proposal(
    proposal_id: str,
    secret: bytes,
    now: datetime,
) -> dict[str, Any]:
    parts = proposal_id.split(".")
    if len(parts) != 3 or parts[0] != SIGNED_PROPOSAL_PREFIX:
        raise B4CommandError("proposal_hash_mismatch", status_code=409)
    try:
        canonical_bytes = _b64url_decode(parts[1])
        signature = _b64url_decode(parts[2])
        if _b64url(canonical_bytes) != parts[1] or _b64url(signature) != parts[2]:
            raise ValueError("non-canonical base64url")
        canonical = canonical_bytes.decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        raise B4CommandError("proposal_hash_mismatch", status_code=409)
    expected = hmac.new(secret, canonical.encode("utf-8"), hashlib.sha256).digest()
    if not hmac.compare_digest(expected, signature):
        raise B4CommandError("proposal_hash_mismatch", status_code=409)
    try:
        payload = json.loads(canonical)
    except json.JSONDecodeError:
        raise B4CommandError("proposal_hash_mismatch", status_code=409)
    if not isinstance(payload, dict):
        raise B4CommandError("proposal_hash_mismatch", status_code=409)
    if payload.get("schema_version") != SIGNED_PROPOSAL_SCHEMA_VERSION:
        raise B4CommandError("proposal_hash_mismatch", status_code=409)
    proposal_hash = payload.get("proposal_hash")
    if not isinstance(proposal_hash, str) or not re.fullmatch(
        SHA256_PATTERN, proposal_hash
    ):
        raise B4CommandError("proposal_hash_mismatch", status_code=409)
    material = {key: value for key, value in payload.items() if key != "proposal_hash"}
    if _sha256(material) != proposal_hash:
        raise B4CommandError("proposal_hash_mismatch", status_code=409)
    expires_at = _parse_dt(payload.get("expires_at"))
    if expires_at is None:
        raise B4CommandError("proposal_hash_mismatch", status_code=409)
    if now >= expires_at:
        raise B4CommandError("proposal_expired", status_code=410)
    return payload


def _assert_proposal_matches_request(
    payload: dict[str, Any],
    *,
    practice_ref: str,
    actor_ref: str,
    runtime_role: str,
    correlation_id: str,
    request_proposal_id: str,
    request_proposal_hash: str,
    request_proposal_expires_at: datetime,
    practitioner_ref: str,
    requested_location_ref: str,
    expected_aggregate_version: int,
) -> None:
    del request_proposal_id
    if payload.get("practice_ref") != practice_ref:
        raise B4CommandError("practice_scope_mismatch", status_code=403)
    if payload.get("actor_ref") != actor_ref:
        raise B4CommandError("confirmer_not_authorized", status_code=403)
    if payload.get("role") != runtime_role:
        raise B4CommandError("confirmer_not_authorized", status_code=403)
    if payload.get("correlation_id") != correlation_id:
        raise B4CommandError("practice_scope_mismatch", status_code=403)
    if payload.get("practitioner_ref") != practitioner_ref:
        raise B4CommandError("proposal_hash_mismatch", status_code=409)
    if payload.get("requested_default_location_ref") != requested_location_ref:
        raise B4CommandError("proposal_hash_mismatch", status_code=409)
    if payload.get("expected_aggregate_version") != expected_aggregate_version:
        raise B4CommandError("aggregate_version_mismatch", status_code=409)
    if payload.get("proposal_hash") != request_proposal_hash:
        raise B4CommandError("proposal_hash_mismatch", status_code=409)
    if payload.get("expires_at") != _iso(request_proposal_expires_at):
        raise B4CommandError("proposal_hash_mismatch", status_code=409)


def generate_default_location_proposal(
    *,
    db: Session,
    current_user: User,
    request: DefaultLocationProposalRequest,
    correlation_id: str,
    now: datetime | None = None,
) -> DefaultLocationProposalEnvelope:
    """Recompute one non-mutating signed proposal from current practice truth."""
    _gate_allows_or_raise(current_user.practice_id)
    runtime_role = _assert_session_binding(
        current_user=current_user,
        binding=request.binding,
        correlation_id=correlation_id,
    )
    now = now or _now()
    practice_ref = _practice_ref(current_user.practice_id)
    actor_ref = _actor_ref(current_user.id)
    secret = _b4_secret()
    registry = _build_registry(
        db,
        practice_id=current_user.practice_id,
        practice_ref=practice_ref,
        secret=secret,
    )
    practitioner_uuid = _resolve_practitioner(registry, request.practitioner_ref)
    location_uuid = _resolve_location(registry, request.requested_default_location_ref)

    practitioner = (
        db.query(Practitioner)
        .filter(
            Practitioner.practice_id == current_user.practice_id,
            Practitioner.id == practitioner_uuid,
            Practitioner.is_active.is_(True),
        )
        .first()
    )
    if practitioner is None:
        raise B4CommandError("resource_scope_mismatch", status_code=403)
    location = (
        db.query(PracticeLocation)
        .filter(
            PracticeLocation.practice_id == current_user.practice_id,
            PracticeLocation.id == location_uuid,
            PracticeLocation.is_active.is_(True),
        )
        .first()
    )
    if location is None:
        raise B4CommandError("location_not_active", status_code=409)

    current_version = int(practitioner.aggregate_version or 0)
    if request.expected_aggregate_version != current_version:
        raise B4CommandError("aggregate_version_mismatch", status_code=409)
    if practitioner.default_location_id == location_uuid:
        raise B4CommandError("no_change", status_code=409)

    before_location_ref: str | None = None
    if practitioner.default_location_id is not None:
        before_location_ref = registry.ref_by_location.get(
            practitioner.default_location_id
        )
        if before_location_ref is None:
            raise B4CommandError("before_state_conflict", status_code=409)

    dry_run_expires_at = _parse_dt(request.dry_run_expires_at)
    if dry_run_expires_at is None:
        raise B4CommandError("invalid_envelope", status_code=422)
    if dry_run_expires_at <= now:
        raise B4CommandError("proposal_expired", status_code=410)
    expires_at = min(now + PROPOSAL_LIFETIME, dry_run_expires_at)
    if expires_at <= now:
        raise B4CommandError("proposal_expired", status_code=410)

    before_state_hash = _compute_before_state_hash(
        practice_ref=practice_ref,
        practitioner_ref=request.practitioner_ref,
        default_location_ref=before_location_ref,
        aggregate_version=current_version,
    )

    proposal_material: dict[str, Any] = {
        "schema_version": SIGNED_PROPOSAL_SCHEMA_VERSION,
        "practice_ref": practice_ref,
        "practitioner_ref": request.practitioner_ref,
        "requested_default_location_ref": request.requested_default_location_ref,
        "expected_aggregate_version": current_version,
        "before_state_hash": before_state_hash,
        "dry_run_proposal_hash": request.dry_run_proposal_hash,
        "dry_run_context_revision": request.dry_run_context_revision,
        "dry_run_expires_at": _iso(dry_run_expires_at),
        "correlation_id": correlation_id,
        "actor_ref": actor_ref,
        "role": runtime_role,
        "generated_at": _iso(now),
        "expires_at": _iso(expires_at),
        "maximum_lifetime_seconds": MAXIMUM_LIFETIME_SECONDS,
        "proposal_nonce": secrets.token_hex(16),
    }
    proposal_hash = _sha256(proposal_material)
    signed_payload = dict(proposal_material)
    signed_payload["proposal_hash"] = proposal_hash
    proposal_id = _sign_proposal(signed_payload, secret)

    return DefaultLocationProposalEnvelope(
        schema_version=PROPOSAL_ENVELOPE_SCHEMA_VERSION,
        status="proposal_only",
        proposal_id=proposal_id,
        practice_ref=practice_ref,
        practitioner_ref=request.practitioner_ref,
        operation=OPERATION_RESULT,
        expected_aggregate_version=current_version,
        change=DefaultLocationChange(
            changed_path=CHANGED_PATH,
            before_location_ref=before_location_ref,
            after_location_ref=request.requested_default_location_ref,
        ),
        before_state_hash=before_state_hash,
        dry_run_proposal_hash=request.dry_run_proposal_hash,
        proposal_hash=proposal_hash,
        generated_at=now,
        expires_at=expires_at,
        maximum_lifetime_seconds=MAXIMUM_LIFETIME_SECONDS,
        human_confirmation_required=True,
        permitted_confirmer_roles=PERMITTED_CONFIRMER_ROLES,
        applies_change=False,
        davida_can_confirm=False,
        warnings=[],
        blocks=[],
    )


def _claim_evidence(
    db: Session,
    *,
    practice_id: UUID,
    actor_user_id: UUID,
    actor_role: str,
    proposal_id: str,
    proposal_hash: str,
    canonical_request_hash: str,
    before_state_hash: str,
    practitioner_id: UUID,
    requested_location_id: UUID,
    expected_aggregate_version: int,
    correlation_id: str,
    idempotency_key_hash: str,
    nonce: str,
    now: datetime,
) -> PracticeAdministrationConfirmationEvidence:
    inserted_id = db.execute(
        postgresql_insert(PracticeAdministrationConfirmationEvidence)
        .values(
            id=uuid.uuid4(),
            practice_id=practice_id,
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            proposal_id=proposal_id,
            proposal_hash=proposal_hash,
            canonical_request_hash=canonical_request_hash,
            before_state_hash=before_state_hash,
            practitioner_id=practitioner_id,
            requested_location_id=requested_location_id,
            expected_aggregate_version=expected_aggregate_version,
            correlation_id=correlation_id,
            idempotency_key_hash=idempotency_key_hash,
            nonce=nonce,
            state="live",
            issued_at=now,
            expires_at=now + EVIDENCE_LIFETIME,
        )
        .on_conflict_do_nothing(
            constraint="uq_b4_evidence_practice_actor_proposal"
        )
        .returning(PracticeAdministrationConfirmationEvidence.id)
    ).scalar_one_or_none()
    if inserted_id is not None:
        return (
            db.query(PracticeAdministrationConfirmationEvidence)
            .filter(PracticeAdministrationConfirmationEvidence.id == inserted_id)
            .one()
        )
    record = (
        db.query(PracticeAdministrationConfirmationEvidence)
        .filter(
            PracticeAdministrationConfirmationEvidence.practice_id == practice_id,
            PracticeAdministrationConfirmationEvidence.actor_user_id == actor_user_id,
            PracticeAdministrationConfirmationEvidence.proposal_hash == proposal_hash,
        )
        .with_for_update()
        .one()
    )
    if record.canonical_request_hash != canonical_request_hash:
        raise B4CommandError("idempotency_conflict", status_code=409)
    if record.state == "consumed":
        raise B4CommandError("confirmation_replay_rejected", status_code=409)
    if record.expires_at <= now:
        raise B4CommandError("confirmation_evidence_expired", status_code=410)
    return record


def issue_confirmation_evidence(
    *,
    db: Session,
    current_user: User,
    proposal_id: str,
    request: DefaultLocationEvidenceRequest,
    idempotency_key: str,
    correlation_id: str,
    now: datetime | None = None,
) -> ConfirmationEvidenceEnvelope:
    """Record a current human attestation and return one opaque server-held ref."""
    _gate_allows_or_raise(current_user.practice_id)
    runtime_role = _assert_session_binding(
        current_user=current_user,
        binding=request.binding,
        correlation_id=correlation_id,
    )
    now = now or _now()
    if request.proposal_id != proposal_id:
        raise B4CommandError("proposal_hash_mismatch", status_code=409)
    secret = _b4_secret()
    payload = _verify_proposal(proposal_id, secret, now)
    practice_ref = _practice_ref(current_user.practice_id)
    actor_ref = _actor_ref(current_user.id)
    _assert_proposal_matches_request(
        payload,
        practice_ref=practice_ref,
        actor_ref=actor_ref,
        runtime_role=runtime_role,
        correlation_id=correlation_id,
        request_proposal_id=request.proposal_id,
        request_proposal_hash=request.proposal_hash,
        request_proposal_expires_at=request.proposal_expires_at,
        practitioner_ref=request.practitioner_ref,
        requested_location_ref=request.requested_default_location_ref,
        expected_aggregate_version=request.expected_aggregate_version,
    )

    existing_evidence = (
        db.query(PracticeAdministrationConfirmationEvidence)
        .filter(
            PracticeAdministrationConfirmationEvidence.practice_id
            == current_user.practice_id,
            PracticeAdministrationConfirmationEvidence.actor_user_id
            == current_user.id,
            PracticeAdministrationConfirmationEvidence.proposal_hash
            == request.proposal_hash,
        )
        .first()
    )
    if existing_evidence is not None and existing_evidence.state == "consumed":
        raise B4CommandError("confirmation_replay_rejected", status_code=409)

    registry = _build_registry(
        db,
        practice_id=current_user.practice_id,
        practice_ref=practice_ref,
        secret=secret,
    )
    practitioner_uuid = _resolve_practitioner(registry, request.practitioner_ref)
    location_uuid = _resolve_location(registry, request.requested_default_location_ref)
    practitioner = (
        db.query(Practitioner)
        .filter(
            Practitioner.practice_id == current_user.practice_id,
            Practitioner.id == practitioner_uuid,
            Practitioner.is_active.is_(True),
        )
        .first()
    )
    if practitioner is None:
        raise B4CommandError("resource_scope_mismatch", status_code=403)
    location = (
        db.query(PracticeLocation)
        .filter(
            PracticeLocation.practice_id == current_user.practice_id,
            PracticeLocation.id == location_uuid,
            PracticeLocation.is_active.is_(True),
        )
        .first()
    )
    if location is None:
        raise B4CommandError("location_not_active", status_code=409)

    current_version = int(practitioner.aggregate_version or 0)
    if request.expected_aggregate_version != current_version:
        raise B4CommandError("aggregate_version_mismatch", status_code=409)
    if practitioner.default_location_id == location_uuid:
        raise B4CommandError("no_change", status_code=409)

    before_location_ref: str | None = None
    if practitioner.default_location_id is not None:
        before_location_ref = registry.ref_by_location.get(
            practitioner.default_location_id
        )
        if before_location_ref is None:
            raise B4CommandError("before_state_conflict", status_code=409)
    before_state_hash = _compute_before_state_hash(
        practice_ref=practice_ref,
        practitioner_ref=request.practitioner_ref,
        default_location_ref=before_location_ref,
        aggregate_version=current_version,
    )
    if payload["before_state_hash"] != before_state_hash:
        raise B4CommandError("before_state_conflict", status_code=409)

    canonical_request_hash = _sha256(request.model_dump(mode="json"))
    idem_hash = hash_idempotency_key(idempotency_key, secret)
    nonce = f"b4_evidence_{secrets.token_hex(16)}"
    evidence = _claim_evidence(
        db,
        practice_id=current_user.practice_id,
        actor_user_id=current_user.id,
        actor_role=runtime_role,
        proposal_id=proposal_id,
        proposal_hash=request.proposal_hash,
        canonical_request_hash=canonical_request_hash,
        before_state_hash=before_state_hash,
        practitioner_id=practitioner.id,
        requested_location_id=location.id,
        expected_aggregate_version=current_version,
        correlation_id=correlation_id,
        idempotency_key_hash=idem_hash,
        nonce=nonce,
        now=now,
    )
    envelope = ConfirmationEvidenceEnvelope(
        schema_version=EVIDENCE_ENVELOPE_SCHEMA_VERSION,
        status="evidence_issued",
        confirmation_evidence_ref=evidence.nonce,
        proposal_hash=evidence.proposal_hash,
        canonical_request_hash=evidence.canonical_request_hash,
        issued_at=evidence.issued_at,
        expires_at=evidence.expires_at,
        applies_change=False,
    )
    # The attestation is a durable server-held one-use record for a later
    # confirm transaction, so it commits in its own transaction. It changes no
    # practitioner truth.
    db.commit()
    return envelope


def claim_b4_command(
    *,
    db: Session,
    practice_id: UUID,
    actor_user_id: UUID,
    actor_role: str,
    operation_id: str,
    route_family: str,
    raw_idempotency_key: str,
    canonical_request_hash: str,
    proposal_hash: str,
    secret: bytes,
) -> tuple[str, PracticeAdministrationCommandIdempotency]:
    idem_hash = hash_idempotency_key(raw_idempotency_key, secret)
    fingerprint = _sha256(
        {
            "canonical_request_hash": canonical_request_hash,
            "proposal_hash": proposal_hash,
        }
    )
    identity_filter = (
        PracticeAdministrationCommandIdempotency.practice_id == practice_id,
        PracticeAdministrationCommandIdempotency.actor_user_id == actor_user_id,
        PracticeAdministrationCommandIdempotency.operation_id == operation_id,
        PracticeAdministrationCommandIdempotency.idempotency_key_hash == idem_hash,
    )
    inserted_id = db.execute(
        postgresql_insert(PracticeAdministrationCommandIdempotency)
        .values(
            id=uuid.uuid4(),
            practice_id=practice_id,
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            operation_id=operation_id,
            route_family=route_family,
            idempotency_key_hash=idem_hash,
            request_body_hash=fingerprint,
            canonical_request_hash=canonical_request_hash,
            proposal_hash=proposal_hash,
            state="in_progress",
        )
        .on_conflict_do_nothing(
            constraint="uq_b4_cmd_idem_practice_actor_operation_key"
        )
        .returning(PracticeAdministrationCommandIdempotency.id)
    ).scalar_one_or_none()
    record = (
        db.query(PracticeAdministrationCommandIdempotency)
        .filter(
            PracticeAdministrationCommandIdempotency.id == inserted_id
            if inserted_id is not None
            else identity_filter[0],
            *(() if inserted_id is not None else identity_filter[1:]),
        )
        .with_for_update()
        .one()
    )
    if inserted_id is not None:
        return "started", record
    if record.request_body_hash != fingerprint:
        return "conflict", record
    if record.state == "completed":
        return "replay", record
    if record.state == "in_progress":
        return "in_progress", record
    return "failed_transient", record


def confirm_default_location_change(
    *,
    db: Session,
    current_user: User,
    proposal_id: str,
    request: DefaultLocationConfirmationCommand,
    idempotency_key: str,
    correlation_id: str,
    now: datetime | None = None,
) -> tuple[DefaultLocationConfirmationResult, bool]:
    """Consume the evidence and commit the single administrative command."""
    _gate_allows_or_raise(current_user.practice_id)
    runtime_role = _assert_session_binding(
        current_user=current_user,
        binding=request.binding,
        correlation_id=correlation_id,
    )
    now = now or _now()
    if request.proposal_id != proposal_id:
        raise B4CommandError("proposal_hash_mismatch", status_code=409)
    secret = _b4_secret()
    payload = _verify_proposal(proposal_id, secret, now)
    practice_ref = _practice_ref(current_user.practice_id)
    actor_ref = _actor_ref(current_user.id)
    _assert_proposal_matches_request(
        payload,
        practice_ref=practice_ref,
        actor_ref=actor_ref,
        runtime_role=runtime_role,
        correlation_id=correlation_id,
        request_proposal_id=request.proposal_id,
        request_proposal_hash=request.proposal_hash,
        request_proposal_expires_at=request.proposal_expires_at,
        practitioner_ref=request.practitioner_ref,
        requested_location_ref=request.requested_default_location_ref,
        expected_aggregate_version=request.expected_aggregate_version,
    )
    canonical_request_hash = _sha256(request.model_dump(mode="json"))
    proposal_hash = payload["proposal_hash"]

    kind, idem_record = claim_b4_command(
        db=db,
        practice_id=current_user.practice_id,
        actor_user_id=current_user.id,
        actor_role=runtime_role,
        operation_id=B4_OPERATION_ID_CONFIRM,
        route_family=B4_ROUTE_FAMILY,
        raw_idempotency_key=idempotency_key,
        canonical_request_hash=canonical_request_hash,
        proposal_hash=proposal_hash,
        secret=secret,
    )
    if kind == "replay":
        return (
            DefaultLocationConfirmationResult.model_validate(
                idem_record.response_body_json
            ),
            True,
        )
    if kind == "conflict":
        raise B4CommandError("idempotency_conflict", status_code=409)
    if kind == "in_progress":
        raise B4CommandError("idempotency_in_progress", status_code=409)
    if kind == "failed_transient":
        raise B4CommandError("atomic_transaction_failed", status_code=500)

    evidence = (
        db.query(PracticeAdministrationConfirmationEvidence)
        .filter(
            PracticeAdministrationConfirmationEvidence.practice_id
            == current_user.practice_id,
            PracticeAdministrationConfirmationEvidence.nonce
            == request.confirmation_evidence_ref,
        )
        .with_for_update()
        .first()
    )
    if evidence is None:
        raise B4CommandError("confirmation_evidence_invalid", status_code=409)
    if evidence.state == "consumed":
        raise B4CommandError("confirmation_replay_rejected", status_code=409)
    if evidence.expires_at <= now:
        raise B4CommandError("confirmation_evidence_expired", status_code=410)
    if evidence.proposal_hash != proposal_hash:
        raise B4CommandError("confirmation_evidence_invalid", status_code=409)
    if evidence.actor_user_id != current_user.id:
        raise B4CommandError("confirmation_evidence_invalid", status_code=409)
    if evidence.actor_role != runtime_role:
        raise B4CommandError("confirmation_evidence_invalid", status_code=409)

    practitioner = (
        db.query(Practitioner)
        .filter(
            Practitioner.practice_id == current_user.practice_id,
            Practitioner.id == evidence.practitioner_id,
            Practitioner.is_active.is_(True),
        )
        .with_for_update()
        .first()
    )
    if practitioner is None:
        raise B4CommandError("resource_scope_mismatch", status_code=403)

    registry = _build_registry(
        db,
        practice_id=current_user.practice_id,
        practice_ref=practice_ref,
        secret=secret,
    )
    current_version = int(practitioner.aggregate_version or 0)
    if evidence.expected_aggregate_version != current_version:
        raise B4CommandError("aggregate_version_mismatch", status_code=409)
    if payload["expected_aggregate_version"] != current_version:
        raise B4CommandError("aggregate_version_mismatch", status_code=409)

    before_location_uuid = practitioner.default_location_id
    before_location_ref: str | None = None
    if before_location_uuid is not None:
        before_location_ref = registry.ref_by_location.get(before_location_uuid)
        if before_location_ref is None:
            raise B4CommandError("before_state_conflict", status_code=409)
    expected_before_hash = _compute_before_state_hash(
        practice_ref=practice_ref,
        practitioner_ref=request.practitioner_ref,
        default_location_ref=before_location_ref,
        aggregate_version=current_version,
    )
    if payload["before_state_hash"] != expected_before_hash:
        raise B4CommandError("before_state_conflict", status_code=409)
    if evidence.before_state_hash != expected_before_hash:
        raise B4CommandError("before_state_conflict", status_code=409)

    location = (
        db.query(PracticeLocation)
        .filter(
            PracticeLocation.practice_id == current_user.practice_id,
            PracticeLocation.id == evidence.requested_location_id,
            PracticeLocation.is_active.is_(True),
        )
        .first()
    )
    if location is None:
        raise B4CommandError("location_not_active", status_code=409)
    if practitioner.default_location_id == location.id:
        raise B4CommandError("no_change", status_code=409)

    resulting_version = current_version + 1
    practitioner.default_location_id = location.id
    practitioner.aggregate_version = resulting_version

    evidence.state = "consumed"
    evidence.consumed_at = now
    evidence.consumed_by_command_id = idem_record.id

    audit = PracticeAdministrationAuditEvent(
        practice_id=current_user.practice_id,
        actor_user_id=current_user.id,
        actor_role=runtime_role,
        action="practitioner_default_location_changed",
        command_id=idem_record.id,
        practitioner_id=practitioner.id,
        before_location_id=before_location_uuid,
        after_location_id=location.id,
        expected_aggregate_version=current_version,
        resulting_aggregate_version=resulting_version,
        proposal_hash=proposal_hash,
        correlation_id=correlation_id,
        committed_at=now,
    )
    db.add(audit)
    db.flush()
    outbox = PracticeAdministrationOutboxEvent(
        practice_id=current_user.practice_id,
        event_type=EVENT_TYPE,
        schema_version=EVENT_SCHEMA_VERSION,
        source_system=EVENT_SOURCE_SYSTEM,
        actor_user_id=current_user.id,
        actor_role=runtime_role,
        command_id=idem_record.id,
        audit_event_id=audit.id,
        correlation_id=correlation_id,
        published=False,
        payload={
            "practitioner_id": str(practitioner.id),
            "before_location_id": (
                str(before_location_uuid) if before_location_uuid is not None else None
            ),
            "after_location_id": str(location.id),
            "aggregate_version": resulting_version,
            "reason_codes": REASON_CODES,
        },
    )
    db.add(outbox)
    db.flush()

    receipt_id = f"receipt_{idem_record.id.hex}"
    audit_ref = f"audit_{audit.id.hex}"
    outbox_ref = f"outbox_{outbox.id.hex}"
    idem_key_hash = hash_idempotency_key(idempotency_key, secret)
    receipt = DefaultLocationCommitReceipt(
        schema_version=COMMIT_RECEIPT_SCHEMA_VERSION,
        outcome="practitioner_default_location_updated",
        receipt_id=receipt_id,
        practice_ref=practice_ref,
        practitioner_ref=request.practitioner_ref,
        before_location_ref=before_location_ref,
        after_location_ref=request.requested_default_location_ref,
        proposal_hash=proposal_hash,
        canonical_request_hash=canonical_request_hash,
        idempotency_key_hash=idem_key_hash,
        correlation_id=correlation_id,
        expected_aggregate_version=current_version,
        resulting_aggregate_version=resulting_version,
        confirmed_by_actor_ref=actor_ref,
        confirmed_by_role=runtime_role,
        audit_event_id=audit_ref,
        outbox_event_id=outbox_ref,
        committed_at=now,
        verification=ConfirmationVerification(),
    )
    result = DefaultLocationConfirmationResult(
        schema_version=CONFIRMATION_RESULT_SCHEMA_VERSION,
        status="committed",
        receipt=receipt,
    )
    result_json = result.model_dump(mode="json")

    idem_record.state = "completed"
    idem_record.response_status_code = 200
    idem_record.response_body_hash = _sha256(result_json)
    idem_record.response_body_json = result_json
    idem_record.result_kind = "practitioner_default_location_updated"
    idem_record.receipt_id = receipt_id
    idem_record.practitioner_id = practitioner.id
    idem_record.confirmation_evidence_id = evidence.id
    idem_record.audit_event_id = audit.id
    idem_record.outbox_event_id = outbox.id

    db.commit()

    fresh = (
        db.query(Practitioner)
        .filter(
            Practitioner.practice_id == current_user.practice_id,
            Practitioner.id == practitioner.id,
        )
        .one()
    )
    if (
        fresh.default_location_id != location.id
        or int(fresh.aggregate_version or 0) != resulting_version
    ):
        raise B4CommandError("atomic_transaction_failed", status_code=500)
    return result, False


__all__ = [
    "B4CommandError",
    "B4_OPERATION_ID_CONFIRM",
    "B4_OPERATION_ID_EVIDENCE",
    "B4_OPERATION_ID_PROPOSE",
    "B4_ROUTE_FAMILY",
    "claim_b4_command",
    "confirm_default_location_change",
    "generate_default_location_proposal",
    "hash_idempotency_key",
    "issue_confirmation_evidence",
]
