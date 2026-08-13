"""Advance Continuity and Compass for CF-D2 event/cue catalogue admission."""

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
    "raisa-provider-free-disposable-postgresql-cf-d2-event-cue-parse-catalogue-rehearsal"
)
PARENT = "raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering"
SOURCE_HEAD = "579e9e0e86bd92469d82eb1199e8b3120808844e"
UPDATED_AT = "2026-08-13T09:56:16Z"
PLAN = "docs/raisa-provider-free-disposable-postgresql-cf-d2-event-cue-parse-catalogue-rehearsal-plan.md"
DESIGN = "docs/raisa-provider-free-disposable-postgresql-cf-d2-event-cue-parse-catalogue-rehearsal-design.md"
THREAT = "docs/security/raisa-provider-free-disposable-postgresql-cf-d2-event-cue-parse-catalogue-rehearsal-threat-model-delta.md"
BASE = "orchestration/continuity/raisa-provider-free-disposable-postgresql-cf-d2-event-cue-parse-catalogue-rehearsal/"
CONTRACT = BASE + "rehearsal-contract.json"
CONTRACT_SCHEMA = BASE + "rehearsal-contract.schema.json"
EVIDENCE_SCHEMA = BASE + "provider-free-parse-catalogue-evidence.schema.json"
FAILURE = BASE + "provider-free-parse-catalogue-failure-evidence.json"
EVIDENCE = BASE + "provider-free-parse-catalogue-evidence.json"
HARNESS = "scripts/raisa_provider_free_disposable_postgresql_cf_d2_event_cue_parse_catalogue_rehearsal.py"
TEST = "tests/test_raisa_provider_free_disposable_postgresql_cf_d2_event_cue_parse_catalogue_rehearsal.py"
CONTINUITY_TEST = "tests/test_raisa_provider_free_disposable_postgresql_cf_d2_event_cue_parse_catalogue_rehearsal_continuity.py"
UPDATER = "scripts/raisa_provider_free_disposable_postgresql_cf_d2_event_cue_parse_catalogue_rehearsal_continuity_update.py"
INCIDENT = "docs/ariadne-agent-error-correction-register-revision-260.md"
CLOSEOUT = "docs/raisa-provider-free-disposable-postgresql-cf-d2-event-cue-parse-catalogue-rehearsal-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-cf-d2-event-cue-parse-catalogue-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-13--cf-d2-event-cue-parse-catalogue-rehearsal.md"
RECEIPTS = [
    "orchestration/agent_inbox/codex/raisa-cf-d2-event-cue-parse-catalogue-resumption-postcompaction-receipt.json",
    "orchestration/agent_inbox/codex/raisa-cf-d2-event-cue-parse-catalogue-candidate-precommit-receipt.json",
    "orchestration/agent_inbox/codex/raisa-cf-d2-event-cue-parse-catalogue-candidate-prepush-receipt.json",
    "orchestration/agent_inbox/codex/raisa-cf-d2-event-cue-parse-catalogue-closeout-precommit-receipt.json",
]
NOT_YET_EMITTED_RECEIPTS = {
    "orchestration/agent_inbox/codex/raisa-cf-d2-event-cue-parse-catalogue-closeout-prepush-receipt.json",
}


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
        FAILURE,
        EVIDENCE,
        HARNESS,
        TEST,
        INCIDENT,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        *RECEIPTS,
    ]


