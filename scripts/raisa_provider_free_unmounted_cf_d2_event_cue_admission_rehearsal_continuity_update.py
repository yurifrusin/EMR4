"""Advance Continuity and Compass for the unmounted CF-D2 admission rehearsal."""

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
NODE_ID = "raisa-provider-free-unmounted-cf-d2-event-cue-admission-rehearsal"
PARENT = "raisa-provider-free-cf-d2-observability-first-event-cue"
SOURCE_HEAD = "a7c6f7a66b06fbc065ae8a6eede7fa8baaee1b6b"
UPDATED_AT = "2026-08-13T07:00:06Z"
PLAN = "docs/raisa-provider-free-unmounted-cf-d2-event-cue-admission-rehearsal-plan.md"
THREAT = (
    "docs/security/"
    "raisa-provider-free-unmounted-cf-d2-event-cue-admission-rehearsal-threat-model-delta.md"
)
BASE = (
    "orchestration/continuity/"
    "raisa-provider-free-unmounted-cf-d2-event-cue-admission-rehearsal/"
)
CONTRACT = BASE + "admission-contract.json"
CONTRACT_SCHEMA = BASE + "admission-contract.schema.json"
EVIDENCE = BASE + "provider-free-unmounted-admission-evidence.json"
REHEARSAL = (
    "scripts/raisa_provider_free_unmounted_cf_d2_event_cue_admission_rehearsal.py"
)
TEST = "tests/test_raisa_provider_free_unmounted_cf_d2_event_cue_admission_rehearsal.py"
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_cf_d2_event_cue_admission_rehearsal_continuity.py"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_cf_d2_event_cue_admission_rehearsal_continuity_update.py"
)
CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-cf-d2-event-cue-admission-rehearsal-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-provider-free-unmounted-cf-d2-event-cue-admission-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-13--cf-d2-unmounted-event-cue-admission-rehearsal.md"
)
RECEIPTS = [
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-cf-d2-event-cue-admission-preplanning-receipt.json",
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-cf-d2-event-cue-admission-preacceptance-receipt.json",
]


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        CONTRACT,
        CONTRACT_SCHEMA,
        EVIDENCE,
        REHEARSAL,
        TEST,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        *RECEIPTS,
    ]


def _node() -> dict[str, Any]:
    contract_evidence = [PLAN, CONTRACT, EVIDENCE, TEST, CLOSEOUT]
    return {
        "id": NODE_ID,
        "title": "Provider-free unmounted CF-D2 event and cue admission rehearsal",
        "kind": "implementation",
        "status": "accepted",
        "created_at": UPDATED_AT,
        "updated_at": UPDATED_AT,
        "coordinates": {
            "git_ref": "codex/ariadne-bernie-davida-parallel-seam",
            "source_head": SOURCE_HEAD,
            "thread_id": None,
            "worktree_role": "task",
        },
        "relationships": [{"node_id": PARENT, "relation": "implements"}],
        "authority": {
            "authorized_openings": [],
            "notes": [
                "The exact accepted observability architecture remains the authority boundary.",
                "The state machine is ephemeral and pure; repository evidence is not operational persistence.",
                "No watcher, database/source, persistence, product data, provider, route, command, deployment or protected-ref authority was opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-unmounted-cf-d2-event-cue-admission-rehearsal",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept exact pure admission behavior for durable refresh cues before relational representation or runtime.",
            }
        ],
        "claim_scope": [
            "Twenty-two canonical authored-synthetic state sequences pass for duplicate reuse, conflict, gaps, checkpointing, coalescing, fencing, lag and reconciliation.",
            "All sixty hostile contract and candidate variants fail closed; every denied hostile candidate preserves the complete normalized state digest.",
            "Ninety-one focused lineage checks and the 193-test canonical fast profile pass.",
            "Events and cues remain non-authoritative acceleration hints; fresh scoped reads and command-time rechecks remain mandatory.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": contract_evidence,
                "note": "The payload-free state machine contains no appointment identity or intent fields and cannot mutate the accepted combined appointment proposal.",
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": contract_evidence,
                "note": "A delivered cue can record only a typed fresh-read reconciliation; it cannot supply authoritative projection values or future freshness.",
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [CONTRACT, EVIDENCE],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": RECEIPTS,
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [CONTRACT, CONTRACT_SCHEMA, REHEARSAL, UPDATER],
        },
        "unresolved_gates": [
            "Relational representation, transactions, database/source access and persistence remain unproved.",
            "Watcher ownership, restart, unknown commit, dispatch transport, retention and operations remain unproved.",
            "Product/patient data, provider, command/write, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 276 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 277
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 277 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected unmounted admission Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove durable cue admission semantics before choosing storage machinery",
        "outcome": "Pure duplicate, gap, checkpoint, coalescing, fencing, lag and fresh-read reconciliation behavior passes; inert representation architecture is next.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 258
        and compass["source_graph_revision"] == 276
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 259
        and compass["source_graph_revision"] == 277
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected unmounted admission Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve source-owned truth and command-time current-authority checks as the correctness kernel.",
                "Preserve the accepted payload-free observability and pure admission transitions.",
                "Specify an inert relational representation before considering a database connection or migration execution.",
                "Keep future patient channels behind the accepted identity, assurance, recovery, projection and confirmation foundation.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Pure durable-cue admission passes; inert relational representation next",
        "why_now": "The state transitions are now independently executable and fail closed, so representation can be judged against stable semantics rather than driving them.",
        "outcome": "Duplicate identity, gaps, atomic obligation admission, checkpointing, coalescing, fencing, lag and reconciliation have exact provider-free behavior.",
        "unlocks": [
            "Freeze the smallest provider-free unmounted event/cue representation architecture.",
            "Map only the accepted partition, receipt, obligation, checkpoint, dispatch and reconciliation facts into an inert relational design.",
            "Use deterministic representability checks without opening a database connection, migration or watcher.",
        ],
        "does_not_solve": [
            "PostgreSQL admission, transactions, source observation or persistent operational state.",
            "Watcher process ownership, restart, unknown commit, delivery transport, retention, rotation or performance.",
            "Product/patient data, external identity/channel delivery, provider access, commands, deployment, production or release.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 277 / Compass 259. The provider-free unmounted "
        "CF-D2 event/cue admission rehearsal passes 22 canonical scenarios and "
        "rejects 60 hostile variants without state drift. The next safe gate is "
        "an inert relational representation architecture; no database, watcher, "
        "persistence or product-data authority is open."
    )
    limit = (
        "The CF-D2 admission state machine is ephemeral repository evidence, not operational persistence, restart, delivery or database proof."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 277
    compass["map_revision"] = 259
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
