"""Idempotently accept the occupied model-required Context Fabric intent path."""

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
    "raisa-authored-synthetic-model-required-practice-context-fabric-"
    "intent-shaping"
)
PARENT = (
    "raisa-provider-free-practice-context-fabric-intent-shaped-temporal-"
    "retrieval"
)
SOURCE_HEAD = "44f341481b55f99a18a47838da0f2b7e43a2f73e"
UPDATED_AT = "2026-08-06T08:20:00Z"
PLAN = (
    "docs/raisa-authored-synthetic-model-required-practice-context-fabric-"
    "intent-shaping-rehearsal-plan.md"
)
DESIGN = (
    "docs/raisa-authored-synthetic-model-required-practice-context-fabric-"
    "intent-shaping-rehearsal-design.md"
)
THREAT = (
    "docs/security/raisa-authored-synthetic-model-required-practice-context-"
    "fabric-intent-shaping-rehearsal-threat-model-delta.md"
)
ARTIFACT_ROOT = (
    "orchestration/continuity/raisa-authored-synthetic-model-required-"
    "practice-context-fabric-intent-shaping-rehearsal/"
)
PROVIDER_FREE_EVIDENCE = ARTIFACT_ROOT + "provider-free-acceptance-evidence.json"
DRY_RUN_EVIDENCE = ARTIFACT_ROOT + "provider-free-dry-run-evidence.json"
OCCUPIED_EVIDENCE = ARTIFACT_ROOT + "occupied-rehearsal-evidence.json"
COST_LEDGER = ARTIFACT_ROOT + "occupied-rehearsal-cost-ledger.json"
PREFLIGHT = (
    ARTIFACT_ROOT
    + "rayleen-context-fabric-intent-shaping-attempt-1-preflight.json"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-context-fabric-model-"
    "required-intent-shaping-source-review-receipt.json"
)
SOURCE_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-authored-synthetic-model-required-"
    "practice-context-fabric-intent-shaping-source-review-receipt.json"
)
CLOSEOUT = (
    "docs/raisa-authored-synthetic-model-required-practice-context-fabric-"
    "intent-shaping-rehearsal-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-authored-synthetic-model-required-"
    "practice-context-fabric-intent-shaping-sol-acceptance.md"
)
TEST = (
    "tests/test_raisa_authored_synthetic_model_required_practice_context_"
    "fabric_intent_shaping_rehearsal.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_authored_synthetic_model_required_practice_context_"
    "fabric_intent_shaping_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Authored-synthetic model-required Context Fabric intent shaping",
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
                "The occupied authority was consumed by one primary call; no correction or post-success call remains open.",
                "The model proposed only a closed non-authoritative intent; deterministic code owned context and release.",
                "Reception One and Clinician One remain workspace brands while atomic Bureau capability gates remain backend-owned.",
                "Any real product source, persistent watcher, clinical source or command is a separate authority boundary.",
            ],
        },
        "decisions": [
            {
                "id": "accept-model-required-context-fabric-intent-shaping",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept one source-reviewed Sydney Vertex model-shaped "
                    "intent candidate admitted through the unchanged "
                    "deterministic Context Fabric retrieval proofreader."
                ),
            }
        ],
        "claim_scope": [
            "One authored-synthetic staff utterance produced one closed comparison intent through required gemini-2.5-flash inference.",
            "The exact parent catalog, authority binding, retrieval packet and same-packet proofreader were rebuilt in trusted code.",
            "One call and USD 0.25 were consumed; positive thinking evidence, no fallback, no post-success call and complete cleanup hold.",
            "No patient/product data, real source, watcher, persistence, runtime, command, clinical, deployment or protected capability is established.",
        ],
        "contract_evidence": [
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [
                    "tests/test_reception_one_availability_reconciliation.py",
                    OCCUPIED_EVIDENCE,
                    CLOSEOUT,
                ],
                "note": (
                    "The model selects intent only; Current state still requires "
                    "the accepted fresh authorised read and invalidation rules."
                ),
            },
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [
                    "tests/test_bernie_reception_one_combined_scope.py",
                    OCCUPIED_EVIDENCE,
                    CLOSEOUT,
                ],
                "note": (
                    "The released intent remains read-only and cannot bypass "
                    "the accepted proposal or command path."
                ),
            },
        ],
        "evidence": {
            "plans": [PLAN, DESIGN, THREAT],
            "findings": [
                PROVIDER_FREE_EVIDENCE,
                DRY_RUN_EVIDENCE,
                OCCUPIED_EVIDENCE,
                COST_LEDGER,
                PREFLIGHT,
            ],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [REVIEW, SOURCE_RECEIPT],
            "tests": [
                "tests/test_bernie_reception_one_combined_scope.py",
                "tests/test_reception_one_availability_reconciliation.py",
                TEST,
                "tests/test_raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_plan.py",
                "tests/test_raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal.py",
                "tests/test_raisa_practice_context_fabric_direction.py",
                "tests/test_api_spine_artifacts.py",
                CONTINUITY_TEST,
            ],
        },
        "unresolved_gates": [
            "Patient, clinical, product-derived, protected, financial and historical-PHI data and real practice/user/source identifiers remain closed.",
            "Real databases, event transport, live watchers/feeds, persistence, operational retention and ordinary services remain closed.",
            "External evidence/RAG, product runtime/routes and cross-Bureau or clinical source handoffs remain closed.",
            "Clinical, prescribing, referral, billing, administrative and all other commands and writes remain separately closed.",
            "Cloud/IAM mutation, deployment, production, release, Pages, protected refs and protected evidence remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 220 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 221
        graph["updated_at"] = UPDATED_AT
        _write(GRAPH, graph)
    elif graph["graph_revision"] == 221 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
    else:
        raise SystemExit("Unexpected model intent-shaping Continuity predecessor")

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Model-required closed intent proposal",
        "outcome": (
            "One source-reviewed Sydney Vertex call proposed the exact closed "
            "synthetic comparison intent; deterministic Context Fabric code "
            "alone rebuilt and admitted the parent retrieval packet."
        ),
        "evidence": [
            PLAN,
            DESIGN,
            THREAT,
            PROVIDER_FREE_EVIDENCE,
            DRY_RUN_EVIDENCE,
            OCCUPIED_EVIDENCE,
            COST_LEDGER,
            PREFLIGHT,
            REVIEW,
            SOURCE_RECEIPT,
            CLOSEOUT,
            ACCEPTANCE,
        ],
    }
    if (
        compass["map_revision"] == 202
        and compass["source_graph_revision"] == 220
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 203
        and compass["source_graph_revision"] == 221
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected model intent-shaping Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "The provider-free Fabric/Memory contract, Current operational weave, patient-free temporal weave and intent-shaped retrieval rehearsal plus the occupied authored-synthetic model-required intent path are accepted at exact source-reviewed HEADs.",
                "The next safe candidate is a separately frozen provider-free adapter over one already authorised current operational read shape, without a new route or real-data execution.",
                "Separately gate every real product/patient source, watcher/feed, persistence/retention, cross-Bureau or clinical source, command, deployment, production and release boundary.",
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
            "Occupied authored-synthetic intent shaping accepted; one-source "
            "provider-free adapter planning is the next safe candidate"
        ),
        "why_now": (
            "The required model can now propose a closed intent without seeing "
            "source frames or inheriting authority, and the deterministic parent "
            "retrieval path remains intact."
        ),
        "outcome": (
            "One primary Sydney Vertex call passed exact identity, schema, "
            "reasoning, accounting, proofreader, retention and cleanup gates."
        ),
        "unlocks": [
            "Freeze a provider-free adapter contract around one existing authorised current operational read shape.",
            "Keep the adapter unmounted and authored-synthetic until a separate real-product authority opens.",
        ],
        "does_not_solve": [
            "General natural-language understanding or real staff-language fitness.",
            "Patient, clinical or product-data access; live retrieval/watching; persistence, retention or external evidence.",
            "Cross-Bureau/clinical source access, product runtime, commands, deployment or production.",
            "Release, Pages, protected evidence or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 221 / Compass 203. The authored-synthetic "
        "model-required Practice Context Fabric intent-shaping rehearsal passes "
        "with one source-reviewed Sydney Vertex call and deterministic parent "
        "admission. A separately frozen provider-free one-source adapter is the "
        "next safe candidate; real data and runtime remain closed."
    )
    limit = (
        "Occupied intent-shaping acceptance proves one authored-synthetic closed "
        "model proposal only; it creates no real-source, patient, product, live-"
        "watcher, persistence, runtime, command, clinical, deployment or "
        "protected authority."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 203
    compass["source_graph_revision"] = 221
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit(
            "Compass validation failed: " + ", ".join(report["reasons"])
        )
    REPORT.write_text(
        ariadne_compass.render_markdown(report), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
