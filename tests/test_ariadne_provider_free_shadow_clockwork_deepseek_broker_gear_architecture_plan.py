from __future__ import annotations

import json
from pathlib import Path

from orchestration_harness.active_operation import validate_active_operation


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-architecture-plan.md"
ARCHITECTURE = ROOT / "docs/ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-architecture.md"
THREAT = ROOT / "docs/security/ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-architecture-threat-model-delta.md"
RECEIPT = ROOT / "orchestration/agent_inbox/codex/ariadne-shadow-clockwork-deepseek-broker-gear-architecture-preplanning-receipt.json"
LATCH = ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"
SOURCE_HEAD = "a29e99c2fbfca59a24c348ded49dd29352b72aa3"
REVIEWED_SOURCE_HEAD = "f6cbd33fd3322754e06ac6dafa1503f5200e0803"
OPERATION_ID = "ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-architecture"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_plan_architecture_and_threat_have_exact_brisbane_headers() -> None:
    for path in (PLAN, ARCHITECTURE, THREAT):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-19" in head
        assert "Timestamp: 2026-08-19T05:20:02.5485051+10:00" in head
        assert SOURCE_HEAD in head


def test_preplanning_receipt_names_all_five_authority_sources() -> None:
    receipt = _json(RECEIPT)

    assert receipt["status"] == "passed"
    assert receipt["continuation_event"] == "pre_sprint_planning"
    assert receipt["rehydrated_from_receipt"] is True
    assert receipt["rehydration_sources"] == [
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ]
    assert set(receipt["source_evidence"]) == set(receipt["rehydration_sources"])


def test_preplanning_parallelism_assessment_is_explicit_and_bounded() -> None:
    assessment = _json(RECEIPT)["parallelism_assessment"]
    lanes = {item["lane_id"]: item for item in assessment["lanes"]}

    assert lanes["deepseek_flash"]["disposition"] == "declined"
    assert "HMR boot proof" in lanes["deepseek_flash"]["rationale"]
    assert lanes["gemini_verifier"]["disposition"] == "reserved"
    assert lanes["gemini_verifier"]["work_packages"]
    assert lanes["native_subagents"]["disposition"] == "declined"
    assert assessment["serial_constraints"]
    assert assessment["reassessment_triggers"]


def test_live_latch_validly_projects_the_new_operation_or_a_later_state() -> None:
    latch = _json(LATCH)
    assert validate_active_operation(latch) == latch
    assert len(latch["source_head"]) == 40
    assert set(latch["source_head"]) <= set("0123456789abcdef")

    if latch["operation_id"] == OPERATION_ID:
        assert latch["status"] in {"in_progress", "complete"}
        expected_source = (
            SOURCE_HEAD if latch["status"] == "in_progress" else REVIEWED_SOURCE_HEAD
        )
        assert latch["source_head"] == expected_source
        assert "single_writer_lease_and_acknowledged_terminal_digest_required" in (
            latch["protected_boundaries"]
        )
        assert "no_live_clockwork_adoption_or_current_control_retirement" in (
            latch["protected_boundaries"]
        )
        assert latch["terminal_response"]["permitted"] is (
            latch["status"] == "complete"
        )


def test_plan_freezes_zero_derived_fields_and_acknowledged_terminal_clutch() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "no caller-supplied Git object" in text
    assert "single-writer gear clutch" in text
    assert "exactly one terminal result receipt" in text
    assert "only Ariadne's acknowledgement reclaims" in text
    assert "financial budget mechanism" in text
    assert "at least 50 percent" in text


def test_plan_keeps_accepted_clock_and_broker_sources_read_only() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "orchestration_harness/transactional_closeout.py" in text
    assert "scripts/ariadne_deepseek_native_harness_broker.mjs" in text
    assert "read-only predecessor evidence" in text
    assert "`app/**`" in text


def test_threat_delta_preserves_provider_product_and_protected_boundaries() -> None:
    text = THREAT.read_text(encoding="utf-8")

    for threat_id in range(1, 19):
        assert f"CG-{threat_id:03d}" in text
    assert "No provider key" in text
    assert "No live clock adoption" in text
    assert "protected-ref movement" in text
    assert "docs/branding" in PLAN.read_text(encoding="utf-8")
