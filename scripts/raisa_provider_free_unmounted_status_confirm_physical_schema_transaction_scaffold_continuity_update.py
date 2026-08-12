"""Advance Continuity and Compass for the unmounted physical scaffold."""

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
    "raisa-provider-free-unmounted-status-confirm-physical-schema-transaction-"
    "scaffold"
)
PARENT = "raisa-provider-free-unmounted-status-confirm-physical-design-architecture"
SOURCE_HEAD = "b36b8a455b70d8bc3e99b5e5dd84a8237375ff3c"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = (
    "docs/raisa-provider-free-unmounted-status-confirm-physical-schema-"
    "transaction-scaffold-plan.md"
)
THREAT = (
    "docs/security/raisa-provider-free-unmounted-status-confirm-physical-schema-"
    "transaction-scaffold-threat-model-delta.md"
)
CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-status-confirm-physical-schema-"
    "transaction-scaffold-closeout.md"
)
BASE = (
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-"
    "physical-schema-transaction-scaffold/"
)
CONTRACT = BASE + "scaffold-contract.json"
SCHEMA = BASE + "scaffold-contract.schema.json"
EVIDENCE = BASE + "provider-free-scaffold-evidence.json"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-status-confirm-physical-schema-"
    "transaction-scaffold-sol-acceptance.md"
)
PREPLANNING = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-confirm-"
    "physical-schema-transaction-scaffold-preplanning-receipt.json"
)
REJECTED_STATE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-confirm-"
    "physical-schema-transaction-scaffold-preacceptance-runtime-state.json"
)
REJECTED_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-confirm-"
    "physical-schema-transaction-scaffold-preacceptance-receipt.json"
)
PRECOMMIT_STATE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-confirm-"
    "physical-schema-transaction-scaffold-precommit-runtime-state.json"
)
PRECOMMIT_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-confirm-"
    "physical-schema-transaction-scaffold-precommit-receipt.json"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-12--status-confirm-physical-schema-transaction-scaffold.md"
)
MODEL = "app/models/appointments.py"
SERVICE = "app/services/appointment_status_physical.py"
MIGRATION = (
    "alembic/versions/w2x3y4z5a6b7_add_status_confirm_physical_scaffold.py"
)
VALIDATOR = (
    "scripts/raisa_provider_free_unmounted_status_confirm_physical_schema_"
    "transaction_scaffold.py"
)
TEST = (
    "tests/test_raisa_provider_free_unmounted_status_confirm_physical_schema_"
    "transaction_scaffold.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_status_confirm_physical_schema_"
    "transaction_scaffold_continuity.py"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_status_confirm_physical_schema_"
    "transaction_scaffold_continuity_update.py"
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
        MODEL,
        SERVICE,
        MIGRATION,
        CLOSEOUT,
        ACCEPTANCE,
        PREPLANNING,
        REJECTED_STATE,
        REJECTED_RECEIPT,
        PRECOMMIT_STATE,
        PRECOMMIT_RECEIPT,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free unmounted status-confirm physical schema-and-transaction scaffold",
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
                "The accepted source is an authored-synthetic, provider-free, unmounted scaffold with runtime authority false.",
                "It maps the exact schema and supplies inert DDL plus pure helpers and a future transaction composition seam.",
                "Migration/database/SQL execution, real locks, routes, providers, product data and commands remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-status-confirm-physical-schema-transaction-scaffold",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept the exact unmounted mapping, inert migration, pure receipt helpers and authority-first transaction seam; hand off only to a disposable PostgreSQL parse/catalogue rehearsal.",
            }
        ],
        "claim_scope": [
            "The ORM maps one positive database-owned BIGINT revision and five nullable-for-legacy private receipt fields with conditional v1 constraints.",
            "One inert seven-phase migration lowers the cutover and synchronous before-update trigger without execution.",
            "Pure helpers produce exact canonical response bytes, raw domain-separated 32-byte session HMACs and constant-time integrity decisions.",
            "The unmounted seam composes one bounded READ COMMITTED practice, appointment and idempotency lock order with two authority checks and conflict-safe insertion.",
            "Sixteen bindings, 80 hostile mutations, 11 focused tests and 274 current descendant tests pass; public OpenAPI remains unchanged.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [THREAT, CONTRACT, SCHEMA, EVIDENCE],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                PREPLANNING,
                REJECTED_STATE,
                REJECTED_RECEIPT,
                PRECOMMIT_STATE,
                PRECOMMIT_RECEIPT,
            ],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [MODEL, SERVICE, MIGRATION, VALIDATOR, UPDATER],
        },
        "unresolved_gates": [
            "PostgreSQL has not parsed or installed the migration and exact catalogues/trigger behavior remain unproved.",
            "No real lock, transaction, rollback, concurrency, restart, unknown-commit or route behavior has run.",
            "Product/patient data, providers, credentials, watchers/events, commands, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 262 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 263
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 263 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected physical-scaffold Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Embody the accepted status safety design without opening a database or route",
        "outcome": "The exact mapping, inert migration, receipt helpers and ordered transaction seam pass as an unmounted scaffold.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 244
        and compass["source_graph_revision"] == 262
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 245
        and compass["source_graph_revision"] == 263
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected physical-scaffold Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve the accepted source-owned-truth, status convergence and physical-design lineage.",
                "Prove only the exact inert migration and catalogue shape in an owned disposable PostgreSQL instance next.",
                "Keep route integration, product data, commands, providers and protected integration separately gated.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "The status safety kernel has an unmounted physical source scaffold but no executed database embodiment",
        "why_now": "The exact physical design passed, allowing a narrow source lowering before any live database or route proof.",
        "outcome": "Mapping, inert DDL, exact-byte/session-digest helpers and the authority-first lock seam pass deterministic gates without runtime authority.",
        "unlocks": [
            "Run a provider-free disposable PostgreSQL status-confirm scaffold parse/catalogue rehearsal.",
            "Verify only exact columns, constraints, function, trigger and rollback-safe authored-synthetic invariants.",
            "Clean up the owned disposable database completely before any later behavior gate.",
        ],
        "does_not_solve": [
            "Mounted-route, real command, application transaction or operational rollout behavior.",
            "Concurrency, restart, unknown commit, retention, performance or production safety.",
            "Provider/credential activity, patient/product data, watchers/events, product commands, deployment, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 263 / Compass 245. The unmounted status-confirm "
        "physical schema-and-transaction scaffold passes with exact mapping, "
        "inert DDL, receipt helpers and ordered-lock composition. A disposable "
        "PostgreSQL parse/catalogue rehearsal is next; routes and product "
        "commands remain closed."
    )
    limit = (
        "The accepted status-confirm physical scaffold proves source lowering only, not PostgreSQL installation, real locks, route behavior or product command safety."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 263
    compass["map_revision"] = 245
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
