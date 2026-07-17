"""Focused integrity tests for the unchanged-product v2 robustness baseline."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from app.services.bernie.synthetic_noise_v2_robustness import (
    DEFAULT_REPORT_PATH_V2,
    build_v2_evaluation_scenarios,
    build_v2_robustness_report,
    check_v2_robustness_report,
)


def test_v2_evaluation_population_is_exact_admission() -> None:
    evaluation = build_v2_evaluation_scenarios()
    assert len(evaluation) == 192
    assert len({candidate["candidate_id"] for candidate, _, _ in evaluation}) == 192


def test_candidate_adapter_preserves_anchor_oracle_and_dialogue_only() -> None:
    for candidate, anchor, scenario in build_v2_evaluation_scenarios():
        contract = anchor["semantic_contract"]
        assert scenario.dialogue_turns == candidate["dialogue_turns"]
        assert scenario.source_spans == {
            key: [type(scenario.source_spans[key][0]).model_validate(span) for span in spans]
            for key, spans in candidate["evidence_spans"].items()
        }
        assert scenario.intended_action == contract["intended_action"]
        assert scenario.expected_outcome_kind == contract["expected_outcome_kind"]
        assert scenario.expected_tool_sequence == contract["expected_tool_sequence"]
        assert scenario.expected_appointment_deltas == contract["expected_appointment_deltas"]
        assert scenario.expected_audit_deltas == contract["expected_audit_deltas"]


def test_v2_baseline_is_complete_safe_and_deterministic_evidence() -> None:
    report = build_v2_robustness_report()
    assert report["decision"] == "baseline_complete"
    assert report["population"]["candidates"] == 192
    assert report["population"]["observations"] == 384
    assert report["safety"] == {"passed": 384, "failed": 0, "total": 384}
    assert report["variance"]["variant_candidate_count"] == 0
    assert len(report["candidate_cases"]) == 192


def test_committed_v2_baseline_regenerates_exactly() -> None:
    assert check_v2_robustness_report() == []
    assert json.loads(DEFAULT_REPORT_PATH_V2.read_text(encoding="utf-8")) == build_v2_robustness_report()


def test_report_binds_admission_and_preserves_closed_boundaries() -> None:
    report = build_v2_robustness_report()
    assert report["input_bindings"]["candidate_hash"].startswith("sha256:")
    assert report["input_bindings"]["admission_hash"].startswith("sha256:")
    assert report["boundaries"] == {
        "protected_holdout_access": False,
        "historical_diary_access": False,
        "external_corpus_access": False,
        "provider_access": False,
        "product_write": False,
        "bounded_parser_refinements_present": True,
        "policy_changes": False,
        "replay_changes": False,
        "scorer_changes": False,
    }


def test_interpretation_call_has_no_expected_keyword_arguments() -> None:
    path = Path("app/services/bernie/synthetic_noise_v2_robustness.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "deterministic_interpret"
    ]
    assert len(calls) == 1
    assert len(calls[0].args) == 1
    assert calls[0].keywords == []
