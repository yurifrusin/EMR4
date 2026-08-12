"""Advance Continuity and Compass for status-confirm physical design."""

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
NODE_ID = "raisa-provider-free-unmounted-status-confirm-physical-design-architecture"
PARENT = "raisa-provider-free-read-only-status-confirm-physical-representability-review"
SOURCE_HEAD = "826aad11c29007b13eaa377e3f7ea494cc82ce70"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = "docs/raisa-provider-free-unmounted-status-confirm-physical-design-architecture-plan.md"
THREAT = (
    "docs/security/raisa-provider-free-unmounted-status-confirm-physical-design-"
    "architecture-threat-model-delta.md"
)
CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-status-confirm-physical-design-"
    "architecture-closeout.md"
)
BASE = (
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-"
    "physical-design-architecture/"
)
CONTRACT = BASE + "physical-design-contract.json"
SCHEMA = BASE + "physical-design-contract.schema.json"
EVIDENCE = BASE + "provider-free-unmounted-architecture-evidence.json"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-status-confirm-physical-design-"
    "architecture-sol-acceptance.md"
)
PREPLANNING = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-confirm-"
    "physical-design-architecture-preplanning-receipt.json"
)
PRECOMMIT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-confirm-"
    "physical-design-architecture-precommit-receipt.json"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-12--status-confirm-physical-design-architecture.md"
)
TEST = "tests/test_raisa_provider_free_unmounted_status_confirm_physical_design_architecture.py"
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_status_confirm_physical_design_"
    "architecture_continuity.py"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_status_confirm_physical_design_"
    "architecture_continuity_update.py"
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
        CLOSEOUT,
        ACCEPTANCE,
        PREPLANNING,
        PRECOMMIT,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free unmounted status-confirm physical-design architecture",
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
                "The accepted design is authored-synthetic, provider-free and unmounted; implementation_authorized is false at its source.",
                "It selects database-owned state versioning, versioned private receipts, exact response bytes and one ordered transaction without executing any of them.",
                "Application edits, executable DDL, database execution, routes, providers, product data and commands remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-status-confirm-physical-design-architecture",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept the exact additive state-version, private-receipt and ordered-transaction design and hand off only to an unmounted scaffold implementation.",
            }
        ],
        "claim_scope": [
            "PostgreSQL owns a positive BIGINT appointment revision with a cutover baseline of one and a synchronous before-update invariant.",
            "A versioned private receipt adds five nullable-for-legacy fields; legacy rows are never inferred as replayable v1 receipts.",
            "Initial and replay delivery use exact stored canonical bytes after integrity verification while the public OpenAPI envelope remains unchanged.",
            "One bounded READ COMMITTED transaction locks practice, appointment and idempotency record in order and checks current authority before classification or disclosure.",
            "All eleven hashes, 91 hostile mutations and 16 focused tests pass; no mounted or database behavior is claimed.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [THREAT, CONTRACT, SCHEMA, EVIDENCE],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING, PRECOMMIT],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "No ORM model, migration, service helper or route embodies the accepted physical design.",
            "Executable DDL, PostgreSQL catalogue/trigger/lock behavior and mounted-route parity remain unproved.",
            "Product/patient data, providers, credentials, watchers/events, commands, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 261 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 262
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 262 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected physical-design Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Freeze the physical source-of-truth and race boundary before any runtime edit",
        "outcome": "One exact additive database-owned version, private receipt and ordered transaction design passes; implementation remains unmounted.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 243
        and compass["source_graph_revision"] == 261
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 244
        and compass["source_graph_revision"] == 262
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected physical-design Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve the accepted source-owned-truth, status protocol, convergence rehearsal and physical representability findings.",
                "Implement only the exact provider-free unmounted physical schema-and-transaction scaffold before any executable database or route proof.",
                "Keep database execution, mounted routes, providers, product data, commands and protected integration separately gated.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "The status safety kernel now has one exact physical design but no runtime embodiment",
        "why_now": "The prior exact-file review proved additive feasibility, allowing material schema, receipt and lock decisions to be frozen without implementation.",
        "outcome": "Database-owned revisioning, versioned exact-byte receipts and the ordered transaction are selected and hostile-tested; all executable surfaces remain closed.",
        "unlocks": [
            "Implement a provider-free unmounted status-confirm physical schema-and-transaction scaffold.",
            "Lower only the exact model, inert migration and unmounted helper contract under deterministic static tests.",
            "Keep database and route execution behind later evidence gates.",
        ],
        "does_not_solve": [
            "Executable Alembic lowering, ORM/service correctness or mounted-route behavior.",
            "PostgreSQL catalogue, trigger, lock-wait, deadlock, rollback, restart or unknown-commit behavior.",
            "Provider/credential activity, patient/product data, watchers/events, product commands, deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 262 / Compass 244. The unmounted status-confirm "
        "physical-design architecture passes with one database-owned revision, "
        "versioned exact-byte private receipt and ordered transaction. An "
        "unmounted scaffold implementation is next; database and route execution "
        "remain closed."
    )
    limit = (
        "The accepted status-confirm physical design proves a closed architecture, not executable DDL, PostgreSQL behavior, ORM/service wiring or a mounted route."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 262
    compass["map_revision"] = 244
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
