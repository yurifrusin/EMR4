"""Advance Continuity and Compass for delete-confirm route readiness review."""

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
NODE_ID = "raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review"
PARENT = "raisa-provider-free-unmounted-delete-confirm-composition-product-adapter-implementation"
SOURCE_HEAD = "da03039f637d3808c8785a6d6fc95309650044d9"
UPDATED_AT = "2026-08-16T17:27:22Z"

PLAN = "docs/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review-plan.md"
THREAT = "docs/security/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review-threat-model-delta.md"
CONTRACT = "orchestration/continuity/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review/route-mounting-readiness-review-contract.json"
SCHEMA = "orchestration/continuity/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review/route-mounting-readiness-review-contract.schema.json"
REVIEWER = "scripts/raisa_provider_free_read_only_delete_confirm_route_mounting_readiness_review.py"
FOCUSED_TEST = "tests/test_raisa_provider_free_read_only_delete_confirm_route_mounting_readiness_review.py"
PLAN_TEST = "tests/test_raisa_provider_free_read_only_delete_confirm_route_mounting_readiness_review_plan.py"
EVIDENCE = "orchestration/continuity/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review/provider-free-read-only-evidence.json"
FINDING = "orchestration/continuity/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review/route-mounting-readiness-review-report.md"
WORKER = "orchestration/agent_inbox/deepseek/raisa-delete-confirm-route-mounting-readiness-review-worker-receipt.json"
CORRECTION = "orchestration/agent_inbox/deepseek/raisa-delete-confirm-route-mounting-readiness-review-mechanical-correction-worker-receipt.json"
REGISTER = "docs/ariadne-agent-error-correction-register-revision-316.md"
PREVERIFIER_FAILED = "orchestration/agent_inbox/codex/raisa-delete-confirm-route-mounting-readiness-review-pre-verifier-acceptance-receipt.json"
PREVERIFIER = "orchestration/agent_inbox/codex/raisa-delete-confirm-route-mounting-readiness-review-pre-verifier-acceptance-v2-receipt.json"
PACKET = "orchestration/agent_inbox/codex/raisa-delete-confirm-route-mounting-readiness-review-gemini37-review-packet.md"
MANIFEST = "orchestration/agent_inbox/codex/raisa-delete-confirm-route-mounting-readiness-review-gemini37-command-manifest.json"
WORKTREE_PREFLIGHT = "orchestration/agent_inbox/codex/raisa-delete-confirm-route-mounting-readiness-review-gemini37-worktree-preflight-v2.json"
REVIEW = "orchestration/agent_inbox/antigravity/raisa-delete-confirm-route-mounting-readiness-review-gemini37-review-receipt.json"
CLOSEOUT = "docs/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-delete-confirm-route-mounting-readiness-review-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-17--delete-confirm-route-mounting-readiness-review.md"
UPDATER = "scripts/raisa_provider_free_read_only_delete_confirm_route_mounting_readiness_review_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_provider_free_read_only_delete_confirm_route_mounting_readiness_review_continuity.py"


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
        REVIEWER,
        FOCUSED_TEST,
        PLAN_TEST,
        EVIDENCE,
        FINDING,
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
        "title": "Provider-free read-only delete-confirm route-mounting readiness review",
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
                "Provider-free read-only static route-readiness evidence only; no route or product runtime authority.",
                "Seven lower-layer dimensions are satisfied and five bounded route-transition gaps remain.",
                "Private six-field receipt bytes remain command truth; future HTTP delivery uses only the canonical validated public projection.",
            ],
        },
        "decisions": [
            {
                "id": "accept-delete-confirm-route-mounting-readiness-review",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept no lower-layer blocker and continue to one bounded provider-free delete-confirm HTTP route-convergence candidate.",
            }
        ],
        "claim_scope": [
            "All 23 canonical-LF bindings match before the exact twelve-dimension classification.",
            "The accepted matrix is seven satisfied, five route-transition gaps and zero blocking gaps.",
            "167 hostile contract mutations fail closed.",
            "The final 412-test provider-free profile, Ruff, compilation, whitespace and byte-identical regeneration pass.",
            "One clean eight-command Gemini 3.7 Flash/high veto passes at unchanged exact candidate HEAD and tree.",
            "AER-0364 and AER-0365 preserve the corrected timestamp and commit-ref evidence incidents.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [CONTRACT, SCHEMA, EVIDENCE, FINDING, REGISTER],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                WORKER,
                CORRECTION,
                PREVERIFIER_FAILED,
                PREVERIFIER,
                WORKTREE_PREFLIGHT,
                REVIEW,
            ],
            "tests": [FOCUSED_TEST, PLAN_TEST, CONTINUITY_TEST],
            "artifacts": [REVIEWER, PACKET, MANIFEST, UPDATER],
        },
        "unresolved_gates": [
            "Canonical and hidden-alias route convergence is not implemented by this review.",
            "Raw compatibility DELETE remains separate and outside the accepted confirmation envelope.",
            "No schema/database execution, capability, product data, provider, deployment, Pages or protected-ref authority is opened.",
        ],
    }


def main() -> int:
    graph = _read(GRAPH)
    if graph["graph_revision"] == 306 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 307
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 307 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected delete-confirm readiness Continuity predecessor")
    _write(GRAPH, graph)

    compass = _read(COMPASS)
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove delete-confirm route readiness without opening route authority",
        "outcome": "No hidden lower-layer blocker remains; five exact route-transition gaps are frozen.",
        "evidence": _all_evidence(),
    }
    if (
        compass["map_revision"] == 288
        and compass["source_graph_revision"] == 306
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 289
        and compass["source_graph_revision"] == 307
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected delete-confirm readiness Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["prerequisites"] = [
                "Preserve the accepted private-receipt/public-projection separation and raw DELETE isolation.",
                "Converge the five frozen transition gaps through one provider-free route handler and adapter call.",
                "Keep database execution, capability, product data, providers and protected integration separately gated.",
            ]
            for path in journey["evidence"]:
                if path not in horizon["evidence"]:
                    horizon["evidence"].append(path)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Delete-confirm is ready for bounded HTTP route convergence",
        "why_now": "The unmounted physical, authority, composition and response foundations pass and no lower-layer blocker remains.",
        "outcome": "Five route-transition gaps are exact: canonical alias, version binding, server dependencies, public schema and canonical public bytes.",
        "unlocks": [
            "Freeze one provider-free delete-confirm HTTP route-convergence plan.",
            "Connect one canonical/hidden-alias handler to the accepted adapter without reopening database foundations.",
        ],
        "does_not_solve": [
            "Mounted route behavior, HTTP execution or product command runtime.",
            "Database execution, capability provisioning or product data.",
            "Provider/credential activity, UI, deployment, release, Pages or protected refs.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 307 / Compass 289. Delete-confirm has no remaining lower-layer route blocker; one provider-free HTTP route-convergence candidate is next."
    )
    limit = "The delete-confirm readiness result is read-only evidence; no route, schema behavior, database, capability or product runtime is opened."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 307
    compass["map_revision"] = 289
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