def _node() -> dict[str, Any]:
    contract_evidence = [
        PLAN,
        DESIGN,
        CONTRACT,
        FAILURE,
        EVIDENCE,
        TEST,
        CLOSEOUT,
    ]
    return {
        "id": NODE_ID,
        "title": "Provider-free disposable PostgreSQL CF-D2 event and cue parse/catalogue rehearsal",
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
                "Only the exact accepted 12,022-byte artifact entered one owned networkless tmpfs PostgreSQL 16 container.",
                "The passing claim is limited to parse, exact empty catalogue shape and verified cleanup.",
                "Events and cues remain acceleration hints; database/source runtime, transaction protocols and product authority remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-cf-d2-event-cue-disposable-postgresql-parse-catalogue",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept exact PostgreSQL 16 parse and empty catalogue admission while preserving all five transaction protocols as separately unproved.",
            }
        ],
        "claim_scope": [
            "Three domains, seven tables, fifty fields, seven primary keys, three unique keys, eighteen table checks and seven foreign keys match exactly.",
            "All seven relations contain zero rows and no function, trigger, view, sequence, policy, rule, row-security table or explicit object ACL was added.",
            "Attempt 001 stopped before artifact execution at a readiness race and cleaned up; AER-0293 precedes passing fresh attempt 002.",
            "Sixty-four hostile contracts, focused/register/lineage gates and the 193-test canonical fast profile pass.",
            "Events and cues remain non-authoritative refresh hints; fresh source reads and command-time authority/truth checks remain mandatory.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": contract_evidence,
                "note": "The empty catalogue contains no appointment, practitioner, patient, time, duration or intent payload and cannot mutate a proposal.",
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": contract_evidence,
                "note": "The reconciliation relation is empty structural evidence only and cannot become projection truth, command evidence or future freshness.",
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [DESIGN, CONTRACT, FAILURE, EVIDENCE, INCIDENT],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": RECEIPTS,
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [CONTRACT_SCHEMA, EVIDENCE_SCHEMA, HARNESS, UPDATER],
        },
        "unresolved_gates": [
            "Terminal admission, pending coalescing, contiguous checkpoint advance, dispatch recording and reconciliation transaction behavior remain unproved.",
            "Concurrency, restart, unknown commit, watcher/source access, persistence, delivery, retention and product wiring remain unproved.",
            "Patient/product data, provider, command/write, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 279 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 280
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 280 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected CF-D2 parse/catalogue Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove the exact payload-free event/cue schema is physically representable in PostgreSQL 16 without opening a runtime",
        "outcome": "Exact parse, catalogue census, zero rows and cleanup pass; the five behavior/transaction protocols are the next separately frozen candidate.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 261
        and compass["source_graph_revision"] == 279
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 262
        and compass["source_graph_revision"] == 280
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected CF-D2 parse/catalogue Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve source-owned truth and command-time current-authority checks as the correctness kernel.",
                "Preserve the accepted observability, admission, representation, inert-DDL and disposable parse/catalogue evidence.",
                "Freeze the narrowest provider-free disposable behavior/transaction scenarios for only the five existing CF-D2 protocols.",
                "Keep concurrency, restart, watcher/source access, persistence/runtime, product data and operational retention separately closed.",
            ]
            horizon["evidence"] = [
                item
                for item in horizon["evidence"]
                if item not in NOT_YET_EMITTED_RECEIPTS
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Exact event/cue PostgreSQL 16 parse and empty catalogue admission passes",
        "why_now": "The inert schema has crossed the narrow database representability boundary without opening runtime, source or product authority.",
        "outcome": "Three domains, seven tables, fifty fields and all exact structural constraints catalogue correctly with zero rows and verified cleanup.",
        "unlocks": [
            "Freeze a provider-free disposable behavior/transaction rehearsal for the five already accepted CF-D2 protocols.",
            "Exercise only authored-synthetic rows and exact lock, rollback and effect observations inside a newly owned disposable server.",
            "Keep concurrency, restart, watcher/source access, persistence/runtime and product wiring separately closed.",
        ],
        "does_not_solve": [
            "Terminal admission, coalescing, checkpoint, dispatch or reconciliation behavior and atomicity.",
            "Concurrency, restart, unknown commit, delivery, watcher ownership, retention, rotation, purge or performance.",
            "Product/patient data, external identity/channel delivery, provider access, commands, deployment, production or release.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 280 / Compass 262. The exact provider-free CF-D2 "
        "event/cue artifact parses and catalogues in PostgreSQL 16 as three "
        "domains, seven empty tables and the frozen constraints, with a preserved "
        "readiness-race correction and exact cleanup. The next candidate is a "
        "separately frozen behavior/transaction rehearsal for the five existing protocols."
    )
    obsolete_limit = (
        "The CF-D2 inert DDL is static text evidence, not PostgreSQL parse, catalogue, constraint, transaction, persistence, restart or delivery proof."
    )
    if obsolete_limit in compass["map_limits"]:
        compass["map_limits"].remove(obsolete_limit)
    limit = (
        "The CF-D2 PostgreSQL catalogue pass proves parse and empty structural shape only, not transaction behavior, persistence, restart, delivery or runtime authority."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 280
    compass["map_revision"] = 262
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
