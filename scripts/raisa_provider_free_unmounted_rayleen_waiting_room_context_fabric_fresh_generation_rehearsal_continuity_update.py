"""Idempotently accept the unmounted Rayleen fresh-generation rehearsal."""

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
    "fresh-generation-rehearsal"
)
PARENT = (
    "raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-"
    "invalidation-reassembly"
)
SOURCE_HEAD = "9516b85542a4de1fcef305423ec15fd34f7731aa"
UPDATED_AT = "2026-08-06T16:30:00Z"
PLAN = (
    "docs/raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-"
    "fresh-generation-rehearsal-plan.md"
)
DESIGN = (
    "docs/raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-"
    "fresh-generation-rehearsal-design.md"
)
THREAT = (
    "docs/security/raisa-provider-free-unmounted-rayleen-waiting-room-context-"
    "fabric-fresh-generation-rehearsal-threat-model-delta.md"
)
MODULE = (
    "scripts/raisa_provider_free_unmounted_rayleen_waiting_room_context_"
    "fabric_fresh_generation_rehearsal.py"
)
GENERATOR = (
    "scripts/raisa_provider_free_unmounted_rayleen_waiting_room_context_"
    "fabric_fresh_generation_rehearsal_acceptance.py"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_rayleen_waiting_room_context_"
    "fabric_fresh_generation_rehearsal_continuity_update.py"
)
ARTIFACT_ROOT = (
    "orchestration/continuity/raisa-provider-free-unmounted-rayleen-waiting-"
    "room-context-fabric-fresh-generation-rehearsal/"
)
EVIDENCE = ARTIFACT_ROOT + "provider-free-acceptance-evidence.json"
PACKET_SCHEMA = ARTIFACT_ROOT + "fresh-generation-packet.schema.json"
EVIDENCE_SCHEMA = ARTIFACT_ROOT + "acceptance-evidence.schema.json"
FIXTURE = ARTIFACT_ROOT + "authored-synthetic-fresh-generation-packet.json"
WORKER_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-rayleen-"
    "fresh-generation-native-worker-receipt.json"
)
FAILED_REVIEW = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-rayleen-"
    "fresh-generation-validity-window-review.md"
)
FINAL_REVIEW = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-rayleen-"
    "fresh-generation-repair-independent-review.md"
)
PREACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-rayleen-"
    "fresh-generation-pre-verifier-acceptance-receipt.json"
)
CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-"
    "fresh-generation-rehearsal-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-rayleen-"
    "waiting-room-context-fabric-fresh-generation-rehearsal-sol-acceptance.md"
)
TEST = (
    "tests/test_raisa_provider_free_unmounted_rayleen_waiting_room_context_"
    "fabric_fresh_generation_rehearsal.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_rayleen_waiting_room_context_"
    "fabric_fresh_generation_rehearsal_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Unmounted Rayleen Context Fabric fresh-generation rehearsal",
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
                "The rehearsal consumes only reconstructed inert obligations and independently authored synthetic completed-read-shaped inputs.",
                "Both predecessor authority objects must remain current; either expiry blocks both release paths.",
                "The observer, source read, watcher, persistence, provider and command boundaries remain closed.",
                "Reception One and Clinician One remain workspace brands; atomic Bureau grants remain backend-owned.",
            ],
        },
        "decisions": [
            {
                "id": "accept-unmounted-rayleen-fresh-generation-rehearsal",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept one provider-free authored-synthetic retire-to-new-"
                    "generation composition with deterministic supersession."
                ),
            }
        ],
        "claim_scope": [
            "Every affected Diary and waiting dependency is refreshed from independent authored-synthetic completed-read-shaped input.",
            "A distinct no-wider request, frame set, manifest and lease are admitted only while predecessor authority is current.",
            "An older result is rejected in both completion orders and cannot restore the immutable retired generation.",
            "The exact repaired candidate passed 45 evidence cases, 26 focused and 238 inherited tests plus a fresh no-finding veto.",
            "No real data, live observation/read, watcher, persistence, provider, command, runtime, deployment or protected capability is established.",
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
                    "Payload-free change metadata can retire old context, while "
                    "only a separately reconstructed fresh generation becomes current."
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
                    "The lifecycle rehearsal stays outside the accepted proposal "
                    "and command path and adds no write authority."
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
                FAILED_REVIEW,
                FINAL_REVIEW,
                PREACCEPTANCE,
            ],
            "tests": [
                TEST,
                "tests/test_raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_invalidation_reassembly.py",
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
            "Real databases, live observation, event transport, watchers/feeds, product reads, persistence, restart recovery and operational retention remain closed.",
            "External evidence, provider calls, product routes and cross-Bureau clinical handoffs remain closed.",
            "Consultant, requests/referrals, prescribing/medicines, billing/claims and all commands/writes remain separately closed.",
            "Deployment, production, release, Pages, protected refs and protected evidence remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 223 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 224
        graph["updated_at"] = UPDATED_AT
        _write(GRAPH, graph)
    elif graph["graph_revision"] == 224 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
    else:
        raise SystemExit("Unexpected Rayleen fresh-generation Continuity predecessor")

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Complete provider-free Rayleen Current lifecycle rehearsal",
        "outcome": (
            "One inert invalidation requirement becomes a distinct same-packet-"
            "proofread new generation and older completion cannot roll it back."
        ),
        "evidence": [
            PLAN,
            DESIGN,
            THREAT,
            EVIDENCE,
            PACKET_SCHEMA,
            EVIDENCE_SCHEMA,
            FIXTURE,
            FAILED_REVIEW,
            FINAL_REVIEW,
            PREACCEPTANCE,
            CLOSEOUT,
            ACCEPTANCE,
        ],
    }
    if (
        compass["map_revision"] == 205
        and compass["source_graph_revision"] == 223
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 206
        and compass["source_graph_revision"] == 224
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected Rayleen fresh-generation Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "The Fabric/Memory contract, Current and temporal weaves, intent-shaped retrieval, model-required intent shaping and the complete unmounted Rayleen retire-to-new-generation lifecycle are accepted at exact reviewed HEADs.",
                "The next safe candidate is an architecture-only provider-free default-off live-source observation boundary.",
                "Separately gate every live database/feed implementation, product read, persistence/retention, cross-Bureau clinical source, command, deployment, production and release boundary.",
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
            "Rayleen fresh-generation rehearsal accepted; architecture-only "
            "live-source observation boundary is the next safe candidate"
        ),
        "why_now": (
            "Retirement, fresh generation and deterministic supersession are now "
            "proven without live observation, so the observer's non-truth boundary "
            "can be frozen before any implementation."
        ),
        "outcome": (
            "The repaired exact candidate passed 45/45 evidence cases, 26 focused "
            "and 238 inherited tests plus a fresh no-finding veto."
        ),
        "unlocks": [
            "Freeze a default-off provider-free architecture for authenticated practice-scoped payload-free change observation.",
            "Define a separately authorised fresh-read request without granting observer truth, data-return or command authority.",
        ],
        "does_not_solve": [
            "Real patient/product data access, a live observation/feed/watcher or product source read.",
            "Database/event transport, persistence, restart recovery or operational retention.",
            "Provider cognition, cross-Bureau clinical sources, commands, deployment or production.",
            "Release, Pages, protected evidence or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 224 / Compass 206. The provider-free unmounted "
        "Rayleen fresh-generation rehearsal passes at exact reviewed HEAD. An "
        "architecture-only default-off live-source observation boundary is next; "
        "live implementation, product reads and real data remain closed."
    )
    limit = (
        "Fresh-generation acceptance proves one authored-synthetic unmounted "
        "retire-to-new-generation lifecycle only; it creates no live observation, "
        "product-read, persistence, provider, command, deployment or protected authority."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 206
    compass["source_graph_revision"] = 224
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
