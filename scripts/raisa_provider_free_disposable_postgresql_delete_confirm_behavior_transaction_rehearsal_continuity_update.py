"""Advance Continuity and Compass for delete-confirm transaction behavior."""

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
    "raisa-provider-free-disposable-postgresql-delete-confirm-behavior-"
    "transaction-rehearsal"
)
PARENT = (
    "raisa-provider-free-disposable-postgresql-delete-confirm-scaffold-"
    "parse-catalogue-rehearsal"
)
SOURCE_HEAD = "49dd2aaa72877adb844da4d0d5d5bb28039c90c8"
UPDATED_AT = "2026-08-16T14:56:08.8155653+10:00"
PLAN = (
    "docs/raisa-provider-free-disposable-postgresql-delete-confirm-behavior-"
    "transaction-rehearsal-plan.md"
)
THREAT = (
    "docs/security/raisa-provider-free-disposable-postgresql-delete-confirm-"
    "behavior-transaction-rehearsal-threat-model-delta.md"
)
TRACE_PLAN = (
    "docs/raisa-provider-free-disposable-postgresql-delete-confirm-behavior-"
    "transaction-trace-recovery-plan.md"
)
TRACE_THREAT = (
    "docs/security/raisa-provider-free-disposable-postgresql-delete-confirm-"
    "behavior-transaction-trace-recovery-threat-model-delta.md"
)
AUTHORITY_ADDENDUM = (
    "docs/raisa-provider-free-disposable-postgresql-delete-confirm-behavior-"
    "transaction-authority-counter-recovery-addendum.md"
)
RELEASE_ADDENDUM = (
    "docs/raisa-provider-free-disposable-postgresql-delete-confirm-behavior-"
    "transaction-release-accounting-recovery-addendum.md"
)
BASE = (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-delete-"
    "confirm-behavior-transaction-rehearsal/"
)
CONTRACT = BASE + "rehearsal-contract.json"
CONTRACT_SCHEMA = BASE + "rehearsal-contract.schema.json"
EVIDENCE_SCHEMA = BASE + "provider-free-behavior-transaction-evidence.schema.json"
EVIDENCE = BASE + "provider-free-behavior-transaction-evidence.json"
FAILURE_EVIDENCE = BASE + "provider-free-behavior-transaction-failure-evidence.json"
SEMANTIC_FREEZE = BASE + "semantic-freeze.json"
HARNESS = (
    "scripts/raisa_provider_free_disposable_postgresql_delete_confirm_behavior_"
    "transaction_rehearsal.py"
)
TEST = (
    "tests/test_raisa_provider_free_disposable_postgresql_delete_confirm_"
    "behavior_transaction_rehearsal.py"
)
PLAN_TEST = (
    "tests/test_raisa_provider_free_disposable_postgresql_delete_confirm_"
    "behavior_transaction_rehearsal_plan.py"
)
UPDATER = (
    "scripts/raisa_provider_free_disposable_postgresql_delete_confirm_behavior_"
    "transaction_rehearsal_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_disposable_postgresql_delete_confirm_"
    "behavior_transaction_rehearsal_continuity.py"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-delete-confirm-behavior-"
    "transaction-gemini37-final-review-receipt.json"
)
REGISTER_REVISION = "docs/ariadne-agent-error-correction-register-revision-309.md"
CLOSEOUT = (
    "docs/raisa-provider-free-disposable-postgresql-delete-confirm-behavior-"
    "transaction-rehearsal-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-delete-confirm-behavior-transaction-"
    "sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-16--delete-confirm-behavior-transaction-rehearsal.md"
)
POSTCOMPACTION_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-delete-confirm-behavior-transaction-"
    "closeout-postcompaction-receipt.json"
)
PREEXECUTION_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-delete-confirm-behavior-transaction-"
    "release-accounting-preexecution-receipt.json"
)
PREVERIFIER_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-delete-confirm-behavior-transaction-"
    "release-accounting-pre-verifier-acceptance-receipt.json"
)
PREDISPATCH_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-delete-confirm-behavior-transaction-"
    "gemini37-veto-predispatch-receipt.json"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        TRACE_PLAN,
        TRACE_THREAT,
        AUTHORITY_ADDENDUM,
        RELEASE_ADDENDUM,
        CONTRACT,
        CONTRACT_SCHEMA,
        EVIDENCE_SCHEMA,
        EVIDENCE,
        FAILURE_EVIDENCE,
        SEMANTIC_FREEZE,
        HARNESS,
        TEST,
        PLAN_TEST,
        REVIEW,
        REGISTER_REVISION,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        POSTCOMPACTION_RECEIPT,
        PREEXECUTION_RECEIPT,
        PREVERIFIER_RECEIPT,
        PREDISPATCH_RECEIPT,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": (
            "Provider-free disposable PostgreSQL delete-confirm "
            "behavior/transaction rehearsal"
        ),
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
                "The result is provider-free, authored-synthetic and limited to one fully removed disposable PostgreSQL 16 lifecycle.",
                "It proves exact serial unmounted authority and transaction behavior; product runtime authority remains false.",
                "Provisioning, mounted routes, product data, concurrency, providers, deployment and protected integration remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-delete-confirm-behavior-transaction-rehearsal",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept exact serial PostgreSQL authority generation, "
                    "default denial, revocation, private receipt, attributable "
                    "audit, replay, rollback, timeout and ordered atomic "
                    "transaction evidence; hand off only to a read-only "
                    "route-convergence admission review."
                ),
            }
        ],
        "claim_scope": [
            "One internal-network, portless, tmpfs-backed cached PostgreSQL 16 server exercised the exact unmounted delete-confirm scaffold through a fixed local relay.",
            "Nine authority groups and eleven transaction groups passed, including current-authority checks, default denial, revocation, overflow, byte-exact replay, scaffold completeness, outer rollback and cumulative timeout.",
            "One hundred twenty-two hostile mutations, 43 owned tests, 36 API Spine tests and the canonical 196-test profile passed.",
            "Exactly one Gemini 3.7 Flash/high final veto passed on unchanged reviewed source, and exact captured-ID container/network cleanup was verified.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, TRACE_PLAN, AUTHORITY_ADDENDUM, RELEASE_ADDENDUM],
            "findings": [
                THREAT,
                TRACE_THREAT,
                CONTRACT,
                CONTRACT_SCHEMA,
                EVIDENCE_SCHEMA,
                EVIDENCE,
                FAILURE_EVIDENCE,
                SEMANTIC_FREEZE,
                REGISTER_REVISION,
            ],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                POSTCOMPACTION_RECEIPT,
                PREEXECUTION_RECEIPT,
                PREVERIFIER_RECEIPT,
                PREDISPATCH_RECEIPT,
                REVIEW,
            ],
            "tests": [TEST, PLAN_TEST, CONTINUITY_TEST],
            "artifacts": [HARNESS, UPDATER],
        },
        "unresolved_gates": [
            "Delete-confirm route, kernel and adapter convergence remains unreviewed; no route was edited, mounted or called.",
            "No product command/database/data, capability provisioning, concurrency, restart, crash, unknown-commit, performance, retention or operations behavior is proved.",
            "Providers, credentials, patient/product data, watchers/events, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 302 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 303
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 303 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected delete-confirm behavior Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": (
            "Prove the exact delete-confirm authority and transaction seam against "
            "PostgreSQL before any route convergence is considered"
        ),
        "outcome": (
            "Nine authority and eleven transaction groups, exact cleanup and one "
            "independent final veto pass."
        ),
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 284
        and compass["source_graph_revision"] == 302
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 285
        and compass["source_graph_revision"] == 303
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected delete-confirm behavior Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve the accepted source-owned-truth, conditional-command and delete-confirm physical/behavior lineage.",
                "Run a provider-free read-only delete-confirm route-convergence admission review next.",
                "Keep route edits/calls, product data/commands, concurrency, providers and protected integration separately gated.",
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
            "The unmounted delete-confirm authority and transaction seam is "
            "PostgreSQL-proved; route convergence remains unopened"
        ),
        "why_now": (
            "The exact physical catalogue already passed, permitting one isolated "
            "serial proof of the trigger and transaction behavior."
        ),
        "outcome": (
            "Authority generation, default denial, revocation, ordered atomic "
            "appointment/audit/receipt effects, replay, rollback, timeout and exact "
            "cleanup pass."
        ),
        "unlocks": [
            "Run a provider-free read-only delete-confirm route-convergence admission review.",
            "Inspect and classify only the exact route, dependency, adapter, kernel and transaction gaps.",
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
        "EMR4 is at Continuity 303 / Compass 285. The exact serial unmounted "
        "delete-confirm authority and transaction seam now passes PostgreSQL 16 "
        "generation, denial, revocation, ordered atomic effect, replay, rollback "
        "and timeout evidence with complete disposable cleanup. Read-only route-"
        "convergence admission is next; route execution and product commands remain closed."
    )
    limit = "The accepted delete-confirm behavior rehearsal proves the exact serial unmounted PostgreSQL authority and transaction seam only, not route, concurrency or product-command safety."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 303
    compass["map_revision"] = 285
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
