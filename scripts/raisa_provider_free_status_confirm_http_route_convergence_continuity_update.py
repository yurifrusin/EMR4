"""Advance Continuity and Compass for accepted status-confirm HTTP convergence."""

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
NODE_ID = "raisa-provider-free-status-confirm-http-route-convergence"
PARENT = (
    "raisa-provider-free-disposable-postgresql-status-confirm-"
    "product-adapter-integration-rehearsal"
)
SOURCE_HEAD = "b414eb256853c301099d9cf7797a69cd3ec077c5"
UPDATED_AT = "2026-08-13T03:09:24Z"
PLAN = "docs/raisa-provider-free-status-confirm-http-route-convergence-plan.md"
THREAT = (
    "docs/security/"
    "raisa-provider-free-status-confirm-http-route-convergence-threat-model-delta.md"
)
CLOSEOUT = "docs/raisa-provider-free-status-confirm-http-route-convergence-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-status-confirm-http-route-convergence-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-13--status-confirm-http-route-convergence.md"
)
BASE = "orchestration/continuity/raisa-provider-free-status-confirm-http-route-convergence/"
CONTRACT = BASE + "rehearsal-contract.json"
CONTRACT_SCHEMA = BASE + "rehearsal-contract.schema.json"
EVIDENCE_SCHEMA = BASE + "provider-free-http-postgresql-evidence.schema.json"
EVIDENCE = BASE + "provider-free-http-postgresql-evidence.json"
FAILURE_EVIDENCE = BASE + "provider-free-http-postgresql-failure-evidence.json"
SCRIPT = "scripts/raisa_provider_free_status_confirm_http_route_convergence.py"
TEST = "tests/test_raisa_provider_free_status_confirm_http_route_convergence.py"
PLAN_TEST = "tests/test_raisa_provider_free_status_confirm_http_route_convergence_plan.py"
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_status_confirm_http_route_convergence_continuity.py"
)
UPDATER = (
    "scripts/raisa_provider_free_status_confirm_http_route_convergence_continuity_update.py"
)
RECEIPTS = [
    "orchestration/agent_inbox/codex/raisa-provider-free-status-confirm-http-route-convergence-preplanning-receipt.json",
    "orchestration/agent_inbox/codex/raisa-provider-free-status-confirm-http-route-convergence-postcompaction-preplanning-receipt.json",
    "orchestration/agent_inbox/codex/raisa-provider-free-status-confirm-http-route-convergence-precommit-receipt.json",
]


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        "app/dependencies.py",
        "app/routers/appointments.py",
        "app/schemas/appointments.py",
        "app/services/diary/confirm_actions.py",
        "docs/api-spine/openapi/appointment-commands.yaml",
        "orchestration/api_spine_appointment_command_alignment_inventory.md",
        CONTRACT,
        CONTRACT_SCHEMA,
        EVIDENCE_SCHEMA,
        EVIDENCE,
        FAILURE_EVIDENCE,
        SCRIPT,
        TEST,
        PLAN_TEST,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        *RECEIPTS,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free status-confirm HTTP route convergence",
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
                "Canonical and hidden compatibility paths share one product-adapter handler.",
                "No provider, product database, patient data, deployment or protected-ref authority was opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-status-confirm-http-route-convergence",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept exact-byte, database-version-bound status-only route convergence and proceed to visible Diary wiring.",
            }
        ],
        "claim_scope": [
            "Canonical status-confirm and its hidden historical alias enter the same adapter-owned command path.",
            "Opaque generation binding, fresh authority/source recheck, atomic status/audit/v1 receipt and exact-byte replay pass against disposable PostgreSQL.",
            "Waiting-area-only input is explicitly unsupported and cannot reach a legacy local write.",
            "Twelve scenarios, 112 hostile mutations, 217 focused/current-lineage tests and the 193-test canonical fast profile pass.",
        ],
        "contract_evidence": [
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [PLAN, EVIDENCE, TEST, CLOSEOUT],
                "note": "The status-only command rechecks current appointment truth and preserves every non-status scheduling field; event/cue durability remains separately closed.",
            },
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [PLAN, EVIDENCE, TEST, CLOSEOUT],
                "note": "Authored-synthetic route proofs retain the existing patient, practitioner, time and duration binding while changing only admitted status fields.",
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [EVIDENCE, FAILURE_EVIDENCE],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": RECEIPTS,
            "tests": [TEST, PLAN_TEST, CONTINUITY_TEST],
            "artifacts": [
                "app/dependencies.py",
                "app/routers/appointments.py",
                "app/schemas/appointments.py",
                "app/services/diary/confirm_actions.py",
                "docs/api-spine/openapi/appointment-commands.yaml",
                CONTRACT_SCHEMA,
                EVIDENCE_SCHEMA,
                SCRIPT,
                UPDATER,
            ],
        },
        "unresolved_gates": [
            "Visible native Diary status-confirm consumption and interaction evidence remain unproved.",
            "Other command families and the waiting-area-only confirmation path remain separately gated.",
            "CF-D2 durability remains deferred to a fresh observability-first event/cue delivery plan.",
            "Product/patient data, providers, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    parent_node = next(node for node in graph["nodes"] if node["id"] == PARENT)
    if parent_node["authority"].get("authorized_openings") == [
        "owned disposable authored-synthetic PostgreSQL read/write and exact cleanup"
    ]:
        parent_node["authority"]["authorized_openings"] = []
    if parent_node.get("contract_evidence") == [
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-status-confirm-product-adapter-integration-rehearsal/rehearsal-contract.json"
    ]:
        parent_node["contract_evidence"] = []
    if graph["graph_revision"] == 272 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 273
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 273 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected status-confirm HTTP Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Close the final backend status-confirm seam before visible Diary work",
        "outcome": "One canonical adapter-owned status-confirm HTTP path now passes; bounded visible Diary wiring is next but paused before commencement at Yuri's request.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 254
        and compass["source_graph_revision"] == 272
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 255
        and compass["source_graph_revision"] == 273
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected status-confirm HTTP Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve accepted conditional-command and status-confirm route correctness.",
                "After Yuri explicitly resumes, wire and prove bounded visible Diary status-confirm behavior.",
                "Return to durable event/cue delivery only through a fresh observability-first CF-D2 plan informed by the visible consumer boundary.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Backend status-confirm convergence complete; paused before visible Diary work",
        "why_now": "The adapter and physical seam already passed independently; the HTTP boundary now proves their exact mounted composition.",
        "outcome": "Canonical and compatibility paths share one fail-closed status-only transaction with exact-byte replay.",
        "unlocks": [
            "After Yuri explicitly resumes, freeze bounded visible native Diary status-confirm wiring against the accepted HTTP contract.",
            "Prove proposal review, confirmation, stale/current-truth reconciliation and responsive interaction without raw fallback.",
            "Use that settled interaction boundary to shape a later observability-first durable event/cue delivery tranche.",
        ],
        "does_not_solve": [
            "Visible Diary interaction or another command family.",
            "CF-D2 restart/unknown-commit durability, watcher operations or cue recovery.",
            "Product/patient data, provider access, deployment, production or release.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 273 / Compass 255. The provider-free status-confirm "
        "HTTP route now converges on the accepted adapter/transaction seam with "
        "opaque generation binding and exact-byte replay. Visible native Diary "
        "status-confirm wiring is next but paused before commencement at Yuri's "
        "request; CF-D2 remains a later observability-first "
        "durable event/cue extension."
    )
    limit = (
        "Status-confirm HTTP convergence proves one authored-synthetic mounted backend family, not visible UI behavior, other commands or durable event/cue delivery."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 273
    compass["map_revision"] = 255
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
