"""Advance Continuity and Compass for the source-owned-truth reorientation."""

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
NODE_ID = "raisa-context-fabric-source-owned-truth-conditional-command-reorientation"
PARENT = "ariadne-cf-d2-workflow-incident-diagnosis-and-fluidity-repair"
SOURCE_HEAD = "037eed060d4519f2f3d6721135143ecb6f70e358"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = "docs/raisa-context-fabric-source-owned-truth-conditional-command-reorientation-plan.md"
ARCHITECTURE = "docs/raisa-context-fabric-source-owned-truth-conditional-command-reorientation-architecture.md"
THREAT = "docs/security/raisa-context-fabric-source-owned-truth-conditional-command-reorientation-threat-model-delta.md"
CONTRACT_DIR = (
    "orchestration/continuity/"
    "raisa-context-fabric-source-owned-truth-conditional-command-reorientation/"
)
CONTRACT = CONTRACT_DIR + "architecture-contract.json"
SCHEMA = CONTRACT_DIR + "architecture-contract.schema.json"
REVIEW = (
    "orchestration/agent_inbox/codex/"
    "raisa-context-fabric-source-owned-truth-reorientation-vertex-review-receipt.json"
)
ZERO_CALL = (
    "orchestration/agent_inbox/codex/"
    "raisa-context-fabric-source-owned-truth-reorientation-vertex-review-zero-call-receipt.json"
)
CLOSEOUT = "docs/raisa-context-fabric-source-owned-truth-conditional-command-reorientation-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-context-fabric-source-owned-truth-reorientation-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-12--context-fabric-source-owned-truth-conditional-command-reorientation.md"
)
TEST = "tests/test_raisa_context_fabric_source_owned_truth_reorientation_continuity.py"
UPDATER = "scripts/raisa_context_fabric_source_owned_truth_reorientation_continuity_update.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        ARCHITECTURE,
        THREAT,
        CONTRACT,
        SCHEMA,
        CLOSEOUT,
        ACCEPTANCE,
        REVIEW,
        ZERO_CALL,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Raisa Context Fabric source-owned truth and conditional commands",
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
                "This is repository-only architecture and changes no route, database, watcher or product behavior.",
                "Authoritative source services own current truth and atomic conditional commands; Context Frames and events have no write authority.",
                "The next descendant is authored-synthetic, provider-free and unmounted.",
            ],
        },
        "decisions": [
            {
                "id": "accept-source-owned-truth-conditional-command-reorientation",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Make command correctness independent of cue durability while retaining a named later Durable Event and Cue Delivery extension.",
            }
        ],
        "claim_scope": [
            "Current truth and mutation serialization belong to authoritative source services.",
            "Context Fabric frames remain read-only and expiring; events are acceleration hints requiring fresh authorised reads.",
            "Freshness, confirmation, idempotency and audit are distinct command evidence.",
            "Appointment create requires schedule-conflict-domain serialization and a final database invariant check.",
            "One logical watcher serves each database event partition; future physical replicas are externally fenced active/standby.",
            "CF-D1 is retained and CF-D2 may reopen only through a fresh observability-first plan.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [ARCHITECTURE, THREAT],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [REVIEW, ZERO_CALL],
            "tests": [
                "tests/test_raisa_context_fabric_source_owned_truth_reorientation.py",
                TEST,
            ],
            "artifacts": [CONTRACT, SCHEMA, UPDATER],
        },
        "unresolved_gates": [
            "No production precondition token, database schedule fence or common command kernel is implemented or proved.",
            "The legacy compatibility routes remain mounted and unchanged pending separate migration evidence.",
            "Durable Event and Cue Delivery remains deferred; restart, unknown-commit, rotation, retention and purge are unproved.",
            "Operational database/source/watcher access, patient/product/clinical data, provider tools, commands, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 244 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 245
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 245 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected source-owned-truth Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Move first-runtime correctness to source-owned conditional commands while keeping events as cue acceleration",
        "outcome": "Architecture passes; durable cue delivery is deferred but retained, and the next safe tranche is an unmounted authored-synthetic admission rehearsal.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 226
        and compass["source_graph_revision"] == 244
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 227
        and compass["source_graph_revision"] == 245
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected source-owned-truth Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Run the provider-free unmounted conditional-command admission rehearsal.",
                "Keep all route, database, watcher, product-data and command surfaces closed until their own descendants pass.",
                "Return to Durable Event and Cue Delivery later through a fresh observability-first plan.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Source-owned correctness architecture accepted; provider-free conditional-command admission rehearsal next",
        "why_now": "The stopped CF-D2 path exposed that durable cue delivery should improve timeliness and observability rather than sit inside the first runtime's correctness kernel.",
        "outcome": "Atomic conditional commands protect database truth even when a cue is delayed or missed, while durability remains a named later extension.",
        "unlocks": [
            "Provider-free authored-synthetic admission scenarios for preconditions, lock plans and typed winner/loser outcomes.",
            "A later route-convergence design after the common command kernel is mechanically admitted.",
            "A future observability-first Durable Event and Cue Delivery programme without making events current truth.",
        ],
        "does_not_solve": [
            "Production precondition tokens, database schedule fencing or legacy-route behavior.",
            "Restart-safe cue delivery, CF-D2, key rotation, retention/purge or operational watcher availability.",
            "Patient/product/clinical data, executable tools, commands, deployment, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 245 / Compass 227. The Context Fabric source-owned-truth "
        "and conditional-command reorientation passes. Events are acceleration hints, "
        "one logical watcher serves each event partition, and command correctness no longer "
        "depends on durable cue delivery. The next safe tranche is the provider-free "
        "unmounted conditional-command admission rehearsal."
    )
    limit = (
        "The source-owned-truth reorientation proves architecture only; it does not prove "
        "a runtime command kernel, database fence, watcher or durable cue delivery."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 245
    compass["map_revision"] = 227
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
