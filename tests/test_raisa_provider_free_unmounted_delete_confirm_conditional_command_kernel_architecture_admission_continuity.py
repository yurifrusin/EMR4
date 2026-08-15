from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = (
    "raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-"
    "architecture-admission"
)
OPERATION_ID = (
    "raisa-reception-one-delete-confirm-conditional-command-kernel-"
    "architecture-admission"
)
SOURCE_HEAD = "356b28a1750e7a7b379406e864f2a3501606938a"
NEXT_HORIZON_ID = "reception-one-delete-confirm-physical-representability"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_delete_confirm_kernel_is_current_at_exact_reviewed_source() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] >= 296
    assert compass["map_revision"] >= 278
    assert compass["source_graph_revision"] == graph["graph_revision"]
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["authority"]["authorized_openings"] == []


def test_continuity_preserves_contract_and_claim_boundary() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    joined = " ".join(node["claim_scope"] + node["unresolved_gates"]).lower()
    for phrase in (
        "practice, appointment and idempotency lock order",
        "24-field signed evidence",
        "publish atomically",
        "67 hostile mutations",
        "first-party reference client",
        "external adapters remain closed",
        "no accepted physical postgresql mapping",
        "real locking, isolation, concurrency",
    ):
        assert phrase in joined


def test_compass_advances_only_to_physical_representability() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    next_horizon = next(
        item
        for item in compass["decision_horizon"]
        if item["id"] == NEXT_HORIZON_ID
    )
    assert next_horizon["status"] == "active"
    assert next_horizon["boundary_changes"] == []
    joined = " ".join(next_horizon["prerequisites"]).lower()
    assert "provider-free read-only" in joined
    assert "no mounted route" in joined
    assert all(
        item["id"] != "reception-one-delete-confirm-conditional-command-kernel"
        for item in compass["decision_horizon"]
    )


def test_latch_completes_without_user_attention() -> None:
    latch = _load(
        "orchestration/continuity/ariadne-active-operation-latch/current.json"
    )
    assert latch["operation_id"] == OPERATION_ID
    assert latch["status"] == "complete"
    assert latch["source_head"] == SOURCE_HEAD
    assert latch["checkpoint"]["next_executable_stage"] is None
    assert latch["resume_after_compaction"] is False
    assert latch["user_attention"]["required"] is False
    assert latch["terminal_response"]["permitted"] is True


def test_new_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/raisa-authority-kernel-reference-client-adapter-seam.md",
        "docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission-rehearsal-closeout.md",
        "orchestration/agent_inbox/codex/raisa-delete-confirm-conditional-command-kernel-architecture-admission-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-15--delete-confirm-conditional-command-kernel-architecture-admission.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:14])
        assert "Date: 2026-08-15" in head
        assert "Timestamp: 2026-08-15T" in head
        assert "+10:00 (Australia/Brisbane)" in head


def test_handover_and_plan_name_result_next_gate_and_reference_client() -> None:
    handover = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    plan = " ".join((ROOT / "implementation_plan.md").read_text(encoding="utf-8").split())
    for text in (handover, plan):
        assert "356b28a1750e7a7b379406e864f2a3501606938a" in text
        assert "physical representability" in text.lower()
        assert "reference client" in text.lower()
    assert "Continuity 296 / Compass 278" in handover
    assert (
        "raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission_pass"
        in handover
    )


def test_reference_client_direction_is_fail_closed_and_does_not_open_channels() -> None:
    text = (
        ROOT / "docs/raisa-authority-kernel-reference-client-adapter-seam.md"
    ).read_text(encoding="utf-8")
    normalized = " ".join(text.split()).lower()
    for phrase in (
        "authority-bearing protocol",
        "first-party native reference client",
        "Unknown required fields",
        "fail closed",
        "identity, account binding",
        "revocable delegation",
        "privacy",
        "first-party reference client for clinical work",
        "clinician attestation",
        "regulated-integration class",
        "source-labelled external evidence",
        "provider-agnostic but provider-qualified",
        "no present safety",
        "creates no external patient client",
    ):
        assert phrase.lower() in normalized
