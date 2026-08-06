"""Idempotently accept the intent-shaped temporal Context Fabric retrieval."""

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
    "raisa-provider-free-practice-context-fabric-intent-shaped-temporal-retrieval"
)
PARENT = "raisa-provider-free-practice-context-fabric-patient-free-temporal-weave"
SOURCE_HEAD = "b24b56bda296f3713b5e2c0e52545c749e71540a"
UPDATED_AT = "2026-08-06T06:08:42Z"
PLAN = (
    "docs/raisa-provider-free-practice-context-fabric-intent-shaped-temporal-"
    "retrieval-rehearsal-plan.md"
)
DESIGN = (
    "docs/raisa-provider-free-practice-context-fabric-intent-shaped-temporal-"
    "retrieval-rehearsal-design.md"
)
THREAT = (
    "docs/security/raisa-provider-free-practice-context-fabric-intent-shaped-"
    "temporal-retrieval-rehearsal-threat-model-delta.md"
)
SCHEMA = (
    "orchestration/continuity/raisa-provider-free-practice-context-fabric-"
    "intent-shaped-temporal-retrieval-rehearsal/intent-shaped-temporal-"
    "retrieval-contract.schema.json"
)
EXAMPLE = (
    "orchestration/continuity/raisa-provider-free-practice-context-fabric-"
    "intent-shaped-temporal-retrieval-rehearsal/intent-shaped-temporal-"
    "retrieval-contract.example.json"
)
EVIDENCE = (
    "orchestration/continuity/raisa-provider-free-practice-context-fabric-"
    "intent-shaped-temporal-retrieval-rehearsal/provider-free-acceptance-"
    "evidence.json"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-context-fabric-intent-shaped-"
    "temporal-retrieval-review-receipt.json"
)
CLOSEOUT = (
    "docs/raisa-provider-free-practice-context-fabric-intent-shaped-temporal-"
    "retrieval-rehearsal-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-practice-context-"
    "fabric-intent-shaped-temporal-retrieval-sol-acceptance.md"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free Practice Context Fabric intent-shaped temporal retrieval",
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
                    "boundary": "provider-call",
                    "source": CLOSEOUT,
                    "scope": (
                        "Derive and freeze one authored-synthetic model-required "
                        "intent-shaping rehearsal using exact gemini-2.5-flash, "
                        "the Bernie Vertex development project, australia-"
                        "southeast1, a positive thinking budget, closed schema, "
                        "deterministic proofreader, exact call/cost ledger and no "
                        "fallback; execute no call before that envelope is frozen "
                        "and use no patient/product/runtime/command data or authority."
                    ),
                }
            ],
            "notes": [
                "Reception One and Clinician One are branded workspace families; atomic Bureau grants remain backend-owned.",
                "The Current component stays four-source atomic and private-session bound.",
                "Bureau Memory crosses only through an exact bilateral purpose grant.",
                "Consultant, requests/referrals, medicines/prescribing and billing/claims retain separate professional and command gates.",
            ],
        },
        "decisions": [
            {
                "id": "accept-practice-context-fabric-intent-shaped-temporal-retrieval",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept closed intent mapping, minimal component selection, "
                    "upstream proofreader recomputation, exact catalog binding, "
                    "bilateral sharing, bitemporal selection, safe ambiguity and "
                    "same-packet proofreading."
                ),
            }
        ],
        "claim_scope": [
            "Five closed intents select only minimum authorised Current, Bureau Memory and Historical components.",
            "Invalidated Current state, missing historical coverage and cross-Bureau private session fail closed.",
            "Ambiguous opaque references return alternatives without asserting identity.",
            "No natural-language/provider behaviour, patient/product data, live source, persistence, runtime, command, deployment or protected capability is established.",
        ],
        "contract_evidence": [
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [
                    "tests/test_reception_one_availability_reconciliation.py",
                    EVIDENCE,
                    CLOSEOUT,
                ],
                "note": (
                    "The retrieval layer refuses a Current component whose "
                    "temporal state requires reassembly and executes no read."
                ),
            },
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [
                    "tests/test_bernie_reception_one_combined_scope.py",
                    EVIDENCE,
                    CLOSEOUT,
                ],
                "note": (
                    "Intent-shaped context remains read-only and cannot bypass "
                    "the accepted proposal or command path."
                ),
            },
        ],
        "evidence": {
            "plans": [PLAN, DESIGN, THREAT],
            "findings": [SCHEMA, EXAMPLE, EVIDENCE],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [REVIEW],
            "tests": [
                "tests/test_bernie_reception_one_combined_scope.py",
                "tests/test_reception_one_availability_reconciliation.py",
                "tests/test_raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal.py",
                "tests/test_raisa_provider_free_practice_context_fabric_patient_free_temporal_weave.py",
                "tests/test_raisa_provider_free_practice_context_fabric_current_operational_weave.py",
                "tests/test_raisa_provider_free_practice_context_fabric_bureau_memory_contract.py",
                "tests/test_raisa_practice_context_fabric_direction.py",
                "tests/test_api_spine_artifacts.py",
                "tests/test_raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_continuity.py",
            ],
        },
        "unresolved_gates": [
            "The model-required intent-shaping descendant must freeze its exact authored-synthetic provider, model, region, identity, thinking, schema, proofreader, call and cost envelope before any occupied call.",
            "Patient, clinical, product-derived, protected and financial data; real sources, databases, event transport, watchers and ordinary services remain closed.",
            "Persistence, operational retention, external evidence retrieval, product runtime and new routes remain closed.",
            "Clinical, prescribing, referral, billing and all other commands and writes remain separately closed.",
            "Deployment, production, release, Pages, protected refs and protected evidence remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 219 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 220
        graph["updated_at"] = UPDATED_AT
        _write(GRAPH, graph)
    elif graph["graph_revision"] == 220 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
    else:
        raise SystemExit("Unexpected intent-shaped retrieval Continuity predecessor")

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Intent-shaped minimum Context Fabric retrieval",
        "outcome": (
            "One provider-free authored-synthetic selector converts closed intent "
            "codes into minimum granted Current, recent-work and historical "
            "components with safe ambiguity and same-packet proofreading."
        ),
        "evidence": [
            PLAN,
            DESIGN,
            THREAT,
            SCHEMA,
            EXAMPLE,
            EVIDENCE,
            REVIEW,
            CLOSEOUT,
            ACCEPTANCE,
        ],
    }
    if (
        compass["map_revision"] == 201
        and compass["source_graph_revision"] == 219
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 202
        and compass["source_graph_revision"] == 220
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected intent-shaped retrieval Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "The provider-free Fabric/Memory contract, Current operational weave, patient-free temporal weave and intent-shaped retrieval rehearsal are accepted at exact independently reviewed source HEADs.",
                "The next authored-synthetic model-required intent-shaping rehearsal must freeze exact gemini-2.5-flash Sydney Vertex transport, thinking, schema, proofreader, call/cost and no-fallback boundaries before one occupied sequence.",
                "Separately gate patient, clinical or product data, real sources/watchers, persistence/retention, external evidence, commands, deployment, production and release.",
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
            "Provider-free intent-shaped retrieval accepted; occupied "
            "authored-synthetic intent shaping next"
        ),
        "why_now": (
            "Closed intent mapping, minimum component disclosure, bilateral "
            "Bureau scope, temporal rejection, ambiguity and proofreader bindings "
            "passed deterministic and independent review."
        ),
        "outcome": (
            "The first request-shaped retrieval layer is accepted without opening "
            "a provider call, live source, patient data, runtime or command."
        ),
        "unlocks": [
            "Freeze the exact authored-synthetic model-required intent-shaping envelope.",
            "Test whether the selected model proposes only the closed non-authoritative intent candidate accepted by the deterministic layer.",
        ],
        "does_not_solve": [
            "Patient, clinical or product-data access; live retrieval/watching; real historical retention or external evidence.",
            "Product runtime, persistence, clinical or administrative commands, deployment or production.",
            "Consultant, requests/referrals, medicines/prescribing or billing/claims implementation authority.",
            "Release, Pages, protected evidence or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 220 / Compass 202. The provider-free Practice "
        "Context Fabric intent-shaped temporal retrieval rehearsal passes at an "
        "exact independently reviewed HEAD. A separately frozen authored-"
        "synthetic model-required intent-shaping rehearsal is next."
    )
    limit = (
        "Intent-shaped retrieval acceptance proves pure provider-free authored-"
        "synthetic context selection only; it creates no natural-language, "
        "provider, patient, product, live-source, persistence, runtime, command, "
        "deployment or protected authority."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 202
    compass["source_graph_revision"] = 220
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
