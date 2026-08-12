"""Advance Continuity and Compass for the unmounted status-confirm adapter."""

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
NODE_ID = "raisa-provider-free-unmounted-status-confirm-kernel-adapter-contract"
PARENT = "raisa-provider-free-unmounted-status-transaction-kernel-protocol-rehearsal"
SOURCE_HEAD = "30a49015d23bfcf069be0af838df7091032a40be"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = "docs/raisa-provider-free-unmounted-status-confirm-kernel-adapter-contract-plan.md"
DESIGN = "docs/raisa-provider-free-unmounted-status-confirm-kernel-adapter-contract-design.md"
THREAT = "docs/security/raisa-provider-free-unmounted-status-confirm-kernel-adapter-contract-threat-model-delta.md"
CLOSEOUT = "docs/raisa-provider-free-unmounted-status-confirm-kernel-adapter-contract-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-status-confirm-kernel-adapter-contract-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-12--status-confirm-kernel-adapter-contract.md"
PACKET_ROOT = "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-kernel-adapter-contract"
PREPLANNING = "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-confirm-kernel-adapter-contract-preplanning-receipt.json"
PRECOMMIT = "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-confirm-kernel-adapter-contract-precommit-receipt.json"
TEST = "tests/test_raisa_provider_free_unmounted_status_confirm_kernel_adapter_contract_continuity.py"
UPDATER = "scripts/raisa_provider_free_unmounted_status_confirm_kernel_adapter_contract_continuity_update.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    rendered = json.dumps(value, indent=2, ensure_ascii=False)
    path.write_bytes((rendered + "\n").encode("utf-8"))


def _evidence() -> list[str]:
    return [
        PLAN,
        DESIGN,
        THREAT,
        f"{PACKET_ROOT}/adapter-contract.json",
        f"{PACKET_ROOT}/adapter-contract.schema.json",
        f"{PACKET_ROOT}/adapter-evidence.json",
        CLOSEOUT,
        ACCEPTANCE,
        PREPLANNING,
        PRECOMMIT,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free unmounted status-confirm kernel adapter contract",
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
                "This is an authored-synthetic, provider-free and unmounted pure adapter contract.",
                "It imports or executes no application route, database, provider, watcher, event or command.",
                "AER-0291 is contained; protected-scope content was discarded and contributes no evidence.",
            ],
        },
        "decisions": [
            {
                "id": "accept-unmounted-status-confirm-kernel-adapter-contract",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept the status-only adapter and keep every runtime surface closed.",
            }
        ],
        "claim_scope": [
            "Fifteen admission cases admit only update_appointment_status and stop the waiting-area union variant.",
            "Eight mappings bind shared kernel outcomes to typed route results without inventing policy.",
            "All thirty-seven hostile mutations fail closed before a kernel request can be emitted.",
            "Current authority and state are server-owned; signed evidence, freshness and warnings bind exactly.",
            "Committed and replay outcomes serialize from one canonical stored receipt without another request.",
            "Eleven focused, 59 dependency/API and canonical 191 fast-profile tests pass.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, DESIGN],
            "findings": [THREAT],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING, PRECOMMIT],
            "tests": [
                "tests/test_raisa_provider_free_unmounted_status_confirm_kernel_adapter_contract.py",
                TEST,
            ],
            "artifacts": [
                f"{PACKET_ROOT}/adapter-contract.json",
                f"{PACKET_ROOT}/adapter-contract.schema.json",
                f"{PACKET_ROOT}/adapter-evidence.json",
                UPDATER,
            ],
        },
        "unresolved_gates": [
            "A provider-free read-only status-confirm runtime-gap admission review is next.",
            "Lock order, server session ingress, terminal behavior and stored-receipt delivery remain unmounted review questions.",
            "The review may inspect exact non-protected files but may not edit or execute the route or database.",
            "Create schedule fencing, operational data, providers, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 256 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 257
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 257 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected status-confirm adapter Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Freeze the pure status-confirm boundary before runtime admission",
        "outcome": "The adapter proves exact authority-first input and stored-receipt output mappings without executing an effect.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 238
        and compass["source_graph_revision"] == 256
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 239
        and compass["source_graph_revision"] == 257
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected status-confirm adapter Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Run the provider-free read-only status-confirm runtime-gap admission review.",
                "Inspect only exact non-protected lock, session, terminal and receipt-delivery sources.",
                "Keep the status route and database unedited and unexecuted during review.",
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
        "strategic_role": "Pure status-confirm adapter frozen; read-only runtime-gap review next",
        "why_now": "The route/kernel seam can now be assessed against an exact effect-free transformation.",
        "outcome": "Fifteen cases, eight mappings and thirty-seven hostile mutations prove the closed adapter contract.",
        "unlocks": [
            "Inspect exact lock-order and server-session ingress gaps without executing the route.",
            "Assess terminal-policy parity and stored-receipt delivery prerequisites before runtime planning.",
        ],
        "does_not_solve": [
            "Status route integration, database execution, raw-route convergence or create schedule fencing.",
            "Operational data, providers, commands, deployment, Pages or protected refs.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 257 / Compass 239. The provider-free unmounted "
        "status-confirm kernel adapter contract passes; the read-only runtime-gap "
        "admission review is next."
    )
    for limit in (
        "Adapter success does not authorise an application route, database transaction or command.",
        "Waiting-area union input and terminal status re-transition remain fail-closed.",
    ):
        if limit not in compass["map_limits"]:
            compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 257
    compass["map_revision"] = 239
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
