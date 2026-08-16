"""Advance Continuity and Compass for delete-confirm HTTP/PostgreSQL integration."""

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
    "raisa-provider-free-disposable-postgresql-delete-confirm-http-"
    "integration-rehearsal"
)
PARENT = "raisa-provider-free-delete-confirm-http-route-convergence"
SOURCE_HEAD = "fe5dbcb31b06b027285aa84ee3cafb4fbbffb9db"
UPDATED_AT = "2026-08-16T23:22:02Z"

PLAN = "docs/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal-plan.md"
THREAT = "docs/security/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal-threat-model-delta.md"
CONTRACT = "orchestration/continuity/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal/rehearsal-contract.json"
CONTRACT_SCHEMA = "orchestration/continuity/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal/rehearsal-contract.schema.json"
EVIDENCE = "orchestration/continuity/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal/provider-free-http-postgresql-evidence.json"
EVIDENCE_SCHEMA = "orchestration/continuity/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal/provider-free-http-postgresql-evidence.schema.json"
FAILURE = "orchestration/continuity/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal/provider-free-http-postgresql-failure-evidence.json"
HARNESS = "scripts/raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal.py"
FOCUSED_TEST = "tests/test_raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal.py"
PLAN_TEST = "tests/test_raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal_plan.py"
ROUTE_TEST = "tests/test_raisa_provider_free_delete_confirm_http_route_convergence.py"
PHYSICAL_TEST = "tests/test_raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold.py"
REGISTER = "docs/ariadne-agent-error-correction-register-revision-329.md"
WORKER = "orchestration/agent_inbox/deepseek/raisa-delete-confirm-http-postgresql-worker-result.json"
CORRECTION = "orchestration/agent_inbox/deepseek/raisa-delete-confirm-http-postgresql-correction-result.json"
PREVERIFIER_FAILED = "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal-pre-verifier-receipt.json"
PREVERIFIER = "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal-pre-verifier-v2-receipt.json"
PACKET = "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal-gemini37-review-packet.md"
MANIFEST = "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal-gemini37-command-manifest.json"
WORKTREE_PREFLIGHT = "orchestration/agent_inbox/codex/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal-gemini37-worktree-preflight.json"
REVIEW = "orchestration/agent_inbox/antigravity/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal-gemini37-review-receipt.json"
CLOSEOUT = "docs/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-delete-confirm-http-postgresql-integration-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-17--delete-confirm-http-postgresql-integration-rehearsal.md"
UPDATER = "scripts/raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal_continuity.py"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _all_evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        CONTRACT,
        CONTRACT_SCHEMA,
        EVIDENCE,
        EVIDENCE_SCHEMA,
        FAILURE,
        "app/routers/appointments.py",
        "app/services/appointment_delete_physical.py",
        HARNESS,
        FOCUSED_TEST,
        PLAN_TEST,
        ROUTE_TEST,
        PHYSICAL_TEST,
        WORKER,
        CORRECTION,
        REGISTER,
        PREVERIFIER_FAILED,
        PREVERIFIER,
        PACKET,
        MANIFEST,
        WORKTREE_PREFLIGHT,
        REVIEW,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        UPDATER,
        CONTINUITY_TEST,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free disposable PostgreSQL delete-confirm HTTP integration rehearsal",
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
                "Provider-free authored-synthetic local HTTP/backend/PostgreSQL evidence only.",
                "The server-authenticated practice is transaction-local before protected reads and absent on fresh pooled connections.",
                "Raw DELETE, reusable runtime, product data, UI, provider, deployment and protected integration remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-delete-confirm-http-postgresql-integration",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept the exact canonical/hidden-alias authored-synthetic HTTP/PostgreSQL integration proof and review Ariadne effectiveness before more product work.",
            }
        ],
        "claim_scope": [
            "All twelve DHI scenarios pass against owned disposable PostgreSQL 16.",
            "All 135 hostile contract mutations fail closed.",
            "Non-superuser non-BYPASSRLS role, forced RLS on eight tables, six constraints and four triggers pass.",
            "Public/private bytes remain distinct and independently byte-identical on replay; second and rollback effects are zero.",
            "The 40-test integration/plan, 58-test route/physical, 286-test register, 37-test API Spine/Diary and 130-test maintenance profiles pass.",
            "Exact container/network cleanup and one clean eight-command Gemini 3.7 Flash/high veto pass at unchanged candidate HEAD.",
        ],
        "contract_evidence": [
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [PLAN, EVIDENCE, FOCUSED_TEST, CLOSEOUT],
                "note": "Delete confirmation rechecks current appointment version and authority under the physical lock plan; cancellation does not create a reschedule availability claim.",
            },
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [PLAN, EVIDENCE, ROUTE_TEST, CLOSEOUT],
                "note": "The minimal cancellation projection exposes no mutable patient, practitioner, time or duration state and leaves update families unchanged.",
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [CONTRACT, CONTRACT_SCHEMA, EVIDENCE, EVIDENCE_SCHEMA, FAILURE, REGISTER],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [WORKER, CORRECTION, PREVERIFIER_FAILED, PREVERIFIER, WORKTREE_PREFLIGHT, REVIEW],
            "tests": [FOCUSED_TEST, PLAN_TEST, ROUTE_TEST, PHYSICAL_TEST, CONTINUITY_TEST],
            "artifacts": [
                "app/routers/appointments.py",
                "app/services/appointment_delete_physical.py",
                HARNESS,
                PACKET,
                MANIFEST,
                UPDATER,
            ],
        },
        "unresolved_gates": [
            "Raw compatibility DELETE remains separate from the accepted confirmation envelope.",
            "Visible Reception One cancellation, concurrency/crash recovery and unknown-commit behavior remain unproved.",
            "No product data, reusable runtime, provider, deployment, Pages or protected-ref authority is opened.",
            "The authorised Ariadne effectiveness and DeepSeek Harness review precedes further product work.",
        ],
    }


