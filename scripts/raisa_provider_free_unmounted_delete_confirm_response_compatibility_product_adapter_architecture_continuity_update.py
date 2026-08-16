"""Advance Continuity and Compass for delete-confirm response architecture."""

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
NODE_ID = "raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture"
PARENT = "raisa-provider-free-read-only-delete-confirm-route-convergence-and-ariadne-git-object-resolution"
SOURCE_HEAD = "9f0c166be2276d4e236dbdb4ed5657074ffbd0aa"
UPDATED_AT = "2026-08-16T08:12:23Z"

PLAN = "docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture-plan.md"
ARCHITECTURE = "docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture.md"
THREAT = "docs/security/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture-threat-model-delta.md"
CLOSEOUT = "docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-delete-confirm-response-compatibility-product-adapter-architecture-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-16--delete-confirm-response-compatibility-product-adapter-architecture.md"
BASE = "orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture/"
CONTRACT = BASE + "architecture-contract.json"
CONTRACT_SCHEMA = BASE + "architecture-contract.schema.json"
EVIDENCE = BASE + "provider-free-architecture-evidence.json"
EVIDENCE_SCHEMA = BASE + "provider-free-architecture-evidence.schema.json"
VALIDATOR = "scripts/raisa_provider_free_unmounted_delete_confirm_response_compatibility_product_adapter_architecture.py"
FOCUSED_TEST = "tests/test_raisa_provider_free_unmounted_delete_confirm_response_compatibility_product_adapter_architecture.py"
PROVIDER_FREE_RUNNER = "scripts/ariadne_provider_free_pytest.py"
PROVIDER_FREE_TEST = "tests/test_ariadne_provider_free_pytest.py"
FAILED_WORKER = "orchestration/agent_inbox/deepseek/raisa-delete-confirm-response-compatibility-product-adapter-architecture-worker-result.json"
CORRECTED_WORKER = "orchestration/agent_inbox/deepseek/raisa-delete-confirm-response-compatibility-product-adapter-architecture-correction-worker-result.json"
INCIDENT = "orchestration/agent_inbox/codex/raisa-delete-confirm-response-architecture-provider-free-pytest-boundary-incident.json"
REGISTER = "docs/ariadne-agent-error-correction-register-revision-311.md"
PREVERIFIER = "orchestration/agent_inbox/codex/raisa-delete-confirm-response-compatibility-product-adapter-architecture-pre-verifier-acceptance-corrected-receipt.json"
PREFLIGHT = "orchestration/agent_inbox/codex/raisa-delete-confirm-response-compatibility-product-adapter-architecture-gemini37-review-worktree-preflight.json"
PREDISPATCH = "orchestration/agent_inbox/codex/raisa-delete-confirm-response-compatibility-product-adapter-architecture-gemini37-veto-predispatch-receipt.json"
REVIEW = "orchestration/agent_inbox/antigravity/raisa-delete-confirm-response-compatibility-product-adapter-architecture-gemini37-review-receipt.json"
UPDATER = "scripts/raisa_provider_free_unmounted_delete_confirm_response_compatibility_product_adapter_architecture_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_provider_free_unmounted_delete_confirm_response_compatibility_product_adapter_architecture_continuity.py"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _all_evidence() -> list[str]:
    return [
        PLAN,
        ARCHITECTURE,
        THREAT,
        CONTRACT,
        CONTRACT_SCHEMA,
        EVIDENCE,
        EVIDENCE_SCHEMA,
        VALIDATOR,
        FOCUSED_TEST,
        PROVIDER_FREE_RUNNER,
        PROVIDER_FREE_TEST,
        FAILED_WORKER,
        CORRECTED_WORKER,
        INCIDENT,
        REGISTER,
        PREVERIFIER,
        PREFLIGHT,
        PREDISPATCH,
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
        "title": "Provider-free unmounted delete-confirm response compatibility and product-adapter architecture",
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
                "Provider-free unmounted architecture and authored-synthetic contract proof only; no product runtime authority.",
                "The six-field private canonical bytes remain sole persisted command truth; the public v1 envelope is a pure deterministic projection.",
                "Raw DELETE remains isolated and no route, schema, database or capability is opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-delete-confirm-response-and-product-adapter-architecture",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept server-owned ingress, locked proposal re-admission, physical-seam composition and byte-identical minimal public response replay; continue only to a provider-free unmounted implementation.",
            }
        ],
        "claim_scope": [
            "Fourteen canonical-LF input bindings and four semantic-output digests match.",
            "The exact six-field private receipt rejects reordered, whitespace-altered, CRLF, duplicate-key and alternate-escape JSON.",
            "All 136 contract and 20 evidence hostile mutations fail closed.",
            "Provider-free 191-test canonical-static and 424-test focused profiles pass; exact Python 3.11 runtime validation is unclaimed on this host.",
            "One clean six-command Gemini 3.7 Flash/high veto passes at the unchanged exact candidate.",
            "AER-0358 is corrected by the provider-free no-conftest pytest entry point.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [ARCHITECTURE, CONTRACT, CONTRACT_SCHEMA, EVIDENCE, EVIDENCE_SCHEMA, INCIDENT, REGISTER],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [FAILED_WORKER, CORRECTED_WORKER, PREVERIFIER, PREFLIGHT, PREDISPATCH, REVIEW],
            "tests": [FOCUSED_TEST, PROVIDER_FREE_TEST, CONTINUITY_TEST],
            "artifacts": [VALIDATOR, PROVIDER_FREE_RUNNER, UPDATER],
        },
        "unresolved_gates": [
            "The response projection, server-owned ingress and locked re-admission composition are architecture only and remain unimplemented in product source.",
            "No route/schema edit, route call, database execution, capability provisioning or product data is admitted.",
            "Provider, deployment, release, Pages and protected-ref authority remain closed.",
        ],
    }


