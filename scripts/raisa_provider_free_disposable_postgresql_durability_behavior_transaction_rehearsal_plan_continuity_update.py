"""Advance Continuity and Compass for the accepted behavior rehearsal plan."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts import ariadne_compass


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = (
    "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-"
    "rehearsal-plan"
)
PARENT = (
    "raisa-provider-free-disposable-postgresql-durability-parse-catalogue-"
    "rehearsal"
)
SOURCE_HEAD = "07e8750548ed69aba5a19f693a72397121a340e5"
UPDATED_AT = "2026-08-08T00:00:00Z"
PLAN = (
    "docs/raisa-provider-free-disposable-postgresql-durability-behavior-"
    "transaction-rehearsal-plan.md"
)
DESIGN = PLAN.replace("-plan.md", "-design.md")
THREAT = (
    "docs/security/raisa-provider-free-disposable-postgresql-durability-"
    "behavior-transaction-rehearsal-threat-model-delta.md"
)
CONTRACT_DIR = (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "durability-behavior-transaction-rehearsal"
)
CONTRACT = CONTRACT_DIR + "/behavior-transaction-rehearsal-contract.json"
SCHEMA = CONTRACT_DIR + "/behavior-transaction-rehearsal-contract.schema.json"
REJECTED_REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-"
    "behavior-transaction-rehearsal-plan-review-receipt.json"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-"
    "behavior-transaction-rehearsal-plan-correction-review-receipt.json"
)
AER_REVISION = "docs/ariadne-agent-error-correction-register-revision-92.md"
CLOSEOUT = PLAN.replace("-plan.md", "-plan-closeout.md")
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-durability-behavior-"
    "transaction-rehearsal-plan-sol-acceptance.md"
)
PLAN_TEST = (
    "tests/test_raisa_provider_free_disposable_postgresql_durability_behavior_"
    "transaction_rehearsal_plan.py"
)
CONTINUITY_TEST = PLAN_TEST.replace("_plan.py", "_plan_continuity.py")
UPDATER = (
    "scripts/raisa_provider_free_disposable_postgresql_durability_behavior_"
    "transaction_rehearsal_plan_continuity_update.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Disposable PostgreSQL durability behavior/transaction rehearsal plan",
        "kind": "concept",
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
                "The accepted result freezes twenty authored-synthetic serial scenarios but proves no database behavior.",
                "A future implementation remains limited to one owned networkless tmpfs-only local PostgreSQL 16 container with exact-ID cleanup.",
                "No applied migration, operational database/source, product read, provider product path, command, deployment or protected capability is opened.",
                "Yuri explicitly requested a pause after this planning closeout, so runtime implementation has not begun.",
            ],
        },
        "decisions": [
            {
                "id": "accept-disposable-postgresql-durability-behavior-transaction-rehearsal-plan",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept the exact twenty-scenario behavior/transaction "
                    "experiment specification while keeping all runtime and "
                    "operational authority closed."
                ),
            }
        ],
        "claim_scope": [
            "Exactly twenty ordered scenarios cover 6 entry-point, 4 trigger, 3 RLS/privilege, 4 idempotency and 3 rollback cases.",
            "All six text parents are canonical UTF-8/LF SHA-256 bound without changing a parent artifact.",
            "Fresh r74 passes 124/124 admitted planning tests and 79/79 AER tests with zero P0-P3 findings.",
            "The result proves planning completeness only; no Docker/PostgreSQL behavior run occurred.",
        ],
        "contract_evidence": [
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [PLAN, DESIGN, REVIEW, PLAN_TEST, CLOSEOUT],
                "note": (
                    "The plan freezes one synthetic update-confirm projection "
                    "thread without opening a product command or event runtime."
                ),
            },
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [DESIGN, PLAN_TEST, CLOSEOUT],
                "note": (
                    "Every fixture is opaque and authored-synthetic; no patient "
                    "identity, name, reason or clinical value is admitted."
                ),
            },
        ],
        "evidence": {
            "plans": [PLAN, DESIGN, THREAT],
            "findings": [REJECTED_REVIEW, REVIEW, AER_REVISION],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                "orchestration/agent_inbox/codex/raisa-context-fabric-durability-behavior-transaction-rehearsal-plan-correction-veto-predispatch-receipt.json"
            ],
            "tests": [
                PLAN_TEST,
                "tests/test_ariadne_agent_error_register.py",
                "tests/test_ariadne_continuity_engine.py",
                "tests/test_ariadne_compass.py",
                CONTINUITY_TEST,
            ],
            "artifacts": [CONTRACT, SCHEMA, UPDATER],
        },
        "unresolved_gates": [
            "Patient, clinical, product-derived, financial, protected and historical-PHI data remain closed.",
            "The fixed harness, fresh implementation veto and twenty-scenario disposable PostgreSQL run remain unstarted.",
            "Concurrency, key rotation, retention execution and unknown-commit recovery remain later finite gates.",
            "Applied migration, operational database/outbox/feed/watcher/listener/source access, persistence and credentials remain closed.",
            "Product reads, providers, routes, commands, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 232 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 233
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 233 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected behavior-plan Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Freeze the first server-backed durability behavior experiment",
        "outcome": (
            "Twenty exact synthetic behavior/transaction scenarios are accepted "
            "for later implementation while the database run remains closed."
        ),
        "evidence": [
            PLAN,
            DESIGN,
            THREAT,
            CONTRACT,
            SCHEMA,
            REJECTED_REVIEW,
            REVIEW,
            AER_REVISION,
            CLOSEOUT,
            ACCEPTANCE,
        ],
    }
    if (
        compass["map_revision"] == 214
        and compass["source_graph_revision"] == 232
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 215
        and compass["source_graph_revision"] == 233
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected behavior-plan Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Exact durability structure, bodies, inert lowering and isolated PostgreSQL-16 catalogue admission are accepted.",
                "The twenty-scenario serial behavior/transaction experiment is frozen and awaits its fixed harness after Yuri's requested pause.",
                "Separately gate concurrency, rotation, retention, applied migration, application wiring, operational sources and product/patient data.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Behavior experiment frozen; runtime implementation paused",
        "why_now": (
            "PostgreSQL already accepts the exact durability catalogue, so the "
            "next safe proof is now finite and implementation-ready."
        ),
        "outcome": (
            "The exact twenty-scenario plan passes 124 planning tests and 79 AER "
            "tests under a fresh zero-finding independent veto."
        ),
        "unlocks": [
            "After the requested pause, implement the fixed-path provider-free harness and evidence schema.",
            "Obtain a fresh exact-HEAD implementation veto before one owned disposable PostgreSQL run.",
        ],
        "does_not_solve": [
            "Function, trigger, RLS, idempotency or rollback behavior until the planned runtime passes.",
            "Concurrency, key rotation, retention execution or unknown-commit recovery.",
            "Applied migration, database/outbox/feed/watcher/listener/source access, credentials or persistence.",
            "Application/runtime wiring, product reads, patient/product data, providers, routes or commands.",
            "Deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 233 / Compass 215. The first provider-free "
        "database-backed durability behavior/transaction experiment is frozen "
        "as twenty exact synthetic scenarios at a fresh reviewed planning HEAD. "
        "Runtime implementation is paused at Yuri's request; every operational "
        "and product boundary remains closed."
    )
    limit = (
        "Behavior/transaction planning acceptance proves experiment completeness "
        "only; it does not prove PostgreSQL function, trigger, RLS, idempotency "
        "or rollback behavior and opens no applied migration or product runtime."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 215
    compass["source_graph_revision"] = 233
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
