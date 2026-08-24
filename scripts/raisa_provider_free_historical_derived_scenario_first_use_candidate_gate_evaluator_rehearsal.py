"""Run the provider-free authored-synthetic first-use gate matrix."""

from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError

from orchestration_harness.historical_diary_first_use_candidate_gate import (
    ACCEPTED_SOURCE_COMMIT,
    CandidateDeclaration,
    CandidateEnvelope,
    CandidatePayload,
    GateResult,
    StructuralEvent,
    StructuralUtilityReading,
    canonical_candidate_sha256,
    evaluate,
    structural_utility,
)


class RehearsalForm(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class SchemaRejections(RehearsalForm):
    abbreviated_git_id: Literal[True]
    unknown_artifact_class: Literal[True]
    unknown_candidate_key: Literal[True]
    free_form_event_kind: Literal[True]
    out_of_range_integer: Literal[True]


class RehearsalReading(RehearsalForm):
    schema_version: Literal[
        "raisa.historical_first_use_gate_authored_synthetic_rehearsal.v1"
    ] = "raisa.historical_first_use_gate_authored_synthetic_rehearsal.v1"
    evidence_label: Literal["authored_synthetic_gate_behavior_only"] = (
        "authored_synthetic_gate_behavior_only"
    )
    positive: GateResult
    wrong_source: GateResult
    digest_mismatch: GateResult
    forbidden_field_nonzero: GateResult
    utility_declaration_mismatch: GateResult
    insufficient_minimised_utility: GateResult
    bounded_multi_event: GateResult
    whole_day_or_near_lossless: GateResult
    schema_rejections: SchemaRejections
    historical_candidate_materialised: Literal[False] = False
    first_use_gate_opened: Literal[False] = False


def _positive_candidate() -> CandidatePayload:
    return CandidatePayload(
        events=(
            StructuralEvent(
                event_kind="scheduled_slot_present",
                relative_minute=0,
                synthetic_subject_slot=0,
                resource_slot=0,
            ),
            StructuralEvent(
                event_kind="scheduled_slot_moved",
                relative_minute=10,
                synthetic_subject_slot=0,
                resource_slot=0,
            ),
            StructuralEvent(
                event_kind="scheduled_slot_added",
                relative_minute=30,
                synthetic_subject_slot=1,
                resource_slot=1,
            ),
            StructuralEvent(
                event_kind="scheduled_slot_format_changed",
                relative_minute=40,
                synthetic_subject_slot=1,
                resource_slot=1,
            ),
        )
    )


def _declaration(
    candidate: CandidatePayload,
    *,
    source: str = ACCEPTED_SOURCE_COMMIT,
    digest: str | None = None,
    artifact_class: str = "minimised_structural_scenario",
    forbidden_count: int = 0,
    utility: StructuralUtilityReading | None = None,
) -> CandidateDeclaration:
    return CandidateDeclaration.model_validate(
        {
            "full_40_character_accepted_source_commit": source,
            "candidate_sha256": digest or canonical_candidate_sha256(candidate),
            "closed_artifact_class": artifact_class,
            "exact_development_purpose": (
                "provider_free_reception_check_in_context_scenario_development"
            ),
            "source_independent_synthetic_identity_policy": (
                "source_independent_synthetic_identity_only"
            ),
            "relative_or_shifted_date_policy": "relative_day_offset_only",
            "deterministic_zero_forbidden_field_reading": forbidden_count,
            "structural_utility_reading": utility or structural_utility(candidate),
            "non_transitive_authority_ceiling": (
                "local_provider_free_development_test_only"
            ),
        }
    )


def _envelope(
    candidate: CandidatePayload, declaration: CandidateDeclaration
) -> CandidateEnvelope:
    return CandidateEnvelope(declaration=declaration, candidate=candidate)


def _schema_rejected(factory: object) -> Literal[True]:
    if not callable(factory):
        raise TypeError("schema_rejection_factory_not_callable")
    try:
        factory()
    except ValidationError:
        return True
    raise AssertionError("hostile_schema_case_was_not_rejected")


def run_rehearsal() -> RehearsalReading:
    positive_candidate = _positive_candidate()
    positive_declaration = _declaration(positive_candidate)

    insufficient = CandidatePayload(
        events=(
            StructuralEvent(
                event_kind="scheduled_slot_present",
                relative_minute=0,
                synthetic_subject_slot=0,
                resource_slot=0,
            ),
            StructuralEvent(
                event_kind="scheduled_slot_present",
                relative_minute=5,
                synthetic_subject_slot=0,
                resource_slot=0,
            ),
        )
    )
    mismatched_utility = structural_utility(positive_candidate).model_copy(
        update={"event_count": 3}
    )

    base_declaration = positive_declaration.model_dump(mode="python")
    return RehearsalReading(
        positive=evaluate(_envelope(positive_candidate, positive_declaration)),
        wrong_source=evaluate(
            _envelope(
                positive_candidate,
                _declaration(positive_candidate, source="0" * 40),
            )
        ),
        digest_mismatch=evaluate(
            _envelope(
                positive_candidate,
                _declaration(positive_candidate, digest="0" * 64),
            )
        ),
        forbidden_field_nonzero=evaluate(
            _envelope(
                positive_candidate,
                _declaration(positive_candidate, forbidden_count=1),
            )
        ),
        utility_declaration_mismatch=evaluate(
            _envelope(
                positive_candidate,
                _declaration(positive_candidate, utility=mismatched_utility),
            )
        ),
        insufficient_minimised_utility=evaluate(
            _envelope(insufficient, _declaration(insufficient))
        ),
        bounded_multi_event=evaluate(
            _envelope(
                positive_candidate,
                _declaration(
                    positive_candidate,
                    artifact_class="bounded_multi_event_scenario",
                ),
            )
        ),
        whole_day_or_near_lossless=evaluate(
            _envelope(
                positive_candidate,
                _declaration(
                    positive_candidate,
                    artifact_class="whole_day_or_near_lossless_replay",
                ),
            )
        ),
        schema_rejections=SchemaRejections(
            abbreviated_git_id=_schema_rejected(
                lambda: CandidateDeclaration.model_validate(
                    {
                        **base_declaration,
                        "full_40_character_accepted_source_commit": "7f9a526",
                    }
                )
            ),
            unknown_artifact_class=_schema_rejected(
                lambda: CandidateDeclaration.model_validate(
                    {
                        **base_declaration,
                        "closed_artifact_class": "helpful_replay",
                    }
                )
            ),
            unknown_candidate_key=_schema_rejected(
                lambda: CandidatePayload.model_validate(
                    {
                        **positive_candidate.model_dump(mode="python"),
                        "description": "free form is not admitted",
                    }
                )
            ),
            free_form_event_kind=_schema_rejected(
                lambda: StructuralEvent.model_validate(
                    {
                        "event_kind": "patient_arrived_with_note",
                        "relative_minute": 10,
                        "synthetic_subject_slot": 0,
                        "resource_slot": 0,
                    }
                )
            ),
            out_of_range_integer=_schema_rejected(
                lambda: StructuralEvent(
                    event_kind="scheduled_slot_present",
                    relative_minute=721,
                    synthetic_subject_slot=0,
                    resource_slot=0,
                )
            ),
        ),
    )


def main() -> int:
    reading = run_rehearsal()
    print(json.dumps(reading.model_dump(mode="json"), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
