"""Advance Continuity and Compass for the accepted database behavior pass."""

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
    "rehearsal"
)
PARENT = NODE_ID + "-plan"
SOURCE_HEAD = "f3383dc4099b4ee590014bea62dddb146f5d2a16"
UPDATED_AT = "2026-08-08T00:00:00Z"
PLAN = "docs/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal-plan.md"
DESIGN = PLAN.replace("-plan.md", "-design.md")
THREAT = "docs/security/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal-threat-model-delta.md"
BASE = "orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/"
PASS = (
    BASE
    + "provider-free-behavior-transaction-evidence-admission-replay-recovery-pass.json"
)
SCHEMA = BASE + "provider-free-behavior-transaction-evidence.schema.json"
CONTRACT = BASE + "behavior-transaction-rehearsal-contract.json"
REVIEW = "orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-behavior-attempt-048-review-receipt.json"
AER = "docs/ariadne-agent-error-correction-register-revision-204.md"
CLOSEOUT = PLAN.replace("-plan.md", "-closeout.md")
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-context-fabric-durability-behavior-transaction-rehearsal-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-08--context-fabric-database-durability-behavior-transaction.md"
PASS_TEST = "tests/test_raisa_context_fabric_durability_behavior_attempt_048_pass.py"
BEHAVIOR_TEST = "tests/test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py"
CONTINUITY_TEST = "tests/test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_continuity.py"
UPDATER = "scripts/raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_continuity_update.py"


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
        PASS,
        SCHEMA,
        REVIEW,
        AER,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Disposable PostgreSQL durability behavior/transaction rehearsal",
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
                "The accepted runtime used exactly one owned networkless tmpfs-only local PostgreSQL 16 container with opaque authored-synthetic fixtures.",
                "Twenty selected serial entry-point, idempotency, RLS, trigger and outer-rollback scenarios passed; this is not a claim of infallibility or concurrent/operational behavior.",
                "No applied migration, operational database/source, watcher, product read, provider, command, deployment or protected capability is opened.",
                "Yuri explicitly requested a pause after this closeout; the next read-only architectural-health review has not begun.",
            ],
        },
        "decisions": [
            {
                "id": "accept-disposable-postgresql-durability-behavior-transaction-rehearsal",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept the first complete twenty-scenario serial database behavior pass with exact cleanup and no operational authority.",
            }
        ],
        "claim_scope": [
            "Immutable attempt-048 evidence passes 20/20 frozen scenarios in exact contract order and category counts 6/4/3/4/3.",
            "Cross-transaction replay and fixed injected outer rollback pass with bounded readback.",
            "Fresh r182 independently passes 498/498 focused tests with no P0-P2 finding and clean unchanged postflight.",
            "The exact owned container is removed and absence verified; no call follows success.",
            "Concurrency, restart, unknown commit, rotation, retention, applied migration and operational/product boundaries remain unproved and closed.",
        ],
        "contract_evidence": [
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [PLAN, DESIGN, PASS, REVIEW, PASS_TEST, CLOSEOUT],
                "note": "The selected synthetic update-confirm projection thread is transactionally server-proven without opening the product command or event runtime.",
            },
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [DESIGN, PASS, REVIEW, PASS_TEST, CLOSEOUT],
                "note": "Fixtures remain opaque and authored-synthetic; no patient identity, appointment reason or clinical value is admitted.",
            },
        ],
        "evidence": {
            "plans": [PLAN, DESIGN, THREAT],
            "findings": [REVIEW, AER, PASS],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                "orchestration/agent_inbox/codex/raisa-context-fabric-durability-behavior-attempt-048-preexecution-receipt.json"
            ],
            "tests": [
                PASS_TEST,
                BEHAVIOR_TEST,
                "tests/test_ariadne_agent_error_register.py",
                "tests/test_ariadne_continuity_engine.py",
                "tests/test_ariadne_compass.py",
                CONTINUITY_TEST,
            ],
            "artifacts": [CONTRACT, SCHEMA, PASS, UPDATER],
        },
        "unresolved_gates": [
            "Patient, clinical, product-derived, financial, protected and historical-PHI data remain closed.",
            "Concurrency, crash restart, unknown-commit recovery, key rotation, retention execution, purge, performance and monitoring remain later finite gates.",
            "Applied migration, operational database/outbox/feed/watcher/listener/source access, persistence and credentials remain closed.",
            "Application/runtime wiring, product reads, providers, tools, commands, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 233 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 234
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 234 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected behavior-pass Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove the first serial database behavior spine",
        "outcome": "All twenty exact synthetic behavior/transaction scenarios pass with immutable evidence and exact cleanup.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 215
        and compass["source_graph_revision"] == 233
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 216
        and compass["source_graph_revision"] == 234
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected behavior-pass Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Exact durability structure, bodies, inert lowering, isolated PostgreSQL catalogue admission and twenty-scenario serial behavior now pass.",
                "Run the requested read-only architecture-health pulse before the Agent Execution Surface and Containment Gate.",
                "Separately gate concurrency, restart, rotation, retention, applied migration, application wiring, operational sources and product/patient data.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Serial database durability accepted; closeout pause",
        "why_now": "The frozen database behavior experiment has passed, so system-level architectural conformance can be reviewed before executable Bureau containment work.",
        "outcome": "Attempt 048 passes 20/20 scenarios and fresh r182 passes 498/498 focused checks with exact cleanup.",
        "unlocks": [
            "After Yuri's requested pause, perform the bounded read-only architecture-health and conformance review.",
            "Use its findings to inform the already planned Agent Execution Surface and Containment Gate.",
        ],
        "does_not_solve": [
            "Concurrent behavior, crash restart, unknown-commit recovery, key rotation, retention execution, purge, performance or monitoring.",
            "Applied migration, database/outbox/feed/watcher/listener/source access, credentials or operational persistence.",
            "Application/runtime wiring, product reads, patient/product data, providers, tools, routes or commands.",
            "Deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 234 / Compass 216. The first provider-free "
        "Context Fabric database behavior spine passes all twenty exact serial "
        "synthetic scenarios with immutable evidence and exact cleanup. Work is "
        "paused at Yuri's requested closeout before a read-only architectural-"
        "health pulse; operational and product boundaries remain closed."
    )
    limit = (
        "Behavior/transaction acceptance proves the selected serial database slice "
        "only; it does not prove concurrency, restart, unknown-commit recovery, "
        "rotation, retention, applied migration or product runtime."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 234
    compass["map_revision"] = 216
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
