"""Strict schemas for Davida's default-location dry-run proposal.

The models in this module are provider-free, unmounted and non-authoritative.
They admit exactly one operation and cannot express confirmation, command,
apply, write, provider, model, database, network or model-to-database authority.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

CANDIDATE_SCHEMA_VERSION = (
    "emr4.davida.practice_administration_default_location.candidate.v1"
)
PROPOSAL_SCHEMA_VERSION = (
    "emr4.davida.practice_administration_default_location.proposal.v1"
)
RESULT_SCHEMA_VERSION = (
    "emr4.davida.practice_administration_default_location.result.v1"
)
CONTEXT_SCHEMA_VERSION = "emr4.davida.practice_administration_context.v1"

OPERATION = "PROPOSE_UPDATE_PRACTITIONER_DEFAULT_LOCATION"
ALLOWED_OPERATIONS = frozenset({OPERATION})
REASON_CODE = "PRACTICE_ASSIGNMENT_UPDATE"
RISK_TIER = "admin_proposal"
EVIDENCE_MODE = "provider_free_unoccupied_default_location_dry_run"
DATA_CLASS = "authored_synthetic"
ARTIFACT_TYPE = "proposal_candidate"
STATUS = "dry_run_only"
CHANGED_PATH = "practitioner.default_location_ref"

REASON_RELEASED = "proposal_candidate_released"
REJECTION_REASONS = (
    "operation_not_allowed",
    "candidate_noncanonical",
    "candidate_schema_invalid",
    "input_over_bounded",
    "context_frame_invalid",
    "context_revision_mismatch",
    "context_boundary_invalid",
    "scope_mismatch",
    "evaluated_at_naive",
    "evaluated_at_out_of_range",
    "practitioner_not_resolved",
    "location_not_resolved",
    "wrong_resource_kind",
    "no_change",
)
RejectionReason = Literal[
    "operation_not_allowed",
    "candidate_noncanonical",
    "candidate_schema_invalid",
    "input_over_bounded",
    "context_frame_invalid",
    "context_revision_mismatch",
    "context_boundary_invalid",
    "scope_mismatch",
    "evaluated_at_naive",
    "evaluated_at_out_of_range",
    "practitioner_not_resolved",
    "location_not_resolved",
    "wrong_resource_kind",
    "no_change",
]

_REF_PATTERN = re.compile(r"^[A-Za-z0-9._~-]{1,64}$")
_CORRELATION_PATTERN = re.compile(r"^correlation-[A-Za-z0-9._~-]{1,64}$")
_OPAQUE_PATTERN = re.compile(r"^[A-Za-z0-9._~-]{8,64}$")
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class DefaultLocationProposalCandidate(_StrictModel):
    schema_version: Literal[
        "emr4.davida.practice_administration_default_location.candidate.v1"
    ]
    operation: Literal["PROPOSE_UPDATE_PRACTITIONER_DEFAULT_LOCATION"]
    practice_ref: str = Field(pattern=_REF_PATTERN.pattern, min_length=1, max_length=64)
    principal_ref: str = Field(pattern=_REF_PATTERN.pattern, min_length=1, max_length=64)
    correlation_id: str = Field(
        pattern=_CORRELATION_PATTERN.pattern, min_length=1, max_length=100
    )
    content_revision: str = Field(pattern=_SHA256_PATTERN.pattern)
    evaluated_at: datetime
    practitioner_ref: str = Field(
        pattern=_OPAQUE_PATTERN.pattern, min_length=8, max_length=64
    )
    location_ref: str = Field(
        pattern=_OPAQUE_PATTERN.pattern, min_length=8, max_length=64
    )
    reason_code: Literal["PRACTICE_ASSIGNMENT_UPDATE"]
    risk_tier: Literal["admin_proposal"]
    confirmation_authorized: Literal[False]
    apply_authorized: Literal[False]
    writes_authorized: Literal[False]
    command_authorized: Literal[False]
    provider_executed: Literal[False]
    model_executed: Literal[False]
    database_used: Literal[False]
    network_used: Literal[False]
    model_to_database: Literal[False]


class DefaultLocationState(_StrictModel):
    practitioner_ref: str = Field(
        pattern=_OPAQUE_PATTERN.pattern, min_length=8, max_length=64
    )
    default_location_ref: str | None = Field(
        default=None,
        pattern=_OPAQUE_PATTERN.pattern,
        min_length=8,
        max_length=64,
    )


class DefaultLocationProposalAuthority(_StrictModel):
    command_ready: Literal[False]
    confirmation_authorized: Literal[False]
    apply_authorized: Literal[False]
    writes_authorized: Literal[False]
    provider_executed: Literal[False]
    model_executed: Literal[False]
    database_used: Literal[False]
    network_used: Literal[False]
    model_to_database: Literal[False]


class DefaultLocationContextBinding(_StrictModel):
    context_schema_version: Literal[
        "emr4.davida.practice_administration_context.v1"
    ]
    practice_ref: str = Field(pattern=_REF_PATTERN.pattern, min_length=1, max_length=64)
    principal_ref: str = Field(pattern=_REF_PATTERN.pattern, min_length=1, max_length=64)
    correlation_id: str = Field(
        pattern=_CORRELATION_PATTERN.pattern, min_length=1, max_length=100
    )
    content_revision: str = Field(pattern=_SHA256_PATTERN.pattern)


class DefaultLocationProposal(_StrictModel):
    schema_version: Literal[
        "emr4.davida.practice_administration_default_location.proposal.v1"
    ]
    artifact_type: Literal["proposal_candidate"]
    status: Literal["dry_run_only"]
    evidence_mode: Literal[
        "provider_free_unoccupied_default_location_dry_run"
    ]
    data_class: Literal["authored_synthetic"]
    operation: Literal["PROPOSE_UPDATE_PRACTITIONER_DEFAULT_LOCATION"]
    reason_code: Literal["PRACTICE_ASSIGNMENT_UPDATE"]
    risk_tier: Literal["admin_proposal"]
    human_confirmation_required: Literal[True]
    context_binding: DefaultLocationContextBinding
    evaluated_at: datetime
    expires_at: datetime
    practitioner_ref: str = Field(
        pattern=_OPAQUE_PATTERN.pattern, min_length=8, max_length=64
    )
    location_ref: str = Field(
        pattern=_OPAQUE_PATTERN.pattern, min_length=8, max_length=64
    )
    source_paths: list[str] = Field(min_length=2, max_length=2)
    changed_paths: list[Literal["practitioner.default_location_ref"]] = Field(
        min_length=1, max_length=1
    )
    before_state: DefaultLocationState
    after_state: DefaultLocationState
    proposal_hash: str = Field(pattern=_SHA256_PATTERN.pattern)
    grounding_hash: str = Field(pattern=_SHA256_PATTERN.pattern)
    authority_ceiling: DefaultLocationProposalAuthority


class DefaultLocationProposalReleased(_StrictModel):
    schema_version: Literal[
        "emr4.davida.practice_administration_default_location.result.v1"
    ]
    verdict: Literal["released"]
    reason: Literal["proposal_candidate_released"]
    candidate_hash: str = Field(pattern=_SHA256_PATTERN.pattern)
    context_revision: str = Field(pattern=_SHA256_PATTERN.pattern)
    repair_performed: Literal[False]
    retry_authorized: Literal[False]
    proposal_candidate: DefaultLocationProposal


class DefaultLocationProposalRejected(_StrictModel):
    schema_version: Literal[
        "emr4.davida.practice_administration_default_location.result.v1"
    ]
    verdict: Literal["rejected"]
    reason: RejectionReason
    candidate_hash: str = Field(pattern=_SHA256_PATTERN.pattern)
    context_revision: str = Field(
        pattern=r"^(?:|[0-9a-f]{64})$", min_length=0, max_length=64
    )
    repair_performed: Literal[False]
    retry_authorized: Literal[False]


DefaultLocationProposalResult = Annotated[
    Union[DefaultLocationProposalReleased, DefaultLocationProposalRejected],
    Field(discriminator="verdict"),
]

DefaultLocationProposalResultAdapter = TypeAdapter(DefaultLocationProposalResult)

__all__ = [
    "ALLOWED_OPERATIONS",
    "ARTIFACT_TYPE",
    "CANDIDATE_SCHEMA_VERSION",
    "CHANGED_PATH",
    "CONTEXT_SCHEMA_VERSION",
    "DATA_CLASS",
    "DefaultLocationProposal",
    "DefaultLocationProposalAuthority",
    "DefaultLocationProposalCandidate",
    "DefaultLocationProposalRejected",
    "DefaultLocationProposalReleased",
    "DefaultLocationProposalResult",
    "DefaultLocationProposalResultAdapter",
    "DefaultLocationState",
    "EVIDENCE_MODE",
    "OPERATION",
    "PROPOSAL_SCHEMA_VERSION",
    "REASON_CODE",
    "REASON_RELEASED",
    "REJECTION_REASONS",
    "RESULT_SCHEMA_VERSION",
    "RISK_TIER",
    "STATUS",
]
