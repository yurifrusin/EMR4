"""Advance Continuity and Compass for the accepted durability DDL architecture."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts import ariadne_compass


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = "raisa-provider-free-unmounted-durability-migration-transaction-architecture"
PARENT = (
    "raisa-provider-free-unmounted-authored-synthetic-durability-state-machine-"
    "rehearsal"
)
SOURCE_HEAD = "c55d25d6c9704ae4612ef2d123158f71302ab411"
UPDATED_AT = "2026-08-06T00:00:00Z"
PLAN = "docs/raisa-provider-free-unmounted-durability-migration-transaction-architecture-plan.md"
DESIGN = PLAN.replace("-plan.md", "-design.md")
THREAT = (
    "docs/security/raisa-provider-free-unmounted-durability-migration-transaction-"
    "architecture-threat-model-delta.md"
)
CONTRACT_DIR = (
    "orchestration/continuity/raisa-provider-free-unmounted-durability-migration-"
    "transaction-architecture"
)
TEST = (
    "tests/test_raisa_provider_free_unmounted_durability_migration_transaction_"
    "architecture_plan.py"
)
REVIEW = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-durability-migration-"
    "transaction-architecture-recovery-9-independent-veto.md"
)
CLOSEOUT = PLAN.replace("-plan.md", "-closeout.md")
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-durability-migration-"
    "transaction-architecture-sol-acceptance.md"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_durability_migration_transaction_"
    "architecture_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_durability_migration_transaction_"
    "architecture_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Unmounted durability migration-and-transaction architecture",
        "kind": "implementation",
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
                "The accepted catalogue is pure, provider-free, unmounted and structural/signature-only.",
                "Entry-point and trigger-function bodies, trigger declarations and execute grants remain machine-omitted.",
                "No SQL/DDL, migration, database/source, product read, provider, command, runtime or deployment capability is opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-durability-migration-transaction-architecture",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept the future PostgreSQL structural, role/RLS, admission, "
                    "transaction, temporal-fence, key and retention boundary."
                ),
            }
        ],
        "claim_scope": [
            "The complete deterministic packet passes 212 tests at the accepted source HEAD.",
            "Eight vetoes remain preserved as rejections and the ninth reports no P0-P2 finding.",
            "Exact structural renderer omission prevents prose from becoming invented PL/pgSQL.",
            "No executable SQL/DDL, migration, live database/source, persistence, product read, provider, command, runtime or protected capability is established.",
        ],
        "contract_evidence": [
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [PLAN, DESIGN, TEST, CLOSEOUT],
                "note": (
                    "The future durability family remains patient-free and "
                    "unmounted; no feed, read, persistence or command is added."
                ),
            },
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [DESIGN, TEST, CLOSEOUT],
                "note": "The declarative architecture carries no patient or appointment payload.",
            },
        ],
        "evidence": {
            "plans": [PLAN, DESIGN, THREAT],
            "findings": [
                REVIEW,
                "docs/ariadne-agent-error-correction-register-revision-61.md",
            ],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [],
            "tests": [
                TEST,
                "tests/test_raisa_provider_free_unmounted_authored_synthetic_durability_state_machine_rehearsal_plan.py",
                "tests/test_raisa_provider_free_unmounted_source_specific_durability_architecture.py",
                "tests/test_api_spine_artifacts.py",
                "tests/test_api_spine_blueprint_first_boundary.py",
                "tests/test_ariadne_agent_error_register.py",
                CONTINUITY_TEST,
            ],
            "artifacts": [CONTRACT_DIR, UPDATER],
        },
        "unresolved_gates": [
            "Patient, clinical, product-derived, financial, protected and historical-PHI data remain closed.",
            "Function and trigger bodies, SQL/DDL, migrations, database/outbox/feed/watcher/listener/source access and operational credentials remain closed.",
            "Operational persistence, product reads, providers and every route or command/write remain closed.",
            "Deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 228 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 229
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 229 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected durability architecture Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Freeze future durability structure before executable bodies",
        "outcome": (
            "The structural/signature architecture passes while all unreviewed "
            "function bodies, triggers, grants and DDL remain omitted."
        ),
        "evidence": [PLAN, DESIGN, THREAT, REVIEW, CLOSEOUT, ACCEPTANCE],
    }
    if (
        compass["map_revision"] == 210
        and compass["source_graph_revision"] == 228
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 211
        and compass["source_graph_revision"] == 229
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected durability architecture Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "The durability state machine and structural migration/transaction architecture are accepted at exact reviewed HEADs.",
                "The next safe candidate is a function-and-trigger-body architecture that still renders or executes no SQL.",
                "Separately gate DDL rehearsal, live database/source access, credentials, implementation, product reads, clinical data, commands, deployment and release.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": (
            "Durability structure accepted; function-and-trigger-body architecture is next"
        ),
        "why_now": (
            "Executable semantics must be independently frozen before any inert DDL "
            "renderer or rehearsal can safely exist."
        ),
        "outcome": (
            "The complete packet passes 212 checks and the final independent veto "
            "finds no P0-P2 issue."
        ),
        "unlocks": [
            "Specify exact security-definer and trigger-function bodies as repository-local authored-synthetic metadata.",
            "Bind exact relations, columns, SQLSTATE failures, privilege effects and renderer ordering without rendering SQL.",
        ],
        "does_not_solve": [
            "Executable bodies, trigger declarations, execute grants, SQL/DDL, migrations or database objects.",
            "Live database/outbox/feed/watcher/listener/source access, credentials or operational persistence.",
            "Application/runtime implementation, product reads, patient/product data, providers, routes or commands.",
            "Deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 229 / Compass 211. The provider-free unmounted "
        "durability migration-and-transaction structural architecture passes at "
        "exact reviewed HEAD. Function-and-trigger-body architecture is next; "
        "DDL and every live or real-data boundary remain closed."
    )
    limit = (
        "Durability migration/transaction acceptance proves declarative structure "
        "and transaction semantics, not executable bodies, SQL/DDL, a migration, "
        "database/source contact, persistence, product-read, provider, command, "
        "runtime or deployment safety."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 211
    compass["source_graph_revision"] = 229
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
