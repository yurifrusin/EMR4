"""Advance Continuity and Compass for delete-confirm route convergence review."""

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
NODE_ID = "raisa-provider-free-read-only-delete-confirm-route-convergence-and-ariadne-git-object-resolution"
PARENT = "raisa-provider-free-disposable-postgresql-delete-confirm-behavior-transaction-rehearsal"
SOURCE_HEAD = "1cc75672abba6e011e0de03f26a3ad2ba9bae396"
UPDATED_AT = "2026-08-16T06:13:48Z"

PLAN = "docs/raisa-provider-free-read-only-delete-confirm-route-convergence-and-ariadne-git-object-resolution-plan.md"
THREAT = "docs/security/raisa-provider-free-read-only-delete-confirm-route-convergence-and-ariadne-git-object-resolution-threat-model-delta.md"
REPORT_PATH = "docs/raisa-provider-free-read-only-delete-confirm-route-convergence-review.md"
CLOSEOUT = "docs/raisa-provider-free-read-only-delete-confirm-route-convergence-and-ariadne-git-object-resolution-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-delete-confirm-route-convergence-git-object-resolution-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-16--delete-confirm-route-convergence-and-ariadne-git-object-resolution.md"
BASE = "orchestration/continuity/raisa-delete-confirm-route-convergence-and-ariadne-git-object-resolution/"
CONTRACT = BASE + "route-convergence-contract.json"
EVIDENCE = BASE + "provider-free-read-only-evidence.json"
REVIEWER = "scripts/raisa_provider_free_read_only_delete_confirm_route_convergence_review.py"
TEST = "tests/test_raisa_provider_free_read_only_delete_confirm_route_convergence_review.py"
RESOLVER = "orchestration_harness/git_object_resolution.py"
RESOLVER_TEST = "tests/test_ariadne_git_object_resolution.py"
FAILED_REVIEW = "orchestration/agent_inbox/antigravity/raisa-delete-confirm-route-convergence-git-object-resolution-gemini37-review-receipt.json"
PASS_REVIEW = "orchestration/agent_inbox/antigravity/raisa-delete-confirm-route-convergence-git-object-resolution-corrected-gemini37-review-receipt.json"
INCIDENT = "orchestration/agent_inbox/codex/raisa-delete-confirm-route-convergence-checkout-hash-recurrence-incident.json"
REGISTER = "docs/ariadne-agent-error-correction-register-revision-310.md"
PREVERIFIER = "orchestration/agent_inbox/codex/raisa-delete-confirm-route-convergence-git-object-resolution-corrected-pre-verifier-receipt.json"
PREDISPATCH = "orchestration/agent_inbox/codex/raisa-delete-confirm-route-convergence-git-object-resolution-corrected-gemini37-veto-predispatch-receipt.json"
PREFLIGHT = "orchestration/agent_inbox/codex/raisa-delete-confirm-route-convergence-git-object-resolution-corrected-gemini37-review-worktree-preflight.json"
UPDATER = "scripts/raisa_provider_free_read_only_delete_confirm_route_convergence_git_object_resolution_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_provider_free_read_only_delete_confirm_route_convergence_git_object_resolution_continuity.py"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _all_evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        CONTRACT,
        EVIDENCE,
        REVIEWER,
        TEST,
        RESOLVER,
        RESOLVER_TEST,
        REPORT_PATH,
        FAILED_REVIEW,
        INCIDENT,
        REGISTER,
        PREVERIFIER,
        PREFLIGHT,
        PREDISPATCH,
        PASS_REVIEW,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        UPDATER,
        CONTINUITY_TEST,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free read-only delete-confirm route convergence and Ariadne Git-object resolution",
        "kind": "review",
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
                "Provider-free exact-file read-only product review and repository-only Ariadne control; no product runtime authority.",
                "The mounted route remains blocked pending one unmounted response-compatibility and product-adapter architecture.",
                "Git resolution proves exact commit identity/type/ancestry only and cannot move refs or infer semantic acceptance.",
            ],
        },
        "decisions": [
            {
                "id": "accept-delete-confirm-route-block-and-git-object-resolution",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept three satisfied, one partial and six blocking route dimensions plus fail-closed machine Git commit resolution; continue only to an unmounted response/product-adapter architecture.",
            }
        ],
        "claim_scope": [
            "The deterministic route verdict is unmounted_adapter_and_response_transition_required.",
            "The minimized six-field private receipt cannot be silently relabelled or reconstructed from later mutable state as the full public response.",
            "Strict-UTF-8 canonical-LF hashing binds eighteen sources across clean Windows checkouts and rejects bare CR.",
            "Every configured Ariadne continuation event resolves exact commit/type/ancestry and fails closed with dispatch false.",
            "The corrected canonical 197-test profile and one clean Gemini 3.7 Flash/high veto pass.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [CONTRACT, EVIDENCE, REPORT_PATH, INCIDENT, REGISTER],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [FAILED_REVIEW, PREVERIFIER, PREFLIGHT, PREDISPATCH, PASS_REVIEW],
            "tests": [TEST, RESOLVER_TEST, CONTINUITY_TEST],
            "artifacts": [REVIEWER, RESOLVER, UPDATER],
        },
        "unresolved_gates": [
            "Server-owned authority ingress, locked proposal re-admission, physical-seam composition and response mapping remain absent from the mounted route.",
            "The private six-field receipt and full public confirmation envelope need one byte-authoritative off-route replay architecture.",
            "No route edit/call, product data, database execution, capability provisioning, provider, deployment, release, Pages or protected-ref authority is open.",
        ],
    }


