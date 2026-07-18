from __future__ import annotations

import ast
from copy import deepcopy
import json
from pathlib import Path

import pytest

from app.services.ai.evals.bernie_vertex_au_readiness import (
    BLOCKED_DECISION,
    READY_DECISION,
    build_readiness_report,
)


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "docs" / "bernie-t3r5-vertex-au-feasibility.json"
REPORT_PATH = ROOT / "docs" / "bernie-t3r5-vertex-au-readiness-report.json"
MODULE_PATH = ROOT / "app" / "services" / "ai" / "evals" / "bernie_vertex_au_readiness.py"


def _evidence() -> dict:
    return json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))


def _make_controls_ready(evidence: dict) -> None:
    observations = evidence["local_observations"]
    observations.update(
        {
            "vertex_ai_api_enabled": True,
            "billing_enabled": True,
            "project_environment_pin_present": True,
            "location_environment_pin": "australia-southeast1",
            "vertex_transport_environment_pin_present": True,
        }
    )
    for key in evidence["control_verification"]:
        evidence["control_verification"][key] = True


def test_committed_report_is_exact_and_stays_blocked() -> None:
    expected = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    actual = build_readiness_report(_evidence())
    assert actual == expected
    assert actual["decision"] == BLOCKED_DECISION
    assert actual["authorizes_provider_call"] is False


def test_current_successors_lack_sydney_and_legacy_model_has_only_90_days() -> None:
    report = build_readiness_report(_evidence())
    models = {item["model_id"]: item for item in report["model_assessments"]}
    assert models["gemini-3.5-flash"]["required_location_available"] is False
    assert models["gemini-3.1-flash-lite"]["required_location_available"] is False
    assert models["gemini-2.5-flash"]["required_location_available"] is True
    assert models["gemini-2.5-flash"]["documented_runway_days"] == 90
    assert models["gemini-2.5-flash"]["minimum_runway_satisfied"] is False
    assert report["eligible_models"] == []


def test_global_endpoint_never_satisfies_sydney_policy() -> None:
    evidence = _evidence()
    candidate = evidence["documentary_evidence"]["models"][0]
    candidate["available_locations"] = ["global"]
    candidate["regional_isolation"] = False
    _make_controls_ready(evidence)
    report = build_readiness_report(evidence)
    assert report["decision"] == BLOCKED_DECISION
    assert "no_ga_model_has_both_sydney_availability_and_minimum_runway" in report["blocking_reasons"]


@pytest.mark.parametrize(
    "control",
    [
        "prediction_only_iam_verified",
        "data_access_audit_logging_verified",
        "request_response_logging_disabled_verified",
        "australian_resource_location_policy_verified",
        "global_endpoint_denied_verified",
        "retention_and_abuse_monitoring_posture_verified",
        "cost_acceptance_recorded",
        "billing_budget_alert_verified",
        "application_hard_limit_and_kill_switch_verified",
    ],
)
def test_each_sensitive_control_fails_closed(control: str) -> None:
    evidence = _evidence()
    candidate = evidence["documentary_evidence"]["models"][0]
    candidate["available_locations"] = ["australia-southeast1"]
    candidate["regional_isolation"] = True
    _make_controls_ready(evidence)
    evidence["control_verification"][control] = False
    report = build_readiness_report(evidence)
    assert report["decision"] == BLOCKED_DECISION
    assert control in report["blocking_reasons"]


def test_hypothetical_long_lived_sydney_successor_only_reaches_separate_approval_gate() -> None:
    evidence = deepcopy(_evidence())
    candidate = evidence["documentary_evidence"]["models"][0]
    candidate["available_locations"] = ["australia-southeast1"]
    candidate["regional_isolation"] = True
    _make_controls_ready(evidence)
    report = build_readiness_report(evidence)
    assert report["decision"] == READY_DECISION
    assert report["eligible_models"] == ["gemini-3.5-flash"]
    assert report["authorizes_provider_call"] is False
    assert report["next_boundary"].startswith("obtain_separate_user_approval")


def test_policy_rejects_non_sydney_location_and_authority_expansion() -> None:
    evidence = _evidence()
    evidence["policy"]["required_location"] = "global"
    with pytest.raises(ValueError, match="Sydney"):
        build_readiness_report(evidence)

    evidence = _evidence()
    evidence["scope"]["product_runtime_wiring"] = True
    with pytest.raises(ValueError, match="prohibited authority"):
        build_readiness_report(evidence)


def test_reducer_has_no_cloud_sdk_network_subprocess_or_runtime_imports() -> None:
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
