import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
PLAN = ROOT / "implementation_plan.md"
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
NODE_ID = "raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal"
PROTECTED_SHA = "2e34bdad732fdab32fbf778280b3d3c70d66d602"


def _table_row(text: str, label: str) -> str:
    prefix = f"| {label} |"
    matches = [line for line in text.splitlines() if line.startswith(prefix)]
    assert len(matches) == 1, f"expected one AGENTS row for {label}"
    return matches[0]


def test_continuity_and_compass_bind_the_live_cf_d1_result() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))

    assert graph["graph_revision"] == 243
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert compass["map_revision"] == 225
    assert compass["source_graph_revision"] == 243
    assert compass["current_position"]["node_id"] == NODE_ID


def test_live_baton_rows_agree_on_cf_d1_and_cf_d2_handoff() -> None:
    text = AGENTS.read_text(encoding="utf-8")
    current = _table_row(text, "Current result")
    relation = _table_row(text, "Required Git relation")
    next_work = _table_row(text, "Next implementation")

    assert "Continuity 243 / Compass 225" in current
    assert "CF-D1 passes" in current
    assert "fed81847b4155d49cf997905e79cf31808ceb017" in current
    assert "43f168f3d5d1f71ec0f9071c40fadf14b6107621" in current
    assert "Timeout/PgSleep" in current
    assert "12 participants and 11 preconditions" in current
    assert "zero retry" in current
    assert "AER-0269 through AER-0272" in current
    assert "codex/ariadne-bernie-davida-parallel-seam" in relation
    assert PROTECTED_SHA in relation
    assert "fed81847b4155d49cf997905e79cf31808ceb017" in relation
    assert "CF-D2" in next_work
    assert "restart and unknown-commit" in next_work
    assert "five-source rehydration" in next_work
    assert "definitely committed" in next_work
    assert "genuinely indeterminate" in next_work
    assert "without guessing success" in next_work
    assert "operational database/source" in next_work
    assert "tool/command" in next_work
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
        "cf-d2",
        "restart and unknown-commit",
        "operational database/source",
        "real/product/patient/clinical data",
        "tool/command",
        "reusable runtime",
        "docs/branding/",
        "deployment",
        "pages",
        "protected-ref authority",
    ):
        assert phrase in next_work
