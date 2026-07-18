from __future__ import annotations

import ast
from copy import deepcopy
import json
from pathlib import Path

import pytest

from app.services.ai.evals.bernie_us_synthetic_development_readiness import (
    READY_DECISION,
    SCHEDULED_DECISION,
    build_readiness_report,
)


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "docs" / "bernie-t3r6-us-synthetic-development-policy.json"
REPORT_PATH = ROOT / "docs" / "bernie-t3r6-us-synthetic-development-report.json"
MODULE_PATH = (
    ROOT / "app" / "services" / "ai" / "evals"
    / "bernie_us_synthetic_development_readiness.py"
)


def _evidence() -> dict:
    return json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))


def _verify_controls(evidence: dict) -> None:
    for key in evidence["control_verification"]:
        evidence["control_verification"][key] = True


def test_committed_report_records_policy_but_stops_before_call() -> None:
    report = build_readiness_report(_evidence())
    assert report == json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert report["policy_decision"] == (
        "accepted_us_synthetic_development_after_au_2_5_retirement"
    )
    assert report["readiness_decision"] == SCHEDULED_DECISION
    assert report["transition_effective"] is False
    assert report["authorizes_provider_call"] is False


def test_gemini_3_5_flash_is_a_long_lived_location_controlled_us_candidate() -> None:
    report = build_readiness_report(_evidence())
    models = {item["model_id"]: item for item in report["model_assessments"]}
    candidate = models["gemini-3.5-flash"]
    assert candidate["required_development_location_available"] is True
    assert candidate["documented_runway_days"] == 305
    assert candidate["minimum_runway_satisfied"] is True
    assert candidate["eligible"] is True


def test_us_policy_becomes_effective_on_australian_2_5_retirement_date() -> None:
    evidence = _evidence()
    before = build_readiness_report(evidence, as_of="2026-10-15")
    on_date = build_readiness_report(evidence, as_of="2026-10-16")
    assert before["transition_effective"] is False
    assert on_date["transition_effective"] is True
    assert on_date["model_assessments"][0]["documented_runway_days"] == 215


def test_fully_verified_future_path_only_reaches_separate_call_approval() -> None:
    evidence = deepcopy(_evidence())
    _verify_controls(evidence)
    report = build_readiness_report(evidence, as_of="2026-10-16")
    assert report["readiness_decision"] == READY_DECISION
    assert report["eligible_models"] == ["gemini-3.5-flash"]
    assert report["authorizes_provider_call"] is False
    assert report["next_boundary"].startswith("obtain_exact_model")


@pytest.mark.parametrize(
    "control",
    [
        "vertex_ai_api_enabled",
        "billing_and_cost_acceptance_verified",
        "keyless_prediction_only_iam_verified",
        "us_location_pin_verified",
        "global_and_non_us_fallback_denied_verified",
        "data_access_audit_logging_verified",
        "request_response_logging_disabled_verified",
        "retention_and_abuse_monitoring_posture_verified",
        "grounding_tools_and_explicit_cache_disabled_verified",
        "application_hard_limit_and_kill_switch_verified",
    ],
)
def test_each_control_fails_closed_after_transition(control: str) -> None:
    evidence = _evidence()
    _verify_controls(evidence)
    evidence["control_verification"][control] = False
    report = build_readiness_report(evidence, as_of="2026-10-16")
    assert report["readiness_decision"] != READY_DECISION
    assert control in report["blocking_reasons"]


def test_us_development_never_authorizes_pii_production_or_automatic_fallback() -> None:
    evidence = _evidence()
    _verify_controls(evidence)
    report = build_readiness_report(evidence, as_of="2026-10-16")
    assert report["production_pii_location"] == "australia-southeast1"
    assert report["production_pii_earliest_review_year"] == 2027
    assert report["authorizes_pii"] is False
    assert report["authorizes_production"] is False
    assert report["automatic_location_fallback"] is False


def test_global_path_and_data_scope_expansion_are_rejected() -> None:
    evidence = _evidence()
    evidence["policy"]["development_location"] = "global"
    with pytest.raises(ValueError, match="US multi-region"):
        build_readiness_report(evidence)

    evidence = _evidence()
    evidence["policy"]["patient_or_practice_data_allowed"] = True
    with pytest.raises(ValueError, match="prohibited data"):
        build_readiness_report(evidence)


def test_global_availability_cannot_be_declared_location_controlled() -> None:
    evidence = _evidence()
    evidence["documentary_evidence"]["models"][0][
        "location_controlled_locations"
    ].append("global")
    with pytest.raises(ValueError, match="global availability"):
        build_readiness_report(evidence)


def test_reducer_has_no_provider_network_subprocess_or_runtime_imports() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported.isdisjoint(
        {
            "google",
            "vertexai",
            "requests",
            "httpx",
            "subprocess",
            "fastapi",
            "sqlalchemy",
            "app",
        }
    )
