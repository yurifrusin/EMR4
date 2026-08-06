"""Idempotently accept the unmounted source-specific durability architecture."""

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
NODE_ID = "raisa-provider-free-unmounted-source-specific-durability-architecture"
PARENT = (
    "raisa-provider-free-unmounted-authored-synthetic-observation-to-"
    "temporal-signal-rehearsal"
)
SOURCE_HEAD = "14e8d3257b9531601260bef094c73e08a9c7b92d"
UPDATED_AT = "2026-08-06T19:00:00Z"
PLAN = "docs/raisa-provider-free-unmounted-source-specific-durability-architecture-plan.md"
DESIGN = (
    "docs/raisa-provider-free-unmounted-source-specific-durability-"
    "architecture-design.md"
)
THREAT = (
    "docs/security/raisa-provider-free-unmounted-source-specific-durability-"
    "architecture-threat-model-delta.md"
)
CONTRACT_DIR = (
    "orchestration/continuity/raisa-provider-free-unmounted-source-specific-"
    "durability-architecture/"
)
TEST = (
    "tests/test_raisa_provider_free_unmounted_source_specific_durability_"
    "architecture.py"
)
ANALYSIS = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-source-specific-"
    "durability-architecture-analysis.md"
)
FIRST_VETO = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-source-specific-"
    "durability-architecture-independent-veto.md"
)
LEASE = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-source-specific-"
    "durability-architecture-sol-recovery-lease.md"
)
FINAL_REVIEW = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-source-specific-"
    "durability-architecture-final-independent-review.md"
)
PREACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-source-specific-"
    "durability-architecture-pre-verifier-acceptance-receipt.json"
)
CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-source-specific-durability-"
    "architecture-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-source-"
    "specific-durability-architecture-sol-acceptance.md"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_source_specific_durability_"
    "architecture_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_source_specific_durability_"
    "architecture_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Unmounted source-specific durability architecture",
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
                "The architecture is provider-free, unmounted and payload-free.",
                "Observer, durability coordinator and application principals remain distinct.",
                "Durable watermark and source-head fence are specifications, not operational persistence.",
                "No database, no source, no product read, no provider, no command, no runtime or protected capability is opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-source-specific-durability-architecture",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept the rollback-safe source position, atomic durability "
                    "unit, fail-closed continuity and exact closed machine contract."
                ),
            }
        ],
        "claim_scope": [
            "A distinct payload-free observer and internal durability coordinator are frozen.",
            "The future producer coordinate is per-practice, transactional, rollback-safe and independent of aggregate revision.",
            "Durable invalidation watermark, source-head fence, checkpoint, restart, retention and key rotation contracts are exact.",
            "The fresh recovery veto rejected 28/28 tuple mutations and found no P0-P2 issue across 160 checks.",
            "No live source, persistence, product read, provider, command, runtime, deployment or protected capability is established.",
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
                    "The existing event contract is retained, while the future "
                    "payload-free durability projection is a separately gated surface."
                ),
            },
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [
                    "docs/api-spine/graphql/practice-context-fabric-read.graphql",
                    DESIGN,
                    TEST,
                    CLOSEOUT,
                ],
                "note": (
                    "Frame invalidation architecture adds neither a read model nor "
                    "command authority."
                ),
            },
        ],
        "evidence": {
            "plans": [PLAN, DESIGN, THREAT],
            "findings": [
                ANALYSIS,
                FIRST_VETO,
                LEASE,
                FINAL_REVIEW,
                "docs/ariadne-agent-error-correction-register-revision-41.md",
                "docs/ariadne-agent-error-correction-register-revision-42.md",
                "docs/api-spine/async/integration-events.yaml",
                "docs/api-spine/openapi/diary-committed-events.yaml",
                "docs/api-spine/graphql/practice-context-fabric-read.graphql",
            ],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREACCEPTANCE],
            "tests": [
                TEST,
                "tests/test_raisa_provider_free_default_off_live_source_observation_boundary_plan.py",
                "tests/test_raisa_provider_free_unmounted_authored_synthetic_observation_to_temporal_signal_rehearsal_plan.py",
                "tests/test_api_spine_artifacts.py",
                "tests/test_ariadne_agent_error_register.py",
                CONTINUITY_TEST,
            ],
            "artifacts": [CONTRACT_DIR, UPDATER],
        },
        "unresolved_gates": [
            "Patient, clinical, product-derived, financial, protected and historical-PHI data remain closed.",
            "Database/outbox/feed/watcher/listener/source access and operational credentials remain closed.",
            "Migrations, source rows, checkpoint persistence, runtime restart and live retention remain closed.",
            "Product reads, providers, cross-Bureau clinical sources and every route or command/write remain closed.",
            "Deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 226 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 227
        graph["updated_at"] = UPDATED_AT
        _write(GRAPH, graph)
    elif graph["graph_revision"] == 227 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
    else:
        raise SystemExit("Unexpected durability-architecture Continuity predecessor")

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Freeze no-loss source-specific durability before runtime",
        "outcome": (
            "A rollback-safe source coordinate, durable watermark/frame fence and "
            "fail-closed checkpoint lifecycle pass as exact unmounted contracts."
        ),
        "evidence": [
            PLAN,
            DESIGN,
            THREAT,
            ANALYSIS,
            FIRST_VETO,
            LEASE,
            FINAL_REVIEW,
            PREACCEPTANCE,
            CLOSEOUT,
            ACCEPTANCE,
        ],
    }
    if (
        compass["map_revision"] == 208
        and compass["source_graph_revision"] == 226
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 209
        and compass["source_graph_revision"] == 227
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected durability-architecture Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "The unmounted observation-to-signal rehearsal and source-specific durability architecture are accepted at exact reviewed HEADs.",
                "The next safe candidate is a pure provider-free unmounted durability state-machine rehearsal over authored-synthetic state.",
                "Separately gate migrations, live source/database access, operational credentials, persistence, product reads, clinical data, commands, deployment and release.",
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
            "Unmounted source-specific durability architecture accepted; pure "
            "durability state-machine rehearsal is next"
        ),
        "why_now": (
            "The exact no-loss coordinate, atomic durability unit, watermark/fence "
            "and failure lifecycle are independently accepted before implementation."
        ),
        "outcome": (
            "The repaired exact candidate rejected all 28 tuple mutations, passed "
            "160 checks and received a fresh no-finding veto."
        ),
        "unlocks": [
            "Implement pure in-memory provider-free transitions for redelivery, contiguous processing, invalidation, gaps, restart, key intervals and retention eligibility.",
            "Exercise the exact durability contract without mounting a source or persisting operational state.",
        ],
        "does_not_solve": [
            "Real patient/product data, migrations or live database/outbox/feed/watcher/listener/source access.",
            "Operational credentials, checkpoint persistence, product reads or runtime retention.",
            "Provider cognition, cross-Bureau clinical sources, routes, commands, deployment or production.",
            "Release, Pages, protected evidence or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 227 / Compass 209. The provider-free unmounted "
        "source-specific durability architecture passes at exact reviewed HEAD. "
        "A pure in-memory durability state-machine rehearsal is next; every live "
        "and real-data boundary remains closed."
    )
    limit = (
        "Source-specific durability architecture acceptance proves only exact "
        "provider-free unmounted contracts; it creates no migration, live source, "
        "database, persistence, product-read, provider, command, runtime, deployment "
        "or protected authority."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 209
    compass["source_graph_revision"] = 227
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
