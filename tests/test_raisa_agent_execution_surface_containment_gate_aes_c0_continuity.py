from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-agent-execution-surface-containment-gate-aes-c0"
SOURCE_HEAD = "01d355f42df5981341196f3aa0caec2cccce7a2d"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_aes_c0_is_current_and_aes_c1_is_next_after_explicit_pause() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")

    assert graph["graph_revision"] == 237
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 219
    assert compass["source_graph_revision"] == 237
    assert compass["current_position"]["node_id"] == NODE_ID
    orientation = compass["orientation_statement"].lower()
    assert "aes-c0 passes" in orientation
    assert "fresh task window before aes-c1" in orientation


def test_aes_c0_continuity_opens_no_runtime_authority() -> None:
    node = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]

    assert node["kind"] == "foundation"
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "no capability broker",
        "work-cell",
        "provider",
        "product context",
        "database/source",
        "tool",
        "command",
        "protected evidence",
        "deployment",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_aes_c0_contract_and_user_mailbox_are_bound() -> None:
    node = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]

    assert node["contract_evidence"] == []
    assert {
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/architecture-contract.json"
        ,
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/architecture-contract.schema.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/authored-synthetic-contract-examples.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/provider-free-acceptance-evidence.json",
    } <= set(node["evidence"]["findings"])
    assert (
        "orchestration/human_inbox/yuri/2026-08-11--aes-c0-architecture-contract.md"
        in node["evidence"]["closeouts"]
    )
    assert node["status"] == "accepted"


def test_compass_handoff_is_provider_free_admission_only() -> None:
    position = _load("orchestration/continuity/emr4-compass.json")[
        "current_position"
    ]
    joined = " ".join(position["unlocks"] + position["does_not_solve"]).lower()

    for phrase in (
        "authored-synthetic admission",
        "manifest/grant/lease intersection",
        "default denial",
        "runtime broker",
        "patient/product/clinical",
        "provider",
        "database/source",
        "command",
        "protected-ref",
    ):
        assert phrase in joined
