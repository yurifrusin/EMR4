"""Advance Continuity and Compass for delete-confirm HTTP route convergence."""

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
NODE_ID = "raisa-provider-free-delete-confirm-http-route-convergence"
PARENT = "raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review"
SOURCE_HEAD = "c7a01edd96ebabf3ea2c07be89a5b405c9629853"
UPDATED_AT = "2026-08-16T20:42:01Z"

PLAN = "docs/raisa-provider-free-delete-confirm-http-route-convergence-plan.md"
THREAT = "docs/security/raisa-provider-free-delete-confirm-http-route-convergence-threat-model-delta.md"
CONTRACT = "orchestration/continuity/raisa-provider-free-delete-confirm-http-route-convergence/route-convergence-contract.json"
SCHEMA = "orchestration/continuity/raisa-provider-free-delete-confirm-http-route-convergence/route-convergence-contract.schema.json"
EVIDENCE = "orchestration/continuity/raisa-provider-free-delete-confirm-http-route-convergence/provider-free-route-convergence-evidence.json"
REPORT_EVIDENCE = "orchestration/continuity/raisa-provider-free-delete-confirm-http-route-convergence/route-convergence-report.md"
REVIEWER = "scripts/raisa_provider_free_delete_confirm_http_route_convergence.py"
FOCUSED_TEST = "tests/test_raisa_provider_free_delete_confirm_http_route_convergence.py"
PLAN_TEST = "tests/test_raisa_provider_free_delete_confirm_http_route_convergence_plan.py"
WORKER = "orchestration/agent_inbox/deepseek/raisa-provider-free-delete-confirm-http-route-convergence-worker-receipt.json"
WORKER_FAILURE = "orchestration/agent_inbox/codex/raisa-provider-free-delete-confirm-http-route-convergence-deepseek-mechanical-correction-failure-receipt.json"
RECOVERY = "orchestration/agent_inbox/codex/raisa-provider-free-delete-confirm-http-route-convergence-sol-recovery-lease.md"
REGISTER = "docs/ariadne-agent-error-correction-register-revision-319.md"
PREVERIFIER_FAILED = "orchestration/agent_inbox/codex/raisa-provider-free-delete-confirm-http-route-convergence-pre-verifier-acceptance-receipt.json"
PREVERIFIER = "orchestration/agent_inbox/codex/raisa-provider-free-delete-confirm-http-route-convergence-pre-verifier-acceptance-v2-receipt.json"
PACKET = "orchestration/agent_inbox/codex/raisa-provider-free-delete-confirm-http-route-convergence-gemini37-review-packet.md"
MANIFEST = "orchestration/agent_inbox/codex/raisa-provider-free-delete-confirm-http-route-convergence-gemini37-command-manifest.json"
WORKTREE_PREFLIGHT = "orchestration/agent_inbox/codex/raisa-provider-free-delete-confirm-http-route-convergence-gemini37-worktree-preflight.json"
REVIEW = "orchestration/agent_inbox/antigravity/raisa-provider-free-delete-confirm-http-route-convergence-gemini37-review-receipt.json"
CLOSEOUT = "docs/raisa-provider-free-delete-confirm-http-route-convergence-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-delete-confirm-http-route-convergence-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-17--delete-confirm-http-route-convergence.md"
UPDATER = "scripts/raisa_provider_free_delete_confirm_http_route_convergence_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_provider_free_delete_confirm_http_route_convergence_continuity.py"


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
        SCHEMA,
        "app/routers/appointments.py",
        "app/schemas/appointments.py",
        "app/services/diary/confirm_actions.py",
        "docs/api-spine/openapi/appointment-commands.yaml",
        "orchestration/api_spine_appointment_command_alignment_inventory.md",
        REVIEWER,
        FOCUSED_TEST,
        PLAN_TEST,
        EVIDENCE,
        REPORT_EVIDENCE,
        WORKER,
        WORKER_FAILURE,
        RECOVERY,
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
        "title": "Provider-free delete-confirm HTTP route convergence",
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
                "Provider-free static and in-memory route-composition evidence only; no database command was executed.",
                "Canonical and hidden historical delete-confirm paths share one handler and one accepted-adapter call.",
                "Private stored receipt bytes remain internal command truth and cannot become HTTP content.",
            ],
        },
        "decisions": [
            {
                "id": "accept-delete-confirm-http-route-convergence",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept the exact provider-free canonical/alias route composition and proceed to disposable PostgreSQL HTTP integration.",
            }
        ],
        "claim_scope": [
            "All twelve delete-confirm HTTP composition scenarios pass.",
            "149 hostile contract and public-envelope mutations fail closed.",
            "The strict dedicated public envelope and reciprocal private-byte invariants pass 27 focused and 78 API Spine/Diary tests.",
            "Register revision 319 passes 274 tests and preserves AER-0366 through AER-0368.",
            "The integrated provider-free closeout profile passes 439 tests.",
            "One clean eight-command Gemini 3.7 Flash/high veto passes at unchanged exact candidate HEAD and tree.",
        ],
        "contract_evidence": [
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [PLAN, EVIDENCE, FOCUSED_TEST, CLOSEOUT],
                "note": "The delete-confirm transport carries the server-minted current appointment-version binding into the accepted adapter and adds no route-local scheduling mutation; database effect remains separately unproved.",
            },
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [PLAN, EVIDENCE, FOCUSED_TEST, CLOSEOUT],
                "note": "The minimal cancellation response exposes no mutable patient, practitioner, time or duration projection, while raw update and reschedule families remain unchanged.",
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [CONTRACT, SCHEMA, EVIDENCE, REPORT_EVIDENCE, REGISTER],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                WORKER,
                WORKER_FAILURE,
                PREVERIFIER_FAILED,
                PREVERIFIER,
                WORKTREE_PREFLIGHT,
                REVIEW,
            ],
            "tests": [FOCUSED_TEST, PLAN_TEST, CONTINUITY_TEST],
            "artifacts": [
                "app/routers/appointments.py",
                "app/schemas/appointments.py",
                "app/services/diary/confirm_actions.py",
                "docs/api-spine/openapi/appointment-commands.yaml",
                "orchestration/api_spine_appointment_command_alignment_inventory.md",
                REVIEWER,
                RECOVERY,
                PACKET,
                MANIFEST,
                UPDATER,
            ],
        },
        "unresolved_gates": [
            "Mounted delete-confirm HTTP behavior and atomic effect against PostgreSQL remain unproved.",
            "Raw compatibility DELETE remains separate and outside the accepted confirmation envelope.",
            "No product data, provider, UI, deployment, Pages or protected-ref authority is opened.",
        ],
    }


