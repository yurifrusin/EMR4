"""Advance Continuity and Compass for status-confirm composition rehearsal."""

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
    "raisa-provider-free-unmounted-status-confirm-route-convergence-"
    "composition-rehearsal"
)
PARENT = "raisa-status-confirm-preflight-idempotency-expectation-repair"
SOURCE_HEAD = "41f978ae9837cba50737cfb5f457ab62ac28dbdb"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = (
    "docs/raisa-provider-free-unmounted-status-confirm-route-convergence-"
    "composition-rehearsal-plan.md"
)
THREAT = (
    "docs/security/raisa-provider-free-unmounted-status-confirm-route-"
    "convergence-composition-rehearsal-threat-model-delta.md"
)
SERVICE = "app/services/appointment_status_composition.py"
CONTRACT = (
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-"
    "route-convergence-composition-rehearsal/composition-contract.json"
)
SCHEMA = (
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-"
    "route-convergence-composition-rehearsal/composition-contract.schema.json"
)
EVIDENCE = (
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-"
    "route-convergence-composition-rehearsal/provider-free-composition-evidence.json"
)
REHEARSAL = (
    "scripts/raisa_provider_free_unmounted_status_confirm_route_convergence_"
    "composition_rehearsal.py"
)
TEST = (
    "tests/test_raisa_provider_free_unmounted_status_confirm_route_convergence_"
    "composition_rehearsal.py"
)
PREPLAN_STATE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-confirm-"
    "route-convergence-composition-rehearsal-preplanning-runtime-state.json"
)
PREPLAN_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-confirm-"
    "route-convergence-composition-rehearsal-preplanning-receipt.json"
)
PRECOMMIT_STATE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-confirm-"
    "route-convergence-composition-rehearsal-precommit-runtime-state.json"
)
PRECOMMIT_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-confirm-"
    "route-convergence-composition-rehearsal-precommit-receipt.json"
)
CLOSEOUT_PRECOMMIT_STATE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-confirm-"
    "route-convergence-composition-rehearsal-closeout-precommit-runtime-state.json"
)
CLOSEOUT_PRECOMMIT_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-confirm-"
    "route-convergence-composition-rehearsal-closeout-precommit-receipt.json"
)
CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-status-confirm-route-convergence-"
    "composition-rehearsal-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-status-confirm-route-convergence-"
    "composition-rehearsal-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/2026-08-12--status-confirm-route-"
    "convergence-composition-rehearsal.md"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_status_confirm_route_convergence_"
    "composition_rehearsal_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_status_confirm_route_convergence_"
    "composition_rehearsal_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        SERVICE,
        CONTRACT,
        SCHEMA,
        EVIDENCE,
        REHEARSAL,
        TEST,
        PREPLAN_STATE,
        PREPLAN_RECEIPT,
        PRECOMMIT_STATE,
        PRECOMMIT_RECEIPT,
        CLOSEOUT_PRECOMMIT_STATE,
        CLOSEOUT_PRECOMMIT_RECEIPT,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free unmounted status-confirm route-convergence composition rehearsal",
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
                "The application service is unmounted and absent from the router.",
                "All execution evidence uses authored-synthetic in-memory doubles; no route or real database executes.",
                "Product data, commands, providers, deployment and protected integration remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-status-confirm-route-composition-rehearsal",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept the unmounted composition and full-envelope stored-replay reconciliation; proceed only to read-only route readiness re-review.",
            }
        ],
        "claim_scope": [
            "One unmounted callable composes status-only admission, server ingress, physical transaction factory, locked readmission, injected effect and closed response mapping.",
            "The complete current public envelope is canonical receipt authority and its five status fields are validated as a projection.",
            "Twelve scenarios, 65 hostile mutations, 13 focused, 163 current lineage and 191 canonical tests pass.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                PREPLAN_STATE,
                PREPLAN_RECEIPT,
                PRECOMMIT_STATE,
                PRECOMMIT_RECEIPT,
                CLOSEOUT_PRECOMMIT_STATE,
                CLOSEOUT_PRECOMMIT_RECEIPT,
            ],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [SERVICE, CONTRACT, SCHEMA, EVIDENCE, REHEARSAL, UPDATER],
        },
        "unresolved_gates": [
            "The mounted route does not invoke the composition and product locked-state/effect adapters remain unproved.",
            "The composition has not executed the physical PostgreSQL seam; concurrency, restart and unknown-commit claims remain closed.",
            "No route/database execution, product data/command, provider, deployment or protected integration is authorized.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 267 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 268
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 268 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected composition-rehearsal Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Compose the status-confirm safety path off-route and reconcile exact stored public replay",
        "outcome": "The unmounted callable passes finite execution/replay/failure rehearsal without opening route or database authority.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 249
        and compass["source_graph_revision"] == 267
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 250
        and compass["source_graph_revision"] == 268
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected composition-rehearsal Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve the accepted physical PostgreSQL status-confirm proof without reopening durability.",
                "Re-review route-mounting readiness against the accepted unmounted composition source.",
                "Identify only remaining product locked-state/effect adapter and route prerequisites.",
                "Keep route edits/calls, product data/commands, providers and protected integration separately gated.",
            ]
            horizon["evidence"] = [
                item
                for item in horizon["evidence"]
                if item
                != "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-route-convergence-composition-rehearsal/"
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "The status-confirm safety path is composed off-route with exact stored-envelope replay",
        "why_now": "The route admission review required composition before any mounting decision.",
        "outcome": "The unmounted callable and response reconciliation pass all finite authored-synthetic checks.",
        "unlocks": [
            "Run a provider-free read-only status-confirm route-mounting readiness re-review.",
            "Reclassify the seven prior blockers against exact composition source and name the narrowest remaining prerequisites.",
        ],
        "does_not_solve": [
            "Mounted-route convergence, route execution, product adapters or a real product command.",
            "Physical PostgreSQL composition execution, concurrency, restart, crash or unknown commit.",
            "Provider/credential activity, patient/product data, deployment, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 268 / Compass 250. The provider-free unmounted "
        "status-confirm composition and exact stored-envelope replay pass. A "
        "read-only route-mounting readiness re-review is next; mounted execution "
        "and product authority remain closed."
    )
    compass["source_graph_revision"] = 268
    compass["map_revision"] = 250
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
