"""Typed, write-free first-use gate for one minimised structural scenario."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator


ACCEPTED_SOURCE_COMMIT = "7f9a526e57a4c10502f01b0e7c1cc5ec6910f00c"

Hex40 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]
Hex64 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]

ArtifactClass = Literal[
    "minimised_structural_scenario",
    "bounded_multi_event_scenario",
    "whole_day_or_near_lossless_replay",
]
DevelopmentPurpose = Literal[
    "provider_free_reception_check_in_context_scenario_development"
]
IdentityPolicy = Literal["source_independent_synthetic_identity_only"]
DatePolicy = Literal["relative_day_offset_only"]
AuthorityCeiling = Literal["local_provider_free_development_test_only"]
Decision = Literal[
    "blocked",
    "revision_required",
    "admitted_for_exact_declared_artifact_only",
]
EventKind = Literal[
    "scheduled_slot_present",
    "scheduled_slot_added",
    "scheduled_slot_removed",
    "scheduled_slot_moved",
    "scheduled_slot_replaced",
    "scheduled_slot_format_changed",
]
ReasonCode = Literal[
    "accepted_source_commit_not_exact",
    "candidate_digest_mismatch",
    "forbidden_field_reading_nonzero",
    "structural_utility_declaration_mismatch",
    "whole_day_or_near_lossless_replay_forbidden",
    "bounded_multi_event_scenario_not_yet_admissible",
    "event_count_outside_minimised_range",
    "insufficient_distinct_relative_minutes",
    "relative_minute_span_outside_minimised_range",
    "insufficient_distinct_event_kinds",
    "too_many_synthetic_subject_slots",
    "too_many_resource_slots",
]


class StrictForm(BaseModel):
    """Base for forms whose fields and values are closed before evaluation."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class StructuralEvent(StrictForm):
    schema_version: Literal["raisa.historical_first_use_structural_event.v1"] = (
        "raisa.historical_first_use_structural_event.v1"
    )
    event_kind: EventKind
    relative_minute: int = Field(ge=0, le=720)
    synthetic_subject_slot: int = Field(ge=0, le=7)
    resource_slot: int = Field(ge=0, le=3)


class CandidatePayload(StrictForm):
    schema_version: Literal["raisa.historical_first_use_candidate_payload.v1"] = (
        "raisa.historical_first_use_candidate_payload.v1"
    )
    relative_day_offset: Literal[0] = 0
    events: tuple[StructuralEvent, ...]

    @model_validator(mode="after")
    def _bounded_event_count(self) -> CandidatePayload:
        if not 1 <= len(self.events) <= 12:
            raise ValueError("candidate_event_count_out_of_schema_range")
        return self


class StructuralUtilityReading(StrictForm):
    schema_version: Literal["raisa.historical_first_use_structural_utility.v1"] = (
        "raisa.historical_first_use_structural_utility.v1"
    )
    event_count: int = Field(ge=1, le=12)
    distinct_relative_minutes: int = Field(ge=1, le=12)
    relative_minute_span: int = Field(ge=0, le=720)
    distinct_event_kinds: int = Field(ge=1, le=6)
    synthetic_subject_slots: int = Field(ge=1, le=8)
    resource_slots: int = Field(ge=1, le=4)


class CandidateDeclaration(StrictForm):
    schema_version: Literal["raisa.historical_first_use_candidate_declaration.v1"] = (
        "raisa.historical_first_use_candidate_declaration.v1"
    )
    full_40_character_accepted_source_commit: Hex40
    candidate_sha256: Hex64
    closed_artifact_class: ArtifactClass
    exact_development_purpose: DevelopmentPurpose
    source_independent_synthetic_identity_policy: IdentityPolicy
    relative_or_shifted_date_policy: DatePolicy
    deterministic_zero_forbidden_field_reading: int = Field(ge=0, le=64)
    structural_utility_reading: StructuralUtilityReading
    non_transitive_authority_ceiling: AuthorityCeiling


class CandidateEnvelope(StrictForm):
    schema_version: Literal["raisa.historical_first_use_candidate_envelope.v1"] = (
        "raisa.historical_first_use_candidate_envelope.v1"
    )
    declaration: CandidateDeclaration
    candidate: CandidatePayload


class ExactArtifactBinding(StrictForm):
    schema_version: Literal["raisa.historical_first_use_exact_binding.v1"] = (
        "raisa.historical_first_use_exact_binding.v1"
    )
    accepted_source_commit: Hex40
    candidate_sha256: Hex64
    artifact_class: Literal["minimised_structural_scenario"]
    development_purpose: DevelopmentPurpose
    authority_ceiling: AuthorityCeiling
    non_transitive: Literal[True] = True


