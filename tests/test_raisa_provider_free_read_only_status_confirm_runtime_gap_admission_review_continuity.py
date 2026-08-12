from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-read-only-status-confirm-runtime-gap-admission-review"
SOURCE_HEAD = "426ccbbd26a2ab0bfb70c65d7adce113f0239f3a"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_gap_review_remains_an_accepted_continuity_ancestor() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)

    assert graph["graph_revision"] >= 258
    assert compass["map_revision"] >= 240
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert any(item["node_id"] == NODE_ID for item in compass["journey"])
    assert node["status"] == "accepted"
    assert node["coordinates"]["source_head"] == SOURCE_HEAD


def test_gap_review_preserves_the_negative_admission_boundary() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"]
        + node["claim_scope"]
        + node["unresolved_gates"]
    ).lower()

    assert node["authority"]["authorized_openings"] == []
    for phrase in (
        "not_admitted",
        "seven blocker",
        "two partial",
        "no application edit",
        "route edit",
        "database execution",
        "provider/credential",
        "product/patient",
        "commands",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_gap_review_evidence_and_mailbox_are_bound() -> None:
    nodes = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"]
    node = next(item for item in nodes if item["id"] == NODE_ID)

    assert {
        "orchestration/continuity/raisa-provider-free-read-only-status-confirm-runtime-gap-admission-review/runtime-gap-review-contract.json",
        "orchestration/continuity/raisa-provider-free-read-only-status-confirm-runtime-gap-admission-review/runtime-gap-review-contract.schema.json",
        "orchestration/continuity/raisa-provider-free-read-only-status-confirm-runtime-gap-admission-review/runtime-gap-review-evidence.json",
    } <= set(node["evidence"]["findings"])
    assert (
        "orchestration/human_inbox/yuri/2026-08-12--status-confirm-runtime-gap-admission-review.md"
        in node["evidence"]["closeouts"]
    )


def test_next_direction_remains_unmounted_and_non_executing() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    journey = next(item for item in compass["journey"] if item["node_id"] == NODE_ID)
    joined = " ".join(
        [journey["outcome"]] + node["unresolved_gates"]
    ).lower()

    assert "unmounted status-confirm runtime convergence architecture" in joined
    for phrase in (
        "route edit",
        "database execution",
        "runtime kernel",
        "raw-route change",
        "provider/credential",
        "product/patient",
        "commands",
        "deployment",
        "pages",
        "protected refs",
    ):
        assert phrase in joined
