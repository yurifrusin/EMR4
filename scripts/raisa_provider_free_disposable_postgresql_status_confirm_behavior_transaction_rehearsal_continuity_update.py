"""Advance Continuity and Compass for status-confirm transaction behavior."""

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
    "raisa-provider-free-disposable-postgresql-status-confirm-behavior-"
    "transaction-rehearsal"
)
PARENT = (
    "raisa-provider-free-disposable-postgresql-status-confirm-scaffold-"
    "parse-catalogue-rehearsal"
)
SOURCE_HEAD = "aed1bb076835e8cb6302f614869a285dba79983b"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = (
    "docs/raisa-provider-free-disposable-postgresql-status-confirm-behavior-"
    "transaction-rehearsal-plan.md"
)
THREAT = (
    "docs/security/raisa-provider-free-disposable-postgresql-status-confirm-"
    "behavior-transaction-rehearsal-threat-model-delta.md"
)
CLOSEOUT = (
    "docs/raisa-provider-free-disposable-postgresql-status-confirm-behavior-"
    "transaction-rehearsal-closeout.md"
)
BASE = (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-status-"
    "confirm-behavior-transaction-rehearsal/"
)
CONTRACT = BASE + "rehearsal-contract.json"
CONTRACT_SCHEMA = BASE + "rehearsal-contract.schema.json"
EVIDENCE_SCHEMA = BASE + "provider-free-behavior-transaction-evidence.schema.json"
EVIDENCE = BASE + "provider-free-behavior-transaction-evidence.json"
FAILURE_EVIDENCE = BASE + "provider-free-behavior-transaction-failure-evidence.json"
ATTEMPT_001_RECOVERY = BASE + "attempt-001-cleanup-recovery.json"
ATTEMPT_002_RECOVERY = BASE + "attempt-002-cleanup-recovery.json"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-status-confirm-behavior-transaction-"
    "sol-acceptance.md"
)
PREPLANNING_STATE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-"
    "status-confirm-behavior-transaction-preplanning-runtime-state.json"
)
PREPLANNING_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-"
    "status-confirm-behavior-transaction-preplanning-receipt.json"
)
PRECOMMIT_STATE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-"
    "status-confirm-behavior-transaction-precommit-runtime-state.json"
)
PRECOMMIT_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-"
    "status-confirm-behavior-transaction-precommit-receipt.json"
)
PREPUSH_STATE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-"
    "status-confirm-behavior-transaction-closeout-prepush-runtime-state.json"
)
PREPUSH_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-"
    "status-confirm-behavior-transaction-closeout-prepush-receipt.json"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-12--status-confirm-behavior-transaction-rehearsal.md"
)
HARNESS = (
    "scripts/raisa_provider_free_disposable_postgresql_status_confirm_behavior_"
    "transaction_rehearsal.py"
)
TEST = (
    "tests/test_raisa_provider_free_disposable_postgresql_status_confirm_"
    "behavior_transaction_rehearsal.py"
)
UPDATER = (
    "scripts/raisa_provider_free_disposable_postgresql_status_confirm_behavior_"
    "transaction_rehearsal_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_disposable_postgresql_status_confirm_"
    "behavior_transaction_rehearsal_continuity.py"
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
        ATTEMPT_001_RECOVERY,
        ATTEMPT_002_RECOVERY,
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
        "title": "Provider-free disposable PostgreSQL status-confirm behavior/transaction rehearsal",
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
                "The result is provider-free, authored-synthetic and limited to one fully removed disposable PostgreSQL 16 server.",
                "It proves the exact serial unmounted transaction seam and selected rollback boundaries; runtime authority remains false.",
                "Routes, product databases/data, concurrency, providers, deployment and protected integration remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-status-confirm-behavior-transaction-rehearsal",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept exact serial PostgreSQL lock order, atomic appointment/audit/v1-receipt behavior, stored replay and selected rollback evidence; hand off only to read-only route-mounting admission.",
            }
        ],
        "claim_scope": [
            "One internal-network, portless, tmpfs-backed cached PostgreSQL 16 server admitted the exact selected schema and host SQLAlchemy seam through a fixed local relay.",
            "Sixteen serial authored-synthetic scenarios proved current-authority precedence, exact statement lock classes, one atomic effect, stored replay and four rollback boundaries.",
            "Eleven source bindings, 100 hostile mutations, 13 focused tests and 45 current lineage checks pass.",
            "The relay stopped and exact captured-ID container and network cleanup was verified.",
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
                ATTEMPT_001_RECOVERY,
                ATTEMPT_002_RECOVERY,
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
            "Mounted-route and adapter convergence remain unreviewed; no route was edited, mounted or called.",
            "No product command/database/data, concurrency, restart, crash, unknown-commit, performance, retention or operations behavior is proved.",
            "Providers, credentials, patient/product data, watchers/events, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 264 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 265
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 265 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected status-confirm behavior Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove the exact status-confirm application transaction against PostgreSQL before route convergence is considered",
        "outcome": "Sixteen serial transaction scenarios, exact lock classes, atomic effects, stored replay, rollback and complete disposable cleanup pass.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 246
        and compass["source_graph_revision"] == 264
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 247
        and compass["source_graph_revision"] == 265
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected status-confirm behavior Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve the accepted source-owned-truth, conditional-command and status-confirm physical/transaction lineage.",
                "Run a provider-free read-only status-confirm route-mounting admission review next.",
                "Keep route edits/calls, product data/commands, providers and protected integration separately gated.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "The unmounted status-confirm transaction is PostgreSQL-proved; route convergence remains unopened",
        "why_now": "The exact physical migration passed PostgreSQL catalogue admission, permitting one isolated serial transaction proof.",
        "outcome": "Current-authority/lock order, atomic appointment-audit-receipt behavior, stored replay, selected rollback and exact cleanup pass.",
        "unlocks": [
            "Run a provider-free read-only status-confirm route-mounting admission review.",
            "Inspect and classify only the exact route, dependency, adapter, kernel and transaction boundaries.",
            "Return an evidence-backed converge/block decision without editing, mounting or calling a route.",
        ],
        "does_not_solve": [
            "Mounted-route, adapter, real command, product-database or product-data safety.",
            "Concurrency, restart, crash, unknown commit, retention, performance or production operations.",
            "Provider/credential activity, patient/product data, watchers/events, deployment, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 265 / Compass 247. The exact serial unmounted "
        "status-confirm transaction now passes PostgreSQL 16 lock-order, atomic "
        "effect, stored-replay and rollback evidence with complete disposable "
        "cleanup. Read-only route-mounting admission is next; route execution "
        "and product commands remain closed."
    )
    limit = (
        "The accepted status-confirm behavior rehearsal proves the exact serial unmounted PostgreSQL transaction and selected rollback boundaries only, not route, concurrency or product-command safety."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 265
    compass["map_revision"] = 247
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