class AuthorityReading(StrictForm):
    schema_version: Literal["raisa.historical_first_use_authority_reading.v1"] = (
        "raisa.historical_first_use_authority_reading.v1"
    )
    exact_candidate_binding_created: bool
    candidate_materialisation_allowed_by_evaluator: Literal[False] = False
    archive_or_attempt_access_allowed: Literal[False] = False
    provider_model_product_database_client_or_runtime_allowed: Literal[False] = False
    ordinary_practice_allowed: Literal[False] = False
    production_deployment_release_pages_or_protected_refs_allowed: Literal[False] = (
        False
    )


class GateResult(StrictForm):
    schema_version: Literal["raisa.historical_first_use_gate_result.v1"] = (
        "raisa.historical_first_use_gate_result.v1"
    )
    evidence_label: Literal["authored_synthetic_gate_behavior_only"] = (
        "authored_synthetic_gate_behavior_only"
    )
    decision: Decision
    reason_codes: tuple[ReasonCode, ...]
    binding: ExactArtifactBinding | None
    authority: AuthorityReading

    @model_validator(mode="after")
    def _binding_matches_decision(self) -> GateResult:
        admitted = self.decision == "admitted_for_exact_declared_artifact_only"
        if admitted != (self.binding is not None):
            raise ValueError("gate_result_binding_decision_mismatch")
        if admitted != self.authority.exact_candidate_binding_created:
            raise ValueError("gate_result_authority_decision_mismatch")
        return self


def canonical_candidate_sha256(candidate: CandidatePayload) -> str:
    """Return one unambiguous digest for the exact typed candidate payload."""

    payload = json.dumps(
        candidate.model_dump(mode="json"),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def structural_utility(candidate: CandidatePayload) -> StructuralUtilityReading:
    """Compute the only utility reading accepted by the gate."""

    minutes = {event.relative_minute for event in candidate.events}
    return StructuralUtilityReading(
        event_count=len(candidate.events),
        distinct_relative_minutes=len(minutes),
        relative_minute_span=max(minutes) - min(minutes),
        distinct_event_kinds=len({event.event_kind for event in candidate.events}),
        synthetic_subject_slots=len(
            {event.synthetic_subject_slot for event in candidate.events}
        ),
        resource_slots=len({event.resource_slot for event in candidate.events}),
    )


def _result(
    decision: Decision,
    reasons: tuple[ReasonCode, ...],
    *,
    binding: ExactArtifactBinding | None = None,
) -> GateResult:
    return GateResult(
        decision=decision,
        reason_codes=reasons,
        binding=binding,
        authority=AuthorityReading(
            exact_candidate_binding_created=binding is not None,
        ),
    )


def evaluate(envelope: CandidateEnvelope) -> GateResult:
    """Evaluate one candidate without reading or writing any external state."""

    declaration = envelope.declaration
    candidate = envelope.candidate

    if declaration.full_40_character_accepted_source_commit != ACCEPTED_SOURCE_COMMIT:
        return _result("blocked", ("accepted_source_commit_not_exact",))

    if declaration.candidate_sha256 != canonical_candidate_sha256(candidate):
        return _result("blocked", ("candidate_digest_mismatch",))

    if declaration.deterministic_zero_forbidden_field_reading != 0:
        return _result("blocked", ("forbidden_field_reading_nonzero",))

    utility = structural_utility(candidate)
    if declaration.structural_utility_reading != utility:
        return _result("blocked", ("structural_utility_declaration_mismatch",))

    artifact_class = declaration.closed_artifact_class
    if artifact_class == "whole_day_or_near_lossless_replay":
        return _result("blocked", ("whole_day_or_near_lossless_replay_forbidden",))
    if artifact_class == "bounded_multi_event_scenario":
        return _result(
            "revision_required",
            ("bounded_multi_event_scenario_not_yet_admissible",),
        )

    reasons: list[ReasonCode] = []
    if not 3 <= utility.event_count <= 12:
        reasons.append("event_count_outside_minimised_range")
    if utility.distinct_relative_minutes < 3:
        reasons.append("insufficient_distinct_relative_minutes")
    if not 10 <= utility.relative_minute_span <= 120:
        reasons.append("relative_minute_span_outside_minimised_range")
    if utility.distinct_event_kinds < 2:
        reasons.append("insufficient_distinct_event_kinds")
    if utility.synthetic_subject_slots > 4:
        reasons.append("too_many_synthetic_subject_slots")
    if utility.resource_slots > 2:
        reasons.append("too_many_resource_slots")
    if reasons:
        return _result("revision_required", tuple(reasons))

    binding = ExactArtifactBinding(
        accepted_source_commit=ACCEPTED_SOURCE_COMMIT,
        candidate_sha256=declaration.candidate_sha256,
        artifact_class="minimised_structural_scenario",
        development_purpose=declaration.exact_development_purpose,
        authority_ceiling=declaration.non_transitive_authority_ceiling,
    )
    return _result(
        "admitted_for_exact_declared_artifact_only",
        (),
        binding=binding,
    )


def is_full_git_object_id(value: str) -> bool:
    """Expose the exact source-format predicate for deterministic tests."""

    return re.fullmatch(r"[0-9a-f]{40}", value) is not None