def main() -> int:
    graph = _read(GRAPH)
    if graph["graph_revision"] == 304 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 305
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 305 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected response-architecture Continuity predecessor")
    _write(GRAPH, graph)

    compass = _read(COMPASS)
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Settle stable minimal delete-confirm delivery and server-owned adapter authority before implementation",
        "outcome": "The off-route architecture now binds exact private command truth to byte-identical public replay and locked current-authority composition.",
        "evidence": _all_evidence(),
    }
    if (
        compass["map_revision"] == 286
        and compass["source_graph_revision"] == 304
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 287
        and compass["source_graph_revision"] == 305
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected response-architecture Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["prerequisites"] = [
                "Preserve the accepted serial PostgreSQL delete-confirm foundation and raw DELETE isolation.",
                "Implement the accepted response/product-adapter architecture in one provider-free unmounted composition tranche.",
                "Keep route/schema execution, product data, capabilities, providers and protected integration separately gated.",
            ]
            for path in journey["evidence"]:
                if path not in horizon["evidence"]:
                    horizon["evidence"].append(path)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Delete-confirm response and adapter meaning are frozen before any product implementation",
        "why_now": "The route review identified six coupled blockers; stable response replay and server-owned authority now have one accepted off-route contract.",
        "outcome": "The minimal public v1 envelope is a byte-deterministic projection of exact private command truth, with locked current-authority re-admission and raw DELETE isolation.",
        "unlocks": [
            "Freeze one provider-free unmounted delete-confirm composition and product-adapter implementation tranche.",
            "Implement pure projection, server-owned ingress, locked re-admission composition and closed outcome mapping without a route or database.",
        ],
        "does_not_solve": [
            "Route or schema editing, mounting, calling or product execution.",
            "Capability provisioning, product data or additional database behavior.",
            "Provider/credential activity, deployment, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 305 / Compass 287. Delete-confirm now has an accepted minimal byte-authoritative response and server-owned product-adapter architecture; one provider-free unmounted implementation is next before route work."
    )
    limit = "The accepted delete-confirm response architecture opens no route, schema, database, capability or product runtime; its next implementation remains provider-free and unmounted."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 305
    compass["map_revision"] = 287
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
