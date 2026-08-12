"""Advance Continuity and Compass for the shadow-comparison rehearsal."""

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
    "raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal"
)
PARENT = "raisa-provider-free-unmounted-default-off-shadow-comparison-architecture"
SOURCE_HEAD = "47b5f09ecf35225da25812ba87bb656a1094fc7e"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = "docs/raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal-plan.md"
DESIGN = "docs/raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal-design.md"
THREAT = "docs/security/raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal-threat-model-delta.md"
PACKET_DIR = "orchestration/continuity/raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal/"
EVIDENCE = PACKET_DIR + "provider-free-authored-synthetic-shadow-comparison-evidence.json"
SCHEMA = PACKET_DIR + "provider-free-authored-synthetic-shadow-comparison-evidence.schema.json"
CLOSEOUT = "docs/raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-authored-synthetic-shadow-comparison-rehearsal-sol-acceptance.md"
PREPLANNING_RECEIPT = "orchestration/agent_inbox/codex/raisa-authored-synthetic-shadow-comparison-rehearsal-preplanning-receipt.json"
PRECOMMIT_RECEIPT = "orchestration/agent_inbox/codex/raisa-authored-synthetic-shadow-comparison-rehearsal-candidate-precommit-receipt.json"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-12--authored-synthetic-shadow-comparison-rehearsal.md"
TEST = "tests/test_raisa_provider_free_unmounted_authored_synthetic_shadow_comparison_rehearsal_continuity.py"
UPDATER = "scripts/raisa_provider_free_unmounted_authored_synthetic_shadow_comparison_rehearsal_continuity_update.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        DESIGN,
        THREAT,
        EVIDENCE,
        SCHEMA,
        CLOSEOUT,
        ACCEPTANCE,
        PREPLANNING_RECEIPT,
        PRECOMMIT_RECEIPT,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free unmounted authored-synthetic shadow-comparison rehearsal",
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
                "This is provider-free, unmounted and authored-synthetic evidence.",
                "It imports or executes no application route and creates no observer runtime.",
                "Diagnostic loss is permitted; no shadow result has command, audit or response authority.",
            ],
        },
        "decisions": [
            {
                "id": "accept-authored-synthetic-shadow-comparison-rehearsal",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept the eighteen-case no-feedback shadow rehearsal and its byte-identical primary-result proof.",
            }
        ],
        "claim_scope": [
            "Six denied and twelve admitted cases cover all required shadow classifications and failures.",
            "All four current raw adapters reproduce the exact three accepted gap codes.",
            "All eighteen primary results remain byte-for-byte unchanged.",
            "Ten record candidates produce nine exact minimized records, never more than one per scenario.",
            "All fifty-one hostile evidence mutations fail closed.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [DESIGN, THREAT],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING_RECEIPT, PRECOMMIT_RECEIPT],
            "tests": [
                "tests/test_raisa_provider_free_unmounted_authored_synthetic_shadow_comparison_rehearsal.py",
                TEST,
            ],
            "artifacts": [EVIDENCE, SCHEMA, UPDATER],
        },
        "unresolved_gates": [
            "No application hook, route edit, feature runtime, thread, process, queue, sink, persistence, retention or monitoring exists.",
            "Real route placement, dependency exclusion, product hashing, latency and backpressure remain unproved.",
            "Database/source/watcher/event access, patient/product data, providers, commands, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 249 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 250
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 250 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected shadow rehearsal Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove diagnostic shadow behavior without route or runtime authority",
        "outcome": "Eighteen pure cases pass with byte-identical primary results; runtime-instrumentation architecture review is next.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 231
        and compass["source_graph_revision"] == 249
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 232
        and compass["source_graph_revision"] == 250
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected shadow rehearsal Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Freeze the separately reviewed default-off runtime-instrumentation architecture before any route edit.",
                "Prove exact post-result placement, default-off configuration and dependency exclusion at the four raw route seams.",
                "Then prove ordinary and fallback client proposal/confirm parity before raw-route kernel convergence.",
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
        "strategic_role": "Pure shadow behavior proved; default-off mounting architecture next",
        "why_now": "The static boundary and pure failure behavior now pass, so the four real route seams can be inspected without yet editing or executing them.",
        "outcome": "Eighteen scenarios preserve every primary byte, bound output to one minimized record and contain timeout, overflow, observer and sink failure.",
        "unlocks": [
            "Freeze exact post-result hook points, dependency exclusions and immutable default-off controls for the four raw route seams.",
            "Define the deterministic static proof required before any route instrumentation implementation can begin.",
        ],
        "does_not_solve": [
            "Application instrumentation, feature runtime, product hashing, queue/sink persistence, latency isolation, client migration or database fencing.",
            "Durable cue delivery, CF-D2, patient/product data, providers, commands, deployment, Pages or protected refs.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 250 / Compass 232. The provider-free unmounted "
        "authored-synthetic shadow rehearsal passes eighteen cases with all "
        "primary bytes unchanged, nine minimized records and 51 hostile "
        "mutations rejected. The next safe tranche is a separately reviewed "
        "default-off runtime-instrumentation architecture plan."
    )
    limit = (
        "The shadow result is pure authored-synthetic evidence only; no route "
        "instrumentation, observer runtime, queue, sink or persistence exists."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 250
    compass["map_revision"] = 232
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
