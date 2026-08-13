"""Advance Continuity and Compass for two-projection truth parity."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ariadne_compass


GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
HANDOVER = ROOT / "AGENTS.md"
MASTER_PLAN = ROOT / "implementation_plan.md"
NODE_ID = "raisa-provider-free-two-projection-truth-parity-conformance-rehearsal"
PARENT = "raisa-post-status-action-compass-baton-orientation"
SOURCE_HEAD = "18aa4b613d735a68a7f6f2e55d34e498176c9935"
UPDATED_AT = "2026-08-13T14:20:41Z"
PLAN = "docs/raisa-provider-free-two-projection-truth-parity-conformance-rehearsal-plan.md"
THREAT = "docs/security/raisa-provider-free-two-projection-truth-parity-conformance-rehearsal-threat-model-delta.md"
ARCHITECTURE = "docs/raisa-projection-neutral-kernel-truth-architecture.md"
HELPER = "scripts/raisa_provider_free_two_projection_truth_parity_conformance_rehearsal.py"
BROWSER = "review/test_two_projection_truth_parity.py"
TRACE_SCHEMA = "orchestration/continuity/raisa-provider-free-two-projection-truth-parity-conformance-rehearsal/projection-truth-trace.schema.json"
EVIDENCE_SCHEMA = "orchestration/continuity/raisa-provider-free-two-projection-truth-parity-conformance-rehearsal/two-projection-truth-parity-evidence.schema.json"
EVIDENCE = "orchestration/continuity/raisa-provider-free-two-projection-truth-parity-conformance-rehearsal/two-projection-truth-parity-evidence.json"
TEST = "tests/test_raisa_provider_free_two_projection_truth_parity_conformance_rehearsal.py"
PLAN_TEST = "tests/test_raisa_provider_free_two_projection_truth_parity_conformance_rehearsal_plan.py"
EVIDENCE_TEST = "tests/test_raisa_provider_free_two_projection_truth_parity_conformance_rehearsal_evidence.py"
HISTORICAL_TEST_REPAIR = "tests/test_raisa_reception_one_selected_appointment_status_action_composition_plan.py"
CLOSEOUT = "docs/raisa-provider-free-two-projection-truth-parity-conformance-rehearsal-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-two-projection-truth-parity-conformance-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-14--two-projection-truth-parity-conformance.md"
UPDATER = "scripts/raisa_provider_free_two_projection_truth_parity_conformance_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_provider_free_two_projection_truth_parity_conformance_continuity.py"
RECEIPT = "orchestration/agent_inbox/codex/raisa-two-projection-truth-parity-conformance-preplanning-receipt.json"
DECISION_ID = "post-truth-parity-programme-direction"


def _update_handover_and_plan() -> None:
    handover = HANDOVER.read_text(encoding="utf-8")
    relation_old = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted Reception One selected-appointment status-action composition"
    relation_new = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted two-projection truth-parity conformance rehearsal at exact source `18aa4b613d735a68a7f6f2e55d34e498176c9935`, the accepted Reception One selected-appointment status-action composition"
    if relation_new not in handover:
        if relation_old not in handover:
            raise SystemExit("Required Git relation anchor missing")
        handover = handover.replace(relation_old, relation_new, 1)

    stale_track = "The CF-D2 observability, admission, representation, inert SQL, parse/catalogue and fixed serial transaction sequence passes while remaining an optional acceleration layer. A fresh read-only Compass and baton orientation is next."
    current_track = "The CF-D2 observability, admission, representation, inert SQL, parse/catalogue and fixed serial transaction sequence passes while remaining an optional acceleration layer. The two-projection truth-parity rehearsal now protects six paired status outcomes without changing product code; the next functional direction is a genuine Yuri-owned fork."
    if stale_track in handover:
        handover = handover.replace(stale_track, current_track, 1)

    acceptance_row = "| Two-projection truth-parity conformance acceptance | `docs/raisa-provider-free-two-projection-truth-parity-conformance-rehearsal-plan.md`, `docs/security/raisa-provider-free-two-projection-truth-parity-conformance-rehearsal-threat-model-delta.md`, `docs/raisa-projection-neutral-kernel-truth-architecture.md`, `scripts/raisa_provider_free_two_projection_truth_parity_conformance_rehearsal.py`, `review/test_two_projection_truth_parity.py`, `orchestration/continuity/raisa-provider-free-two-projection-truth-parity-conformance-rehearsal/`, `tests/test_raisa_provider_free_two_projection_truth_parity_conformance_rehearsal.py`, `tests/test_raisa_provider_free_two_projection_truth_parity_conformance_rehearsal_plan.py`, `tests/test_raisa_provider_free_two_projection_truth_parity_conformance_rehearsal_evidence.py`, `docs/raisa-provider-free-two-projection-truth-parity-conformance-rehearsal-closeout.md`, `orchestration/agent_inbox/codex/raisa-two-projection-truth-parity-conformance-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-14--two-projection-truth-parity-conformance.md`, `scripts/raisa_provider_free_two_projection_truth_parity_conformance_continuity_update.py`, and `tests/test_raisa_provider_free_two_projection_truth_parity_conformance_continuity.py` |"
    if acceptance_row not in handover:
        anchor = next(line for line in handover.splitlines() if line.startswith("| Post-status-action truth-parity orientation acceptance |"))
        handover = handover.replace(anchor, anchor + "\n" + acceptance_row, 1)

    replacements = {
        "Current result": "| Current result | At Continuity 285 / Compass 267, `raisa_provider_free_two_projection_truth_parity_conformance_rehearsal_pass` is accepted at exact source `18aa4b613d735a68a7f6f2e55d34e498176c9935`. Twelve route-intercepted browser traces cover safe, cancelled, blocked, stale, failed and committed outcomes across `conventional_grid` and `reception_one`; all six pairs agree on seven kernel-owned field groups while renderer-local layout, wording, focus and history differ. Raw compatibility requests and every external/product authority count are zero. This proves truth parity, not general feature parity, for the existing appointment-status family. |",
        "Next implementation": "| Next implementation | Implementation is paused at a genuine Yuri-attention programme fork. Yuri must select one exact value-bearing direction: another Reception One command family, representative Stage 3B staff execution, a first patient channel/identity flow, another typed Diary event family, or operational watcher/durability work. General visual polish remains possible but does not choose functional breadth. Once Yuri selects, freeze that direction's narrowest fail-closed plan and resume under standing authority. No new command/event/renderer, cohort, patient channel, database/source/watcher runtime, product/patient data, provider/ADC, credentials/IAM/network, deployment, production, release, Pages or protected-ref movement is inferred. Preserve `docs/branding/` and all unrelated untracked files; use explicit-path staging only. |",
    }
    lines = handover.splitlines()
    for label, replacement in replacements.items():
        prefix = f"| {label} |"
        indices = [index for index, line in enumerate(lines) if line.startswith(prefix)]
        if len(indices) != 1:
            raise SystemExit(f"Expected one handover row for {label}")
        lines[indices[0]] = replacement
    HANDOVER.write_text("\n".join(lines) + "\n", encoding="utf-8")

    plan = MASTER_PLAN.read_text(encoding="utf-8")
    old = """The subsequent orientation now
