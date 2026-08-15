from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-reception-one-cancellation-command-path-readiness-review"
SOURCE_HEAD = "bb36e19c774eb1bc4ace8cafc6ae2b5c35bc8735"
DECISION_ID = "reception-one-appointment-cancellation-direction"
NEXT_HORIZON_ID = "reception-one-delete-confirm-conditional-command-kernel"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_readiness_review_is_current_at_exact_reviewed_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 295
    assert compass["map_revision"] >= 277
    assert compass["source_graph_revision"] == graph["graph_revision"]
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["authority"]["authorized_openings"] == []


def test_continuity_preserves_exact_readiness_finding_and_claim_boundary() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    joined = " ".join(node["claim_scope"] + node["unresolved_gates"]).lower()
    for phrase in (
        "explicit confirmation",
        "does not lock the appointment",
        "current actor authority",
        "404 fallback",
        "omits free-text cancellation reason",
        "repository_static_authored_synthetic",
        "raw compatibility delete remains mounted",
    ):
        assert phrase in joined


def test_compass_resolves_cancellation_choice_and_plans_only_unmounted_kernel() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    decision = next(
        item for item in compass["decision_horizon"] if item["id"] == DECISION_ID
    )
    next_horizon = next(
        item
        for item in compass["decision_horizon"]
        if item["id"] == NEXT_HORIZON_ID
    )
    assert decision["status"] == "active"
    assert all(item["id"] != DECISION_ID for item in compass["user_owned_decisions"])
    assert next_horizon["status"] == "active"
    assert "unmounted" in " ".join(next_horizon["prerequisites"]).lower()
    assert next_horizon["boundary_changes"] == []


def test_latch_completes_and_continues_to_authorized_descendant() -> None:
    latch = _load(
        "orchestration/continuity/ariadne-active-operation-latch/current.json"
    )
    assert latch["operation_id"] == NODE_ID
    assert latch["status"] == "complete"
    assert latch["source_head"] == SOURCE_HEAD
    assert latch["checkpoint"]["next_executable_stage"] is None
    assert latch["resume_after_compaction"] is False
    assert latch["user_attention"]["required"] is False
    assert latch["terminal_response"]["permitted"] is True


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-reception-one-cancellation-command-path-readiness-review-closeout.md",
        "orchestration/agent_inbox/codex/raisa-reception-one-cancellation-command-path-readiness-review-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-15--reception-one-cancellation-command-path-readiness-review.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-15" in head
        assert "Timestamp: 2026-08-15T" in head
        assert "+10:00 (Australia/Brisbane)" in head


def test_handover_and_plan_name_result_and_next_unmounted_tranche() -> None:
    handover = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    plan = " ".join((ROOT / "implementation_plan.md").read_text(encoding="utf-8").split())
    assert "Continuity 295 / Compass 277" in handover
    assert "raisa_reception_one_cancellation_command_path_readiness_review_pass" in handover
    assert "provider-free unmounted delete-confirm conditional-command kernel" in handover
    assert "bb36e19c774eb1bc4ace8cafc6ae2b5c35bc8735" in plan
    assert "unmounted delete-confirm conditional-command" in plan
