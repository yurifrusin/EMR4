"""Advance Continuity and Compass for the status-confirm catalogue rehearsal."""

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
    "raisa-provider-free-disposable-postgresql-status-confirm-scaffold-"
    "parse-catalogue-rehearsal"
)
PARENT = (
    "raisa-provider-free-unmounted-status-confirm-physical-schema-transaction-"
    "scaffold"
)
SOURCE_HEAD = "bccc64f87eb0c1ae755b642fb6c4eb082298051d"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = (
    "docs/raisa-provider-free-disposable-postgresql-status-confirm-scaffold-"
    "parse-catalogue-rehearsal-plan.md"
)
THREAT = (
    "docs/security/raisa-provider-free-disposable-postgresql-status-confirm-"
    "scaffold-parse-catalogue-rehearsal-threat-model-delta.md"
)
CLOSEOUT = (
    "docs/raisa-provider-free-disposable-postgresql-status-confirm-scaffold-"
    "parse-catalogue-rehearsal-closeout.md"
)
BASE = (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-status-"
    "confirm-scaffold-parse-catalogue-rehearsal/"
)
CONTRACT = BASE + "rehearsal-contract.json"
CONTRACT_SCHEMA = BASE + "rehearsal-contract.schema.json"
EVIDENCE_SCHEMA = BASE + "provider-free-disposable-postgresql-evidence.schema.json"
EVIDENCE = BASE + "provider-free-disposable-postgresql-evidence.json"
FAILURE_EVIDENCE = BASE + "provider-free-disposable-postgresql-failure-evidence.json"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-status-confirm-scaffold-parse-"
    "catalogue-sol-acceptance.md"
)
PREPLANNING_STATE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-"
    "status-confirm-scaffold-parse-catalogue-preplanning-runtime-state.json"
)
PREPLANNING_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-"
    "status-confirm-scaffold-parse-catalogue-preplanning-receipt.json"
)
PRECOMMIT_STATE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-"
    "status-confirm-scaffold-parse-catalogue-precommit-runtime-state.json"
)
PRECOMMIT_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-"
    "status-confirm-scaffold-parse-catalogue-precommit-receipt.json"
)
PREPUSH_STATE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-"
    "status-confirm-scaffold-parse-catalogue-closeout-prepush-runtime-state.json"
)
PREPUSH_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-"
    "status-confirm-scaffold-parse-catalogue-closeout-prepush-receipt.json"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-12--status-confirm-scaffold-parse-catalogue-rehearsal.md"
)
HARNESS = (
    "scripts/raisa_provider_free_disposable_postgresql_status_confirm_scaffold_"
    "parse_catalogue_rehearsal.py"
)
TEST = (
    "tests/test_raisa_provider_free_disposable_postgresql_status_confirm_"
    "scaffold_parse_catalogue_rehearsal.py"
)
UPDATER = (
    "scripts/raisa_provider_free_disposable_postgresql_status_confirm_scaffold_"
    "parse_catalogue_rehearsal_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_disposable_postgresql_status_confirm_"
    "scaffold_parse_catalogue_rehearsal_continuity.py"
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
        CONTRACT_SCHEMA,
        EVIDENCE_SCHEMA,
        EVIDENCE,
        FAILURE_EVIDENCE,
        HARNESS,
        TEST,
        CLOSEOUT,
        ACCEPTANCE,
        PREPLANNING_STATE,
        PREPLANNING_RECEIPT,
        PRECOMMIT_STATE,
        PRECOMMIT_RECEIPT,
        PREPUSH_STATE,
        PREPUSH_RECEIPT,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free disposable PostgreSQL status-confirm scaffold parse/catalogue rehearsal",
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
                "The accepted result is provider-free, authored-synthetic and limited to one removed disposable PostgreSQL 16 instance.",
                "It proves exact migration admission, catalogue shape and nine rolled-back invariants; runtime authority remains false.",
                "Existing/product databases, routes, commands, patient/product data, providers, deployment and protected integration remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-status-confirm-scaffold-parse-catalogue-rehearsal",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept exact PostgreSQL 16 migration/catalogue admission and nine rolled-back authored-synthetic invariants; hand off only to the disposable behavior/transaction rehearsal.",
            }
        ],
        "claim_scope": [
            "Offline Alembic SQL for only v1w2x3y4z5b6:w2x3y4z5a6b7 installed into one networkless, portless, tmpfs-backed cached PostgreSQL 16 container.",
            "The exact Alembic head, six columns, three constraints, one invoker function, one enabled trigger and cutover version matched.",
            "Nine rolled-back probes proved defaults, database-owned increment, invalid-version rejection, v1 receipt admission, malformed-receipt rejection and legacy-null compatibility.",
            "Eight source bindings, 80 hostile mutations and 13 focused tests pass with captured-ID cleanup verified.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [
                THREAT,
                CONTRACT,
                CONTRACT_SCHEMA,
                EVIDENCE_SCHEMA,
                EVIDENCE,
                FAILURE_EVIDENCE,
            ],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                PREPLANNING_STATE,
                PREPLANNING_RECEIPT,
                PRECOMMIT_STATE,
                PRECOMMIT_RECEIPT,
                PREPUSH_STATE,
                PREPUSH_RECEIPT,
            ],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [HARNESS, UPDATER],
        },
        "unresolved_gates": [
            "The application transaction seam, ordered real locks, atomic appointment/audit/receipt write set, stored replay, response-loss retry and outer rollback remain unproved.",
            "No mounted route, product command, product data, concurrency, restart, unknown-commit, retention, performance or operations behavior has run.",
            "Providers, credentials, patient/product data, watchers/events, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 263 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 264
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 264 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected status-confirm catalogue Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove the exact status-confirm physical scaffold is admitted by PostgreSQL before application behavior is attempted",
        "outcome": "PostgreSQL 16 accepts the exact migration and catalogue, nine rolled-back synthetic invariants pass and the owned container is absent.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 245
        and compass["source_graph_revision"] == 263
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 246
        and compass["source_graph_revision"] == 264
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected status-confirm catalogue Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve the accepted source-owned-truth, conditional-command and status-confirm physical lineage.",
                "Prove the exact unmounted transaction seam in a provider-free disposable PostgreSQL behavior/transaction rehearsal next.",
                "Keep mounted routes, product data, commands, providers and protected integration separately gated.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "The status safety scaffold is admitted by PostgreSQL but application transaction behavior remains unproved",
        "why_now": "The inert source scaffold passed, permitting one isolated PostgreSQL parse/catalogue proof before composing application behavior.",
        "outcome": "Exact migration/catalogue admission, nine rolled-back invariants and complete exact-ID cleanup pass without route or durable product authority.",
        "unlocks": [
            "Run a provider-free disposable PostgreSQL status-confirm behavior/transaction rehearsal.",
            "Prove current-authority and lock order, atomic appointment/audit/v1-receipt commit, stored replay, response-loss retry and outer rollback.",
            "Use only authored-synthetic rows and remove the owned disposable database completely.",
        ],
        "does_not_solve": [
            "Mounted-route, real command, product-data or operational rollout behavior.",
            "Concurrency, restart, unknown commit, retention, performance or production safety.",
            "Provider/credential activity, patient/product data, watchers/events, deployment, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 264 / Compass 246. The exact status-confirm "
        "scaffold migration, PostgreSQL catalogue and nine rolled-back "
        "authored-synthetic invariants pass with complete disposable cleanup. "
        "The provider-free behavior/transaction rehearsal is next; routes and "
        "product commands remain closed."
    )
    limit = (
        "The accepted status-confirm PostgreSQL rehearsal proves parse/catalogue and selected rolled-back invariants only, not application transaction, route or product-command safety."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 264
    compass["map_revision"] = 246
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
