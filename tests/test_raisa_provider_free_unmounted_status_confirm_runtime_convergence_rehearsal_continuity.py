from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-unmounted-status-confirm-runtime-convergence-rehearsal"
PARENT = "raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture"
SOURCE_HEAD = "a1629f2441e2bdb350d00c6d6016e94123ff0d8d"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_rehearsal_remains_an_accepted_continuity_ancestor() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)

    assert graph["graph_revision"] >= 260
    assert compass["map_revision"] >= 242
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert any(item["node_id"] == NODE_ID for item in compass["journey"])
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_rehearsal_opens_no_runtime_or_implementation_authority() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"]
        + node["claim_scope"]
        + node["unresolved_gates"]
    ).lower()

    assert node["authority"]["authorized_openings"] == []
    for phrase in (
        "implementation_authorized is false",
        "pure in-memory",
        "physical storage",
        "migration/backfill",
        "application/database execution",
        "providers",
        "product/patient",
        "commands",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_packet_acceptance_receipts_and_mailbox_are_bound() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)

    assert {
        "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-rehearsal/rehearsal-packet.json",
        "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-rehearsal/rehearsal-packet.schema.json",
        "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-runtime-convergence-rehearsal/provider-free-rehearsal-evidence.json",
    } <= set(node["evidence"]["findings"])
    assert len(node["evidence"]["receipts"]) == 3
    assert (
        "orchestration/human_inbox/yuri/2026-08-12--status-confirm-runtime-convergence-rehearsal.md"
        in node["evidence"]["closeouts"]
    )


def test_rehearsal_handoff_remains_read_only_physical_representability() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    journey = next(item for item in compass["journey"] if item["node_id"] == NODE_ID)
    joined = " ".join([journey["outcome"]] + node["unresolved_gates"]).lower()
    for phrase in (
        "read-only physical representability review",
        "appointment_state_version",
        "private receipts",
        "ordered lock boundary",
        "migration/backfill",
        "mounted-route parity",
        "postgresql behavior",
        "providers",
        "product/patient",
        "commands",
        "pages",
        "protected refs",
    ):
        assert phrase in joined
