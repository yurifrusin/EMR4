import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
PLAN = ROOT / "implementation_plan.md"
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
NODE_ID = "raisa-context-fabric-source-owned-truth-conditional-command-reorientation"
PROTECTED_SHA = "2e34bdad732fdab32fbf778280b3d3c70d66d602"


def _table_row(text: str, label: str) -> str:
    prefix = f"| {label} |"
    matches = [line for line in text.splitlines() if line.startswith(prefix)]
    assert len(matches) == 1, f"expected one AGENTS row for {label}"
    return matches[0]


def test_continuity_and_compass_bind_the_live_reorientation_result() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))

    assert graph["graph_revision"] == 245
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert compass["map_revision"] == 227
    assert compass["source_graph_revision"] == 245
    assert compass["current_position"]["node_id"] == NODE_ID


def test_live_baton_rows_accept_reorientation_and_keep_cf_d2_deferred() -> None:
    text = AGENTS.read_text(encoding="utf-8")
    current = _table_row(text, "Current result")
    relation = _table_row(text, "Required Git relation")
    next_work = _table_row(text, "Next implementation")

    assert "Continuity 245 / Compass 227" in current
    assert "events are acceleration hints" in current
    assert "Freshness, human/policy confirmation, idempotency and audit are distinct" in current
    assert "One logical watcher" in current
    assert "CF-D1 is retained" in current
    assert "CF-D2 remains stopped and unproved" in current
    assert "037eed060d4519f2f3d6721135143ecb6f70e358" in current
    assert "codex/ariadne-bernie-davida-parallel-seam" in relation
    assert PROTECTED_SHA in relation
    assert "28cd0ce6639fd831960c57d5289b08f3d36ca3fb" in relation
    assert "fe8313d224a92115aa31bea14f0cd3b14e4c9967" in relation
    assert "018099dd6c5f0502121360732feb602252eb34cc" in relation
    assert "037eed060d4519f2f3d6721135143ecb6f70e358" in relation
    assert "provider-free unmounted conditional-command admission rehearsal" in next_work
    assert "open a database/source/watcher" in next_work
    assert "product/patient/clinical data" in next_work
    assert "executable tool" in next_work
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
        "provider-free unmounted",
        "open a database/source/watcher",
        "product/patient/clinical data",
        "executable tool",
        "command/write",
        "docs/branding/",
        "deployment",
        "pages",
        "protected refs",
    ):
        assert phrase in next_work
