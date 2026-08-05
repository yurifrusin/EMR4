"""Strict closed schemas for the B4.1 Davida default-location command runtime.

The models admit exactly one practice-administration command family: propose a
practitioner default-location change, issue one server-held one-use
confirmation-evidence reference, and confirm the change as the exact
authenticated human ``Admin``/``PracticeOwner``. Every schema is
``extra=forbid`` so unknown fields, free text and client-selected authority
are rejected at the envelope boundary. No patient, provider, session secret or
free-text field is modelled here.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

OPAQUE_REF_PATTERN = r"^[a-z][a-z0-9_]*_[A-Za-z0-9_-]+$"
SHA256_PATTERN = r"^[0-9a-f]{64}$"
SIGNED_PROPOSAL_PATTERN = r"^dlp1\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$"
MAX_SIGNED_PROPOSAL_LENGTH = 4096
HEADER_VALUE_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{7,127}$"

PROPOSAL_REQUEST_SCHEMA_VERSION = (
    "emr4.practice_administration.default_location.proposal_request.v1"
)
PROPOSAL_ENVELOPE_SCHEMA_VERSION = (
    "emr4.practice_administration.default_location.proposal_envelope.v1"
)
EVIDENCE_REQUEST_SCHEMA_VERSION = (
    "emr4.practice_administration.default_location.confirmation_evidence_request.v1"
)
EVIDENCE_ENVELOPE_SCHEMA_VERSION = (
    "emr4.practice_administration.default_location.confirmation_evidence.v1"
)
CONFIRMATION_COMMAND_SCHEMA_VERSION = (
    "emr4.practice_administration.default_location.confirmation_command.v1"
)
COMMIT_RECEIPT_SCHEMA_VERSION = (
    "emr4.practice_administration.default_location.commit_receipt.v1"
)
CONFIRMATION_RESULT_SCHEMA_VERSION = (
    "emr4.practice_administration.default_location.confirmation_result.v1"
)
REJECTION_SCHEMA_VERSION = (
    "emr4.practice_administration.default_location.rejection.v1"
)

OPERATION_PROPOSE = "PROPOSE_UPDATE_PRACTITIONER_DEFAULT_LOCATION"
OPERATION_CONFIRM = "CONFIRM_UPDATE_PRACTITIONER_DEFAULT_LOCATION"
OPERATION_RESULT = "UPDATE_PRACTITIONER_DEFAULT_LOCATION"
CHANGED_PATH = "practitioner.default_location_ref"
PERMITTED_ROLES = ("practice_manager", "practice_owner")
PERMITTED_SOURCE_SURFACES = ("practice_administration_console", "command_centre")
PERMITTED_DELEGATED_AGENTS = ("davida",)
MAXIMUM_LIFETIME_SECONDS = 120
REASON_CODE = "practitioner_default_location_changed"
REASON_CODES = (REASON_CODE,)

REJECTION_CODES = (
    "unauthenticated",
    "not_authorized",
    "confirmer_not_authorized",
    "practice_scope_mismatch",
    "resource_scope_mismatch",
    "location_not_active",
    "no_change",
    "proposal_stale",
    "proposal_expired",
    "proposal_hash_mismatch",
    "aggregate_version_mismatch",
    "before_state_conflict",
    "confirmation_evidence_invalid",
    "confirmation_evidence_expired",
    "idempotency_conflict",
    "idempotency_in_progress",
    "confirmation_replay_rejected",
    "atomic_transaction_failed",
    "invalid_envelope",
)
RejectionReason = Literal[
    "unauthenticated",
    "not_authorized",
    "confirmer_not_authorized",
    "practice_scope_mismatch",
    "resource_scope_mismatch",
    "location_not_active",
    "no_change",
    "proposal_stale",
    "proposal_expired",
    "proposal_hash_mismatch",
    "aggregate_version_mismatch",
    "before_state_conflict",
    "confirmation_evidence_invalid",
    "confirmation_evidence_expired",
    "idempotency_conflict",
    "idempotency_in_progress",
    "confirmation_replay_rejected",
    "atomic_transaction_failed",
    "invalid_envelope",
]


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SessionActorBindingAssertion(_StrictModel):
    """Non-authoritative actor assertion; the session remains the authority."""

    actor_ref: str = Field(pattern=OPAQUE_REF_PATTERN)
    actor_type: Literal["human_user"] = "human_user"
    role: Literal["practice_manager", "practice_owner"]


class SessionBindingAssertion(_StrictModel):
    """Non-authoritative body binding that must exact-match session authority."""

    practice_ref: str = Field(pattern=OPAQUE_REF_PATTERN)
    actor: SessionActorBindingAssertion
    source_surface: Literal["practice_administration_console", "command_centre"]
    correlation_id: str = Field(
        min_length=8, max_length=128, pattern=HEADER_VALUE_PATTERN
    )
    requested_at: datetime
    delegated_agent: Literal["davida"] | None = None


class DefaultLocationProposalRequest(_StrictModel):
    schema_version: Literal[
        "emr4.practice_administration.default_location.proposal_request.v1"
    ]
    operation: Literal["PROPOSE_UPDATE_PRACTITIONER_DEFAULT_LOCATION"]
    binding: SessionBindingAssertion
    practitioner_ref: str = Field(pattern=OPAQUE_REF_PATTERN)
    requested_default_location_ref: str = Field(pattern=OPAQUE_REF_PATTERN)
    expected_aggregate_version: int = Field(ge=0)
    dry_run_proposal_hash: str = Field(pattern=SHA256_PATTERN)
    dry_run_context_revision: str = Field(pattern=SHA256_PATTERN)
    dry_run_expires_at: datetime


class DefaultLocationChange(_StrictModel):
    changed_path: Literal["practitioner.default_location_ref"]
    before_location_ref: str | None = Field(default=None, pattern=OPAQUE_REF_PATTERN)
    after_location_ref: str = Field(pattern=OPAQUE_REF_PATTERN)


class Issue(_StrictModel):
    code: str = Field(min_length=1, max_length=64)
    severity: Literal["warning", "blocked"]


class DefaultLocationProposalEnvelope(_StrictModel):
    schema_version: Literal[
        "emr4.practice_administration.default_location.proposal_envelope.v1"
    ]
    status: Literal["proposal_only"]
    proposal_id: str = Field(
        max_length=MAX_SIGNED_PROPOSAL_LENGTH,
        pattern=SIGNED_PROPOSAL_PATTERN,
    )
    practice_ref: str = Field(pattern=OPAQUE_REF_PATTERN)
    practitioner_ref: str = Field(pattern=OPAQUE_REF_PATTERN)
    operation: Literal["UPDATE_PRACTITIONER_DEFAULT_LOCATION"]
    expected_aggregate_version: int = Field(ge=0)
    change: DefaultLocationChange
    before_state_hash: str = Field(pattern=SHA256_PATTERN)
    dry_run_proposal_hash: str = Field(pattern=SHA256_PATTERN)
    proposal_hash: str = Field(pattern=SHA256_PATTERN)
    generated_at: datetime
    expires_at: datetime
    maximum_lifetime_seconds: Literal[120] = 120
    human_confirmation_required: Literal[True] = True
    permitted_confirmer_roles: tuple[
        Literal["practice_manager"], Literal["practice_owner"]
    ] = ("practice_manager", "practice_owner")
    applies_change: Literal[False] = False
    davida_can_confirm: Literal[False] = False
    warnings: list[Issue] = Field(default_factory=list, max_length=16)
    blocks: list[Issue] = Field(default_factory=list, max_length=16)


class DefaultLocationEvidenceRequest(_StrictModel):
    schema_version: Literal[
        "emr4.practice_administration.default_location.confirmation_evidence_request.v1"
    ]
    operation: Literal["CONFIRM_UPDATE_PRACTITIONER_DEFAULT_LOCATION"]
    confirmed: Literal[True] = True
    binding: SessionBindingAssertion
    proposal_id: str = Field(
        max_length=MAX_SIGNED_PROPOSAL_LENGTH,
        pattern=SIGNED_PROPOSAL_PATTERN,
    )
    proposal_hash: str = Field(pattern=SHA256_PATTERN)
    proposal_expires_at: datetime
    practitioner_ref: str = Field(pattern=OPAQUE_REF_PATTERN)
    requested_default_location_ref: str = Field(pattern=OPAQUE_REF_PATTERN)
    expected_aggregate_version: int = Field(ge=0)


class ConfirmationEvidenceEnvelope(_StrictModel):
    schema_version: Literal[
        "emr4.practice_administration.default_location.confirmation_evidence.v1"
    ]
    status: Literal["evidence_issued"]
    confirmation_evidence_ref: str = Field(pattern=OPAQUE_REF_PATTERN)
    proposal_hash: str = Field(pattern=SHA256_PATTERN)
    canonical_request_hash: str = Field(pattern=SHA256_PATTERN)
    issued_at: datetime
    expires_at: datetime
    applies_change: Literal[False] = False


class DefaultLocationConfirmationCommand(_StrictModel):
    schema_version: Literal[
        "emr4.practice_administration.default_location.confirmation_command.v1"
    ]
    operation: Literal["CONFIRM_UPDATE_PRACTITIONER_DEFAULT_LOCATION"]
    confirmed: Literal[True] = True
    binding: SessionBindingAssertion
    proposal_id: str = Field(
        max_length=MAX_SIGNED_PROPOSAL_LENGTH,
        pattern=SIGNED_PROPOSAL_PATTERN,
    )
    proposal_hash: str = Field(pattern=SHA256_PATTERN)
    proposal_expires_at: datetime
    practitioner_ref: str = Field(pattern=OPAQUE_REF_PATTERN)
    requested_default_location_ref: str = Field(pattern=OPAQUE_REF_PATTERN)
    expected_aggregate_version: int = Field(ge=0)
    confirmation_evidence_ref: str = Field(pattern=OPAQUE_REF_PATTERN)


class ConfirmationVerification(_StrictModel):
    application_session_authenticated: Literal[True] = True
    practice_scope_authorized: Literal[True] = True
    role_authorized: Literal[True] = True
    resource_scope_authorized: Literal[True] = True
    proposal_revalidated: Literal[True] = True
    aggregate_version_matched: Literal[True] = True
    confirmation_evidence_verified: Literal[True] = True
    idempotency_verified: Literal[True] = True
    audit_appended: Literal[True] = True
    outbox_appended: Literal[True] = True
    publication_after_commit_only: Literal[True] = True


class DefaultLocationCommitReceipt(_StrictModel):
    schema_version: Literal[
        "emr4.practice_administration.default_location.commit_receipt.v1"
    ]
    outcome: Literal["practitioner_default_location_updated"]
    receipt_id: str = Field(pattern=OPAQUE_REF_PATTERN)
    practice_ref: str = Field(pattern=OPAQUE_REF_PATTERN)
    practitioner_ref: str = Field(pattern=OPAQUE_REF_PATTERN)
    before_location_ref: str | None = Field(default=None, pattern=OPAQUE_REF_PATTERN)
    after_location_ref: str = Field(pattern=OPAQUE_REF_PATTERN)
    proposal_hash: str = Field(pattern=SHA256_PATTERN)
    canonical_request_hash: str = Field(pattern=SHA256_PATTERN)
    idempotency_key_hash: str = Field(pattern=SHA256_PATTERN)
    correlation_id: str = Field(
        min_length=8, max_length=128, pattern=HEADER_VALUE_PATTERN
    )
    expected_aggregate_version: int = Field(ge=0)
    resulting_aggregate_version: int = Field(ge=1)
    confirmed_by_actor_ref: str = Field(pattern=OPAQUE_REF_PATTERN)
    confirmed_by_role: Literal["practice_manager", "practice_owner"]
    audit_event_id: str = Field(pattern=OPAQUE_REF_PATTERN)
    outbox_event_id: str = Field(pattern=OPAQUE_REF_PATTERN)
    committed_at: datetime
    verification: ConfirmationVerification


class DefaultLocationConfirmationResult(_StrictModel):
    schema_version: Literal[
        "emr4.practice_administration.default_location.confirmation_result.v1"
    ]
    status: Literal["committed"] = "committed"
    receipt: DefaultLocationCommitReceipt


class Rejection(_StrictModel):
    schema_version: Literal[
        "emr4.practice_administration.default_location.rejection.v1"
    ]
    status: Literal["rejected"] = "rejected"
    reason_code: RejectionReason
    correlation_id: str = Field(
        min_length=8, max_length=128, pattern=HEADER_VALUE_PATTERN
    )
    retryable: bool


__all__ = [
    "CHANGED_PATH",
    "COMMIT_RECEIPT_SCHEMA_VERSION",
    "CONFIRMATION_COMMAND_SCHEMA_VERSION",
    "CONFIRMATION_RESULT_SCHEMA_VERSION",
    "ConfirmationEvidenceEnvelope",
    "ConfirmationVerification",
    "DefaultLocationChange",
    "DefaultLocationCommitReceipt",
    "DefaultLocationConfirmationCommand",
    "DefaultLocationConfirmationResult",
    "DefaultLocationEvidenceRequest",
    "DefaultLocationProposalEnvelope",
    "DefaultLocationProposalRequest",
    "EVIDENCE_ENVELOPE_SCHEMA_VERSION",
    "EVIDENCE_REQUEST_SCHEMA_VERSION",
    "HEADER_VALUE_PATTERN",
    "Issue",
    "MAX_SIGNED_PROPOSAL_LENGTH",
    "MAXIMUM_LIFETIME_SECONDS",
    "OPAQUE_REF_PATTERN",
    "OPERATION_CONFIRM",
    "OPERATION_PROPOSE",
    "OPERATION_RESULT",
    "PERMITTED_DELEGATED_AGENTS",
    "PERMITTED_ROLES",
    "PERMITTED_SOURCE_SURFACES",
    "PROPOSAL_ENVELOPE_SCHEMA_VERSION",
    "PROPOSAL_REQUEST_SCHEMA_VERSION",
    "REASON_CODE",
    "REASON_CODES",
    "REJECTION_CODES",
    "REJECTION_SCHEMA_VERSION",
    "Rejection",
    "RejectionReason",
    "SHA256_PATTERN",
    "SIGNED_PROPOSAL_PATTERN",
    "SessionActorBindingAssertion",
    "SessionBindingAssertion",
]
