"""Advance Continuity and Compass for the status-confirm preflight repair."""

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
NODE_ID = "raisa-status-confirm-preflight-idempotency-expectation-repair"
PARENT = (
    "raisa-provider-free-read-only-status-confirm-route-mounting-admission-review"
)
SOURCE_HEAD = "ec9aa1b1d2813b3e864b37f331ac6b587816610a"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = "docs/raisa-status-confirm-preflight-idempotency-expectation-repair-plan.md"
CLOSEOUT = (
    "docs/raisa-status-confirm-preflight-idempotency-expectation-repair-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-status-confirm-preflight-"
    "idempotency-expectation-repair-sol-acceptance.md"
)
STATE = (
    "orchestration/agent_inbox/codex/raisa-status-confirm-preflight-"
    "idempotency-expectation-repair-preplanning-runtime-state.json"
)
RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-status-confirm-preflight-"
    "idempotency-expectation-repair-preplanning-receipt.json"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-12--status-confirm-preflight-idempotency-expectation-repair.md"
)
REPAIRED_TEST = "tests/test_api_spine_status_confirm_idempotency_preflight.py"
UPDATER = (
    "scripts/raisa_status_confirm_preflight_idempotency_expectation_repair_"
    "continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_status_confirm_preflight_idempotency_expectation_repair_"
    "continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        REPAIRED_TEST,
        STATE,
        RECEIPT,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Status-confirm preflight idempotency expectation repair",
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
                "The result changes one test expectation only; no application behavior changes.",
                "It restores current idempotency-route lineage evidence and opens no runtime authority.",
                "Product data, commands, providers, deployment and protected integration remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-status-confirm-preflight-expectation-repair",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept the test-only rebinding and proceed to the already-planned provider-free unmounted composition rehearsal.",
            }
        ],
        "claim_scope": [
            "The current update, status and delete confirmation-route tests now agree on required Idempotency-Key handling.",
            "Six focused, 125 status-confirm lineage and 191 canonical tests pass.",
            "The historical Sprint-136 preflight and all application source remain unchanged.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [STATE, RECEIPT],
            "tests": [REPAIRED_TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "The accepted adapter, server authority/session ingress, physical seam and response mapper remain uncomposed and unmounted.",
            "No mounted-route edit/call, product command/database/data, concurrency, restart, unknown commit, provider, deployment or protected integration is proved or authorized.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 266 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 267
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 267 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected preflight repair Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Remove one stale lifecycle-test contradiction before composing the status-confirm route seam",
        "outcome": "The test-only expectation now matches accepted idempotency behavior and all 125 lineage checks pass.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 248
        and compass["source_graph_revision"] == 266
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 249
        and compass["source_graph_revision"] == 267
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected preflight repair Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve the accepted physical PostgreSQL status-confirm proof without reopening durability.",
                "Rehearse one provider-free unmounted status-confirm route-convergence composition.",
                "Join status-only admission, server authority/session ingress, physical seam and closed response mapping.",
                "Keep route edits/calls, product data/commands, providers and protected integration separately gated.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "The status-confirm route lineage is internally consistent and ready for off-route composition",
        "why_now": "The admission review isolated one historical test contradiction before implementation rehearsal.",
        "outcome": "The contradiction is corrected test-only; 125 current lineage checks and the canonical profile pass.",
        "unlocks": [
            "Freeze and run a provider-free unmounted status-confirm route-convergence composition rehearsal.",
            "Join the accepted status-only adapter, server authority/session ingress, physical seam and closed response mapper off-route.",
        ],
        "does_not_solve": [
            "Mounted-route convergence, route execution or a real product command.",
            "Concurrency, restart, crash, unknown commit, retention, performance or production operations.",
            "Provider/credential activity, patient/product data, deployment, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 267 / Compass 249. The stale status-confirm "
        "preflight expectation is repaired with no product change, and all 125 "
        "current lineage checks pass. The provider-free unmounted route "
        "composition rehearsal is next; mounted execution remains closed."
    )
    compass["source_graph_revision"] = 267
    compass["map_revision"] = 249
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
