"""Advance Continuity and Compass for the status-confirm runtime-gap review."""

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
NODE_ID = "raisa-provider-free-read-only-status-confirm-runtime-gap-admission-review"
PARENT = "raisa-provider-free-unmounted-status-confirm-kernel-adapter-contract"
SOURCE_HEAD = "426ccbbd26a2ab0bfb70c65d7adce113f0239f3a"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = (
    "docs/raisa-provider-free-read-only-status-confirm-runtime-gap-"
    "admission-review-plan.md"
)
REVIEW = (
    "docs/raisa-provider-free-read-only-status-confirm-runtime-gap-"
    "admission-review.md"
)
THREAT = (
    "docs/security/raisa-provider-free-read-only-status-confirm-runtime-gap-"
    "admission-review-threat-model-delta.md"
)
CLOSEOUT = (
    "docs/raisa-provider-free-read-only-status-confirm-runtime-gap-"
    "admission-review-closeout.md"
)
BASE = (
    "orchestration/continuity/raisa-provider-free-read-only-status-confirm-"
    "runtime-gap-admission-review/"
)
CONTRACT = BASE + "runtime-gap-review-contract.json"
SCHEMA = BASE + "runtime-gap-review-contract.schema.json"
EVIDENCE = BASE + "runtime-gap-review-evidence.json"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-read-only-status-"
    "confirm-runtime-gap-admission-review-sol-acceptance.md"
)
PREPLANNING = (
    "orchestration/agent_inbox/codex/raisa-provider-free-read-only-status-"
    "confirm-runtime-gap-admission-review-preplanning-receipt.json"
)
PRECOMMIT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-read-only-status-"
    "confirm-runtime-gap-admission-review-precommit-receipt.json"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-12--status-confirm-runtime-gap-admission-review.md"
)
TEST = (
    "tests/test_raisa_provider_free_read_only_status_confirm_runtime_gap_"
    "admission_review.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_read_only_status_confirm_runtime_gap_"
    "admission_review_continuity.py"
)
UPDATER = (
    "scripts/raisa_provider_free_read_only_status_confirm_runtime_gap_"
    "admission_review_continuity_update.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        REVIEW,
        THREAT,
        CONTRACT,
        SCHEMA,
        EVIDENCE,
        CLOSEOUT,
        ACCEPTANCE,
        PREPLANNING,
        PRECOMMIT,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free read-only status-confirm runtime-gap admission review",
        "kind": "review",
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
                "The review is provider-free, read-only and limited to eleven exact hash-bound non-protected source files.",
                "Its accepted verdict is not_admitted: seven blocking gaps, two partial gaps and zero satisfied dimensions.",
                "No application edit/import, route/database execution, provider, credential, product data, command or runtime opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-status-confirm-runtime-gap-not-admitted-verdict",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept the finite nine-dimension gap review and require an unmounted convergence architecture before runtime implementation.",
            }
        ],
        "claim_scope": [
            "The current route passes its existing behavior contracts but is not admitted unchanged to the stricter status transaction kernel.",
            "Seven blockers cover lock order, current authority/session, status-only discrimination, terminal policy, exact warnings, audit correlation and authority-first replay disclosure.",
            "Two partial gaps cover session/source-version evidence and canonical initial/replay stored-receipt delivery.",
            "The result is exact-file structural admission evidence, not a runtime safety or database concurrency proof.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [REVIEW, THREAT, CONTRACT, SCHEMA, EVIDENCE],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING, PRECOMMIT],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "The provider-free unmounted status-confirm runtime convergence architecture has not yet been frozen or accepted.",
            "No route edit, database execution, runtime kernel, raw-route change or create schedule fence is authorised.",
            "Provider/credential activity, product/patient data, watchers/events, commands, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 257 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 258
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 258 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected status-confirm gap-review Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prevent premature runtime convergence by resolving exact route-to-kernel gaps",
        "outcome": "The exact current route is not admitted unchanged: seven blockers and two partial gaps define one finite unmounted convergence-architecture handoff.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 239
        and compass["source_graph_revision"] == 257
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 240
        and compass["source_graph_revision"] == 258
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected status-confirm gap-review Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve the accepted source-owned-truth and status transaction-kernel contracts.",
                "Freeze the provider-free unmounted status-confirm runtime convergence architecture before any route or database implementation.",
                "Keep create schedule fencing, raw-route changes, providers, product data, runtime commands and protected integration separately gated.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Exact route-to-kernel gaps frozen before runtime convergence",
        "why_now": "The pure adapter passes, so the next safe step was to compare its contract with the current route without opening application or database authority.",
        "outcome": "The review passes with a not_admitted verdict: seven blockers, two partial gaps, 15 structural assertions and 37 hostile rejections.",
        "unlocks": [
            "Freeze a provider-free unmounted status-confirm runtime convergence architecture over the finite nine-dimension gap set.",
            "Preserve current signed evidence, atomic mutation/audit/idempotency staging and stored replay while moving them behind authority-first locks.",
            "Continue under standing authority without editing or executing the route or database.",
        ],
        "does_not_solve": [
            "Route implementation, database concurrency or a mounted transaction kernel.",
            "Raw compatibility-route removal or create schedule-conflict fencing.",
            "Provider/credential activity, patient/product data, watchers/events or product commands.",
            "Deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 258 / Compass 240. The read-only status-confirm "
        "runtime-gap review passes with the existing route not admitted unchanged: "
        "seven blockers and two partial gaps now define a finite provider-free "
        "unmounted convergence-architecture tranche."
    )
    limit = (
        "The status-confirm runtime-gap review is structural exact-file evidence; it does not prove runtime locking, database concurrency or route safety under the stricter kernel."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 258
    compass["map_revision"] = 240
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
