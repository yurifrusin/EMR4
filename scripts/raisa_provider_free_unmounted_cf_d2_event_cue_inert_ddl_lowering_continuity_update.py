"""Advance Continuity and Compass for the inert CF-D2 DDL lowering."""

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
NODE_ID = "raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering"
PARENT = "raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture"
SOURCE_HEAD = "cd890647d327a3d9bf4f60e5e1d6f9a1924bab29"
UPDATED_AT = "2026-08-13T08:45:10Z"
PLAN = "docs/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering-plan.md"
DESIGN = "docs/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering-design.md"
THREAT = "docs/security/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering-threat-model-delta.md"
BASE = "orchestration/continuity/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering/"
CONTRACT = BASE + "inert-ddl-contract.json"
CONTRACT_SCHEMA = BASE + "inert-ddl-contract.schema.json"
SQL = BASE + "event-cue-schema.sql.inert"
MANIFEST = BASE + "inert-ddl-manifest.json"
EVIDENCE = BASE + "provider-free-unmounted-inert-ddl-evidence.json"
RENDERER = "scripts/raisa_provider_free_unmounted_cf_d2_event_cue_inert_ddl_lowering.py"
TEST = "tests/test_raisa_provider_free_unmounted_cf_d2_event_cue_inert_ddl_lowering.py"
CONTINUITY_TEST = "tests/test_raisa_provider_free_unmounted_cf_d2_event_cue_inert_ddl_lowering_continuity.py"
UPDATER = "scripts/raisa_provider_free_unmounted_cf_d2_event_cue_inert_ddl_lowering_continuity_update.py"
CLOSEOUT = "docs/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-13--cf-d2-event-cue-inert-ddl-lowering.md"
RECEIPTS = [
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-preplanning-receipt.json",
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-preacceptance-receipt.json",
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-precommit-receipt.json",
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-prepush-receipt.json",
]


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN, DESIGN, THREAT, CONTRACT, CONTRACT_SCHEMA, SQL, MANIFEST, EVIDENCE,
        RENDERER, TEST, CLOSEOUT, ACCEPTANCE, MAILBOX, *RECEIPTS,
    ]


def _node() -> dict[str, Any]:
    contract_evidence = [PLAN, DESIGN, CONTRACT, SQL, MANIFEST, EVIDENCE, TEST, CLOSEOUT]
    return {
        "id": NODE_ID,
        "title": "Provider-free unmounted CF-D2 event and cue inert-DDL lowering",
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
                "The exact accepted seven-relation representation and its SHA-256 remain the authority boundary.",
                "One .sql.inert artifact proves deterministic structural text lowering only; PostgreSQL parse and catalogue admission remain unproved.",
                "No database/source, SQL execution, persistence, watcher, product data, provider, command, deployment or protected-ref authority was opened.",
            ],
        },
        "decisions": [{
            "id": "accept-unmounted-cf-d2-event-cue-inert-ddl-lowering",
            "source": ACCEPTANCE,
            "status": "accepted",
            "summary": "Accept exact byte-stable structural SQL text while leaving semantic, transaction and external-authority enforcement explicitly unlowered.",
        }],
        "claim_scope": [
            "Seven relations, fifty fields, seven primary keys, three unique keys, seven references and nineteen honest check dispositions are deterministically lowered.",
            "Two isolated renders are byte-identical and all sixty-five hostile text variants fail closed without changing canonical artifacts.",
            "One hundred forty-two focused lineage checks and the 193-test canonical fast profile pass.",
            "Events and cues remain acceleration hints; fresh scoped reads and command-time current-authority and source-truth checks remain mandatory.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": contract_evidence,
                "note": "The DDL admits no appointment, practitioner, patient, time, duration or intent payload and cannot mutate a proposal.",
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": contract_evidence,
                "note": "Reconciliation remains one fresh-read-attempt record and does not become projection truth, command evidence or future freshness.",
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [DESIGN, CONTRACT, SQL, MANIFEST, EVIDENCE],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": RECEIPTS,
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [CONTRACT_SCHEMA, RENDERER, UPDATER],
        },
        "unresolved_gates": [
            "PostgreSQL parsing, catalogue creation, constraint behavior, transactions and persistence remain unproved.",
            "Source observation, watcher ownership, restart, unknown commit, dispatch transport, retention and operations remain unproved.",
            "Product/patient data, provider, command/write, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 278 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 279
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 279 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected CF-D2 inert-DDL Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Make the accepted payload-free event/cue relations concrete as inert SQL text without claiming database behavior",
        "outcome": "Exact byte-stable PostgreSQL-16-shaped DDL text passes static admission; disposable parse/catalogue rehearsal is next but explicitly paused for Yuri's paper discussion.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 260
        and compass["source_graph_revision"] == 278
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 261
        and compass["source_graph_revision"] == 279
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected CF-D2 inert-DDL Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve source-owned truth and command-time current-authority checks as the correctness kernel.",
                "Preserve the accepted payload-free observability, admission, representation and inert-DDL contracts.",
                "After Yuri's explicit paper-review pause, admit only the exact inert artifact in a disposable PostgreSQL-16 parse/catalogue rehearsal.",
                "Keep transaction behavior, runtime wiring, product data and operational retention separately closed.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Inert SQL-text lowering passes; explicit pause before disposable parse/catalogue admission",
        "why_now": "The accepted abstract relations now have exact deterministic SQL text, and Yuri requested a brief pause to read and discuss 2509.26507v1.pdf before database contact.",
        "outcome": "Seven tables, fifty fields, exact structural constraints and sixty-five hostile rejections pass without SQL execution or database contact.",
        "unlocks": [
            "After the explicit pause is lifted, freeze a disposable PostgreSQL-16 parse-and-catalogue admission of the exact inert artifact.",
            "Verify exact types, tables, fields, constraints and references inside one isolated disposable server only.",
            "Keep transaction behavior, source access, persistence/runtime and product wiring closed.",
        ],
        "does_not_solve": [
            "PostgreSQL parse or catalogue acceptance, constraint behavior, transactions, source observation or persistent operational state.",
            "Watcher process ownership, restart, unknown commit, delivery transport, retention, rotation or performance.",
            "Product/patient data, external identity/channel delivery, provider access, commands, deployment, production or release.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 279 / Compass 261. The provider-free unmounted "
        "CF-D2 inert-DDL lowering passes one exact byte-stable PostgreSQL-16-shaped "
        "artifact and sixty-five hostile variants without database contact. Yuri "
        "requested an explicit pause before disposable parse/catalogue admission "
        "while Sol reads and discusses 2509.26507v1.pdf."
    )
    limit = "The CF-D2 inert DDL is static text evidence, not PostgreSQL parse, catalogue, constraint, transaction, persistence, restart or delivery proof."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 279
    compass["map_revision"] = 261
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
