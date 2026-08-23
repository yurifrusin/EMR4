from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-unmounted-default-off-canonical-check-in-environment-evidence-admission-input-seam-rehearsal-plan.md"
THREAT = ROOT / "docs/security/raisa-provider-free-unmounted-default-off-canonical-check-in-environment-evidence-admission-input-seam-rehearsal-threat-model-delta.md"
CONTRACT = ROOT / "orchestration/continuity/raisa-provider-free-unmounted-default-off-canonical-check-in-environment-evidence-admission-input-seam-rehearsal/contract.json"
RECEIPT = ROOT / "orchestration/agent_inbox/codex/raisa-check-in-environment-evidence-admission-input-seam-preplanning-receipt.json"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_plan_freezes_the_narrow_default_off_seam() -> None:
    text = PLAN.read_text(encoding="utf-8")
    for required in (
        "calls `evaluate_admission` first",
        "ordinary_activation_closed",
        "ordinary_evidence_missing",
        "Authored-synthetic-only admission is unchanged",
        "zero automatic retry",
        "accepted_or_recovered",
        "No ordinary practice is enabled",
    ):
        assert required.lower() in text.lower()


def test_contract_preserves_every_existing_control_and_releases_no_ordinary_admission() -> None:
    contract = _json(CONTRACT)
    assert contract["seam"]["calls_existing_kernel_first"] is True
    assert contract["seam"]["ordinary_admission_release_possible"] is False
    assert contract["reading_requirements"]["exact_type"] == "EnvironmentEvidenceGateReading"
    assert contract["reading_requirements"]["subclass_or_duck_type_allowed"] is False
    assert "operational_evidence_valid_boolean" in contract["preserved_controls"]
    assert contract["verification"]["ordinary_release_count"] == 0
    assert all(value is False for value in contract["closed_boundaries"].values())


def test_worker_packet_is_bounded_to_two_paths_and_three_tools() -> None:
    worker = _json(CONTRACT)["worker"]
    assert worker["transport"] == "deepseek_native_harness"
    assert worker["owned_paths"] == [
        "orchestration_harness/check_in_environment_evidence_admission.py",
        "tests/test_check_in_environment_evidence_admission.py",
    ]
    assert worker["effective_tools"] == ["edit", "glob", "read"]
    assert worker["automatic_retries"] == 0
    assert worker["fallbacks"] == 0
    assert worker["auxiliary_models"] == 0


def test_threat_delta_covers_substitution_replay_and_harness_scope() -> None:
    text = THREAT.read_text(encoding="utf-8").lower()
    for required in (
        "boolean or duck-typed",
        "another environment",
        "another admission generation",
        "another manifest",
        "exact `edit`, `glob`, `read`",
        "zero automatic retry",
        "no live manifest",
    ):
        assert required in text


def test_fresh_orchestrator_receipt_names_all_five_sources_and_lanes() -> None:
    receipt = _json(RECEIPT)
    assert receipt["status"] == "passed"
    assert receipt["rehydration_sources"] == [
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ]
    lanes = {row["lane_id"]: row for row in receipt["parallelism_assessment"]["lanes"]}
    assert lanes["deepseek_flash"]["disposition"] == "planned"
    assert lanes["gemini_verifier"]["disposition"] == "reserved"
    assert lanes["native_subagents"]["disposition"] == "declined"
