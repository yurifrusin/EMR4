"""Advance Continuity and Compass for delete-confirm adapter implementation."""

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
NODE_ID = "raisa-provider-free-unmounted-delete-confirm-composition-product-adapter-implementation"
PARENT = "raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture"
SOURCE_HEAD = "43e993a98ffec3f9ffe2740b0b38816bcb2d6adb"
UPDATED_AT = "2026-08-16T12:07:55Z"

PLAN = "docs/raisa-provider-free-unmounted-delete-confirm-composition-product-adapter-implementation-plan.md"
CONTRACT = "orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-composition-product-adapter-implementation/implementation-contract.json"
COMPOSITION = "app/services/appointment_delete_composition.py"
ADAPTER = "app/services/appointment_delete_product_adapter.py"
COMPOSITION_TEST = "tests/test_appointment_delete_composition.py"
ADAPTER_TEST = "tests/test_appointment_delete_product_adapter.py"
WORKER = "orchestration/agent_inbox/deepseek/raisa-delete-confirm-composition-product-adapter-implementation-worker-receipt.json"
CORRECTION = "orchestration/agent_inbox/deepseek/raisa-delete-confirm-composition-product-adapter-implementation-correction-worker-receipt.json"
REJECTION = "orchestration/agent_inbox/codex/raisa-delete-confirm-composition-product-adapter-worker-candidate-rejection.json"
LEASE = "orchestration/agent_inbox/codex/raisa-delete-confirm-composition-product-adapter-sol-recovery-lease.md"
REGISTER_312 = "docs/ariadne-agent-error-correction-register-revision-312.md"
REGISTER_313 = "docs/ariadne-agent-error-correction-register-revision-313.md"
PREVERIFIER = "orchestration/agent_inbox/codex/raisa-delete-confirm-composition-product-adapter-pre-verifier-acceptance-receipt.json"
PACKET = "orchestration/agent_inbox/codex/raisa-delete-confirm-composition-product-adapter-gemini37-review-packet.md"
MANIFEST = "orchestration/agent_inbox/codex/raisa-delete-confirm-composition-product-adapter-gemini37-command-manifest.json"
MANIFEST_ADMISSION = "orchestration/agent_inbox/codex/raisa-delete-confirm-composition-product-adapter-gemini37-command-manifest-admission.json"
REVIEW = "orchestration/agent_inbox/antigravity/raisa-delete-confirm-composition-product-adapter-gemini37-review-receipt.json"
CLOSEOUT = "docs/raisa-provider-free-unmounted-delete-confirm-composition-product-adapter-implementation-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-delete-confirm-composition-product-adapter-implementation-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-16--delete-confirm-composition-product-adapter-implementation.md"
UPDATER = "scripts/raisa_provider_free_unmounted_delete_confirm_composition_product_adapter_implementation_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_provider_free_unmounted_delete_confirm_composition_product_adapter_implementation_continuity.py"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _all_evidence() -> list[str]:
    return [
        PLAN,
        CONTRACT,
        COMPOSITION,
        ADAPTER,
        COMPOSITION_TEST,
        ADAPTER_TEST,
        WORKER,
        CORRECTION,
        REJECTION,
        LEASE,
        REGISTER_312,
        REGISTER_313,
        PREVERIFIER,
        PACKET,
        MANIFEST,
        MANIFEST_ADMISSION,
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
        "title": "Provider-free unmounted delete-confirm composition and product-adapter implementation",
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
                "Provider-free unmounted authored-synthetic implementation only; no route or product runtime authority.",
                "Server-owned ingress and locked re-admission compose only through the accepted physical seam.",
                "The six-field private receipt remains sole persisted command truth and replay has no effect.",
            ],
        },
        "decisions": [
            {
                "id": "accept-delete-confirm-composition-product-adapter-implementation",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept the unmounted pure projection and server-owned product adapter; continue only to a provider-free read-only route-mounting readiness review.",
            }
        ],
        "claim_scope": [
            "Twelve canonical-LF input bindings match and forbidden route/schema/model/migration/API Spine paths are unchanged.",
            "Both freshness coordinates and the proposal evidence copy must equal recomputed signed truth before a command session.",
            "The consolidated provider-free profile passes 517 tests with Ruff, compilation and whitespace.",
            "One clean seven-command Gemini 3.7 Flash/high veto passes at the unchanged exact candidate.",
            "AER-0359 through AER-0362 preserve both worker rejections, the Sol recovery and two harness guards.",
            "Exact Python 3.11 runtime execution is unclaimed on this host.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [CONTRACT, COMPOSITION, ADAPTER, REJECTION, LEASE, REGISTER_312, REGISTER_313],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [WORKER, CORRECTION, PREVERIFIER, MANIFEST_ADMISSION, REVIEW],
            "tests": [COMPOSITION_TEST, ADAPTER_TEST, CONTINUITY_TEST],
            "artifacts": [MANIFEST, PACKET, UPDATER],
        },
        "unresolved_gates": [
            "No canonical or hidden alias route is edited, mounted or called; raw DELETE remains isolated.",
            "No schema, database execution, capability provisioning or product data is admitted.",
            "Provider, UI, deployment, release, Pages and protected-ref authority remain closed.",
        ],
    }


def main() -> int:
    graph = _read(GRAPH)
    if graph["graph_revision"] == 305 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 306
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 306 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected delete-confirm implementation Continuity predecessor")
    _write(GRAPH, graph)

    compass = _read(COMPASS)
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Implement the accepted delete-confirm truth-kernel adapter before route work",
        "outcome": "The pure projection and server-owned locked composition now exist as tested unmounted product services.",
        "evidence": _all_evidence(),
    }
    if (
        compass["map_revision"] == 287
        and compass["source_graph_revision"] == 305
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 288
        and compass["source_graph_revision"] == 306
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected delete-confirm implementation Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["prerequisites"] = [
                "Preserve the accepted delete-confirm physical seam, private receipt and raw DELETE isolation.",
                "Review route-mounting readiness read-only before any canonical/hidden alias edit.",
                "Keep database execution, capabilities, product data, providers and protected integration separately gated.",
            ]
            for path in journey["evidence"]:
                if path not in horizon["evidence"]:
                    horizon["evidence"].append(path)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Delete-confirm composition is implemented off-route before mounting decisions",
        "why_now": "The accepted architecture could now be realized without opening database or route authority.",
        "outcome": "Unmounted services enforce server-owned ingress, exact proposal/locked re-admission and byte-stable private-to-public replay.",
        "unlocks": [
            "Freeze one provider-free read-only route-mounting readiness review.",
            "Measure canonical/hidden alias convergence against the implemented services without route edits.",
        ],
        "does_not_solve": [
            "Route editing, mounting, calling or product execution.",
            "Schema/database execution, capability provisioning or product data.",
            "Provider/credential activity, UI, deployment, release, Pages or protected refs.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 306 / Compass 288. Delete-confirm now has accepted unmounted composition and server-owned adapter services; a provider-free read-only route-mounting readiness review is next."
    )
    limit = "The accepted delete-confirm services remain unmounted and provider-free; route/schema/database/capability/product-data authority is still closed."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 306
    compass["map_revision"] = 288
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
