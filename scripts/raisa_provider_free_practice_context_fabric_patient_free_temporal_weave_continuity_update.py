"""Idempotently accept the Practice Context Fabric patient-free temporal weave."""

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
NODE_ID = "raisa-provider-free-practice-context-fabric-patient-free-temporal-weave"
PARENT = "raisa-provider-free-practice-context-fabric-current-operational-weave"
SOURCE_HEAD = "f32004a2f39ac769ba746afe2663813f7c422d8a"
UPDATED_AT = "2026-08-06T05:17:04Z"
PLAN = "docs/raisa-provider-free-practice-context-fabric-patient-free-temporal-weave-plan.md"
DESIGN = "docs/raisa-provider-free-practice-context-fabric-patient-free-temporal-weave-design.md"
THREAT = (
    "docs/security/raisa-provider-free-practice-context-fabric-patient-free-"
    "temporal-weave-threat-model-delta.md"
)
SCHEMA = (
    "orchestration/continuity/raisa-provider-free-practice-context-fabric-"
    "patient-free-temporal-weave/temporal-weave-contract.schema.json"
)
EXAMPLE = (
    "orchestration/continuity/raisa-provider-free-practice-context-fabric-"
    "patient-free-temporal-weave/temporal-weave-contract.example.json"
)
EVIDENCE = (
    "orchestration/continuity/raisa-provider-free-practice-context-fabric-"
    "patient-free-temporal-weave/provider-free-acceptance-evidence.json"
)
WORKER_FAILURE = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-patient-free-"
    "temporal-weave-deepseek-timeout-failure-receipt.json"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-context-fabric-patient-free-"
    "temporal-weave-review-1-receipt.json"
)
RECONCILIATION = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-patient-free-"
    "temporal-weave-review-evidence-reconciliation-receipt.json"
)
ERROR_REVISION = "docs/ariadne-agent-error-correction-register-revision-31.md"
CLOSEOUT = (
    "docs/raisa-provider-free-practice-context-fabric-patient-free-temporal-"
    "weave-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-practice-context-"
    "fabric-patient-free-temporal-weave-sol-acceptance.md"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free Practice Context Fabric patient-free temporal weave",
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
            "authorized_openings": [
                {
                    "boundary": "api-change",
                    "source": CLOSEOUT,
                    "scope": (
                        "Define a provider-free patient-free unmounted intent-shaped "
                        "temporal retrieval rehearsal over closed authored-synthetic "
                        "frames; no patient/product data, real source, persistence, "
                        "provider call, product route, runtime or command."
                    ),
                }
            ],
            "notes": [
                "The accepted watcher classifies sealed patient-free metadata only and executes no read.",
                "A relevant signal retires an immutable frame set and emits one inert reassembly requirement.",
                "Bitemporal snapshots are selected as historical context and never current truth.",
                "Reception One and Clinician One are branded workspace families; atomic Bureau grants remain backend-owned.",
            ],
        },
        "decisions": [
            {
                "id": "accept-practice-context-fabric-patient-free-temporal-weave",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept exact parent-bound invalidation, monotonic checkpointing, "
                    "fail-closed continuity gaps, stale-result rejection and "
                    "purpose-scoped bitemporal selection."
                ),
            }
        ],
        "claim_scope": [
            "One pure provider-free watcher contract invalidates but never patches an immutable ContextFrameSet.",
            "Observed cursors, decisions, state-after and committed checkpoints are sealed before any later read.",
            "Historical snapshots preserve valid time, transaction time, correction lineage and explicit coverage gaps.",
            "No live watcher, database/feed, patient/product data, persistence, provider, runtime, command, deployment or protected capability is established.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [
                    "tests/test_bernie_reception_one_combined_scope.py",
                    EVIDENCE,
                ],
                "note": (
                    "The temporal control plane invalidates read context only "
                    "and does not alter the accepted combined-intent proposal "
                    "or command path."
                ),
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [
                    "tests/test_reception_one_availability_reconciliation.py",
                    EVIDENCE,
                    CLOSEOUT,
                ],
                "note": (
                    "Committed events remain invalidation signals for a later "
                    "fresh authorised read and never become current truth."
                ),
            },
        ],
        "evidence": {
            "plans": [PLAN, DESIGN, THREAT],
            "findings": [SCHEMA, EXAMPLE, EVIDENCE, ERROR_REVISION],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [WORKER_FAILURE, REVIEW, RECONCILIATION],
            "tests": [
                "tests/test_bernie_reception_one_combined_scope.py",
                "tests/test_raisa_provider_free_practice_context_fabric_patient_free_temporal_weave.py",
                "tests/test_raisa_provider_free_practice_context_fabric_current_operational_weave.py",
                "tests/test_raisa_provider_free_practice_context_fabric_bureau_memory_contract.py",
                "tests/test_raisa_practice_context_fabric_direction.py",
                "tests/test_reception_one_availability_reconciliation.py",
                "tests/test_api_spine_artifacts.py",
                "tests/test_ariadne_synaptic_event_router.py",
                "tests/test_raisa_provider_free_practice_context_fabric_patient_free_temporal_weave_continuity.py",
            ],
        },
        "unresolved_gates": [
            "The intent-shaped retrieval rehearsal may use only closed authored-synthetic patient-free frames under a separately frozen contract.",
            "Patient, clinical, product-derived, protected and production data; real databases, event transport, watchers and ordinary services remain closed.",
            "Persistence, operational retention, provider calls, external retrieval, product runtime and new routes remain closed.",
            "Commands, writes, deployment, production, release, Pages, protected refs and protected evidence remain closed.",
            "Requests/referrals, prescribing/medicines, billing/claims and other future Bureau implementations remain separately closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 218 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 219
        graph["updated_at"] = UPDATED_AT
        _write(GRAPH, graph)
    elif graph["graph_revision"] == 219 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
    else:
        raise SystemExit("Unexpected patient-free temporal weave Continuity predecessor")

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Temporal freshness and historical-context protocol",
        "outcome": (
            "One provider-free authored-synthetic control plane retires stale "
            "frame sets, preserves checkpoint causes and selects explicit "
            "bitemporal historical context without executing a read."
        ),
        "evidence": [
            PLAN,
            DESIGN,
            THREAT,
            SCHEMA,
            EXAMPLE,
            EVIDENCE,
            WORKER_FAILURE,
            REVIEW,
            RECONCILIATION,
            ERROR_REVISION,
            CLOSEOUT,
            ACCEPTANCE,
        ],
    }
    if (
        compass["map_revision"] == 200
        and compass["source_graph_revision"] == 218
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 201
        and compass["source_graph_revision"] == 219
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected patient-free temporal weave Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "The provider-free Fabric/Memory contract, Current operational weave and patient-free temporal weave are accepted at exact independently reviewed source HEADs.",
                "The next provider-free patient-free unmounted intent-shaped retrieval rehearsal must prove minimum disclosure, ambiguity, provenance and stale-frame rejection without opening real sources or runtime.",
                "Separately gate patient, clinical or product data, real event transport and watchers, persistence and retention, provider or external retrieval, commands, deployment, production and release.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Patient-free temporal weave accepted; intent-shaped retrieval rehearsal next",
        "why_now": (
            "Immutable invalidation, monotonic checkpointing, fail-closed gaps, "
            "stale-result rejection and bitemporal selection passed deterministic "
            "and independent review."
        ),
        "outcome": (
            "The first temporal Context Fabric control plane is accepted without "
            "opening a live watcher, persistence, product data, runtime or commands."
        ),
        "unlocks": [
            "Freeze the provider-free patient-free unmounted intent-shaped temporal retrieval rehearsal.",
            "Prove minimal current, recent-work and historical frame selection with explicit ambiguity and provenance.",
        ],
        "does_not_solve": [
            "Patient, clinical or product-data access, live event watching, real historical retention or external evidence retrieval.",
            "Provider-model memory, product runtime, persistence, commands, deployment or production.",
            "Requests/referrals, prescribing/medicines or billing/claims implementation authority.",
            "Release, Pages, protected evidence or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 219 / Compass 201. The provider-free Practice "
        "Context Fabric patient-free temporal weave passes at an exact "
        "independently reviewed HEAD. The provider-free patient-free unmounted "
        "intent-shaped temporal retrieval rehearsal is next."
    )
    limit = (
        "Patient-free temporal-weave acceptance proves pure provider-free "
        "authored-synthetic invalidation and bitemporal selection only; it "
        "creates no live watcher, patient, product, persistence, provider, "
        "runtime, command, deployment or protected authority."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 201
    compass["source_graph_revision"] = 219
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
