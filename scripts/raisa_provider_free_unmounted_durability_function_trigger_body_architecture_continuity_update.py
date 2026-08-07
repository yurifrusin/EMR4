"""Advance Continuity and Compass for accepted durability body architecture."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts import ariadne_compass


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = "raisa-provider-free-unmounted-durability-function-trigger-body-architecture"
PARENT = "raisa-provider-free-unmounted-durability-migration-transaction-architecture"
SOURCE_HEAD = "a93d07405ad35d7d6c0603065625c17ec14ab23e"
UPDATED_AT = "2026-08-08T00:00:00Z"
PLAN = (
    "docs/raisa-provider-free-unmounted-durability-function-trigger-body-"
    "architecture-plan.md"
)
DESIGN = PLAN.replace("-plan.md", "-design.md")
FOURTH_RECOVERY = PLAN.replace("-plan.md", "-fourth-exact-veto-recovery.md")
THREAT = (
    "docs/security/raisa-provider-free-unmounted-durability-function-trigger-"
    "body-architecture-threat-model-delta.md"
)
CONTRACT_DIR = (
    "orchestration/continuity/raisa-provider-free-unmounted-durability-"
    "function-trigger-body-architecture"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-context-fabric-function-"
    "trigger-body-architecture-r7-final-review-retry-receipt.json"
)
FAILURE = REVIEW.replace("-retry-receipt.json", "-transport-failure-receipt.json")
CLOSEOUT = PLAN.replace("-plan.md", "-closeout.md")
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-"
    "body-architecture-sol-acceptance.md"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_durability_function_trigger_body_"
    "architecture_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_"
    "architecture_continuity.py"
)
BODY_TEST = (
    "tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_"
    "architecture.py"
)
PLAN_TEST = BODY_TEST.replace("architecture.py", "architecture_plan.py")


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Unmounted durability function-and-trigger-body architecture",
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
                "The accepted body catalogue is pure, provider-free, unmounted and machine-readable only.",
                "Nine entry-point and thirteen trigger-function programs are exact typed metadata, not SQL/DDL.",
                "No migration, database/source, product read, provider product path, command, runtime or deployment capability is opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-durability-function-trigger-body-architecture",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept exact typed bodies and the field-complete key-rotation "
                    "anchor fence without rendering or executing SQL."
                ),
            }
        ],
        "claim_scope": [
            "The complete deterministic packet passes 339 tests at the accepted source HEAD.",
            "A fresh focused Gemini 3.6 Flash/high veto passes 44 tests with no P0-P3 finding.",
            "The exact eleven-equality F_ANCHOR fence precedes prior-key lock, digest use and effect while replay remains inert.",
            "No SQL/DDL, migration, database/source contact, persistence, product read, provider product path, command, runtime or protected capability is established.",
        ],
        "contract_evidence": [
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [
                    PLAN,
                    DESIGN,
                    FOURTH_RECOVERY,
                    REVIEW,
                    BODY_TEST,
                    CLOSEOUT,
                ],
                "note": (
                    "The future durability family remains patient-free and "
                    "unmounted; the bodies add no live feed, read or command."
                ),
            },
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [DESIGN, REVIEW, PLAN_TEST, CLOSEOUT],
                "note": "The body contract carries no patient or appointment payload.",
            },
        ],
        "evidence": {
            "plans": [PLAN, DESIGN, FOURTH_RECOVERY, THREAT],
            "findings": [
                REVIEW,
                FAILURE,
                "orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-body-architecture-continuity-baseline-failure-receipt.json",
                "docs/ariadne-agent-error-correction-register-revision-80.md",
                "docs/ariadne-agent-error-correction-register-revision-81.md",
            ],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                "orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-body-architecture-r7-pre-verifier-acceptance-receipt.json"
            ],
            "tests": [
                BODY_TEST,
                PLAN_TEST,
                "tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_fourth_veto_rotation_anchor.py",
                "tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_third_veto_schema.py",
                "tests/test_ariadne_agent_error_register.py",
                "tests/test_ariadne_continuity_engine.py",
                "tests/test_ariadne_compass.py",
                CONTINUITY_TEST,
            ],
            "artifacts": [CONTRACT_DIR, UPDATER],
        },
        "unresolved_gates": [
            "Patient, clinical, product-derived, financial, protected and historical-PHI data remain closed.",
            "SQL/DDL execution, an applied migration, database/outbox/feed/watcher/listener/source access and operational credentials remain closed.",
            "Operational persistence, product reads, providers and every route or command/write remain closed.",
            "Deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 229 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 230
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 230 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected body-architecture Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Freeze exact durability bodies before inert DDL lowering",
        "outcome": (
            "The nine entry-point and thirteen trigger-function body programs "
            "pass while SQL lowering and every executable/live boundary remain closed."
        ),
        "evidence": [PLAN, DESIGN, FOURTH_RECOVERY, THREAT, REVIEW, CLOSEOUT, ACCEPTANCE],
    }
    if (
        compass["map_revision"] == 211
        and compass["source_graph_revision"] == 229
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 212
        and compass["source_graph_revision"] == 230
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected body-architecture Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Durability structure/signatures and exact function/trigger bodies are accepted at fresh reviewed HEADs.",
                "The next safe candidate is a provider-free unmounted inert DDL rehearsal with no execution or database contact.",
                "Separately gate applied migration, live database/source access, credentials, implementation, product reads, clinical data, commands, deployment and release.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Exact durability bodies accepted; inert DDL rehearsal is next",
        "why_now": (
            "The accepted typed body programmes can now be mechanically lowered "
            "and statically checked without applying or executing them."
        ),
        "outcome": (
            "The complete packet passes 339 checks and a fresh focused independent "
            "veto passes 44 checks with no P0-P3 issue."
        ),
        "unlocks": [
            "Freeze a mechanical PostgreSQL-16 renderer for the exact accepted parent and child contracts.",
            "Generate inert repository-local SQL artifacts and static grammar, ordering, catalogue and privilege assertions without execution.",
        ],
        "does_not_solve": [
            "SQL/DDL execution, an applied migration, live database objects or operational privileges.",
            "Database/outbox/feed/watcher/listener/source access, credentials or operational persistence.",
            "Application/runtime implementation, product reads, patient/product data, providers, routes or commands.",
            "Deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 230 / Compass 212. The provider-free unmounted "
        "durability function-and-trigger-body architecture passes at exact reviewed "
        "HEAD. Inert DDL rehearsal is next; SQL execution and every live or real-data "
        "boundary remain closed."
    )
    limit = (
        "Durability body-architecture acceptance proves exact typed programmes and "
        "static hostile-mutation resistance, not rendered or executable SQL/DDL, an "
        "applied migration, database/source contact, persistence, product-read, "
        "provider, command, runtime or deployment safety."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 212
    compass["source_graph_revision"] = 230
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
