from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-read-only-check-in-attempt-008-plan-admissibility-decision-plan.md"
THREAT = ROOT / "docs/security/raisa-provider-free-read-only-check-in-attempt-008-plan-admissibility-decision-threat-model-delta.md"
CONTRACT = ROOT / "orchestration/continuity/raisa-provider-free-read-only-check-in-attempt-008-plan-admissibility-decision/contract.json"
RECEIPT = ROOT / "orchestration/agent_inbox/codex/raisa-provider-free-read-only-check-in-attempt-008-plan-admissibility-decision-preplanning-receipt.json"
LATCH = ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_plan_freezes_exact_fourteen_rows_and_non_execution_verdict() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    contract = _json(CONTRACT)
    assert plan.count("| `P") == 14
    assert [row["id"] for row in contract["prerequisites"]] == [
        f"P{index:02d}" for index in range(1, 15)
    ]
    assert [row["expected_state"] for row in contract["prerequisites"]] == [
        *("satisfied" for _ in range(5)),
        *("plan_required" for _ in range(6)),
        *("preexecution_required" for _ in range(3)),
    ]
    assert contract["positive_verdict"] == "admissible_for_separate_plan_freeze"
    assert "never `ready_to_execute`" in plan


def test_plan_and_contract_use_full_machine_resolvable_sources() -> None:
    contract = _json(CONTRACT)
    assert re.fullmatch(r"[0-9a-f]{40}", contract["plan_source"])
    introducing_source = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", str(PLAN.relative_to(ROOT))],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()
    assert contract["plan_source"] == introducing_source
    assert all(
        re.fullmatch(r"[0-9a-f]{40}", row["source"])
        for row in contract["accepted_git_sources"]
    )


def test_receipt_and_latch_preserve_read_only_authority() -> None:
    receipt = _json(RECEIPT)
    latch = _json(LATCH)
    decision_id = (
        "raisa-provider-free-read-only-check-in-attempt-008-plan-admissibility-"
        "decision"
    )
    successor_id = "raisa-provider-free-check-in-relay-free-recovery-attempt-008"
    assert receipt["status"] == "passed"
    assert receipt["rehydration_sources"] == [
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ]
    assert receipt["git_ref_evidence_binding"]["manually_supplied_object_id_count"] == 0
    assert receipt["active_operation"]["operation_id"] == decision_id
    assert latch["operation_id"] in {decision_id, successor_id}
    if latch["operation_id"] == decision_id:
        assert (
            "no_attempt_008_plan_freeze_checkpoint_or_execution"
            in latch["protected_boundaries"]
        )
    else:
        assert latch["checkpoint"]["completed_stage"] == (
            f"Accepted {decision_id} at the machine-resolved source."
        )
        assert "p06_through_p14_remain_hard_fail_closed_conditions" in latch[
            "protected_boundaries"
        ]


def test_plan_and_threat_keep_forbidden_surfaces_closed() -> None:
    text = (
        PLAN.read_text(encoding="utf-8") + THREAT.read_text(encoding="utf-8")
    ).lower()
    for term in (
        "No attempt-008 plan",
        "No ordinary or serial pytest",
        "database conftest/engine",
        "protected-ref",
        "docs/branding/",
        "explicit-path staging",
    ):
        assert term.lower() in text
