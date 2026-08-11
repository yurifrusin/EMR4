from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "raisa-agent-execution-surface-containment-gate-aes-c5"
SOURCE_HEAD = "4e5d96ada19c51432fa4db46c76e23c952147c52"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_aes_c5_is_current_and_completes_the_finite_aes_sequence() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")

    assert graph["graph_revision"] == 242
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 224
    assert compass["source_graph_revision"] == 242
    assert compass["current_position"]["node_id"] == NODE_ID
    orientation = compass["orientation_statement"].lower()
    for phrase in (
        "aes-c5 completes",
        "aes-c0 through aes-c5",
        "authenticated practice-scoped",
        "one minimized sydney vertex call",
        "consumed ledgers",
        "no aes-c6",
        "yuri-owned programme choice",
    ):
        assert phrase in orientation


def test_aes_c5_opens_no_continuing_authority() -> None:
    node = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]

    assert node["kind"] == "foundation"
    assert node["status"] == "accepted"
    assert node["authority"]["authorized_openings"] == []
    joined = " ".join(
        node["authority"]["notes"] + node["claim_scope"] + node["unresolved_gates"]
    ).lower()
    for phrase in (
        "exactly one authenticated",
        "exactly one sydney vertex call",
        "separate one-grant, one-destination",
        "both ledgers are terminal",
        "no aes-c6",
        "real practice population",
        "patient/clinical data",
        "product/database read",
        "filesystem capability",
        "provider tool",
        "command/write",
        "deployment",
        "pages",
        "protected-ref",
    ):
        assert phrase in joined


def test_aes_c5_exact_source_provider_and_cleanup_evidence_are_bound() -> None:
    node = _load("orchestration/continuity/emr4-continuity-graph.json")["nodes"][-1]

    findings = set(node["evidence"]["findings"])
    assert {
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c5/product-runtime-envelope.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c5/local-fake-core-evidence.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c5/live-preexecution-cloud-preflight.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c5/occupied-core-evidence.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c5/occupied-lifecycle-evidence.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c5/occupied-ledgers/source-ledger.json",
        "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c5/occupied-ledgers/provider-ledger.json",
    } <= findings
    assert (
        "orchestration/agent_inbox/antigravity/raisa-aes-c5-gemini-36-high-review-receipt.json"
        in node["evidence"]["receipts"]
    )
    assert (
        "orchestration/agent_inbox/codex/raisa-aes-c5-product-runtime-admission-sol-acceptance.md"
        in node["evidence"]["acceptances"]
    )
    assert (
        "orchestration/human_inbox/yuri/2026-08-11--aes-c5-product-runtime-admission.md"
        in node["evidence"]["closeouts"]
    )


def test_compass_handoff_requires_a_new_programme_choice() -> None:
    position = _load("orchestration/continuity/emr4-compass.json")["current_position"]
    joined = " ".join(position["unlocks"] + position["does_not_solve"]).lower()

    for phrase in (
        "new exact source",
        "principal",
        "purpose",
        "retention",
        "provider/cost",
        "proofreader",
        "cleanup",
        "no aes-c6",
        "yuri-owned programme choice",
        "patient",
        "production identity",
        "reusable broker/runtime",
        "command/write",
        "credential/iam",
        "protected-ref",
    ):
        assert phrase in joined
