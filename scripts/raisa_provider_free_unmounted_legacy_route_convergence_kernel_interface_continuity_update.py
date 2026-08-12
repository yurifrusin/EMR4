"""Advance Continuity and Compass for legacy-route kernel convergence design."""

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
    "raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface"
)
PARENT = "raisa-provider-free-unmounted-conditional-command-admission-rehearsal"
SOURCE_HEAD = "47e08eada878d8f6dd2a9b100e706404d3594e5a"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = (
    "docs/raisa-provider-free-unmounted-legacy-route-convergence-"
    "kernel-interface-plan.md"
)
DESIGN = (
    "docs/raisa-provider-free-unmounted-legacy-route-convergence-"
    "kernel-interface-design.md"
)
THREAT = (
    "docs/security/raisa-provider-free-unmounted-legacy-route-convergence-"
    "kernel-interface-threat-model-delta.md"
)
PACKET_DIR = (
    "orchestration/continuity/"
    "raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface/"
)
CONTRACT = PACKET_DIR + "contract.json"
SCHEMA = PACKET_DIR + "contract.schema.json"
CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-legacy-route-convergence-"
    "kernel-interface-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-legacy-route-convergence-kernel-interface-sol-acceptance.md"
)
FAILED_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-legacy-route-convergence-kernel-interface-preplanning-receipt.json"
)
CORRECTED_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-legacy-route-convergence-kernel-interface-preplanning-v2-receipt.json"
)
REGISTER_REVISION = "docs/ariadne-agent-error-correction-register-revision-257.md"
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-12--legacy-route-convergence-kernel-interface.md"
)
TEST = (
    "tests/test_raisa_provider_free_unmounted_legacy_route_convergence_"
    "kernel_interface_continuity.py"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_legacy_route_convergence_"
    "kernel_interface_continuity_update.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        DESIGN,
        THREAT,
        CONTRACT,
        SCHEMA,
        CLOSEOUT,
        ACCEPTANCE,
        FAILED_RECEIPT,
        CORRECTED_RECEIPT,
        REGISTER_REVISION,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free unmounted legacy-route kernel convergence design",
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
                "This is a provider-free unmounted source-hashed API Spine contract.",
                "It imports or changes no application route and performs no database, provider or command effect.",
                "All raw compatibility routes remain kernel-ineligible today.",
            ],
        },
        "decisions": [
            {
                "id": "accept-legacy-route-kernel-convergence-design",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept one common conditional-command interface and fail-closed migration DAG without route behavior change.",
            }
        ],
        "claim_scope": [
            "Exactly four raw, six proposal and five confirm routes map to four canonical operations.",
            "All forty-eight hostile mutations fail closed.",
            "Separate confirmation, precondition, idempotency and audit remain mandatory for raw convergence.",
            "Create remains blocked on a separately reviewed database-owned schedule-domain fence.",
            "Deprecation and retirement remain downstream release decisions after convergence.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [DESIGN, THREAT],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [FAILED_RECEIPT, CORRECTED_RECEIPT],
            "tests": [
                "tests/test_raisa_provider_free_unmounted_legacy_route_convergence_kernel_interface.py",
                TEST,
            ],
            "artifacts": [CONTRACT, SCHEMA, UPDATER],
        },
        "unresolved_gates": [
            "No application route adapter, shadow mapping or behavior change is implemented.",
            "No production precondition token, database fence, persistent idempotency/audit or RLS behavior is proved.",
            "Database/source/watcher/event access, patient/product data, provider, commands, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 246 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 247
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 247 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected legacy-route convergence Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Map every appointment write ingress onto one fail-closed backend command kernel",
        "outcome": "Static convergence contract passes; pure authored-synthetic route-adapter differential rehearsal is next.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 228
        and compass["source_graph_revision"] == 246
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 229
        and compass["source_graph_revision"] == 247
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected legacy-route convergence Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Rehearse pure authored-synthetic raw and confirm route adapters against the frozen common kernel request.",
                "Keep application route and database behavior closed until a later separately accepted runtime descendant.",
                "Select and prove a database-owned create schedule fence before create convergence.",
                "Retain Durable Event and Cue Delivery as a later observability-first extension.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Common command kernel mapped; inert route-adapter differential proof next",
        "why_now": "The admission semantics passed, so every current write ingress can now be classified against one exact confirmation, freshness, idempotency, audit and locking contract.",
        "outcome": "Four raw, six proposal and five confirm routes are mapped; all raw routes remain ineligible and all 48 attacks fail closed.",
        "unlocks": [
            "Transform authored-synthetic raw and confirm envelopes into one ConditionalAppointmentCommand request.",
            "Prove exact semantic equivalence for complete envelopes and exact missing-control rejection for current raw shapes.",
        ],
        "does_not_solve": [
            "Application route imports, HTTP behavior, database fencing, persistent idempotency/audit or client migration.",
            "Durable cue delivery, CF-D2, patient/product data, provider tools, commands, deployment, Pages or protected refs.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 247 / Compass 229. The provider-free unmounted "
        "legacy-route convergence contract maps four raw, six proposal and five "
        "confirm routes onto one fail-closed kernel; all 48 hostile mutations pass. "
        "The next safe tranche is the pure route-adapter differential rehearsal."
    )
    limit = (
        "The legacy-route convergence result is a static contract only; every raw "
        "route remains mounted, unchanged and kernel-ineligible."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 247
    compass["map_revision"] = 229
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
