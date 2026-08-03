"""Exact strict advisory schemas for the Davida tranche-2 proofreader.

This module is the frozen shape of the provider-free, unmounted and
unoccupied typed interpretation/proofreader envelope. It contains only pure
Pydantic models and literal constants: no SQLAlchemy, model, database,
network, provider, memory or clock dependency.

The closed operation vocabulary admits exactly ``ADVISORY_EXPLAIN_DIRECTORY``
and ``ADVISORY_SUMMARIZE_DIRECTORY``. Every accepted parent proposal
operation, every apply/confirmation/write code and every unknown operation is
absent from this vocabulary and therefore fails closed.

Candidate envelopes are strict extra-forbid. They bind the exact accepted
context schema v1, ``practice_ref``, ``principal_ref``, ``correlation_id``,
``content_revision``, ``authority_class=advisory`` and literal-false
``writes_authorized``, ``proposal_authorized`` and
``confirmation_authorized``. Explain candidates require exactly one
``subject_kind`` and one opaque ``subject_ref``; summary candidates admit no
target, caller-supplied count, prose, template, claim, fact value or open
selector.

The released advisory draft is a strict structured, deterministically
grounded, non-authoritative draft with ``authority_label=model_interpretation``,
``evidence_mode=provider_free_unoccupied_authored_synthetic``,
``status=advisory_only``,
``presentation=structured_fields_only_no_html_or_markdown``, one closed fixed
template code, a payload copied or derived from exact context rows, grounding
paths/digest and exact context binding. The released authority ceiling sets
command, confirmation, proposal, apply, write, provider, memory, database,
network, event and model-to-database fields to literal false.

The proofreader result is an exact discriminated released/rejected union.
Both arms carry a candidate hash, context revision and one closed
verdict/reason; ``repair_performed`` and ``retry_authorized`` are literal
false. A released draft is present only on exact pass; rejection carries no
partial payload.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

CANDIDATE_SCHEMA_VERSION = (
    "emr4.davida.practice_administration_advisory.candidate.v1"
)
DRAFT_SCHEMA_VERSION = "emr4.davida.practice_administration_advisory.draft.v1"
RESULT_SCHEMA_VERSION = "emr4.davida.practice_administration_advisory.result.v1"
CONTEXT_SCHEMA_VERSION = "emr4.davida.practice_administration_context.v1"

OPERATION_EXPLAIN = "ADVISORY_EXPLAIN_DIRECTORY"
OPERATION_SUMMARIZE = "ADVISORY_SUMMARIZE_DIRECTORY"
ADVISORY_OPERATIONS = frozenset({OPERATION_EXPLAIN, OPERATION_SUMMARIZE})

# All four accepted parent proposal operations plus apply/confirmation/write
# codes are deliberately unavailable in the advisory vocabulary.
PARENT_PROPOSAL_OPERATIONS = frozenset(
    {
        "PROPOSE_DEACTIVATE_PRACTITIONER",
        "PROPOSE_REACTIVATE_PRACTITIONER",
        "PROPOSE_UPDATE_PRACTITIONER_DEFAULT_LOCATION",
        "PROPOSE_UPDATE_PRACTITIONER_PROFILE",
    }
)
APPLY_OPERATIONS = frozenset(
    {
        "APPLY_PRACTITIONER_DEACTIVATE",
        "APPLY_PRACTITIONER_REACTIVATE",
        "APPLY_PRACTITIONER_UPDATE_DEFAULT_LOCATION",
        "APPLY_PRACTITIONER_UPDATE_PROFILE",
    }
)

TEMPLATE_CODE = "davida_directory_advisory_v1"
AUTHORITY_LABEL = "model_interpretation"
EVIDENCE_MODE = "provider_free_unoccupied_authored_synthetic"
STATUS_ADVISORY_ONLY = "advisory_only"
PRESENTATION = "structured_fields_only_no_html_or_markdown"
AUTHORITY_CLASS = "advisory"

VERDICT_RELEASED = "released"
VERDICT_REJECTED = "rejected"

REASON_RELEASED = "advisory_draft_released"
REASON_OPERATION_NOT_ALLOWED = "operation_not_allowed"
REASON_CANDIDATE_NONCANONICAL = "candidate_noncanonical"
REASON_CANDIDATE_SCHEMA_INVALID = "candidate_schema_invalid"
REASON_INPUT_OVER_BOUNDED = "input_over_bounded"
REASON_CONTEXT_FRAME_INVALID = "context_frame_invalid"
REASON_CONTEXT_REVISION_MISMATCH = "context_revision_mismatch"
REASON_CONTEXT_BOUNDARY_INVALID = "context_boundary_invalid"
REASON_SCOPE_MISMATCH = "scope_mismatch"
REASON_EVALUATED_AT_NAIVE = "evaluated_at_naive"
REASON_EVALUATED_AT_OUT_OF_RANGE = "evaluated_at_out_of_range"
REASON_AUTHORITY_CEILING_INVALID = "authority_ceiling_invalid"
REASON_SUBJECT_NOT_RESOLVED = "subject_not_resolved"
REASON_DUPLICATE_SUBJECT_REF = "duplicate_subject_ref"
REASON_WRONG_SUBJECT_KIND = "wrong_subject_kind"
REASON_DANGLING_DEFAULT_LOCATION = "dangling_default_location"

REJECTION_REASONS = (
    REASON_OPERATION_NOT_ALLOWED,
    REASON_CANDIDATE_NONCANONICAL,
    REASON_CANDIDATE_SCHEMA_INVALID,
    REASON_INPUT_OVER_BOUNDED,
    REASON_CONTEXT_FRAME_INVALID,
    REASON_CONTEXT_REVISION_MISMATCH,
    REASON_CONTEXT_BOUNDARY_INVALID,
    REASON_SCOPE_MISMATCH,
    REASON_EVALUATED_AT_NAIVE,
    REASON_EVALUATED_AT_OUT_OF_RANGE,
    REASON_AUTHORITY_CEILING_INVALID,
    REASON_SUBJECT_NOT_RESOLVED,
    REASON_DUPLICATE_SUBJECT_REF,
    REASON_WRONG_SUBJECT_KIND,
    REASON_DANGLING_DEFAULT_LOCATION,
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
    "authority_ceiling_invalid",
    "subject_not_resolved",
    "duplicate_subject_ref",
    "wrong_subject_kind",
    "dangling_default_location",
]

# Mirror the accepted context-desk bounded patterns exactly.
_REF_PATTERN = re.compile(r"^[A-Za-z0-9._~-]{1,64}$")
_CORRELATION_PATTERN = re.compile(r"^correlation-[A-Za-z0-9._~-]{1,64}$")
_OPAQUE_PATTERN = re.compile(r"^[A-Za-z0-9._~-]{8,64}$")
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

RELEASED_AUTHORITY_CEILING = {
    "command": False,
    "confirmation": False,
    "proposal": False,
    "apply": False,
    "write": False,
    "provider": False,
    "memory": False,
    "database": False,
    "network": False,
    "event": False,
    "model_to_database": False,
}


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class _CandidateBase(_StrictModel):
    schema_version: Literal[
        "emr4.davida.practice_administration_advisory.candidate.v1"
    ]
    practice_ref: str = Field(
        min_length=1, max_length=64, pattern=_REF_PATTERN.pattern
    )
    principal_ref: str = Field(
        min_length=1, max_length=64, pattern=_REF_PATTERN.pattern
    )
    correlation_id: str = Field(
        min_length=1, max_length=100, pattern=_CORRELATION_PATTERN.pattern
    )
    content_revision: str = Field(pattern=_SHA256_PATTERN.pattern)
    authority_class: Literal["advisory"]
    writes_authorized: Literal[False]
    proposal_authorized: Literal[False]
    confirmation_authorized: Literal[False]
    evaluated_at: datetime


class AdvisoryExplainCandidate(_CandidateBase):
    operation: Literal["ADVISORY_EXPLAIN_DIRECTORY"]
    subject_kind: Literal["practitioner", "location"]
    subject_ref: str = Field(
        min_length=8, max_length=64, pattern=_OPAQUE_PATTERN.pattern
    )


class AdvisorySummarizeCandidate(_CandidateBase):
    operation: Literal["ADVISORY_SUMMARIZE_DIRECTORY"]


AdvisoryCandidate = Annotated[
    Union[AdvisoryExplainCandidate, AdvisorySummarizeCandidate],
    Field(discriminator="operation"),
]


class _ReleasedAuthorityCeiling(_StrictModel):
    command: Literal[False]
    confirmation: Literal[False]
    proposal: Literal[False]
    apply: Literal[False]
    write: Literal[False]
    provider: Literal[False]
    memory: Literal[False]
    database: Literal[False]
    network: Literal[False]
    event: Literal[False]
    model_to_database: Literal[False]


class AdvisoryGrounding(_StrictModel):
    grounding_paths: list[str] = Field(min_length=1, max_length=4)
    grounding_digest: str = Field(pattern=_SHA256_PATTERN.pattern)


class AdvisoryContextBinding(_StrictModel):
    context_schema_version: Literal[
        "emr4.davida.practice_administration_context.v1"
    ]
    practice_ref: str = Field(
        min_length=1, max_length=64, pattern=_REF_PATTERN.pattern
    )
    principal_ref: str = Field(
        min_length=1, max_length=64, pattern=_REF_PATTERN.pattern
    )
    correlation_id: str = Field(
        min_length=1, max_length=100, pattern=_CORRELATION_PATTERN.pattern
    )
    content_revision: str = Field(pattern=_SHA256_PATTERN.pattern)


class AdvisorySummarizePayload(_StrictModel):
    practitioner_count: int = Field(ge=0, le=200)
    location_count: int = Field(ge=0, le=200)
    practitioners_with_role_count: int = Field(ge=0, le=200)
    practitioners_with_default_location_count: int = Field(ge=0, le=200)


class AdvisoryExplainPractitionerPayload(_StrictModel):
    resource_ref: str = Field(
        min_length=8, max_length=64, pattern=_OPAQUE_PATTERN.pattern
    )
    display_name: str = Field(min_length=1, max_length=255)
    role_label: str | None = Field(default=None, max_length=255)
    active: Literal[True]
    default_location_ref: str | None = Field(
        default=None, min_length=8, max_length=64, pattern=_OPAQUE_PATTERN.pattern
    )


class AdvisoryExplainLocationPayload(_StrictModel):
    resource_ref: str = Field(
        min_length=8, max_length=64, pattern=_OPAQUE_PATTERN.pattern
    )
    name: str = Field(min_length=1, max_length=255)


class _AdvisoryDraftBase(_StrictModel):
    schema_version: Literal[
        "emr4.davida.practice_administration_advisory.draft.v1"
    ]
    authority_label: Literal["model_interpretation"]
    evidence_mode: Literal["provider_free_unoccupied_authored_synthetic"]
    status: Literal["advisory_only"]
    presentation: Literal["structured_fields_only_no_html_or_markdown"]
    template_code: Literal["davida_directory_advisory_v1"]
    practice_ref: str = Field(
        min_length=1, max_length=64, pattern=_REF_PATTERN.pattern
    )
    principal_ref: str = Field(
        min_length=1, max_length=64, pattern=_REF_PATTERN.pattern
    )
    correlation_id: str = Field(
        min_length=1, max_length=100, pattern=_CORRELATION_PATTERN.pattern
    )
    content_revision: str = Field(pattern=_SHA256_PATTERN.pattern)
    context_schema_version: Literal[
        "emr4.davida.practice_administration_context.v1"
    ]
    authority_ceiling: _ReleasedAuthorityCeiling
    grounding: AdvisoryGrounding
    context_binding: AdvisoryContextBinding


class AdvisorySummarizeDraft(_AdvisoryDraftBase):
    draft_kind: Literal["summary"]
    operation: Literal["ADVISORY_SUMMARIZE_DIRECTORY"]
    payload: AdvisorySummarizePayload


class AdvisoryExplainPractitionerDraft(_AdvisoryDraftBase):
    draft_kind: Literal["practitioner_explain"]
    operation: Literal["ADVISORY_EXPLAIN_DIRECTORY"]
    subject_kind: Literal["practitioner"]
    payload: AdvisoryExplainPractitionerPayload


class AdvisoryExplainLocationDraft(_AdvisoryDraftBase):
    draft_kind: Literal["location_explain"]
    operation: Literal["ADVISORY_EXPLAIN_DIRECTORY"]
    subject_kind: Literal["location"]
    payload: AdvisoryExplainLocationPayload


AdvisoryDraft = Annotated[
    Union[
        AdvisorySummarizeDraft,
        AdvisoryExplainPractitionerDraft,
        AdvisoryExplainLocationDraft,
    ],
    Field(discriminator="draft_kind"),
]


class AdvisoryReleasedResult(_StrictModel):
    schema_version: Literal[
        "emr4.davida.practice_administration_advisory.result.v1"
    ]
    verdict: Literal["released"]
    reason: Literal["advisory_draft_released"]
    candidate_hash: str = Field(pattern=_SHA256_PATTERN.pattern)
    context_revision: str = Field(pattern=_SHA256_PATTERN.pattern)
    repair_performed: Literal[False]
    retry_authorized: Literal[False]
    draft: AdvisoryDraft


class AdvisoryRejectedResult(_StrictModel):
    schema_version: Literal[
        "emr4.davida.practice_administration_advisory.result.v1"
    ]
    verdict: Literal["rejected"]
    reason: RejectionReason
    candidate_hash: str = Field(pattern=_SHA256_PATTERN.pattern)
    context_revision: str = Field(
        pattern=r"^(?:|[0-9a-f]{64})$", min_length=0, max_length=64
    )
    repair_performed: Literal[False]
    retry_authorized: Literal[False]


PracticeAdministrationAdvisoryResult = Annotated[
    Union[AdvisoryReleasedResult, AdvisoryRejectedResult],
    Field(discriminator="verdict"),
]

# TypeAdapters let callers validate the discriminated union aliases exactly as
# Pydantic models, without losing the union/discriminator semantics.
AdvisoryCandidateAdapter = TypeAdapter(AdvisoryCandidate)
AdvisoryDraftAdapter = TypeAdapter(AdvisoryDraft)
PracticeAdministrationAdvisoryResultAdapter = TypeAdapter(
    PracticeAdministrationAdvisoryResult
)


__all__ = [
    "ADVISORY_OPERATIONS",
    "AdvisoryCandidate",
    "AdvisoryCandidateAdapter",
    "AdvisoryContextBinding",
    "AdvisoryDraft",
    "AdvisoryExplainCandidate",
    "AdvisoryExplainLocationDraft",
    "AdvisoryExplainLocationPayload",
    "AdvisoryExplainPractitionerDraft",
    "AdvisoryExplainPractitionerPayload",
    "AdvisoryGrounding",
    "AdvisoryRejectedResult",
    "AdvisoryReleasedResult",
    "AdvisorySummarizeCandidate",
    "AdvisorySummarizeDraft",
    "AdvisorySummarizePayload",
    "AdvisoryDraftAdapter",
    "APPLY_OPERATIONS",
    "AUTHORITY_CLASS",
    "AUTHORITY_LABEL",
    "CANDIDATE_SCHEMA_VERSION",
    "CONTEXT_SCHEMA_VERSION",
    "DRAFT_SCHEMA_VERSION",
    "EVIDENCE_MODE",
    "OPERATION_EXPLAIN",
    "OPERATION_SUMMARIZE",
    "PARENT_PROPOSAL_OPERATIONS",
    "PRESENTATION",
    "PracticeAdministrationAdvisoryResult",
    "PracticeAdministrationAdvisoryResultAdapter",
    "REASON_AUTHORITY_CEILING_INVALID",
    "REASON_CANDIDATE_NONCANONICAL",
    "REASON_CANDIDATE_SCHEMA_INVALID",
    "REASON_CONTEXT_BOUNDARY_INVALID",
    "REASON_CONTEXT_FRAME_INVALID",
    "REASON_CONTEXT_REVISION_MISMATCH",
    "REASON_DANGLING_DEFAULT_LOCATION",
    "REASON_DUPLICATE_SUBJECT_REF",
    "REASON_EVALUATED_AT_NAIVE",
    "REASON_EVALUATED_AT_OUT_OF_RANGE",
    "REASON_INPUT_OVER_BOUNDED",
    "REASON_OPERATION_NOT_ALLOWED",
    "REASON_RELEASED",
    "REASON_SCOPE_MISMATCH",
    "REASON_SUBJECT_NOT_RESOLVED",
    "REASON_WRONG_SUBJECT_KIND",
    "REJECTION_REASONS",
    "RESULT_SCHEMA_VERSION",
    "RELEASED_AUTHORITY_CEILING",
    "STATUS_ADVISORY_ONLY",
    "TEMPLATE_CODE",
    "VERDICT_REJECTED",
    "VERDICT_RELEASED",
]
