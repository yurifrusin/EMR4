from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-provider-free-unmounted-delete-confirm-composition-product-adapter-implementation"
PARENT = "raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture"
SOURCE_HEAD = "43e993a98ffec3f9ffe2740b0b38816bcb2d6adb"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_delete_confirm_implementation_is_the_accepted_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)

    assert graph["graph_revision"] == 306
    assert compass["map_revision"] == 288
    assert compass["source_graph_revision"] == 306
    assert compass["current_position"]["node_id"] == NODE_ID
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["relationships"] == [{"node_id": PARENT, "relation": "builds_on"}]


def test_implementation_remains_unmounted_and_provider_free() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()

    assert node["authority"]["authorized_openings"] == []
    for phrase in (
        "server-owned ingress",
        "six-field private receipt",
        "523 tests",
        "seven-command gemini 3.7",
        "no canonical or hidden alias route",
        "product data",
        "protected-ref",
    ):
        assert phrase in joined


def test_recovery_and_clean_veto_are_preserved() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    receipts = set(node["evidence"]["receipts"])
    findings = set(node["evidence"]["findings"])

    assert "orchestration/agent_inbox/antigravity/raisa-delete-confirm-composition-product-adapter-gemini37-review-receipt.json" in receipts
    assert "orchestration/agent_inbox/codex/raisa-delete-confirm-composition-product-adapter-sol-recovery-lease.md" in findings
    assert "docs/ariadne-agent-error-correction-register-revision-313.md" in findings
    assert "docs/ariadne-agent-error-correction-register-revision-314.md" in findings
    assert "orchestration/human_inbox/yuri/2026-08-16--delete-confirm-composition-product-adapter-implementation.md" in node["evidence"]["closeouts"]


def test_next_candidate_is_read_only_route_mounting_readiness() -> None:
    compass = _load("orchestration/continuity/emr4-compass.json")
    current = compass["current_position"]
    joined = " ".join(current["unlocks"] + current["does_not_solve"]).lower()
    for phrase in (
        "provider-free read-only route-mounting readiness",
        "canonical/hidden alias",
        "route editing",
        "schema/database execution",
        "product data",
        "provider/credential",
        "protected refs",
    ):
        assert phrase in joined
