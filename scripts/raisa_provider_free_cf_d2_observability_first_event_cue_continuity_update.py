"""Advance Continuity and Compass for CF-D2 observable durable cues."""

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
NODE_ID = "raisa-provider-free-cf-d2-observability-first-event-cue"
PARENT = "raisa-provider-free-visible-native-diary-status-confirm-wiring"
PROTECTED_DIRECTION = (
    "raisa-context-fabric-source-owned-truth-conditional-command-reorientation"
)
SOURCE_HEAD = "e8677b54d1c339dcd14776ce8bf15e7db2980378"
UPDATED_AT = "2026-08-13T06:26:12Z"
PLAN = "docs/raisa-provider-free-cf-d2-observability-first-event-cue-plan.md"
ARCHITECTURE = (
    "docs/raisa-provider-free-cf-d2-observability-first-event-cue-architecture.md"
)
THREAT = (
    "docs/security/"
    "raisa-provider-free-cf-d2-observability-first-event-cue-threat-model-delta.md"
)
API_SPINE = "docs/api-spine/async/durable-diary-event-cue-observability.yaml"
BASE = (
    "orchestration/continuity/"
    "raisa-provider-free-cf-d2-observability-first-event-cue/"
)
CONTRACT = BASE + "observability-contract.json"
CONTRACT_SCHEMA = BASE + "observability-contract.schema.json"
ACCEPTANCE_SCRIPT = (
    "scripts/raisa_provider_free_cf_d2_observability_first_event_cue_acceptance.py"
)
TEST = "tests/test_raisa_provider_free_cf_d2_observability_first_event_cue.py"
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_cf_d2_observability_first_event_cue_continuity.py"
)
UPDATER = (
    "scripts/raisa_provider_free_cf_d2_observability_first_event_cue_continuity_update.py"
)
CLOSEOUT = (
    "docs/raisa-provider-free-cf-d2-observability-first-event-cue-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-cf-d2-observability-first-event-cue-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-13--cf-d2-observability-first-event-cue-architecture.md"
)
RECEIPTS = [
    "orchestration/agent_inbox/codex/raisa-cf-d2-observability-first-plan-preplanning-receipt.json",
    "orchestration/agent_inbox/codex/raisa-cf-d2-observability-first-plan-preacceptance-receipt.json",
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
        API_SPINE,
        CONTRACT,
        CONTRACT_SCHEMA,
        ACCEPTANCE_SCRIPT,
        TEST,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        *RECEIPTS,
    ]


def _node() -> dict[str, Any]:
    contract_evidence = [PLAN, ARCHITECTURE, CONTRACT, TEST, CLOSEOUT]
    return {
        "id": NODE_ID,
        "title": "Provider-free CF-D2 observability-first event and cue architecture",
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
        "relationships": [
            {"node_id": PARENT, "relation": "builds_on"},
            {"node_id": PROTECTED_DIRECTION, "relation": "protects"},
        ],
        "authority": {
            "authorized_openings": [],
            "notes": [
                "Source services retain current truth and commands retain current-authority and source-truth checks.",
                "A durable cue is a payload-free refresh obligation and never command evidence, confirmation or appointment truth.",
                "No watcher, database/source, persistence, product data, provider, route, command, deployment or protected-ref authority was opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-cf-d2-observability-first-event-cue-architecture",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept the smallest independently observable durable refresh-obligation contract before any runtime rehearsal.",
            }
        ],
        "claim_scope": [
            "Partition, opaque source coordinate, terminal classification receipt, checkpoint, cue obligation, dispatch and reconciliation are separate facts.",
            "Checkpoint advancement requires contiguous terminal receipts and atomic creation of every required cue obligation; delivery is a separate backlog.",
            "Ten diagnostic stages retain mutually distinct payload-free operator evidence and safe responses.",
            "All 39 hostile mutations, 114 focused tests and the 193-test canonical fast profile pass without runtime, database, provider or product/patient data.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": contract_evidence,
                "note": "The payload-free cue cannot replace or mutate the accepted combined appointment intent; the consumer must freshly read its authoritative projection.",
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": contract_evidence,
                "note": "Event and cue delivery remain acceleration hints; reconciliation uses a fresh scoped read and preserves the existing selection/proposal rules.",
            },
        ],
        "evidence": {
            "plans": [PLAN, ARCHITECTURE, THREAT],
            "findings": [CONTRACT],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": RECEIPTS,
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [
                API_SPINE,
                CONTRACT_SCHEMA,
                ACCEPTANCE_SCRIPT,
                UPDATER,
            ],
        },
        "unresolved_gates": [
            "PostgreSQL representation, persistence, source observation, restart, unknown commit and delivery remain unproved.",
            "The next gate is a pure provider-free unmounted admission rehearsal over authored-synthetic state sequences only.",
            "Watcher/database/source, operational retention, product/patient data, provider, command/write, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 275 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 276
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 276 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected CF-D2 observability Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Make durable refresh acceleration small, observable and non-authoritative",
        "outcome": "A payload-free cue obligation and ten-stage diagnostic contract pass; pure unmounted state admission is next.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 257
        and compass["source_graph_revision"] == 275
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 258
        and compass["source_graph_revision"] == 276
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected CF-D2 observability Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve source-owned truth and command-time current-authority checks as the correctness kernel.",
                "Preserve the accepted payload-free refresh-obligation and ten-stage observability contract.",
                "Exercise only pure authored-synthetic state admission before considering any persistence or watcher runtime.",
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
        "strategic_role": "Observable payload-free durable cue architecture accepted; pure state admission next",
        "why_now": "The visible Diary consumer identifies the refresh need, while the smaller contract separates every durable handoff before any restart or database proof.",
        "outcome": "Durability is limited to a payload-free refresh obligation; source truth, command authority, checkpoint, delivery and reconciliation remain distinct.",
        "unlocks": [
            "Run the provider-free unmounted event/cue admission rehearsal against the exact accepted contract.",
            "Prove duplicate, gap, checkpoint, coalescing, fencing and reconciliation admission with authored-synthetic state only.",
            "Use the ten diagnostic stages to fail closed without starting a watcher or opening a database/source.",
        ],
        "does_not_solve": [
            "PostgreSQL representation, durable persistence, source observation or a watcher process.",
            "Restart, unknown-commit, dispatch transport, latency, retention, rotation or operational delivery.",
            "Product/patient data, external identity/channel delivery, provider access, commands, deployment, production or release.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 276 / Compass 258. The provider-free CF-D2 "
        "observability-first architecture accepts only a payload-free durable refresh "
        "obligation, with ten distinct diagnostic stages and source/command authority "
        "preserved. The next safe gate is a pure unmounted admission rehearsal; no "
        "watcher, database/source or product-data authority is open."
    )
    limit = (
        "CF-D2 observability evidence is an architecture-only closed-contract proof; it does not prove persistence, restart, unknown commit, source observation or cue delivery."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 276
    compass["map_revision"] = 258
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