def main() -> int:
    graph = _read(GRAPH)
    if graph["graph_revision"] == 307 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 308
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 308 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected delete-confirm HTTP Continuity predecessor")
    _write(GRAPH, graph)

    compass = _read(COMPASS)
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Close delete-confirm transport composition before disposable HTTP/PostgreSQL integration",
        "outcome": "Canonical and historical delete-confirm paths now share one strict adapter-owned transport; database execution remains the next bounded proof.",
        "evidence": _all_evidence(),
    }
    if (
        compass["map_revision"] == 289
        and compass["source_graph_revision"] == 307
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 290
        and compass["source_graph_revision"] == 308
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected delete-confirm HTTP Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["prerequisites"] = [
                "Preserve the accepted canonical/hidden-alias handler, strict public envelope and private receipt boundary.",
                "Prove the exact delete-confirm HTTP path against disposable authored-synthetic PostgreSQL with atomic cleanup.",
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
        "strategic_role": "Delete-confirm HTTP composition accepted; disposable PostgreSQL integration is next",
        "why_now": "The five frozen route-transition gaps close without changing the accepted lower transaction seams or raw DELETE.",
        "outcome": "One server-owned canonical/alias transport emits only canonical minimal public bytes while private receipt truth remains internal.",
        "unlocks": [
            "Freeze the narrowest provider-free disposable PostgreSQL delete-confirm HTTP integration rehearsal.",
            "Exercise committed, replay, denial, rollback and cleanup through the exact canonical route and accepted transaction seam.",
        ],
        "does_not_solve": [
            "Mounted HTTP/database behavior, concurrency or unknown-commit recovery.",
            "Raw compatibility DELETE convergence or visible Reception One cancellation UI.",
            "Product/patient data, provider access, deployment, release, Pages or protected refs.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 308 / Compass 290. Delete-confirm now has one "
        "provider-free canonical/hidden-alias HTTP composition with strict "
        "public/private receipt separation. Disposable PostgreSQL HTTP "
        "integration is the next dependency-satisfied proof."
    )
    limit = "Delete-confirm HTTP convergence proves provider-free composition only, not database execution, raw DELETE convergence or visible client behavior."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 308
    compass["map_revision"] = 290
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
