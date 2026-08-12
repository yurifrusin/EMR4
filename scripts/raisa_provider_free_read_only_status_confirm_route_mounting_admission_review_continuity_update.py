"""Advance Continuity and Compass for status-confirm route-mounting review."""

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
NODE_ID = (
    "raisa-provider-free-read-only-status-confirm-route-mounting-admission-review"
)
PARENT = (
    "raisa-provider-free-disposable-postgresql-status-confirm-behavior-"
    "transaction-rehearsal"
)
SOURCE_HEAD = "fb3772dea0c27a7572df00e1b9d5153f9165ccf3"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = (
    "docs/raisa-provider-free-read-only-status-confirm-route-mounting-"
    "admission-review-plan.md"
)
THREAT = (
    "docs/security/raisa-provider-free-read-only-status-confirm-route-mounting-"
    "admission-review-threat-model-delta.md"
)
REVIEW = (
    "docs/raisa-provider-free-read-only-status-confirm-route-mounting-"
    "admission-review.md"
)
CLOSEOUT = (
    "docs/raisa-provider-free-read-only-status-confirm-route-mounting-"
    "admission-review-closeout.md"
)
BASE = (
    "orchestration/continuity/raisa-provider-free-read-only-status-confirm-"
    "route-mounting-admission-review/"
)
CONTRACT = BASE + "route-mounting-review-contract.json"
SCHEMA = BASE + "route-mounting-review-contract.schema.json"
EVIDENCE = BASE + "route-mounting-review-evidence.json"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-status-confirm-route-mounting-"
    "admission-review-sol-acceptance.md"
)
PREPLANNING_STATE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-read-only-status-confirm-"
    "route-mounting-admission-review-preplanning-runtime-state.json"
)
PREPLANNING_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-read-only-status-confirm-"
    "route-mounting-admission-review-preplanning-receipt.json"
)
PREACCEPTANCE_STATE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-read-only-status-confirm-"
    "route-mounting-admission-review-preacceptance-runtime-state.json"
)
PREACCEPTANCE_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-read-only-status-confirm-"
    "route-mounting-admission-review-preacceptance-receipt.json"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-12--status-confirm-route-mounting-admission-review.md"
)
REVIEWER = (
    "scripts/raisa_provider_free_read_only_status_confirm_route_mounting_"
    "admission_review.py"
)
TEST = (
    "tests/test_raisa_provider_free_read_only_status_confirm_route_mounting_"
    "admission_review.py"
)
UPDATER = (
    "scripts/raisa_provider_free_read_only_status_confirm_route_mounting_"
    "admission_review_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_read_only_status_confirm_route_mounting_"
    "admission_review_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        CONTRACT,
        SCHEMA,
        EVIDENCE,
        REVIEW,
        REVIEWER,
        TEST,
        CLOSEOUT,
        ACCEPTANCE,
        PREPLANNING_STATE,
        PREPLANNING_RECEIPT,
        PREACCEPTANCE_STATE,
        PREACCEPTANCE_RECEIPT,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free read-only status-confirm route-mounting admission review",
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
                "The result is provider-free, exact-file and read-only; implementation authority remains false.",
                "It distinguishes literal route mounting from admission onto the accepted physical seam.",
                "Routes, product databases/data, commands, providers, deployment and protected integration remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-status-confirm-route-mounting-review",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept mounted-but-not-admitted verdict; preserve the PostgreSQL proof and hand off only to bounded test hygiene then unmounted composition rehearsal.",
            }
        ],
        "claim_scope": [
            "The status-confirm endpoint is literally mounted at POST /api/v1/appointments/proposals/status-confirm.",
            "Ten exact hashes, 25 structural assertions, 45 hostile mutations and 11 focused review tests pass.",
            "Two foundations are satisfied, one API-path alias matter is partial and seven composition gaps block unchanged physical convergence.",
            "The accepted sixteen-scenario PostgreSQL durability proof remains closed and is not reopened.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [THREAT, CONTRACT, SCHEMA, EVIDENCE, REVIEW],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                PREPLANNING_STATE,
                PREPLANNING_RECEIPT,
                PREACCEPTANCE_STATE,
                PREACCEPTANCE_RECEIPT,
            ],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [REVIEWER, UPDATER],
        },
        "unresolved_gates": [
            "One stale Sprint-138 test expectation must be corrected without changing product behavior.",
            "The accepted adapter, server authority/session ingress, physical seam and public-response mapper remain uncomposed and unmounted.",
            "No route call/edit, product command/database/data, concurrency, restart, unknown commit, provider, deployment or protected integration is proved or authorized.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 265 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 266
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 266 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected route-mounting review Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Decide whether the mounted status-confirm handler can consume the accepted physical seam unchanged",
        "outcome": "The endpoint is mounted and the physical foundation passes, but seven bounded composition gaps block unchanged convergence.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 247
        and compass["source_graph_revision"] == 265
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 248
        and compass["source_graph_revision"] == 266
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected route-mounting review Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve the accepted physical PostgreSQL status-confirm proof without reopening durability.",
                "Correct the isolated stale Sprint-138 idempotency-header expectation as test-only lifecycle hygiene.",
                "Then rehearse one provider-free unmounted status-confirm route-convergence composition.",
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
        "strategic_role": "The mounted legacy status-confirm route is mapped precisely but remains unadmitted onto the physical seam",
        "why_now": "The PostgreSQL transaction proof permitted an exact read-only inspection of the final route composition boundary.",
        "outcome": "Literal mounting and physical durability are satisfied; seven bounded composition gaps block unchanged convergence.",
        "unlocks": [
            "Repair one stale Sprint-138 test expectation without changing product behavior.",
            "Freeze a provider-free unmounted route-convergence composition rehearsal.",
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
        "EMR4 is at Continuity 266 / Compass 248. The status-confirm endpoint "
        "is literally mounted and its physical PostgreSQL seam is proved, but "
        "the unchanged legacy handler is not admitted onto it. One stale test "
        "expectation and then an unmounted composition rehearsal are next; "
        "route execution and product commands remain closed."
    )
    limit = (
        "The accepted route-mounting review proves static composition facts only; it does not admit or execute the mounted handler against the physical seam."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 266
    compass["map_revision"] = 248
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
