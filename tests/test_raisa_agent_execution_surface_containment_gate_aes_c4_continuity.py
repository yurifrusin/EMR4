from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-agent-execution-surface-containment-gate-aes-c4"
SOURCE_HEAD = "e569da0a9081117b799e9437d8b7025230e2162b"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_aes_c4_is_current_and_aes_c5_requires_a_product_data_choice() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")

    assert graph["graph_revision"] == 241
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 223
    assert compass["source_graph_revision"] == 241
    assert compass["current_position"]["node_id"] == NODE_ID
    orientation = compass["orientation_statement"].lower()
    assert "aes-c4 passes" in orientation
    assert "aes-c5 remains closed" in orientation
    assert "product source" in orientation
    assert "yuri" in orientation


def test_aes_c4_consumes_one_call_and_opens_no_continuing_authority() -> None:
    node = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]

    assert node["kind"] == "foundation"
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "exactly one",
        "ledger is terminal",
        "no continuing provider call",
        "product read",
        "database/source",
        "filesystem capability",
        "provider tool",
        "command/write",
        "reusable runtime",
        "product-derived data",
        "deployment",
        "pages",
        "protected refs",
    ):
        assert phrase in joined


def test_aes_c4_exact_evidence_review_acceptance_and_mailbox_are_bound() -> None:
    node = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]

    assert node["contract_evidence"] == []
    assert {
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c4/provider-envelope.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c4/live-preexecution-cloud-preflight.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c4/occupied-provider-proof-evidence.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c4/occupied-provider-proof-ledger.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c4/provider-free-factual-rebind-invalid-source-evidence.json",
    } <= set(node["evidence"]["findings"])
    assert (
        "orchestration/agent_inbox/antigravity/raisa-aes-c4-provider-proof-rebind-review-receipt.json"
        in node["evidence"]["receipts"]
    )
    assert (
        "orchestration/agent_inbox/codex/raisa-aes-c4-bounded-occupied-provider-proof-sol-acceptance.md"
        in node["evidence"]["acceptances"]
    )
    assert (
        "orchestration/human_inbox/yuri/2026-08-11--aes-c4-bounded-occupied-provider-proof.md"
        in node["evidence"]["closeouts"]
    )
    assert node["status"] == "accepted"


def test_compass_handoff_names_exact_aes_c5_attention_fork() -> None:
    position = _load("orchestration/continuity/emr4-compass.json")["current_position"]
    joined = " ".join(position["unlocks"] + position["does_not_solve"]).lower()

    for phrase in (
        "one exact real product source",
        "one exact purpose",
        "privacy",
        "principal/identity",
        "tenant",
        "field",
        "freshness",
        "retention",
        "proofreader",
        "provider",
        "cost",
        "cleanup",
        "no-command",
        "patient",
        "database/source",
        "command/write",
        "protected-ref",
    ):
        assert phrase in joined
