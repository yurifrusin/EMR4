"""Advance Continuity and Compass for the CF-D2 serial transaction pass."""

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
    "raisa-provider-free-disposable-postgresql-cf-d2-event-cue-behavior-transaction-rehearsal"
)
PARENT = (
    "raisa-provider-free-disposable-postgresql-cf-d2-event-cue-parse-catalogue-rehearsal"
)
SOURCE_HEAD = "f4bd8ca5ec0654f8be7b1d2d74b1aca444038ee9"
UPDATED_AT = "2026-08-13T10:54:23Z"
PLAN = "docs/raisa-provider-free-disposable-postgresql-cf-d2-event-cue-behavior-transaction-rehearsal-plan.md"
DESIGN = "docs/raisa-provider-free-disposable-postgresql-cf-d2-event-cue-behavior-transaction-rehearsal-design.md"
THREAT = "docs/security/raisa-provider-free-disposable-postgresql-cf-d2-event-cue-behavior-transaction-rehearsal-threat-model-delta.md"
BASE = "orchestration/continuity/raisa-provider-free-disposable-postgresql-cf-d2-event-cue-behavior-transaction-rehearsal/"
CONTRACT = BASE + "rehearsal-contract.json"
CONTRACT_SCHEMA = BASE + "rehearsal-contract.schema.json"
EVIDENCE_SCHEMA = BASE + "provider-free-behavior-transaction-evidence.schema.json"
EVIDENCE = BASE + "provider-free-behavior-transaction-evidence.json"
HARNESS = "scripts/raisa_provider_free_disposable_postgresql_cf_d2_event_cue_behavior_transaction_rehearsal.py"
TEST = "tests/test_raisa_provider_free_disposable_postgresql_cf_d2_event_cue_behavior_transaction_rehearsal.py"
UPDATER = "scripts/raisa_provider_free_disposable_postgresql_cf_d2_event_cue_behavior_transaction_rehearsal_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_provider_free_disposable_postgresql_cf_d2_event_cue_behavior_transaction_rehearsal_continuity.py"
CLOSEOUT = "docs/raisa-provider-free-disposable-postgresql-cf-d2-event-cue-behavior-transaction-rehearsal-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-cf-d2-event-cue-behavior-transaction-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-13--cf-d2-event-cue-behavior-transaction-rehearsal.md"
RECEIPTS = [
    "orchestration/agent_inbox/codex/raisa-cf-d2-event-cue-behavior-transaction-postcompaction-preplanning-receipt.json",
    "orchestration/agent_inbox/codex/raisa-cf-d2-event-cue-behavior-transaction-candidate-precommit-receipt.json",
    "orchestration/agent_inbox/codex/raisa-cf-d2-event-cue-behavior-transaction-candidate-prepush-receipt.json",
    "orchestration/agent_inbox/codex/raisa-cf-d2-event-cue-behavior-transaction-preacceptance-receipt.json",
    "orchestration/agent_inbox/codex/raisa-cf-d2-event-cue-behavior-transaction-closeout-precommit-receipt.json",
]


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
        CONTRACT_SCHEMA,
        EVIDENCE_SCHEMA,
        EVIDENCE,
        HARNESS,
        TEST,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        *RECEIPTS,
    ]


