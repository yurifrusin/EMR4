"""Advance Continuity and Compass for the accepted inert DDL rehearsal."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts import ariadne_compass


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = "raisa-provider-free-unmounted-durability-inert-ddl-rehearsal"
PARENT = "raisa-provider-free-unmounted-durability-function-trigger-body-architecture"
SOURCE_HEAD = "46e16622471a192353cb82a33acf301dc2cfb7aa"
UPDATED_AT = "2026-08-07T00:00:00Z"
PLAN = "docs/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-plan.md"
DESIGN = PLAN.replace("-plan.md", "-design.md")
RECOVERY = PLAN.replace("-plan.md", "-postgresql-representability-recovery.md")
THREAT = (
    "docs/security/raisa-provider-free-unmounted-durability-inert-ddl-"
    "rehearsal-threat-model-delta.md"
)
CONTRACT_DIR = (
    "orchestration/continuity/raisa-provider-free-unmounted-durability-inert-"
    "ddl-rehearsal"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-"
    "inert-ddl-postgresql-recovery-implementation-review-receipt.json"
)
CLOSEOUT = PLAN.replace("-plan.md", "-closeout.md")
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-durability-inert-"
    "ddl-rehearsal-sol-acceptance.md"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_"
    "continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_"
    "continuity.py"
)
IMPLEMENTATION_TEST = (
    "tests/test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py"
)
PLAN_TEST = IMPLEMENTATION_TEST.replace(".py", "_plan.py")
RECOVERY_TEST = (
    "tests/test_raisa_provider_free_unmounted_durability_inert_ddl_"
    "postgresql_representability_recovery.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Unmounted durability inert DDL rehearsal",
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
                "The accepted PostgreSQL-16 text has a non-runnable .sql.inert suffix and was never sent to a database.",
                "The fixed-path standard-library renderer and recognizer add no migration, driver, connection or runtime.",
                "No database/source, product read, provider product path, command, deployment or protected capability is opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-durability-inert-ddl-rehearsal",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept exact byte-stable inert PostgreSQL-16 lowering after "
                    "representability recovery, without execution or database contact."
                ),
            }
        ],
        "claim_scope": [
            "The complete deterministic packet passes 62 tests at the accepted source HEAD.",
            "A fresh Gemini 3.6 Flash/high exact-HEAD veto reports no P0-P3 finding.",
            "The artifact contains 412 statements and the exact 9/14/14/23 recovered program and trigger populations.",
            "No SQL execution, migration, database/source contact, persistence, product read, command, runtime or protected capability is established.",
        ],
        "contract_evidence": [
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [
                    PLAN,
                    DESIGN,
                    RECOVERY,
                    REVIEW,
                    IMPLEMENTATION_TEST,
                    CLOSEOUT,
                ],
                "note": (
                    "The inert artifact preserves the exact patient-free durability "
                    "contracts and opens no live event, read or command path."
                ),
            },
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [DESIGN, REVIEW, PLAN_TEST, CLOSEOUT],
                "note": "The rendered evidence contains no patient or appointment payload.",
            },
        ],
        "evidence": {
            "plans": [PLAN, DESIGN, RECOVERY, THREAT],
            "findings": [
                REVIEW,
                "orchestration/agent_inbox/codex/raisa-context-fabric-durability-inert-ddl-rehearsal-sol-rejection-analysis-receipt.json",
                "docs/ariadne-agent-error-correction-register-revision-84.md",
            ],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                "orchestration/agent_inbox/codex/raisa-context-fabric-durability-inert-ddl-postgresql-recovery-implementation-review-predispatch-receipt.json"
            ],
            "tests": [
                IMPLEMENTATION_TEST,
                PLAN_TEST,
                RECOVERY_TEST,
                "tests/test_ariadne_agent_error_register.py",
                "tests/test_ariadne_continuity_engine.py",
                "tests/test_ariadne_compass.py",
                CONTINUITY_TEST,
            ],
            "artifacts": [CONTRACT_DIR, UPDATER],
        },
        "unresolved_gates": [
            "Patient, clinical, product-derived, financial, protected and historical-PHI data remain closed.",
            "PostgreSQL execution, server parse/catalogue acceptance, an applied migration and operational credentials remain separate gates.",
            "Database/outbox/feed/watcher/listener/source access, persistence, product reads and every route or command/write remain closed.",
            "Deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 230 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 231
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 231 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected inert-DDL Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Lower exact durability contracts into inert PostgreSQL-16 evidence",
        "outcome": (
            "The recovered byte-stable DDL artifact passes static admission while "
            "database execution and every operational boundary remain closed."
        ),
        "evidence": [PLAN, DESIGN, RECOVERY, THREAT, REVIEW, CLOSEOUT, ACCEPTANCE],
    }
    if (
        compass["map_revision"] == 212
        and compass["source_graph_revision"] == 230
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 213
        and compass["source_graph_revision"] == 231
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected inert-DDL Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Exact durability structure, bodies and inert PostgreSQL-16 lowering are accepted at fresh reviewed HEADs.",
                "The next safe descendant is a separately bounded provider-free disposable local PostgreSQL parse-and-catalogue rehearsal.",
                "Separately gate applied migration, application behavior, concurrency, live sources, product/patient data, commands, deployment and production.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Inert durability DDL accepted; disposable PostgreSQL planning is next",
        "why_now": (
            "The exact renderer and static recognizer now close the translation "
            "boundary, so server parsing can be isolated as its own disposable gate."
        ),
        "outcome": (
            "The 412-statement artifact passes 62 tests and a fresh independent "
            "veto with no P0-P3 issue."
        ),
        "unlocks": [
            "Freeze the smallest disposable PostgreSQL-16 parse-and-catalogue rehearsal plan.",
            "Use only the accepted inert artifact and synthetic prerequisite stubs with owned cleanup and no application migration.",
        ],
        "does_not_solve": [
            "PostgreSQL execution or catalogue acceptance, trigger/RLS behavior, concurrency or migration safety.",
            "Operational database/outbox/feed/watcher/listener/source access, credentials or persistence.",
            "Application/runtime implementation, product reads, patient/product data, providers, routes or commands.",
            "Deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 231 / Compass 213. The provider-free unmounted "
        "durability inert DDL rehearsal passes at exact reviewed HEAD. A separately "
        "bounded disposable PostgreSQL-16 parse-and-catalogue rehearsal is next; "
        "applied migration and every operational boundary remain closed."
    )
    limit = (
        "Inert DDL acceptance proves deterministic closed-subset PostgreSQL-16 text, "
        "not server parse, catalogue creation, trigger/RLS behavior, an applied "
        "migration, database/source access, persistence, command, runtime or deployment safety."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 213
    compass["source_graph_revision"] = 231
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
