"""Advance Continuity and Compass for the active-operation latch safeguard."""

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
NODE_ID = "ariadne-postcompaction-active-operation-latch"
PARENT = "ariadne-cf-d2-workflow-incident-diagnosis-and-fluidity-repair"
PRODUCT_POSITION = (
    "raisa-provider-free-unmounted-status-confirm-route-convergence-"
    "composition-rehearsal"
)
SOURCE_HEAD = "ac62a6f65612acb624f14b53ba86b1a9dbf72dab"
UPDATED_AT = "2026-08-12T23:31:31Z"
PLAN = "docs/ariadne-postcompaction-active-operation-latch-plan.md"
THREAT = (
    "docs/security/ariadne-postcompaction-active-operation-latch-threat-model-delta.md"
)
POLICY = "orchestration/harness_settings/autonomous_continuation.yaml"
REQUIREMENTS = "orchestration/harness_settings/orchestrator_requirements.yaml"
SCHEMA = (
    "orchestration/continuity/ariadne-active-operation-latch/"
    "active-operation.schema.json"
)
STATE = "orchestration/continuity/ariadne-active-operation-latch/current.json"
MODULE = "orchestration_harness/active_operation.py"
CLI = "scripts/ariadne_active_operation_latch.py"
TEST = "tests/test_ariadne_active_operation_latch.py"
CLOSEOUT = "docs/ariadne-postcompaction-active-operation-latch-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/ariadne-active-operation-latch-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/2026-08-13--ariadne-postcompaction-"
    "active-operation-latch.md"
)
UPDATER = "scripts/ariadne_active_operation_latch_continuity_update.py"
CONTINUITY_TEST = "tests/test_ariadne_active_operation_latch_continuity.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        POLICY,
        REQUIREMENTS,
        SCHEMA,
        STATE,
        MODULE,
        CLI,
        TEST,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Ariadne post-compaction active-operation latch",
        "kind": "foundation",
        "status": "accepted",
        "created_at": UPDATED_AT,
        "updated_at": UPDATED_AT,
        "coordinates": {
            "git_ref": "codex/ariadne-bernie-davida-parallel-seam",
            "source_head": SOURCE_HEAD,
            "thread_id": None,
            "worktree_role": "task",
        },
        "relationships": [{"node_id": PARENT, "relation": "builds_on"}],
        "authority": {
            "authorized_openings": [],
            "notes": [
                "The latch is continuity evidence and does not replace the five authoritative rehydration sources.",
                "An in-progress operation forbids terminal handback and preserves exact checkpoint resumption after compaction.",
                "No product, data, provider, command, deployment or protected-ref authority is opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-active-operation-latch",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Require the validated latch in every continuation receipt and resume the frozen status-confirm readiness re-review.",
            }
        ],
        "claim_scope": [
            "Prompt recency alone is not operation authority; side/status questions answer then resume and additions merge then resume.",
            "Terminal intent against in-progress returns revision_required.",
            "Thirty-nine hostile mutations, 81 focused tests and the 193-test canonical profile pass.",
            "New tranche documents carry an Australia/Brisbane ISO 8601 timestamp with the date.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [POLICY, REQUIREMENTS, SCHEMA, STATE, MODULE, CLI, UPDATER],
        },
        "unresolved_gates": [
            "The repository guard cannot directly intercept a host final-channel operation; model compliance remains required.",
            "The status-confirm route readiness re-review remains in progress and opens no mounted route or database authority.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 268:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 269
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 269 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected active-operation-latch Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if compass["map_revision"] == 250 and compass["source_graph_revision"] == 268:
        pass
    elif compass["map_revision"] == 251 and compass["source_graph_revision"] == 269:
        if compass["journey"][-1]["node_id"] == NODE_ID:
            compass["journey"].pop()
    else:
        raise SystemExit("Unexpected active-operation-latch Compass predecessor")

    if compass["current_position"]["node_id"] != PRODUCT_POSITION:
        raise SystemExit("Product current position changed unexpectedly")
    current = compass["current_position"]
    current["why_now"] = (
        "The unmounted composition passes, and the workflow latch now preserves "
        "this exact readiness-review checkpoint across interruptions."
    )
    current["unlocks"] = [
        "Resume the provider-free read-only status-confirm route-mounting readiness re-review.",
        "Reclassify the ten frozen dimensions and name only the narrowest remaining application adapters or route prerequisites.",
    ]
    for item in _evidence():
        if item not in current["evidence"]:
            current["evidence"].append(item)
    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "ariadne-workflow-executive":
            for item in _evidence():
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Ariadne workflow horizon item missing")
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 269 / Compass 251. The post-compaction active-"
        "operation latch passes and the provider-free read-only status-confirm "
        "route-mounting readiness re-review is in progress. Mounted execution "
        "and product authority remain closed."
    )
    compass["source_graph_revision"] = 269
    compass["map_revision"] = 251
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
