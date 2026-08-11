from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-agent-execution-surface-containment-gate-aes-c1"
SOURCE_HEAD = "285e60216cf22907e8a0f5596ece11f74f455c81"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_aes_c1_is_current_and_aes_c2_is_next() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")

    assert graph["graph_revision"] == 238
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 220
    assert compass["source_graph_revision"] == 238
    assert compass["current_position"]["node_id"] == NODE_ID
    orientation = compass["orientation_statement"].lower()
    assert "aes-c1 passes" in orientation
    assert "aes-c2 inert broker simulation is next" in orientation


def test_aes_c1_continuity_opens_no_runtime_authority() -> None:
    node = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]

    assert node["kind"] == "foundation"
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "unmounted",
        "no runtime broker",
        "work-cell process",
        "provider",
        "product context",
        "database/source",
        "network",
        "executable tool",
        "command",
        "protected evidence",
        "deployment",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_aes_c1_exact_evidence_and_user_mailbox_are_bound() -> None:
    node = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]

    assert node["contract_evidence"] == []
    assert {
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/admission-rehearsal-contract.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/admission-rehearsal-contract.schema.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/authored-synthetic-admission-scenarios.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/provider-free-admission-evidence.json",
    } <= set(node["evidence"]["findings"])
    assert (
        "orchestration/agent_inbox/antigravity/raisa-aes-c1-provider-free-admission-review-receipt.json"
        in node["evidence"]["receipts"]
    )
    assert (
        "orchestration/human_inbox/yuri/2026-08-11--aes-c1-provider-free-admission.md"
        in node["evidence"]["closeouts"]
    )
    assert node["status"] == "accepted"


def test_compass_handoff_is_one_inert_adapter_only() -> None:
    position = _load("orchestration/continuity/emr4-compass.json")["current_position"]
    joined = " ".join(position["unlocks"] + position["does_not_solve"]).lower()

    for phrase in (
        "one inert allowlisted",
        "never receives a credential",
        "destination, method or executable",
        "real runtime broker",
        "patient/product/clinical",
        "provider",
        "database/source",
        "command",
        "protected-ref",
    ):
        assert phrase in joined
