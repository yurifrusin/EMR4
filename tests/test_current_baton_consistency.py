import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
PLAN = ROOT / "implementation_plan.md"
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
NODE_ID = "raisa-agent-execution-surface-containment-gate-aes-c4"
PROTECTED_SHA = "2e34bdad732fdab32fbf778280b3d3c70d66d602"


def _table_row(text: str, label: str) -> str:
    prefix = f"| {label} |"
    matches = [line for line in text.splitlines() if line.startswith(prefix)]
    assert len(matches) == 1, f"expected one AGENTS row for {label}"
    return matches[0]


def test_continuity_and_compass_bind_the_live_aes_c4_result() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))

    assert graph["graph_revision"] == 241
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert compass["map_revision"] == 223
    assert compass["source_graph_revision"] == 241
    assert compass["current_position"]["node_id"] == NODE_ID


def test_live_baton_rows_agree_on_aes_c4_and_closed_aes_c5_fork() -> None:
    text = AGENTS.read_text(encoding="utf-8")
    current = _table_row(text, "Current result")
    relation = _table_row(text, "Required Git relation")
    next_work = _table_row(text, "Next implementation")

    assert "Continuity 241 / Compass 223" in current
    assert "AES-C4 passes" in current
    assert "e569da0a9081117b799e9437d8b7025230e2162b" in current
    assert "HTTP 200/`STOP`" in current
    assert "542 total tokens" in current
    assert "command_authority: false" in current
    assert "one-call/no-retry ledger is consumed" in current
    assert "AER-0261" in current
    assert "codex/ariadne-bernie-davida-parallel-seam" in relation
    assert PROTECTED_SHA in relation
    assert "e569da0a9081117b799e9437d8b7025230e2162b" in relation
    assert "AES-C5 product-runtime admission" in next_work
    assert "genuine Yuri-attention fork" in next_work
    assert "one exact real product source" in next_work
    assert "one exact purpose" in next_work
    assert "privacy" in next_work
    assert "retention" in next_work
    assert "no-command" in next_work
    assert "No AES-C5 product read or provider call has started" in next_work
    assert "attempt-016" not in relation.lower()
    assert "attempt 016" not in relation.lower()
    assert "attempt-016" not in next_work.lower()
    assert "attempt 016" not in next_work.lower()


def test_master_plan_and_handover_contain_no_stale_next_work_instruction() -> None:
    handover = AGENTS.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    compact_plan = " ".join(plan.split())

    stale_review_next = (
        "The next recommended tranche is the bounded read-only "
        "architectural-health/conformance pulse"
    )
    stale_pause = "conformance pulse is next after Yuri's requested closeout pause"
    assert stale_review_next not in handover
    assert stale_pause not in plan
    assert "conformance repair named in that review now also" in compact_plan
    assert (
        "AES-C0 architecture, AES-C1 provider-free admission, AES-C2 inert broker simulation, AES-C3 provider-free hostile containment and AES-C4 bounded occupied authored- synthetic provider proof now pass"
        in compact_plan
    )
    assert (
        "AES-C5 is the next named descendant but remains closed pending its first exact product source and purpose plus privacy, identity, retention and product-data boundaries"
        in compact_plan
    )


def test_current_rows_preserve_closed_surface_boundary() -> None:
    text = AGENTS.read_text(encoding="utf-8")
    next_work = _table_row(text, "Next implementation").lower()
    for phrase in (
        "separately closed",
        "product read",
        "continuing provider call",
        "no-command",
        "reusable runtime",
        "docs/branding/",
        "no aes-c5 product read",
    ):
        assert phrase in next_work
