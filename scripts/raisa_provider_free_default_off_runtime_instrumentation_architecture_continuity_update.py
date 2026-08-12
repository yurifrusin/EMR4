"""Advance Continuity and Compass for runtime-instrumentation architecture."""

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
NODE_ID = "raisa-provider-free-default-off-runtime-instrumentation-architecture"
PARENT = "raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal"
SOURCE_HEAD = "ed52950f451af88892a8f469157ecf8c8567da81"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = "docs/raisa-provider-free-default-off-runtime-instrumentation-architecture-plan.md"
DESIGN = "docs/raisa-provider-free-default-off-runtime-instrumentation-architecture.md"
THREAT = "docs/security/raisa-provider-free-default-off-runtime-instrumentation-architecture-threat-model-delta.md"
PACKET_DIR = "orchestration/continuity/raisa-provider-free-default-off-runtime-instrumentation-architecture/"
CONTRACT = PACKET_DIR + "contract.json"
SCHEMA = PACKET_DIR + "contract.schema.json"
CLOSEOUT = "docs/raisa-provider-free-default-off-runtime-instrumentation-architecture-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-default-off-runtime-instrumentation-architecture-sol-acceptance.md"
PREPLANNING_RECEIPT = "orchestration/agent_inbox/codex/raisa-default-off-runtime-instrumentation-architecture-preplanning-receipt.json"
PRECOMMIT_RECEIPT = "orchestration/agent_inbox/codex/raisa-default-off-runtime-instrumentation-architecture-candidate-precommit-receipt.json"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-12--default-off-runtime-instrumentation-architecture.md"
TEST = "tests/test_raisa_provider_free_default_off_runtime_instrumentation_architecture_continuity.py"
UPDATER = "scripts/raisa_provider_free_default_off_runtime_instrumentation_architecture_continuity_update.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _evidence() -> list[str]:
    return [
        PLAN, DESIGN, THREAT, CONTRACT, SCHEMA, CLOSEOUT, ACCEPTANCE,
        PREPLANNING_RECEIPT, PRECOMMIT_RECEIPT, MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free default-off runtime-instrumentation architecture",
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
                "This is a provider-free source-bound static architecture.",
                "It edits, imports or executes no application route and creates no runtime instrumentation.",
                "Missing safe server-owned request context denies staging; the shadow has no response or command feedback.",
            ],
        },
        "decisions": [
            {
                "id": "accept-default-off-runtime-instrumentation-architecture",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept the two-phase post-helper staging and post-final-send no-return handoff architecture.",
            }
        ],
        "claim_scope": [
            "Exactly four raw route seams are source-hashed with current helper and return-form facts.",
            "Route success seals transaction, audit and logical result, not serialized response bytes.",
            "A single-assignment cell bridges route-local staging to one post-final-send offer_nowait handoff.",
            "The exact twenty-four projection and fifteen diagnostic fields accept no free text or response material.",
            "All twelve feedback edges and all sixty hostile mutations fail closed.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [DESIGN, THREAT],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING_RECEIPT, PRECOMMIT_RECEIPT],
            "tests": [
                "tests/test_raisa_provider_free_default_off_runtime_instrumentation_architecture.py",
                TEST,
            ],
            "artifacts": [CONTRACT, SCHEMA, UPDATER],
        },
        "unresolved_gates": [
            "No request context, configuration, middleware, route hook, observer, queue, sink or persistence is implemented.",
            "Disabled-path route parity, ASGI ordering, request-cell lifecycle and failure isolation remain runtime-scaffold proof obligations.",
            "Practice enablement, operational data, kernel convergence, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 250 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 251
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 251 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected runtime-instrumentation architecture Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Freeze an honest default-off mounting seam at the four raw routes",
        "outcome": "Two-phase static architecture passes; the globally-disabled typed scaffold is next.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 232
        and compass["source_graph_revision"] == 250
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 233
        and compass["source_graph_revision"] == 251
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected runtime-instrumentation architecture Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Implement only a globally-disabled typed instrumentation scaffold with no observer or sink.",
                "Prove disabled-path zero projection/handoff plus exact authored-synthetic response, header, audit, commit and failure parity.",
                "Then prove ordinary and fallback client proposal/confirm parity before raw-route kernel convergence.",
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
        "strategic_role": "Default-off mounting architecture proved; globally-disabled typed scaffold next",
        "why_now": "The pure shadow rehearsal and exact source seams now support the narrowest reversible implementation without enabling observation.",
        "outcome": "Four route-local staging seams and one post-final-send handoff boundary pass sixty hostile mutations with no runtime creation.",
        "unlocks": [
            "Implement immutable generation, safe request context, minimized projection, request cell and after-send interfaces in the disabled state.",
            "Prove zero disabled-path reads/handoffs and exact four-route authored-synthetic behavioral parity.",
        ],
        "does_not_solve": [
            "Practice enablement, observer/sink operation, persistence, monitoring, client migration or database fencing.",
            "Durable cue delivery, CF-D2, patient/product data, providers, commands, deployment, Pages or protected refs.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 251 / Compass 233. The provider-free source-bound "
        "runtime-instrumentation architecture passes with four exact route seams, "
        "a two-phase post-final-send handoff and 60 hostile mutations rejected. "
        "The next safe tranche is the globally-disabled typed scaffold."
    )
    limit = (
        "The runtime-instrumentation result is static architecture only; no request "
        "context, route hook, middleware, observer, queue, sink or persistence exists."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 251
    compass["map_revision"] = 233
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
