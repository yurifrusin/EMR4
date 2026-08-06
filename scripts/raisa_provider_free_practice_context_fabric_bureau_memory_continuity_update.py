"""Idempotently accept the first Practice Context Fabric contract."""

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
NODE_ID = "raisa-provider-free-practice-context-fabric-bureau-memory-contract"
PARENT = "model-required-bureau-c5-occupied-live-rehearsal"
SOURCE_HEAD = "cb1b0a712f8ee5340e73d8adde19103af0d9ed97"
UPDATED_AT = "2026-08-06T03:30:00Z"
PLAN = "docs/raisa-provider-free-practice-context-fabric-bureau-memory-contract-plan.md"
DESIGN = "docs/raisa-provider-free-practice-context-fabric-bureau-memory-contract-design.md"
THREAT = (
    "docs/security/raisa-provider-free-practice-context-fabric-bureau-memory-"
    "contract-threat-model-delta.md"
)
SCHEMA = (
    "orchestration/continuity/raisa-provider-free-practice-context-fabric-"
    "bureau-memory-contract/context-fabric-contract.schema.json"
)
EVIDENCE = (
    "orchestration/continuity/raisa-provider-free-practice-context-fabric-"
    "bureau-memory-contract/provider-free-acceptance-evidence.json"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-context-fabric-bureau-memory-"
    "repair-review-receipt.json"
)
CLOSEOUT = (
    "docs/raisa-provider-free-practice-context-fabric-bureau-memory-contract-"
    "closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-practice-context-"
    "fabric-bureau-memory-contract-sol-acceptance.md"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free Practice Context Fabric and Bureau Memory Bank contract",
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
                        "Compose existing authorised Diary, waiting-room, "
                        "practitioner-directory and application-session read "
                        "projections in a provider-free authored-synthetic "
                        "Current operational weave; no new product route or source."
                    ),
                }
            ],
            "notes": [
                "The accepted GraphQL extension is documentation-only and unmounted.",
                "Backend authority binding and deterministic narrowing remain mandatory.",
                "Bureau Memory is derived read context, not audit, current truth, command evidence or provider-model memory.",
                "The next descendant remains provider-free, authored-synthetic and without product runtime.",
            ],
        },
        "decisions": [
            {
                "id": "accept-practice-context-fabric-bureau-memory-contract",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept the closed provider-free Context Fabric grammar, "
                    "scope-narrowing engine, Memory Bank projection and "
                    "same-packet proofreader."
                ),
            }
        ],
        "claim_scope": [
            "One authored-synthetic candidate is bound to backend authority and can only be narrowed by deterministic policy.",
            "One derived recent-work Memory Bank frame is selected, woven and proofread without raw audit access.",
            "The documentation-only GraphQL extension adds one read field and no mutation, subscription, resolver or route.",
            "No patient, product, provider, database, persistence, runtime, command, deployment or protected capability is established.",
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
                    "The contract adds no appointment read or write path and "
                    "does not alter the accepted combined-intent contract."
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
                    "Events remain signals for fresh authorised reads; no event "
                    "or context frame becomes current truth or command authority."
                ),
            },
        ],
        "evidence": {
            "plans": [PLAN, DESIGN, THREAT],
            "findings": [SCHEMA, EVIDENCE],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [REVIEW],
            "tests": [
                "tests/test_bernie_reception_one_combined_scope.py",
                "tests/test_reception_one_availability_reconciliation.py",
                "tests/test_raisa_provider_free_practice_context_fabric_bureau_memory_contract.py",
                "tests/test_raisa_practice_context_fabric_direction.py",
                "tests/test_api_spine_artifacts.py",
                "tests/test_raisa_provider_free_practice_context_fabric_bureau_memory_continuity.py",
            ],
        },
        "unresolved_gates": [
            "The Current operational weave may compose only existing authorised read projections with authored-synthetic inputs and no new route or source.",
            "Patient, clinical, product-derived, protected and production data; real databases and ordinary services remain closed.",
            "Persistence, retention, provider calls, external retrieval, product runtime and new routes remain closed.",
            "Commands, writes, deployment, production, release, Pages, protected refs and protected evidence remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 216 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 217
        graph["updated_at"] = UPDATED_AT
        _write(GRAPH, graph)
    elif graph["graph_revision"] == 217 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
    else:
        raise SystemExit("Unexpected Context Fabric contract Continuity predecessor")

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "First executable Context Fabric grammar",
        "outcome": (
            "The provider-free authored-synthetic authority, scope, Memory "
            "Bank, weave and same-packet proofreader contract passes."
        ),
        "evidence": [PLAN, DESIGN, THREAT, SCHEMA, EVIDENCE, REVIEW, CLOSEOUT, ACCEPTANCE],
    }
    if (
        compass["map_revision"] == 198
        and compass["source_graph_revision"] == 216
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 199
        and compass["source_graph_revision"] == 217
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected Context Fabric contract Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "The first provider-free authored-synthetic Fabric and Memory Bank contract is accepted at exact reviewed source HEAD.",
                "The Current operational weave may compose only existing authorised read projections without a new product route or source.",
                "Separately gate patient, clinical or product data, persistence or retention, provider or external retrieval, product runtime, commands, deployment, production and release.",
            ]
            for item in (PLAN, DESIGN, THREAT, EVIDENCE, REVIEW, CLOSEOUT, ACCEPTANCE):
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Context Fabric contract accepted; Current operational weave next",
        "why_now": (
            "Closed schemas, deterministic narrowing, portable evidence and a "
            "fresh exact-head independent veto all pass."
        ),
        "outcome": (
            "The first unmounted provider-free Fabric and Memory Bank contract "
            "is accepted without opening data, runtime or command surfaces."
        ),
        "unlocks": [
            "Compose existing Diary, waiting-room, directory and session read projections in the provider-free Current operational weave.",
            "Retain the API Spine read/command separation and same-packet proofreader boundary.",
        ],
        "does_not_solve": [
            "Patient, clinical or product-data access, historical retention or external evidence retrieval.",
            "Provider-model memory, product runtime, persistence, commands, deployment or production.",
            "Release, Pages, protected evidence or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 217 / Compass 199. The first provider-free "
        "Practice Context Fabric and Bureau Memory Bank contract passes at an "
        "exact independently reviewed HEAD. The Current operational weave is next."
    )
    limit = (
        "Context Fabric contract acceptance proves an unmounted provider-free "
        "authored-synthetic grammar only; it creates no product, data, persistence, "
        "provider, command, deployment or protected authority."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 199
    compass["source_graph_revision"] = 217
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
