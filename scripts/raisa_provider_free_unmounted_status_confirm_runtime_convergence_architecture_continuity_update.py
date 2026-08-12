"""Advance Continuity and Compass for status-confirm convergence architecture."""

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
NODE_ID = "raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture"
PARENT = "raisa-provider-free-read-only-status-confirm-runtime-gap-admission-review"
SOURCE_HEAD = "b9cc57b6e607e5896e822abc7b632442df2f907e"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = (
    "docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-"
    "architecture-plan.md"
)
DESIGN = (
    "docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-"
    "architecture.md"
)
THREAT = (
    "docs/security/raisa-provider-free-unmounted-status-confirm-runtime-"
    "convergence-architecture-threat-model-delta.md"
)
CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-"
    "architecture-closeout.md"
)
BASE = (
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-"
    "runtime-convergence-architecture/"
)
CONTRACT = BASE + "convergence-architecture-contract.json"
SCHEMA = BASE + "convergence-architecture-contract.schema.json"
EVIDENCE = BASE + "provider-free-architecture-evidence.json"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-status-confirm-runtime-"
    "convergence-architecture-sol-acceptance.md"
)
PREPLANNING = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-"
    "confirm-runtime-convergence-architecture-preplanning-receipt.json"
)
PRECOMMIT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-"
    "confirm-runtime-convergence-architecture-precommit-receipt.json"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-12--status-confirm-runtime-convergence-architecture.md"
)
TEST = (
    "tests/test_raisa_provider_free_unmounted_status_confirm_runtime_"
    "convergence_architecture.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_status_confirm_runtime_"
    "convergence_architecture_continuity.py"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_status_confirm_runtime_"
    "convergence_architecture_continuity_update.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        DESIGN,
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
        "title": "Provider-free unmounted status-confirm runtime convergence architecture",
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
                "The architecture is provider-free, authored-synthetic and unmounted; implementation_authorized is false.",
                "It closes nine design gaps through a status-only seam and one authority-first ordered transaction.",
                "Physical version storage, migration, route/database execution, provider, product data and commands remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-status-confirm-runtime-convergence-architecture",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept nine closed convergence decisions and hand off only to an unmounted in-memory rehearsal.",
            }
        ],
        "claim_scope": [
            "Status-only discrimination preserves waiting-area behavior outside the kernel.",
            "Practice, appointment and idempotency locks precede current-authority recheck and replay/conflict disclosure.",
            "Signed session/version/warning evidence, terminal deferral, atomic audit/receipt correlation and stored delivery are architecturally bound.",
            "Twenty scenarios and 56 hostile mutations prove contract coherence, not runtime or PostgreSQL behavior.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [DESIGN, THREAT, CONTRACT, SCHEMA, EVIDENCE],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING, PRECOMMIT],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "The provider-free unmounted status-confirm runtime convergence rehearsal has not yet executed.",
            "Physical version storage, migration/backfill, ORM/service and route integration remain unselected and unproved.",
            "Database execution, raw-route change, create schedule fencing, providers, product/patient data, commands, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 258 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 259
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 259 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected convergence-architecture Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Resolve the finite status route-to-kernel gaps before any runtime implementation",
        "outcome": "Nine closed architecture decisions, 20 scenarios and 56 hostile mutations pass; an unmounted state-machine rehearsal is next.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 240
        and compass["source_graph_revision"] == 258
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 241
        and compass["source_graph_revision"] == 259
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected convergence-architecture Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve the accepted source-owned-truth, status protocol, adapter and runtime-gap review contracts.",
                "Run the provider-free unmounted status-confirm convergence rehearsal before any physical storage or route implementation.",
                "Keep raw-route change, create schedule fencing, providers, product data, commands and protected integration separately gated.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Status route-to-kernel convergence is coherent but remains unmounted",
        "why_now": "The read-only review isolated a finite gap set, allowing one architecture to close it without opening application or database authority.",
        "outcome": "Status-only ingress, authority-first ordered locks, version/warning evidence, atomic audit/receipt and stored delivery now pass 20 scenarios and 56 hostile mutations.",
        "unlocks": [
            "Run a provider-free unmounted in-memory convergence rehearsal over the exact architecture.",
            "Prove rollback, response-loss recovery and authority-first replay disclosure without a route or database.",
            "Keep physical version storage and runtime integration behind later evidence gates.",
        ],
        "does_not_solve": [
            "Physical appointment-state version storage, migration/backfill or ORM/service design.",
            "Mounted route behavior, PostgreSQL locking/concurrency or restart/unknown-commit recovery.",
            "Raw compatibility-route removal or create schedule-conflict fencing.",
            "Provider/credential activity, patient/product data, product commands, deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 259 / Compass 241. The provider-free unmounted "
        "status-confirm convergence architecture passes with nine closed decisions, "
        "20 scenarios and 56 hostile rejections. An unmounted state-machine rehearsal "
        "is next; physical storage, route/database runtime and product authority remain closed."
    )
    limit = (
        "The status-confirm convergence architecture proves closed design coherence, not physical state-version storage, route integration or PostgreSQL behavior."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 259
    compass["map_revision"] = 241
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