def main() -> int:
    graph = _read(GRAPH)
    if graph["graph_revision"] == 303 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 304
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 304 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected route-convergence Continuity predecessor")
    _write(GRAPH, graph)

    compass = _read(COMPASS)
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Separate literal delete-confirm mounting from safe authority-kernel and response convergence while hardening Ariadne provenance",
        "outcome": "The route remains blocked by six coupled adapter/response gaps; exact Git commit provenance now fails closed mechanically.",
        "evidence": _all_evidence(),
    }
    if (
        compass["map_revision"] == 285
        and compass["source_graph_revision"] == 303
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 286
        and compass["source_graph_revision"] == 304
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected route-convergence Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["prerequisites"] = [
                "Preserve the accepted serial PostgreSQL delete-confirm foundation and raw DELETE isolation.",
                "Design one provider-free unmounted response-compatibility and product-adapter architecture for the six route blockers.",
                "Keep route execution, product data, providers and protected integration separately gated.",
            ]
            for path in journey["evidence"]:
                if path not in horizon["evidence"]:
                    horizon["evidence"].append(path)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Route readiness is reduced to one bounded unmounted response and product-adapter architecture",
        "why_now": "The serial physical transaction foundation is settled, but literal mounting still bypasses its authority and response contracts.",
        "outcome": "Three satisfied, one partial and six blocking dimensions are accepted; Ariadne source commit provenance is now machine-resolved and fail closed.",
        "unlocks": [
            "Freeze one provider-free unmounted delete-confirm response-compatibility and product-adapter architecture.",
            "Reconcile server-owned authority and locked proposal truth with byte-exact full public response replay off-route.",
        ],
        "does_not_solve": [
            "Route editing, mounting, calling or product execution.",
            "Capability provisioning, real product data or additional database behavior.",
            "Provider/credential activity, deployment, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 304 / Compass 286. Delete-confirm route convergence remains blocked by six coupled authority, lock, atomicity and response-delivery gaps; one unmounted response/product-adapter architecture is next. Ariadne now resolves structured source commits mechanically before continuation receipts pass."
    )
    limit = "The accepted delete-confirm route review opens no route or product runtime; literal mounting remains distinct from authority-kernel and byte-authoritative response convergence."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 304
    compass["map_revision"] = 286
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
