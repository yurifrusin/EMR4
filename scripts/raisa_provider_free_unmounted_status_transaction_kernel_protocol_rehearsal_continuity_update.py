"""Advance Continuity and Compass for the unmounted status-kernel protocol."""

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
NODE_ID = "raisa-provider-free-unmounted-status-transaction-kernel-protocol-rehearsal"
PARENT = (
    "raisa-provider-free-compatibility-conformance-harness-temporal-idempotency-"
    "readiness-repair"
)
SOURCE_HEAD = "bd381de83bc0b5d4b6b43b4bbb4e1e70a68d7f62"
PARENT_SOURCE_HEAD = "48c1821ad8b28c68204e70dea9972b6ba27e4dc1"
BAD_PARENT_SOURCE_HEAD = "48c1821af79f9d22b7c029fdbba8c4f984d239e5"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = "docs/raisa-provider-free-unmounted-status-transaction-kernel-protocol-rehearsal-plan.md"
DESIGN = "docs/raisa-provider-free-unmounted-status-transaction-kernel-protocol-rehearsal-design.md"
THREAT = "docs/security/raisa-provider-free-unmounted-status-transaction-kernel-protocol-rehearsal-threat-model-delta.md"
CLOSEOUT = "docs/raisa-provider-free-unmounted-status-transaction-kernel-protocol-rehearsal-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-status-transaction-kernel-protocol-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-12--status-transaction-kernel-protocol.md"
PACKET_ROOT = "orchestration/continuity/raisa-provider-free-unmounted-status-transaction-kernel-protocol-rehearsal"
PREPLANNING = "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-transaction-kernel-protocol-preplanning-receipt.json"
PRECOMMIT = "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-transaction-kernel-protocol-precommit-receipt.json"
TEST = "tests/test_raisa_provider_free_unmounted_status_transaction_kernel_protocol_rehearsal_continuity.py"
UPDATER = "scripts/raisa_provider_free_unmounted_status_transaction_kernel_protocol_rehearsal_continuity_update.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    rendered = json.dumps(value, indent=2, ensure_ascii=False)
    path.write_bytes((rendered + "\n").encode("utf-8"))


def _evidence() -> list[str]:
    return [
        PLAN,
        DESIGN,
        THREAT,
        f"{PACKET_ROOT}/protocol-packet.json",
        f"{PACKET_ROOT}/protocol-packet.schema.json",
        f"{PACKET_ROOT}/protocol-evidence.json",
        CLOSEOUT,
        ACCEPTANCE,
        PREPLANNING,
        PRECOMMIT,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free unmounted status transaction-kernel protocol rehearsal",
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
                "This is an authored-synthetic, provider-free and unmounted protocol.",
                "No application route, database, provider, watcher, event or command executes.",
                "The prior live parent-source citation is corrected to an existing Git object without rewriting historical closeout evidence.",
            ],
        },
        "decisions": [
            {
                "id": "accept-unmounted-status-transaction-kernel-protocol",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept the closed status transaction protocol and keep all runtime authority closed.",
            }
        ],
        "claim_scope": [
            "Fifteen decision scenarios and eleven transaction schedules bind authority-first evaluation and exact status locking.",
            "All thirty-seven hostile mutations fail closed and only committed plans an effect.",
            "Mutation, audit and completed receipt commit or roll back together; response loss replays the original receipt.",
            "Terminal re-transition remains effect-free and policy-deferred.",
            "Nine focused, 106 dependency/API, 308 compatibility and canonical 191 fast-profile tests pass.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, DESIGN],
            "findings": [THREAT],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING, PRECOMMIT],
            "tests": [
                "tests/test_raisa_provider_free_unmounted_status_transaction_kernel_protocol_rehearsal.py",
                TEST,
            ],
            "artifacts": [
                f"{PACKET_ROOT}/protocol-packet.json",
                f"{PACKET_ROOT}/protocol-packet.schema.json",
                f"{PACKET_ROOT}/protocol-evidence.json",
                UPDATER,
            ],
        },
        "unresolved_gates": [
            "The provider-free unmounted status-confirm kernel adapter contract is next.",
            "Terminal-transition parity and post-commit receipt serialization must remain fail-closed in that pure contract.",
            "No status route imports or executes a kernel yet; raw status remains mounted and unchanged.",
            "Create schedule fencing, operational data, providers, deployment, Pages and protected refs remain closed.",
        ],
    }


def _correct_parent_source(graph: dict[str, Any]) -> None:
    parents = [node for node in graph["nodes"] if node["id"] == PARENT]
    if len(parents) != 1:
        raise SystemExit("Compatibility harness parent node missing")
    parent = parents[0]
    source_head = parent["coordinates"]["source_head"]
    if source_head == BAD_PARENT_SOURCE_HEAD:
        parent["coordinates"]["source_head"] = PARENT_SOURCE_HEAD
        parent["authority"]["notes"].append(
            "Live coordinate corrected from a nonexistent expanded SHA to the existing accepted Git object; historical evidence is unchanged."
        )
    elif source_head != PARENT_SOURCE_HEAD:
        raise SystemExit("Unexpected compatibility harness parent source")


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    _correct_parent_source(graph)
    if graph["graph_revision"] == 255 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 256
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 256 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected status protocol Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Freeze status transaction semantics before any adapter or runtime",
        "outcome": "The closed protocol proves authority, lock, replay and atomic receipt behavior without an effectful surface.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 237
        and compass["source_graph_revision"] == 255
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 238
        and compass["source_graph_revision"] == 256
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected status protocol Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Freeze the provider-free unmounted status-confirm kernel adapter contract.",
                "Preserve current fail-closed terminal-transition behavior until explicit policy acceptance.",
                "Keep every application route outside the adapter contract.",
                "Select and prove a database-owned create schedule fence before create convergence.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Status transaction semantics frozen; pure adapter contract next",
        "why_now": "Authority, locking, rollback and replay are closed before any route can depend on them.",
        "outcome": "Fifteen decisions, eleven schedules and thirty-seven hostile mutations prove the unmounted protocol.",
        "unlocks": [
            "Freeze the pure signed-confirmation-envelope to status-kernel transformation.",
            "Bind fail-closed terminal parity and post-commit receipt serialization without executing a route.",
        ],
        "does_not_solve": [
            "Status route integration, raw-route convergence or create schedule fencing.",
            "Operational data, providers, commands, deployment, Pages or protected refs.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 256 / Compass 238. The provider-free unmounted "
        "status transaction-kernel protocol passes; the pure status-confirm "
        "kernel adapter contract is next."
    )
    for limit in (
        "Protocol schedule success does not authorise an application route, database transaction or command.",
        "Terminal status re-transition remains policy-deferred and fail-closed.",
    ):
        if limit not in compass["map_limits"]:
            compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 256
    compass["map_revision"] = 238
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
