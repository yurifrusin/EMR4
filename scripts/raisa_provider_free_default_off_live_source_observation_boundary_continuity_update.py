"""Idempotently accept the default-off live-source observation architecture."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ariadne_compass


GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = "raisa-provider-free-default-off-live-source-observation-boundary"
PARENT = (
    "raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-"
    "fresh-generation-rehearsal"
)
SOURCE_HEAD = "fdbda21b28371778f5e50b0bc2cbd870bbf40e42"
UPDATED_AT = "2026-08-06T19:30:00Z"
PLAN = "docs/raisa-provider-free-default-off-live-source-observation-boundary-plan.md"
DESIGN = (
    "docs/raisa-provider-free-default-off-live-source-observation-boundary-design.md"
)
THREAT = (
    "docs/security/raisa-provider-free-default-off-live-source-observation-"
    "boundary-threat-model-delta.md"
)
ANALYSIS = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-live-source-"
    "observation-architecture-analysis.md"
)
FIRST_VETO = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-live-source-"
    "observation-architecture-veto.md"
)
FINAL_REVIEW = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-live-source-"
    "observation-architecture-repair-independent-review.md"
)
PREACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-live-source-"
    "observation-architecture-pre-verifier-acceptance-receipt.json"
)
CLOSEOUT = (
    "docs/raisa-provider-free-default-off-live-source-observation-boundary-"
    "closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-default-off-live-"
    "source-observation-boundary-sol-acceptance.md"
)
TEST = (
    "tests/test_raisa_provider_free_default_off_live_source_observation_"
    "boundary_plan.py"
)
UPDATER = (
    "scripts/raisa_provider_free_default_off_live_source_observation_boundary_"
    "continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_default_off_live_source_observation_"
    "boundary_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Default-off live-source observation architecture",
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
        "relationships": [{"node_id": PARENT, "relation": "builds_on"}],
        "authority": {
            "authorized_openings": [],
            "notes": [
                "The observer is not truth and has no returned-data, read, provider, persistence or command authority.",
                "Backend impact floors cannot be narrowed by source metadata; unknown impact requires bounded full invalidation.",
                "The policy stays default-off; synthetic classification activation has fixed zero-effect ceilings and is ineligible for live mode.",
                "Live sources, databases, event transport, product reads and all runtime capabilities remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-default-off-live-source-observation-architecture",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept the three-plane provider-free observer membrane "
                    "with backend-owned impact and no inherited read authority."
                ),
            }
        ],
        "claim_scope": [
            "Observation, temporal classification and fresh-read authority remain separate.",
            "Allowed metadata is closed, bounded and backend-issued or domain-separated.",
            "Baseline, monotonic position, gaps, overflow, restart and coalescing are fail-closed.",
            "The first veto findings were repaired and a fresh exact-worktree veto returned pass with 67 of 67 tests.",
            "No live observation, database, product read, provider, command, runtime, deployment or protected capability is established.",
        ],
        "contract_evidence": [
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [
                    PLAN,
                    "docs/api-spine/async/integration-events.yaml",
                    "docs/api-spine/openapi/diary-committed-events.yaml",
                    TEST,
                    CLOSEOUT,
                ],
                "note": (
                    "The architecture treats events only as invalidation "
                    "signals and explicitly excludes the existing polling "
                    "cursor from any no-loss claim."
                ),
            },
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [
                    "docs/api-spine/graphql/practice-context-fabric-read.graphql",
                    TEST,
                    CLOSEOUT,
                ],
                "note": (
                    "The observer adds no read or write surface and cannot "
                    "become command evidence."
                ),
            },
        ],
        "evidence": {
            "plans": [PLAN, DESIGN, THREAT],
            "findings": [
                ANALYSIS,
                FIRST_VETO,
                FINAL_REVIEW,
                "docs/api-spine/async/integration-events.yaml",
                "docs/api-spine/openapi/diary-committed-events.yaml",
                "docs/api-spine/graphql/practice-context-fabric-read.graphql",
            ],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREACCEPTANCE],
            "tests": [
                TEST,
                "tests/test_raisa_practice_context_fabric_direction.py",
                "tests/test_api_spine_artifacts.py",
                "tests/test_agents_handover_archive.py",
                "tests/test_ariadne_autonomous_continuation.py",
                "tests/test_agents_acceptance_index.py",
                CONTINUITY_TEST,
            ],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "Patient, clinical, product-derived, financial, protected and historical-PHI data remain closed.",
            "The exact first source/event family, transport principal, database/outbox/feed/watcher/listener and durable position/checkpoint remain closed.",
            "Product reads, persistence, restart recovery, operational audit/retention and live runtime remain closed.",
            "External evidence, provider calls, cross-Bureau clinical sources and every command/write remain closed.",
            "Deployment, production, release, Pages, protected refs and protected evidence remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 224 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 225
        graph["updated_at"] = UPDATED_AT
        _write(GRAPH, graph)
    elif graph["graph_revision"] == 225 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
    else:
        raise SystemExit("Unexpected live-source observation Continuity predecessor")

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Freeze the observer non-truth and authority membrane",
        "outcome": (
            "A default-off integration principal may only produce a "
            "backend-mapped payload-free invalidation signal."
        ),
        "evidence": [
            PLAN,
            DESIGN,
            THREAT,
            ANALYSIS,
            FIRST_VETO,
            FINAL_REVIEW,
            PREACCEPTANCE,
            CLOSEOUT,
            ACCEPTANCE,
        ],
    }
    if (
        compass["map_revision"] == 206
        and compass["source_graph_revision"] == 224
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 207
        and compass["source_graph_revision"] == 225
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected live-source observation Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "The complete unmounted Rayleen lifecycle and default-off live-source observation architecture are accepted at exact reviewed HEADs.",
                "The next safe candidate is a provider-free unmounted authored-synthetic observation-to-temporal-signal contract rehearsal.",
                "Separately gate every real source/event family, transport principal, database/feed, product read, persistence, clinical, command, deployment and release boundary.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": (
            "Default-off live-source observation architecture accepted; "
            "unmounted synthetic observation-to-signal rehearsal is next"
        ),
        "why_now": (
            "The observer's non-truth, metadata, impact, activation and authority "
            "boundaries are independently accepted before any implementation."
        ),
        "outcome": (
            "The repaired exact candidate passed 67 of 67 tests and a fresh "
            "no-finding independent veto."
        ),
        "unlocks": [
            "Implement pure typed observation policy, binding, activation, admission and signal-mapping contracts over authored-synthetic metadata.",
            "Prove backend impact floors, registered aliases and zero-effect default-off behavior without a live source.",
        ],
        "does_not_solve": [
            "Real patient/product data, a live observation/feed/watcher or product source read.",
            "Database/event transport, checkpoint persistence, restart recovery or operational retention.",
            "Provider cognition, cross-Bureau clinical sources, commands, deployment or production.",
            "Release, Pages, protected evidence or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 225 / Compass 207. The provider-free default-off "
        "live-source observation architecture passes at exact reviewed HEAD. "
        "An unmounted authored-synthetic observation-to-signal rehearsal is "
        "next; every live and real-data boundary remains closed."
    )
    limit = (
        "Live-source observation architecture acceptance proves only a "
        "provider-free default-off authority design; it creates no live source, "
        "delivery, database, product-read, persistence, provider, command, "
        "deployment or protected authority."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 207
    compass["source_graph_revision"] = 225
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
