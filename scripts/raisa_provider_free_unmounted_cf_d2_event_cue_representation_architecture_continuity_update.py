"""Advance Continuity and Compass for the inert CF-D2 representation."""

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
NODE_ID = "raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture"
PARENT = "raisa-provider-free-unmounted-cf-d2-event-cue-admission-rehearsal"
SOURCE_HEAD = "16ec7993ee3c46d83772f47aa7dab61fc1fcb7ed"
UPDATED_AT = "2026-08-13T07:46:24Z"
PLAN = "docs/raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture-plan.md"
ARCHITECTURE = "docs/raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture.md"
THREAT = (
    "docs/security/"
    "raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture-threat-model-delta.md"
)
BASE = (
    "orchestration/continuity/"
    "raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture/"
)
CONTRACT = BASE + "representation-contract.json"
CONTRACT_SCHEMA = BASE + "representation-contract.schema.json"
EVIDENCE = BASE + "provider-free-unmounted-representation-evidence.json"
CHECKER = (
    "scripts/"
    "raisa_provider_free_unmounted_cf_d2_event_cue_representation_architecture.py"
)
TEST = (
    "tests/"
    "test_raisa_provider_free_unmounted_cf_d2_event_cue_representation_architecture.py"
)
CONTINUITY_TEST = (
    "tests/"
    "test_raisa_provider_free_unmounted_cf_d2_event_cue_representation_architecture_continuity.py"
)
UPDATER = (
    "scripts/"
    "raisa_provider_free_unmounted_cf_d2_event_cue_representation_architecture_continuity_update.py"
)
CLOSEOUT = (
    "docs/"
    "raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-provider-free-unmounted-cf-d2-event-cue-representation-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-13--cf-d2-unmounted-event-cue-representation-architecture.md"
)
RECEIPTS = [
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-cf-d2-event-cue-representation-preplanning-receipt.json",
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-cf-d2-event-cue-representation-precommit-receipt.json",
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-cf-d2-event-cue-representation-preacceptance-receipt.json",
]


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
        CONTRACT_SCHEMA,
        EVIDENCE,
        CHECKER,
        TEST,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        *RECEIPTS,
    ]


def _node() -> dict[str, Any]:
    contract_evidence = [PLAN, ARCHITECTURE, CONTRACT, EVIDENCE, TEST, CLOSEOUT]
    return {
        "id": NODE_ID,
        "title": "Provider-free unmounted CF-D2 event and cue representation architecture",
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
        "relationships": [{"node_id": PARENT, "relation": "implements"}],
        "authority": {
            "authorized_openings": [],
            "notes": [
                "The exact accepted observability and admission contracts remain the authority boundary.",
                "Seven abstract relations prove inert representability only; five transaction protocols remain unexecuted.",
                "No SQL, database/source, persistence, watcher, product data, provider, command, deployment or protected-ref authority was opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-unmounted-cf-d2-event-cue-representation-architecture",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept the smallest payload-free relational representation while keeping transaction enforcement and source truth explicitly separate.",
            }
        ],
        "claim_scope": [
            "Seven exact relation shapes and five future transaction protocols cover the accepted event/cue facts without a generic payload column.",
            "Twelve authored-synthetic row families pass and eighty hostile contract or row variants fail closed without changing canonical inputs.",
            "Ninety-two focused lineage checks and the 193-test canonical fast profile pass.",
            "Events and cues remain acceleration hints; fresh scoped reads and command-time current-authority and source-truth checks remain mandatory.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": contract_evidence,
                "note": "The representation admits no appointment, practitioner, patient, time, duration or intent payload and cannot mutate a proposal.",
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": contract_evidence,
                "note": "A reconciliation receipt represents one typed fresh-read attempt only and cannot supply projection truth or future freshness.",
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [ARCHITECTURE, CONTRACT, EVIDENCE],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": RECEIPTS,
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [CONTRACT_SCHEMA, CHECKER, UPDATER],
        },
        "unresolved_gates": [
            "SQL lowering, PostgreSQL catalogue admission, transactions and persistence remain unproved.",
            "Source observation, watcher ownership, restart, unknown commit, dispatch transport, retention and operations remain unproved.",
            "Product/patient data, provider, command/write, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 277 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 278
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 278 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected CF-D2 representation Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Give accepted durable-cue facts a minimal relational home before SQL or runtime machinery",
        "outcome": "Seven payload-free relations and five explicitly unproved transaction protocols pass inert representability; SQL-text lowering is next.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 259
        and compass["source_graph_revision"] == 277
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 260
        and compass["source_graph_revision"] == 278
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected CF-D2 representation Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve source-owned truth and command-time current-authority checks as the correctness kernel.",
                "Preserve the accepted payload-free observability, admission and seven-relation representation contracts.",
                "Lower the exact representation into inert deterministic SQL text before any database contact.",
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
        "strategic_role": "Inert relational representation passes; exact SQL-text lowering next",
        "why_now": "The accepted state transitions now have a closed payload-free relational home and explicit enforcement classes, so SQL structure can be judged without inventing behavior.",
        "outcome": "Seven exact relations, five future transaction protocols, twelve row families and eighty hostile variants pass without SQL or database contact.",
        "unlocks": [
            "Freeze the smallest provider-free unmounted inert-DDL lowering of the exact seven relations.",
            "Render deterministic SQL text and verify complete structural coverage only.",
            "Keep database connection, migration execution, source access, persistence and watcher runtime closed.",
        ],
        "does_not_solve": [
            "PostgreSQL parsing, catalogue admission, transaction behavior, source observation or persistent operational state.",
            "Watcher process ownership, restart, unknown commit, delivery transport, retention, rotation or performance.",
            "Product/patient data, external identity/channel delivery, provider access, commands, deployment, production or release.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 278 / Compass 260. The provider-free unmounted "
        "CF-D2 representation architecture passes seven payload-free relations, "
        "five explicit future transaction protocols, twelve row families and "
        "eighty hostile variants. The next safe gate is exact inert SQL-text "
        "lowering; no database, watcher, persistence or product-data authority is open."
    )
    limit = (
        "The CF-D2 representation is inert abstract row evidence, not SQL, PostgreSQL, transaction, persistence, restart or delivery proof."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 278
    compass["map_revision"] = 260
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