passes at exact source
`4b6a060c6b1aab42e1062c41d48d109f683abe00`: the conventional grid and
Reception One have truth parity, not general feature parity, for the existing
status family. A provider-free two-projection truth-parity conformance
rehearsal is next; it will formalise the kernel invariant without adding a
runtime contract or another command."""
    new = """The orientation passes at exact source
`4b6a060c6b1aab42e1062c41d48d109f683abe00`, and its two-projection
truth-parity rehearsal now passes at exact source
`18aa4b613d735a68a7f6f2e55d34e498176c9935`. Twelve route-intercepted
traces protect six paired status outcomes without changing product code. The
next functional direction is a genuine Yuri-owned fork; no command, cohort,
patient channel, event family or watcher runtime is inferred."""
    if old in plan:
        plan = plan.replace(old, new, 1)
    elif new not in plan:
        raise SystemExit("Master-plan truth-parity anchor missing")
    MASTER_PLAN.write_text(plan, encoding="utf-8")


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _evidence() -> list[str]:
    return [PLAN, THREAT, ARCHITECTURE, HELPER, BROWSER, TRACE_SCHEMA, EVIDENCE_SCHEMA, EVIDENCE, TEST, PLAN_TEST, EVIDENCE_TEST, HISTORICAL_TEST_REPAIR, CLOSEOUT, ACCEPTANCE, MAILBOX, RECEIPT]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free two-projection truth-parity conformance rehearsal",
        "kind": "review",
        "status": "accepted",
        "created_at": UPDATED_AT,
        "updated_at": UPDATED_AT,
        "coordinates": {"git_ref": "codex/ariadne-bernie-davida-parallel-seam", "source_head": SOURCE_HEAD, "thread_id": None, "worktree_role": "task"},
        "relationships": [{"node_id": PARENT, "relation": "builds_on"}],
        "authority": {"authorized_openings": [], "notes": [
            "Evidence-only route-intercepted rehearsal; product, API, database and event surfaces are unchanged.",
            "Truth parity is proved for exactly two existing renderers and one existing appointment-status family, not general feature parity.",
            "Another command/event/renderer, participant cohort, patient channel and operational watcher remain separately gated.",
        ]},
        "decisions": [{"id": "accept-projection-neutral-kernel-truth-invariant", "source": ACCEPTANCE, "status": "accepted", "summary": "Accept six exact paired browser outcomes as the first executable cross-projection kernel truth invariant."}],
        "claim_scope": [
            "Twelve route-intercepted traces cover safe, cancelled, blocked, stale, failed and committed outcomes across conventional_grid and reception_one.",
            "All seven kernel-owned field groups agree for each pair while renderer-local layout, wording, focus and history differ.",
            "Raw compatibility requests and all external/product authority counts are zero.",
            "Twenty closed schema/evidence checks, 115 focused checks and the 193-test canonical fast profile pass.",
        ],
        "contract_evidence": [],
        "evidence": {"plans": [PLAN, THREAT], "findings": [ARCHITECTURE], "closeouts": [CLOSEOUT, MAILBOX], "acceptances": [ACCEPTANCE], "receipts": [RECEIPT], "tests": [BROWSER, TEST, PLAN_TEST, EVIDENCE_TEST, CONTINUITY_TEST], "artifacts": [HELPER, TRACE_SCHEMA, EVIDENCE_SCHEMA, EVIDENCE, UPDATER, HISTORICAL_TEST_REPAIR]},
        "unresolved_gates": [
            "Yuri must select the next programme direction; no further dependency-satisfied functional tranche is inferable.",
            "Another command/event/renderer, representative cohort, patient channel and watcher/runtime retain their recorded gates.",
            "Product data, providers, deployment, production and release remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 284 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 285
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 285 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected truth-parity Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Make projection-neutral kernel truth parity executable for one complete command family",
        "outcome": "Two existing renderer grammars agree across six status outcomes; the next functional direction is a genuine Yuri-owned fork.",
        "evidence": _evidence(),
    }
    if compass["map_revision"] == 266 and compass["source_graph_revision"] == 284 and compass["current_position"]["node_id"] == PARENT:
        compass["journey"].append(journey)
    elif compass["map_revision"] == 267 and compass["source_graph_revision"] == 285 and compass["current_position"]["node_id"] == NODE_ID:
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected truth-parity Compass predecessor")

    decision = {
        "id": DECISION_ID,
        "title": "Post-truth-parity programme direction",
        "status": "candidate",
        "strategic_question": "Which value-bearing direction should follow the protected truth-parity milestone: another Reception One command, representative staff execution, a patient channel/identity flow, another event family, or operational watcher/durability work?",
        "why_it_matters": "Each option changes functional breadth, evidence population or runtime/data authority differently; no one outcome is inferable from the accepted invariant alone.",
        "prerequisites": [
            "Yuri selects one exact direction and its intended product value.",
            "Sol freezes that choice's narrowest fail-closed plan before implementation.",
        ],
        "boundary_changes": [],
        "evidence": [CLOSEOUT, MAILBOX, ARCHITECTURE],
    }
    existing = next((index for index, item in enumerate(compass["decision_horizon"]) if item["id"] == DECISION_ID), None)
    if existing is None:
        compass["decision_horizon"].insert(0, decision)
    else:
        compass["decision_horizon"][existing] = decision

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "The grid and meta-grid now pass one executable kernel-truth invariant",
        "why_now": "The first complete Reception One status action required protection against future renderer-specific semantic drift.",
        "outcome": "Twelve traces and six exact pairs pass; no further functional tranche is inferable without a Yuri-owned direction choice.",
        "unlocks": ["Judge future modalities by kernel meaning rather than grid imitation.", "Choose the next value-bearing product or runtime direction."],
        "does_not_solve": ["Feature parity across Diary commands is not claimed.", "No new command/event/renderer, cohort, patient channel or watcher runtime is authorised.", "Product data, providers, deployment, production and release remain closed."],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = "EMR4 is at Continuity 285 / Compass 267. Conventional grid and Reception One pass six paired status truth outcomes. The next functional direction is a genuine Yuri-owned programme fork."
    limit = "The truth-parity trace is evidence only and cannot become a runtime, API, database, analytics, audit or transcript contract."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 285
    compass["map_revision"] = 267
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    _update_handover_and_plan()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
