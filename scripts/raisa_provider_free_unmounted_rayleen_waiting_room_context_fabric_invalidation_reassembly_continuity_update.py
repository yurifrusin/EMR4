"""Idempotently accept the unmounted Rayleen invalidation/reassembly seam."""

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
NODE_ID = (
    "raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-"
    "invalidation-reassembly"
)
PARENT = (
    "raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-"
    "source-adapter"
)
SOURCE_HEAD = "72b5f46146393c644ee8fbfa1bb9ee0869d8d994"
UPDATED_AT = "2026-08-06T15:00:00Z"
PLAN = (
    "docs/raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-"
    "invalidation-reassembly-plan.md"
)
DESIGN = (
    "docs/raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-"
    "invalidation-reassembly-design.md"
)
THREAT = (
    "docs/security/raisa-provider-free-unmounted-rayleen-waiting-room-context-"
    "fabric-invalidation-reassembly-threat-model-delta.md"
)
MODULE = (
    "scripts/raisa_provider_free_unmounted_rayleen_waiting_room_context_"
    "fabric_invalidation_reassembly.py"
)
GENERATOR = (
    "scripts/raisa_provider_free_unmounted_rayleen_waiting_room_context_"
    "fabric_invalidation_reassembly_acceptance.py"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_rayleen_waiting_room_context_"
    "fabric_invalidation_reassembly_continuity_update.py"
)
ARTIFACT_ROOT = (
    "orchestration/continuity/raisa-provider-free-unmounted-rayleen-waiting-"
    "room-context-fabric-invalidation-reassembly/"
)
EVIDENCE = ARTIFACT_ROOT + "provider-free-acceptance-evidence.json"
PACKET_SCHEMA = ARTIFACT_ROOT + "seam-packet.schema.json"
EVIDENCE_SCHEMA = ARTIFACT_ROOT + "acceptance-evidence.schema.json"
FIXTURE = ARTIFACT_ROOT + "authored-synthetic-seam-packet.json"
WORKER_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-rayleen-"
    "invalidation-reassembly-native-worker-receipt.json"
)
FINAL_REVIEW = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-rayleen-"
    "invalidation-reassembly-independent-review.md"
)
PREACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-rayleen-"
    "invalidation-reassembly-pre-verifier-acceptance-receipt.json"
)
ORDERING_FAILURE = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-rayleen-"
    "invalidation-reassembly-worker-predispatch-ordering-failure-receipt.json"
)
SEARCH_FAILURE = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-rayleen-"
    "invalidation-reassembly-register-search-scope-failure-receipt.json"
)
CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-"
    "invalidation-reassembly-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-rayleen-"
    "waiting-room-context-fabric-invalidation-reassembly-sol-acceptance.md"
)
TEST = (
    "tests/test_raisa_provider_free_unmounted_rayleen_waiting_room_context_"
    "fabric_invalidation_reassembly.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_rayleen_waiting_room_context_"
    "fabric_invalidation_reassembly_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Unmounted Rayleen Context Fabric invalidation/reassembly seam",
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
                "The seam retires immutable context from payload-free metadata and cannot listen for changes.",
                "Its fresh-reassembly instruction is inert and performs no authority check, source read, provider call or command.",
                "No replacement frame set is admitted in this tranche.",
                "Reception One and Clinician One remain workspace brands; atomic Bureau grants remain backend-owned.",
            ],
        },
        "decisions": [
            {
                "id": "accept-unmounted-rayleen-invalidation-reassembly-seam",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept one provider-free authored-synthetic adapter-to-temporal "
                    "retirement and inert fresh-reassembly handoff."
                ),
            }
        ],
        "claim_scope": [
            "One extractor-recomputed Rayleen source is bound into an unchanged Current weave and exact temporal manifest/lease.",
            "One payload-free signal retires the immutable old set and emits one inert requirement without a fresh read or replacement frame.",
            "The exact candidate passed 32 evidence cases, 22 focused and 212 inherited serial tests plus a fresh no-finding veto.",
            "No real data, live watcher, persistence, provider, command, runtime, deployment or protected capability is established.",
        ],
        "contract_evidence": [
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [
                    TEST,
                    "tests/test_raisa_provider_free_practice_context_fabric_patient_free_temporal_weave.py",
                    CLOSEOUT,
                ],
                "note": (
                    "Committed-event-shaped metadata can only retire context and "
                    "require a future fresh authorised read."
                ),
            },
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [
                    "tests/test_bernie_reception_one_combined_scope.py",
                    TEST,
                    CLOSEOUT,
                ],
                "note": (
                    "The lifecycle seam remains outside the accepted proposal and "
                    "command path and adds no write authority."
                ),
            },
        ],
        "evidence": {
            "plans": [PLAN, DESIGN, THREAT],
            "findings": [EVIDENCE, PACKET_SCHEMA, EVIDENCE_SCHEMA, FIXTURE],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                WORKER_RECEIPT,
                FINAL_REVIEW,
                PREACCEPTANCE,
                ORDERING_FAILURE,
                SEARCH_FAILURE,
            ],
            "tests": [
                TEST,
                "tests/test_raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter.py",
                "tests/test_raisa_provider_free_practice_context_fabric_current_operational_weave.py",
                "tests/test_raisa_provider_free_practice_context_fabric_patient_free_temporal_weave.py",
                "tests/test_raisa_provider_free_practice_context_fabric_bureau_memory_contract.py",
                "tests/test_bernie_reception_one_combined_scope.py",
                "tests/test_ariadne_agent_error_register.py",
                CONTINUITY_TEST,
            ],
            "artifacts": [MODULE, GENERATOR, UPDATER],
        },
        "unresolved_gates": [
            "Patient, clinical, product-derived, financial, protected and historical-PHI data and real source identifiers remain closed.",
            "Real databases, event transport, live watchers/feeds, persistence, restart recovery and operational retention remain closed.",
            "Fresh product reads, external evidence, provider calls, product routes and cross-Bureau clinical handoffs remain closed.",
            "Consultant, requests/referrals, prescribing/medicines, billing/claims and all commands/writes remain separately closed.",
            "Deployment, production, release, Pages, protected refs and protected evidence remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 222 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 223
        graph["updated_at"] = UPDATED_AT
        _write(GRAPH, graph)
    elif graph["graph_revision"] == 223 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
    else:
        raise SystemExit("Unexpected Rayleen invalidation seam Continuity predecessor")

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "First concrete Current-source temporal lifecycle seam",
        "outcome": (
            "One adapter-built Rayleen Current frame set is deterministically "
            "retired by a payload-free signal and yields only an inert fresh-"
            "generation requirement."
        ),
        "evidence": [
            PLAN,
            DESIGN,
            THREAT,
            EVIDENCE,
            PACKET_SCHEMA,
            EVIDENCE_SCHEMA,
            FIXTURE,
            FINAL_REVIEW,
            PREACCEPTANCE,
            ORDERING_FAILURE,
            SEARCH_FAILURE,
            CLOSEOUT,
            ACCEPTANCE,
        ],
    }
    if (
        compass["map_revision"] == 204
        and compass["source_graph_revision"] == 222
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 205
        and compass["source_graph_revision"] == 223
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected Rayleen invalidation seam Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "The Fabric/Memory contract, Current and temporal weaves, intent-shaped retrieval, model-required intent shaping, unmounted Rayleen source adapter and its inert invalidation/reassembly seam are accepted at exact reviewed HEADs.",
                "The next safe candidate is a provider-free unmounted fresh-generation rehearsal consuming the inert requirement and rejecting an older result.",
                "Separately gate every live product source, database watcher/feed, persistence/retention, cross-Bureau clinical source, command, deployment, production and release boundary.",
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
            "Rayleen Current invalidation/reassembly seam accepted; provider-free "
            "fresh-generation rehearsal is the next safe candidate"
        ),
        "why_now": (
            "Retirement and the inert requirement are proven, so a wholly new "
            "authored-synthetic generation can now be rehearsed without a live source."
        ),
        "outcome": (
            "The exact reconstruction passed 32/32 evidence cases, 22 focused "
            "and 212 inherited tests plus a fresh no-finding veto."
        ),
        "unlocks": [
            "Freeze a provider-free unmounted fresh-generation rehearsal over newly authored synthetic source input.",
            "Prove older asynchronous results cannot supersede the newer frame-set generation.",
        ],
        "does_not_solve": [
            "Real patient/product data access, a live source read or waiting-room integration.",
            "Database/event watchers, transport, persistence, restart recovery or operational retention.",
            "Provider cognition, cross-Bureau clinical sources, commands, deployment or production.",
            "Release, Pages, protected evidence or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 223 / Compass 205. The provider-free unmounted "
        "Rayleen invalidation/reassembly seam passes at exact reviewed HEAD. A "
        "provider-free fresh-generation rehearsal is next; live watchers, source "
        "reads and real data remain closed."
    )
    limit = (
        "Invalidation-seam acceptance proves one authored-synthetic unmounted "
        "retire-and-require handoff only; it creates no live-source, watcher, "
        "persistence, provider, command, deployment or protected authority."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 205
    compass["source_graph_revision"] = 223
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
