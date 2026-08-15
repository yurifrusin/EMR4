from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "ariadne-provider-free-continuity-journal-and-refinement-promotion-safeguards"
PRODUCT_POSITION = (
    "raisa-provider-free-unmounted-delete-confirm-physical-design-architecture"
)
SOURCE_HEAD = "79f5d6cf1cbe4ca9ad4893f257e92eccfd2ac2ce"


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_safeguards_are_accepted_without_displacing_product_position() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    compass = _load("orchestration/continuity/emr4-compass.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    assert graph["graph_revision"] >= 299
    assert compass["map_revision"] >= 281
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert compass["current_position"]["node_id"] == PRODUCT_POSITION
    assert node["coordinates"]["source_head"] == SOURCE_HEAD
    assert node["authority"]["authorized_openings"] == []


def test_safeguard_evidence_exists_and_stays_harness_only() -> None:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    node = next(item for item in graph["nodes"] if item["id"] == NODE_ID)
    evidence = node["evidence"]
    paths = {path for values in evidence.values() for path in values}
    for path in paths:
        assert (ROOT / path).is_file(), path
    joined = " ".join(node["authority"]["notes"] + node["unresolved_gates"])
    assert "does not execute or replay commands" in joined
    assert "No Prime runtime" in joined


def test_closeout_documents_have_brisbane_timestamps() -> None:
    paths = [
        "docs/ariadne-provider-free-continuity-journal-and-refinement-promotion-plan.md",
        "docs/security/ariadne-provider-free-continuity-journal-and-refinement-promotion-threat-model-delta.md",
        "docs/ariadne-provider-free-continuity-journal-and-refinement-promotion-closeout.md",
        "orchestration/agent_inbox/codex/ariadne-prime-derived-harness-adaptations-sol-acceptance.md",
        "orchestration/human_inbox/yuri/2026-08-15--ariadne-continuity-journal-and-refinement-safeguards.md",
    ]
    for path in paths:
        head = "\n".join((ROOT / path).read_text(encoding="utf-8").splitlines()[:12])
        assert "Date: 2026-08-15" in head
        assert "Timestamp: 2026-08-15T" in head
        assert "+10:00 (Australia/Brisbane)" in head


def test_live_handover_names_accepted_safeguards_and_next_product_tranche() -> None:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    index = (
        ROOT / "docs/handover-ledgers/current-baton-acceptance-index.md"
    ).read_text(encoding="utf-8")
    assert "ariadne_provider_free_continuity_journal" in text
    assert (
        "Ariadne continuity journal and refinement-promotion safeguards acceptance"
        in index
    )
    assert "Continuity 299 / Compass 281" in text
    assert "delete-confirm physical schema-and-transaction scaffold" in text
