import json
from copy import deepcopy
from pathlib import Path

import yaml

from scripts.ariadne_security_review_gate import evaluate_security_review


ROOT = Path(__file__).resolve().parents[1]
SETTINGS = yaml.safe_load(
    (ROOT / "orchestration/harness_settings/security_review_protocol.yaml").read_text(encoding="utf-8")
)
MANIFEST = json.loads(
    (ROOT / "orchestration/agent_inbox/codex/security-hardening-secure-sdlc-manifest.json").read_text(encoding="utf-8")
)


def test_current_security_sensitive_plan_requires_dual_and_purple_review() -> None:
    result = evaluate_security_review(MANIFEST, SETTINGS, phase="plan")
    assert result == {
        "schema_version": "ariadne.security_review_gate_receipt.v1",
        "phase": "plan",
        "status": "passed",
        "tier": "dual_review",
        "required_reviews": ["blue", "red"],
        "purple_required": True,
        "reasons": [],
    }


def test_material_sprint_fails_closed_for_incomplete_security_delta() -> None:
    manifest = deepcopy(MANIFEST)
    manifest["security_delta"]["abuse_cases"] = []
    result = evaluate_security_review(manifest, SETTINGS, phase="plan")
    assert result["status"] == "revision_required"
    assert "security_delta_field_missing:abuse_cases" in result["reasons"]


def test_non_material_classification_requires_sol_owned_rationale() -> None:
    manifest = deepcopy(MANIFEST)
    manifest["material_sprint"] = False
    manifest["materiality"] = {
        "classification": "non_material",
        "owner_resource_id": "worker",
        "rationale": "",
    }
    result = evaluate_security_review(manifest, SETTINGS, phase="plan")
    assert result["status"] == "revision_required"
    assert "materiality_owner_mismatch" in result["reasons"]
    assert "materiality_rationale_missing" in result["reasons"]
    assert "non_material_has_security_triggers" in result["reasons"]


def test_security_trigger_cannot_omit_independent_red_lane() -> None:
    manifest = deepcopy(MANIFEST)
    del manifest["reviews"]["red"]
    result = evaluate_security_review(manifest, SETTINGS, phase="plan")
    assert result["status"] == "revision_required"
    assert "required_review_missing:red" in result["reasons"]


def test_red_lane_must_be_fresh_and_asymmetric() -> None:
    manifest = deepcopy(MANIFEST)
    manifest["reviews"]["red"]["fresh_context"] = False
    manifest["reviews"]["red"]["packet_path"] = manifest["reviews"]["blue"]["packet_path"]
    result = evaluate_security_review(manifest, SETTINGS, phase="plan")
    assert result["status"] == "revision_required"
    assert "red_independence_missing:fresh_context" in result["reasons"]
    assert "asymmetric_review_packets_required" in result["reasons"]


def test_packet_path_alias_cannot_bypass_asymmetry() -> None:
    manifest = deepcopy(MANIFEST)
    manifest["reviews"]["red"]["packet_path"] = (
        "./orchestration/agent_inbox/codex/security-hardening-blue-packet.md"
    )
    result = evaluate_security_review(manifest, SETTINGS, phase="plan")
    assert "asymmetric_review_packets_required" in result["reasons"]


def test_purple_review_is_required_at_four_material_sprints() -> None:
    manifest = deepcopy(MANIFEST)
    manifest["triggers"] = []
    manifest["declared_tier"] = "routine_delta"
    result = evaluate_security_review(manifest, SETTINGS, phase="plan")
    assert result["tier"] == "routine_delta"
    assert result["purple_required"] is True


def test_purple_cadence_cannot_be_lowered_in_manifest() -> None:
    manifest = deepcopy(MANIFEST)
    manifest["purple_cadence"]["declared_material_sprints_since_purple"] = 0
    result = evaluate_security_review(manifest, SETTINGS, phase="plan")
    assert "purple_cadence_declared_count_mismatch" in result["reasons"]


def test_acceptance_blocks_unresolved_high_finding() -> None:
    manifest = deepcopy(MANIFEST)
    manifest["unresolved_findings"] = [{"id": "SEC-1", "severity": "high"}]
    result = evaluate_security_review(manifest, SETTINGS, phase="acceptance")
    assert result["status"] == "revision_required"
    assert "blocking_finding_unresolved:SEC-1" in result["reasons"]


def test_acceptance_rejects_malformed_and_case_varied_findings() -> None:
    manifest = deepcopy(MANIFEST)
    manifest["unresolved_findings"] = ["SEC-STRING", {"id": "SEC-HIGH", "severity": "High"}]
    result = evaluate_security_review(manifest, SETTINGS, phase="acceptance")
    assert "finding_schema_invalid:0" in result["reasons"]
    assert "finding_severity_not_canonical:SEC-HIGH" in result["reasons"]
    assert "blocking_finding_unresolved:SEC-HIGH" in result["reasons"]


def test_acceptance_requires_distinct_review_artifacts() -> None:
    manifest = deepcopy(MANIFEST)
    shared = "docs/ariadne-secure-sdlc-red-blue-protocol.md"
    manifest["reviews"]["blue"]["artifact_path"] = shared
    manifest["reviews"]["red"]["artifact_path"] = shared
    result = evaluate_security_review(manifest, SETTINGS, phase="acceptance")
    assert "independent_review_artifacts_required" in result["reasons"]


def test_acceptance_rejects_artifact_without_hash_and_candidate_binding() -> None:
    manifest = deepcopy(MANIFEST)
    manifest["reviews"]["blue"].update(
        {
            "decision": "pass",
            "artifact_path": "docs/ariadne-secure-sdlc-red-blue-protocol.md",
            "artifact_sha256": "wrong",
        }
    )
    result = evaluate_security_review(manifest, SETTINGS, phase="acceptance")
    assert "review_artifact_hash_mismatch:blue" in result["reasons"]
    assert "review_artifact_candidate_unbound:blue" in result["reasons"]


def test_acceptance_rejects_artifact_outside_repository(tmp_path: Path) -> None:
    manifest = deepcopy(MANIFEST)
    artifact = tmp_path / "review.md"
    artifact.write_text("DECISION: pass\n", encoding="utf-8")
    manifest["reviews"]["blue"].update(
        {"decision": "pass", "artifact_path": str(artifact), "artifact_sha256": "wrong"}
    )
    result = evaluate_security_review(manifest, SETTINGS, phase="acceptance")
    assert "review_artifact_outside_repository:blue" in result["reasons"]
