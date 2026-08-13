"""Advance Continuity and Compass for the post-status-action orientation."""

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
NODE_ID = "raisa-post-status-action-compass-baton-orientation"
PARENT = "raisa-reception-one-selected-appointment-status-action-composition"
SOURCE_HEAD = "4b6a060c6b1aab42e1062c41d48d109f683abe00"
UPDATED_AT = "2026-08-13T13:21:48Z"
PLAN = "docs/raisa-post-status-action-compass-baton-orientation-plan.md"
FINDING = "docs/raisa-post-status-action-compass-baton-orientation.md"
TEST = "tests/test_raisa_post_status_action_compass_baton_orientation.py"
PLAN_TEST = "tests/test_raisa_post_status_action_compass_baton_orientation_plan.py"
CLOSEOUT = "docs/raisa-post-status-action-compass-baton-orientation-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-post-status-action-compass-baton-orientation-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-13--post-status-action-truth-parity-orientation.md"
UPDATER = "scripts/raisa_post_status_action_compass_baton_orientation_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_post_status_action_compass_baton_orientation_continuity.py"
RECEIPT = "orchestration/agent_inbox/codex/raisa-post-status-action-compass-baton-orientation-preplanning-receipt.json"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _evidence() -> list[str]:
    return [PLAN, FINDING, TEST, PLAN_TEST, CLOSEOUT, ACCEPTANCE, MAILBOX, RECEIPT]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Read-only post-status-action truth-parity orientation",
        "kind": "review",
        "status": "accepted",
        "created_at": UPDATED_AT,
        "updated_at": UPDATED_AT,
        "coordinates": {"git_ref": "codex/ariadne-bernie-davida-parallel-seam", "source_head": SOURCE_HEAD, "thread_id": None, "worktree_role": "task"},
        "relationships": [{"node_id": PARENT, "relation": "builds_on"}],
        "authority": {"authorized_openings": [], "notes": [
            "Read-only repository orientation; no product behavior or runtime changed.",
            "Truth parity is accepted for one status command family; broader feature parity is not claimed.",
            "The kernel remains above every renderer and owns identity, truth, command meaning, commit, audit and receipt.",
        ]},
        "decisions": [{"id": "select-two-projection-truth-parity-rehearsal", "source": ACCEPTANCE, "status": "accepted", "summary": "Select a provider-free conformance rehearsal over the two existing status renderers without adding a command or runtime contract."}],
        "claim_scope": [
            "Both existing renderers converge on the same status interaction and fresh authoritative reconciliation.",
            "Projection differences may remain in layout, wording, focus and local history but not kernel meaning.",
            "Another command/event family, participant cohort, patient channel and operational watcher remain separately gated.",
            "The 72-test focused orientation/latch/baton/Compass packet and the 193-test canonical fast profile pass.",
        ],
        "contract_evidence": [],
        "evidence": {"plans": [PLAN], "findings": [FINDING], "closeouts": [CLOSEOUT, MAILBOX], "acceptances": [ACCEPTANCE], "receipts": [RECEIPT], "tests": [TEST, PLAN_TEST, CONTINUITY_TEST], "artifacts": [UPDATER]},
        "unresolved_gates": [
            "The selected truth-parity rehearsal remains unimplemented until its own frozen plan and evidence pass.",
            "Other commands/events, Stage 3B execution, patient channels and watcher/runtime retain their recorded gates.",
            "Product data, providers, deployment, production and release remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 283 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 284
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 284 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected post-status orientation Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {"node_id": NODE_ID, "lineage_parent": PARENT, "strategic_role": "Recognise cross-projection kernel truth parity and select its narrow conformance proof", "outcome": "Truth parity is distinguished from feature parity and a two-renderer status conformance rehearsal is selected.", "evidence": _evidence()}
    if compass["map_revision"] == 265 and compass["source_graph_revision"] == 283 and compass["current_position"]["node_id"] == PARENT:
        compass["journey"].append(journey)
    elif compass["map_revision"] == 266 and compass["source_graph_revision"] == 284 and compass["current_position"]["node_id"] == NODE_ID:
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected post-status orientation Compass predecessor")
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "The grid and meta-grid now share kernel truth rank for one command family",
        "why_now": "The status composition proves authoritative meaning can remain invariant across different renderer grammars.",
        "outcome": "A provider-free two-projection truth-parity conformance rehearsal is the next dependency-satisfied tranche.",
        "unlocks": ["Freeze and execute the two-projection status truth-parity conformance rehearsal.", "Use the kernel trace—not grid layout—as the future renderer correctness criterion."],
        "does_not_solve": ["Feature parity across Diary command families is not claimed.", "Other commands/events, participants, patient channels and watcher/runtime retain their recorded gates.", "Product data, providers, deployment, production and release remain closed."],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = "EMR4 is at Continuity 284 / Compass 266. The conventional grid and Reception One have truth parity for the existing status family, not general feature parity. A provider-free two-projection truth-parity conformance rehearsal is next."
    limit = "Truth parity is accepted only for the existing status family and does not infer another command, renderer runtime, patient channel or feature-parity claim."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 284
    compass["map_revision"] = 266
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
