import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
PLAN = ROOT / "implementation_plan.md"
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
NODE_ID = "raisa-agent-execution-surface-containment-gate-aes-c5"
PROTECTED_SHA = "2e34bdad732fdab32fbf778280b3d3c70d66d602"


def _table_row(text: str, label: str) -> str:
    prefix = f"| {label} |"
    matches = [line for line in text.splitlines() if line.startswith(prefix)]
    assert len(matches) == 1, f"expected one AGENTS row for {label}"
    return matches[0]


def test_continuity_and_compass_bind_the_live_aes_c5_result() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))

    assert graph["graph_revision"] == 242
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert compass["map_revision"] == 224
    assert compass["source_graph_revision"] == 242
    assert compass["current_position"]["node_id"] == NODE_ID


def test_live_baton_rows_agree_on_aes_c5_and_finite_sequence_close() -> None:
    text = AGENTS.read_text(encoding="utf-8")
    current = _table_row(text, "Current result")
    relation = _table_row(text, "Required Git relation")
    next_work = _table_row(text, "Next implementation")

    assert "Continuity 242 / Compass 224" in current
    assert "AES-C5 passes" in current
    assert "4e5d96ada19c51432fa4db46c76e23c952147c52" in current
    assert "HTTP 200/`STOP`" in current
    assert "947 total tokens" in current
    assert "command_authority: false" in current
    assert "Both ledgers are consumed" in current
    assert "disposable schema is absent" in current
    assert "codex/ariadne-bernie-davida-parallel-seam" in relation
    assert PROTECTED_SHA in relation
    assert "4e5d96ada19c51432fa4db46c76e23c952147c52" in relation
    assert "AES-C5 completes" in next_work
    assert "No AES-C6" in next_work
    assert "Yuri-owned programme choice" in next_work
    assert "real practice population" in next_work
    assert "product-data class" in next_work
    assert "reusable runtime" in next_work
    assert "tool/command" in next_work
    assert "no continuing product/database read" in next_work
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
        "AES-C0 architecture, AES-C1 provider-free admission, AES-C2 inert broker simulation, AES-C3 provider-free hostile containment, AES-C4 bounded occupied authored- synthetic provider proof and AES-C5 product-runtime admission now pass"
        in compact_plan
    )
    assert (
        "The finite AES-C0 through AES-C5 sequence is complete; no AES-C6 is planned or authorised"
        in compact_plan
    )


def test_current_rows_preserve_closed_surface_boundary() -> None:
    text = AGENTS.read_text(encoding="utf-8")
    next_work = _table_row(text, "Next implementation").lower()
    for phrase in (
        "no aes-c6",
        "real practice population",
        "product-data class",
        "tool/command",
        "reusable runtime",
        "docs/branding/",
        "no continuing product/database read",
        "credential/iam change",
        "command/write",
        "protected-ref movement",
    ):
        assert phrase in next_work