def _node() -> dict[str, Any]:
    contract_evidence = [PLAN, DESIGN, CONTRACT, EVIDENCE, TEST, CLOSEOUT]
    return {
        "id": NODE_ID,
        "title": "Provider-free disposable PostgreSQL CF-D2 event and cue behavior/transaction rehearsal",
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
                "Only fixed authored-synthetic rows and the exact accepted artifact entered one owned networkless tmpfs PostgreSQL 16 server.",
                "The passing claim is limited to five fixed serial protocol effects, denials, rollback and uncontended lock footprints.",
                "Events and cues remain acceleration hints; source truth, fresh reads and command authority remain external.",
            ],
        },
        "decisions": [
            {
                "id": "accept-cf-d2-event-cue-disposable-postgresql-behavior-transaction",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept the fixed single-server serial proof for all five CF-D2 protocols without opening concurrency, runtime, source or product authority.",
            }
        ],
        "claim_scope": [
            "Six serial groups prove terminal admission, pending coalescing, contiguous checkpoint advance, dispatch recording and reconciliation.",
            "Three deliberately induced post-write failures restore identical canonical state digests.",
            "Eleven refused transitions preserve state and five protocols expose their required uncontended RowShareLock relation subsets.",
            "Sixty-four hostile contracts, 215 CF-D2/API/continuity tests and the 193-test canonical fast profile pass with exact cleanup.",
            "No real authority or fresh read occurred; events and cues remain non-authoritative refresh hints.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": contract_evidence,
                "note": "All rows remain payload-free authored-synthetic coordinates and cannot mutate an appointment or proposal.",
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": contract_evidence,
                "note": "Reconciliation records one typed synthetic read-attempt outcome and never becomes display truth, command evidence or future freshness.",
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [DESIGN, CONTRACT, EVIDENCE],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": RECEIPTS,
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [CONTRACT_SCHEMA, EVIDENCE_SCHEMA, HARNESS, UPDATER],
        },
        "unresolved_gates": [
            "Multi-session concurrency, contention, restart, crash and unknown-commit recovery remain unproved.",
            "Watcher/source access, real delivery, persistence, retention, rotation, purge, performance and product wiring remain unproved.",
            "Real authority/fresh reads, patient/product data, providers, commands/writes, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 280 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 281
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 281 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected CF-D2 behavior/transaction Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove the five accepted payload-free event/cue protocols as fixed serial PostgreSQL transactions without making durability the correctness kernel",
        "outcome": "All five serial transaction protocols, rollback probes and required uncontended lock footprints pass; read-only programme orientation is next.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 262
        and compass["source_graph_revision"] == 280
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 263
        and compass["source_graph_revision"] == 281
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected CF-D2 behavior/transaction Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve source-owned truth and command-time current-authority checks as the correctness kernel.",
                "Preserve the accepted CF-D2 observability, admission, representation, inert-DDL, parse/catalogue and serial behavior evidence.",
                "Run a fresh read-only post-CF-D2 Compass/baton orientation before selecting the next already-planned product tranche.",
                "Keep concurrency, restart, watcher/source access, persistence/runtime, product data and operational retention separately closed.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "The narrow CF-D2 serial database foundation passes without becoming source truth or command authority",
        "why_now": "All five accepted transaction protocols now have bounded real PostgreSQL behavior evidence, so the programme can reorient before choosing the next visible product tranche.",
        "outcome": "Six serial groups, three rollback probes, eleven non-mutating denials, five uncontended lock footprints and exact cleanup pass.",
        "unlocks": [
            "Run a read-only post-CF-D2 Compass and baton orientation.",
            "Identify the next dependency-satisfied Reception One or product tranche from accepted repository evidence.",
            "Retain the event mechanism as an optional acceleration layer over fresh source reads and conditional commands.",
        ],
        "does_not_solve": [
            "Concurrency, restart, crash, unknown commit, watcher ownership, source observation, delivery or operational retention.",
            "Real authority, real fresh reads, product/runtime wiring or patient/product data handling.",
            "External identity/channels, providers, commands, deployment, production or release.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 281 / Compass 263. CF-D2's five payload-free "
        "event/cue transaction protocols now pass fixed single-server serial "
        "PostgreSQL behavior, rollback and uncontended lock-footprint evidence. "
        "Source truth and command-time current-authority checks remain the "
        "correctness kernel. A read-only post-CF-D2 programme orientation is next."
    )
    obsolete = (
        "The CF-D2 PostgreSQL catalogue pass proves parse and empty structural shape only, not transaction behavior, persistence, restart, delivery or runtime authority."
    )
    if obsolete in compass["map_limits"]:
        compass["map_limits"].remove(obsolete)
    limit = (
        "The CF-D2 PostgreSQL behavior pass proves only fixed single-server serial transaction effects, rollback and uncontended lock footprints; concurrency, restart, source, runtime, delivery and product authority remain unproved."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 281
    compass["map_revision"] = 263
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
