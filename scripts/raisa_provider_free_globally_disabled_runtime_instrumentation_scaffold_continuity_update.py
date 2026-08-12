"""Advance Continuity and Compass for the globally-disabled scaffold."""

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
NODE_ID = "raisa-provider-free-globally-disabled-runtime-instrumentation-scaffold"
PARENT = "raisa-provider-free-default-off-runtime-instrumentation-architecture"
SOURCE_HEAD = "410ea6dbbe28b94cfaa83ac5f6b586910c77aa6a"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = "docs/raisa-provider-free-globally-disabled-runtime-instrumentation-scaffold-plan.md"
DESIGN = "docs/raisa-provider-free-globally-disabled-runtime-instrumentation-scaffold-design.md"
THREAT = "docs/security/raisa-provider-free-globally-disabled-runtime-instrumentation-scaffold-threat-model-delta.md"
CLOSEOUT = "docs/raisa-provider-free-globally-disabled-runtime-instrumentation-scaffold-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-globally-disabled-runtime-instrumentation-scaffold-sol-acceptance.md"
PREPLANNING_RECEIPT = "orchestration/agent_inbox/codex/raisa-globally-disabled-runtime-instrumentation-scaffold-preplanning-receipt.json"
PRECOMMIT_RECEIPT = "orchestration/agent_inbox/codex/raisa-globally-disabled-runtime-instrumentation-scaffold-precommit-receipt.json"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-12--globally-disabled-runtime-instrumentation-scaffold.md"
TEST = "tests/test_raisa_provider_free_globally_disabled_runtime_instrumentation_scaffold_continuity.py"
UPDATER = "scripts/raisa_provider_free_globally_disabled_runtime_instrumentation_scaffold_continuity_update.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        DESIGN,
        THREAT,
        CLOSEOUT,
        ACCEPTANCE,
        PREPLANNING_RECEIPT,
        PRECOMMIT_RECEIPT,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free globally-disabled runtime-instrumentation scaffold",
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
                "This is a provider-free globally-disabled dormant application scaffold.",
                "The only constructible generation has empty allowlists and no digest-key reference.",
                "No context provider, observer, sink, product-data projection or command feedback exists.",
            ],
        },
        "decisions": [
            {
                "id": "accept-globally-disabled-runtime-instrumentation-scaffold",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept exact dormant route and post-send scaffold wiring with zero-work disabled behavior.",
            }
        ],
        "claim_scope": [
            "Enabled, allowlisted, key-bearing and stale generations are structurally rejected.",
            "Four raw routes stage only after helper success and pass only a closed adapter constant.",
            "The disabled route and middleware paths perform zero context, projection, digest, cell or offer work.",
            "Authored-synthetic response, mutation and audit behavior remains equivalent across all four routes.",
            "Seventeen tranche tests, 170 focused regressions and the canonical 191-test profile pass.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [DESIGN, THREAT],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING_RECEIPT, PRECOMMIT_RECEIPT],
            "tests": [
                "tests/test_raisa_provider_free_globally_disabled_runtime_instrumentation_scaffold.py",
                TEST,
            ],
            "artifacts": [
                "app/services/diary/shadow_instrumentation.py",
                "app/middleware/shadow_instrumentation.py",
                UPDATER,
            ],
        },
        "unresolved_gates": [
            "No practice or route is enabled and no operational observer, sink, key custody or diagnostic output exists.",
            "Ordinary and fallback Diary client proposal-confirm parity remains unproved.",
            "Compatibility-route removal, raw-route kernel convergence, product data, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 251 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 252
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 252 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected globally-disabled scaffold Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Mount only the dormant fail-closed instrumentation shapes",
        "outcome": "Globally-disabled zero-work scaffold passes; client proposal-confirm parity is next.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 233
        and compass["source_graph_revision"] == 251
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 234
        and compass["source_graph_revision"] == 252
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected globally-disabled scaffold Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Freeze the exact ordinary and fallback Diary client raw-write inventory.",
                "Prove proposal plus signed-confirm parity before removing or blocking any compatibility route.",
                "Then converge status, delete and update on the accepted backend kernel in order.",
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
        "strategic_role": "Dormant instrumentation scaffold proved; client proposal-confirm parity next",
        "why_now": "The mounting seam is present but structurally unenableable, so client migration can proceed without opening observation.",
        "outcome": "Four raw routes and the outer ASGI boundary preserve authored-synthetic behavior with zero disabled-path work.",
        "unlocks": [
            "Inventory every ordinary and fallback Diary raw-write call site.",
            "Prove proposal and signed-confirm replacements while keeping compatibility routes mounted.",
        ],
        "does_not_solve": [
            "Practice enablement, observer/sink operation, product data, diagnostic persistence or monitoring.",
            "Compatibility removal, raw-route kernel convergence, deployment, Pages or protected refs.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 252 / Compass 234. The provider-free globally-"
        "disabled runtime-instrumentation scaffold passes with 17 tranche tests, "
        "zero disabled-path projection or handoff work and exact four-route "
        "authored-synthetic parity. Client proposal-confirm parity is next."
    )
    limit = (
        "The runtime-instrumentation scaffold is structurally unenableable and has no "
        "context provider, key custody, observer, sink or operational output."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 252
    compass["map_revision"] = 234
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