def main() -> int:
    graph = _read(GRAPH)
    if graph["graph_revision"] == 308 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 309
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 309 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected delete-confirm HTTP/PostgreSQL Continuity predecessor")
    _write(GRAPH, graph)

    compass = _read(COMPASS)
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Close the canonical delete-confirm route-to-database integration proof",
        "outcome": "Authored-synthetic delete confirmation now has one accepted local HTTP/PostgreSQL truth path with replay, denial, rollback and cleanup evidence.",
        "evidence": _all_evidence(),
    }
    if (
        compass["map_revision"] == 290
        and compass["source_graph_revision"] == 308
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 291
        and compass["source_graph_revision"] == 309
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected delete-confirm HTTP/PostgreSQL Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["prerequisites"] = [
                "Preserve the accepted delete-confirm route, adapter, transaction, RLS, audit and private/public receipt boundaries.",
                "Review recent Ariadne effectiveness and implement only evidence-backed high-leverage workflow repairs.",
                "Keep raw DELETE, product data, providers, deployment and protected integration separately closed.",
            ]
            for path in journey["evidence"]:
                if path not in horizon["evidence"]:
                    horizon["evidence"].append(path)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Delete-confirm HTTP/PostgreSQL integration accepted; Ariadne effectiveness review is next",
        "why_now": "The product seam has passed its final independent gate, and recent incident evidence now supports a short workflow repair review before more product work.",
        "outcome": "One authored-synthetic canonical/hidden-alias path rechecks current authority and source truth, commits cancellation/audit/private receipt atomically and projects only strict public bytes.",
        "unlocks": [
            "Review recent Ariadne incidents and tranche timing against the risk-weighted reform.",
            "Inspect DeepSeek Harness primary sources and decide adaptation versus migration using authentication, cost, control and switching evidence.",
            "Implement only the highest-leverage workflow repairs before resuming product work.",
        ],
        "does_not_solve": [
            "Raw compatibility DELETE convergence or visible Reception One cancellation UI.",
            "Concurrent, crash/restart or unknown-commit behavior.",
            "Product/patient data, provider access, deployment, release, Pages or protected refs.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 309 / Compass 291. Delete-confirm now has an "
        "accepted authored-synthetic local HTTP/PostgreSQL truth path with "
        "replay, denial, rollback and cleanup evidence. A short Ariadne "
        "effectiveness and DeepSeek Harness review is next before more product work."
    )
    limit = "Delete-confirm HTTP/PostgreSQL integration proves one authored-synthetic local lifecycle, not raw DELETE, visible UI, product data, concurrency/crash recovery or production."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 309
    compass["map_revision"] = 291
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
