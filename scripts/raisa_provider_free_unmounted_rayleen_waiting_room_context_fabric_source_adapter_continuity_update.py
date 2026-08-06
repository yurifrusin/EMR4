"""Idempotently accept the unmounted Rayleen Context Fabric source adapter."""

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
    "source-adapter"
)
PARENT = (
    "raisa-authored-synthetic-model-required-practice-context-fabric-"
    "intent-shaping"
)
SOURCE_HEAD = "12fbab157551954018e781810e4b100f05698dfb"
UPDATED_AT = "2026-08-06T11:40:00Z"
PLAN = (
    "docs/raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-"
    "source-adapter-plan.md"
)
DESIGN = (
    "docs/raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-"
    "source-adapter-design.md"
)
THREAT = (
    "docs/security/raisa-provider-free-unmounted-rayleen-waiting-room-context-"
    "fabric-source-adapter-threat-model-delta.md"
)
MODULE = (
    "scripts/raisa_provider_free_unmounted_rayleen_waiting_room_context_"
    "fabric_source_adapter.py"
)
GENERATOR = (
    "scripts/raisa_provider_free_unmounted_rayleen_waiting_room_context_"
    "fabric_source_adapter_acceptance.py"
)
ARTIFACT_ROOT = (
    "orchestration/continuity/raisa-provider-free-unmounted-rayleen-waiting-"
    "room-context-fabric-source-adapter/"
)
EVIDENCE = ARTIFACT_ROOT + "provider-free-acceptance-evidence.json"
RESULT_SCHEMA = ARTIFACT_ROOT + "adapter-result.schema.json"
EVIDENCE_SCHEMA = ARTIFACT_ROOT + "acceptance-evidence.schema.json"
FIXTURE = ARTIFACT_ROOT + "authored-synthetic-waiting-room-frame.json"
FINAL_REVIEW = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-rayleen-source-"
    "adapter-provenance-repair-independent-review.md"
)
PACKET_RECONCILIATION = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-rayleen-source-"
    "adapter-review-packet-count-reconciliation-receipt.json"
)
PROTECTED_FAILURE = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-rayleen-source-"
    "adapter-protected-path-enumeration-failure-receipt.json"
)
CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-"
    "source-adapter-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-rayleen-"
    "waiting-room-context-fabric-source-adapter-sol-acceptance.md"
)
TEST = (
    "tests/test_raisa_provider_free_unmounted_rayleen_waiting_room_context_"
    "fabric_source_adapter.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_rayleen_waiting_room_context_"
    "fabric_source_adapter_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Unmounted Rayleen waiting-room Context Fabric source adapter",
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
                "The adapter consumes only a completed authorised read shape and cannot invoke or refresh it.",
                "The sole handoff recomputes the complete result from authoritative inputs and releases a deep copy only.",
                "A live database/feed watcher, real product data and persistence remain separately closed.",
                "Reception One and Clinician One remain workspace brands; atomic Bureau grants remain backend-owned.",
            ],
        },
        "decisions": [
            {
                "id": "accept-unmounted-rayleen-waiting-room-source-adapter",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept one externally anchored provider-free mapping from "
                    "the serialized A4 frame to an unchanged Current-weave "
                    "source-envelope handoff."
                ),
            }
        ],
        "claim_scope": [
            "One authored-synthetic serialized A4 waiting-room frame is validated, minimized and opaquely aliased.",
            "The adapter preserves freshness and all-false authority and composes through the unchanged parent proofreader.",
            "The exact candidate passed fresh allowlisted review with 36 focused and 195 inherited tests.",
            "No live source, product data, watcher, persistence, provider, command, deployment or protected capability is established.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [
                    "tests/test_bernie_reception_one_combined_scope.py",
                    TEST,
                    CLOSEOUT,
                ],
                "note": (
                    "The adapter remains a read-only context source and cannot "
                    "bypass the accepted proposal or command path."
                ),
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [
                    "tests/test_reception_one_availability_reconciliation.py",
                    TEST,
                    CLOSEOUT,
                ],
                "note": (
                    "Freshness remains owned by the source; future invalidation "
                    "must retire and reassemble rather than patch the frame."
                ),
            },
        ],
        "evidence": {
            "plans": [PLAN, DESIGN, THREAT],
            "findings": [EVIDENCE, RESULT_SCHEMA, EVIDENCE_SCHEMA, FIXTURE],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [FINAL_REVIEW, PACKET_RECONCILIATION, PROTECTED_FAILURE],
            "tests": [
                TEST,
                "tests/test_raisa_provider_free_practice_context_fabric_current_operational_weave.py",
                "tests/test_raisa_provider_free_practice_context_fabric_bureau_memory_contract.py",
                "tests/test_raisa_provider_free_practice_context_fabric_patient_free_temporal_weave.py",
                "tests/test_raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal.py",
                "tests/test_raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_rehearsal.py",
                "tests/test_model_required_bureau_a4_product_read.py",
                "tests/test_bernie_reception_one_combined_scope.py",
                "tests/test_reception_one_availability_reconciliation.py",
                "tests/test_ariadne_agent_error_register.py",
                CONTINUITY_TEST,
            ],
            "artifacts": [MODULE, GENERATOR],
        },
        "unresolved_gates": [
            "Patient, clinical, product-derived, financial, protected and historical-PHI data and real source identifiers remain closed.",
            "Real databases, event transport, live watchers/feeds, persistence and operational retention remain closed.",
            "External evidence, provider calls, product routes and cross-Bureau clinical source handoffs remain closed.",
            "Consultant, requests/referrals, prescribing/medicines, billing/claims and all commands/writes remain separately closed.",
            "Deployment, production, release, Pages, protected refs and protected evidence remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 221 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 222
        graph["updated_at"] = UPDATED_AT
        _write(GRAPH, graph)
    elif graph["graph_revision"] == 222 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
    else:
        raise SystemExit("Unexpected Rayleen source-adapter Continuity predecessor")

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Concrete unmounted Current-source adapter",
        "outcome": (
            "One serialized A4 waiting-room frame now reaches the unchanged "
            "Current weave through an externally anchored, minimized and "
            "opaque provider-free adapter."
        ),
        "evidence": [
            PLAN,
            DESIGN,
            THREAT,
            EVIDENCE,
            RESULT_SCHEMA,
            EVIDENCE_SCHEMA,
            FIXTURE,
            FINAL_REVIEW,
            PACKET_RECONCILIATION,
            PROTECTED_FAILURE,
            CLOSEOUT,
            ACCEPTANCE,
        ],
    }
    if (
        compass["map_revision"] == 203
        and compass["source_graph_revision"] == 221
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 204
        and compass["source_graph_revision"] == 222
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected Rayleen source-adapter Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "The Fabric/Memory contract, Current and temporal weaves, intent-shaped retrieval, model-required intent shaping and unmounted Rayleen A4 source adapter are accepted at exact reviewed HEADs.",
                "The next safe candidate is a provider-free unmounted invalidation/reassembly seam over the accepted Rayleen adapter and temporal protocol.",
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
            "Unmounted Rayleen Current-source adapter accepted; provider-free "
            "invalidation/reassembly seam is the next safe candidate"
        ),
        "why_now": (
            "A concrete source now composes safely, so the accepted temporal "
            "retire-and-reassemble protocol can be bound to it without opening "
            "a live watcher."
        ),
        "outcome": (
            "The exact externally anchored adapter passed 18/18 evidence cases "
            "and a fresh allowlisted independent veto."
        ),
        "unlocks": [
            "Freeze a provider-free unmounted Rayleen invalidation/reassembly seam over authored-synthetic signals.",
            "Keep live database/event transport and product reads closed until their separate descendants.",
        ],
        "does_not_solve": [
            "Real patient/product data access or live waiting-room integration.",
            "Database/event watchers, persistence, retention or asynchronous runtime delivery.",
            "Provider cognition, cross-Bureau clinical sources, commands, deployment or production.",
            "Release, Pages, protected evidence or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 222 / Compass 204. The provider-free unmounted "
        "Rayleen A4 waiting-room Context Fabric source adapter passes at exact "
        "reviewed HEAD. A provider-free invalidation/reassembly seam is next; "
        "live watchers and real data remain closed."
    )
    limit = (
        "Source-adapter acceptance proves one authored-synthetic unmounted "
        "read/context mapping only; it creates no live-source, database-watcher, "
        "real-data, persistence, provider, command, deployment or protected authority."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 204
    compass["source_graph_revision"] = 222
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
