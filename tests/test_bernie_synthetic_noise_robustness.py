from __future__ import annotations

import json

from app.services.bernie.synthetic_noise_robustness import (
    DEFAULT_REPORT_PATH,
    EXPECTED_CANDIDATE_HASH,
    EXPECTED_CANDIDATES,
    EXPECTED_OBSERVATIONS,
    FROZEN_SOURCE_COMMIT,
    _sha256,
    build_evaluation_scenarios,
)


def test_evaluation_adapter_preserves_each_frozen_semantic_anchor() -> None:
    evaluation = build_evaluation_scenarios()

    assert len(evaluation) == EXPECTED_CANDIDATES
    for candidate, seed, scenario in evaluation:
        contract = seed["semantic_contract"]
        assert scenario.scenario_id == candidate["candidate_id"]
        assert scenario.dialogue_turns == candidate["dialogue_turns"]
        assert scenario.intended_action == contract["intended_action"]
        assert scenario.action_semantics == contract["action_semantics"]
        assert scenario.temporal_relation == contract["temporal_relation"]
        assert scenario.normalized_values == contract["normalized_values"]
        assert scenario.expected_outcome_kind == contract["expected_outcome_kind"]
        assert scenario.expected_tool_sequence == contract["expected_tool_sequence"]
        assert scenario.expected_appointment_deltas == contract[
            "expected_appointment_deltas"
        ]
        assert scenario.expected_audit_deltas == contract["expected_audit_deltas"]
        assert scenario.provenance == "silver"
        assert scenario.adjudication == "pending"


def _committed_baseline() -> dict:
    return json.loads(DEFAULT_REPORT_PATH.read_text(encoding="utf-8"))


def test_committed_baseline_report_is_immutable_and_self_verifying() -> None:
    committed = json.loads(DEFAULT_REPORT_PATH.read_text(encoding="utf-8"))
    without_hash = {key: value for key, value in committed.items() if key != "report_hash"}
    assert committed["report_hash"] == (
        "sha256:18501cf5c8d28c0e660a9f5c7b15f7690622e44c90b248d51301c6ece03973c5"
    )
    assert _sha256(without_hash) == committed["report_hash"]


def test_baseline_is_complete_deterministic_and_safety_closed() -> None:
    report = _committed_baseline()

    assert report["decision"] == "baseline_complete"
    assert report["source_commit"] == FROZEN_SOURCE_COMMIT
    assert report["input_bindings"]["candidate_canonical_hash"] == (
        EXPECTED_CANDIDATE_HASH
    )
    assert report["population"]["candidates"] == EXPECTED_CANDIDATES
    assert report["population"]["observations"] == EXPECTED_OBSERVATIONS
    assert report["variance"] == {
        "variant_candidate_count": 0,
        "variant_candidate_ids": [],
    }
    assert report["dimension_counts"]["safety"] == {
        "passed": EXPECTED_OBSERVATIONS,
        "failed": 0,
        "total": EXPECTED_OBSERVATIONS,
    }
    assert not any(report["boundaries"].values())


def test_baseline_preserves_the_full_failure_map_without_source_utterances() -> None:
    report = _committed_baseline()
    population = report["population"]
    serialized = json.dumps(report, sort_keys=True)

    assert population["complete_candidates"] == 2
    assert population["failed_candidates"] == 190
    assert len(report["failure_cases"]) == 190
    assert '"utterance"' not in serialized
    assert report["candidate_breakdown"]["by_noise_level"] == {
        "high": {"total": 96, "complete": 1, "failed": 95},
        "medium": {"total": 96, "complete": 1, "failed": 95},
    }
    assert report["diagnostic_category_failure_observations"] == {
        "action_extraction": 228,
        "ambiguity_clarification": 208,
        "entity_semantics": 276,
        "policy_projection": 256,
        "replay_integration": 362,
        "temporal_normalization": 320,
    }
    assert report["primary_diagnostic_category_failure_observations"] == {
        "action_extraction": 228,
        "entity_semantics": 12,
        "replay_integration": 4,
        "temporal_normalization": 136,
    }
