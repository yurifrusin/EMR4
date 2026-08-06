"""Idempotently accept the Practice Context Fabric Current operational weave."""

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
NODE_ID = "raisa-provider-free-practice-context-fabric-current-operational-weave"
PARENT = "raisa-provider-free-practice-context-fabric-bureau-memory-contract"
SOURCE_HEAD = "d8bc059212e65a6ed2d7ac8d57734096d14b9139"
UPDATED_AT = "2026-08-06T03:54:05Z"
PLAN = "docs/raisa-provider-free-practice-context-fabric-current-operational-weave-plan.md"
DESIGN = "docs/raisa-provider-free-practice-context-fabric-current-operational-weave-design.md"
THREAT = (
    "docs/security/raisa-provider-free-practice-context-fabric-current-"
    "operational-weave-threat-model-delta.md"
)
SCHEMA = (
    "orchestration/continuity/raisa-provider-free-practice-context-fabric-"
    "current-operational-weave/operational-weave-contract.schema.json"
)
EVIDENCE = (
    "orchestration/continuity/raisa-provider-free-practice-context-fabric-"
    "current-operational-weave/provider-free-acceptance-evidence.json"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-context-fabric-current-"
    "operational-weave-review-1-receipt.json"
)
RECONCILIATION = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-current-operational-"
    "weave-review-count-reconciliation-receipt.json"
)
CLOSEOUT = (
    "docs/raisa-provider-free-practice-context-fabric-current-operational-"
    "weave-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-practice-context-"
    "fabric-current-operational-weave-sol-acceptance.md"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free Practice Context Fabric Current operational weave",
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
                        "Define the narrow provider-free authored-synthetic "
                        "patient-free temporal weave for bounded committed-event "
                        "index and historical-snapshot semantics; no real event "
                        "transport, database, persistence, product route or command."
                    ),
                }
            ],
            "notes": [
                "The accepted weave is a pure function over four sealed synthetic read shapes.",
                "The four source families remain distinct and command authority remains false.",
                "The review's test-count underreport is reconciled to 155 exact passing tests.",
                "The next descendant remains patient-free, provider-free and unmounted.",
            ],
        },
        "decisions": [
            {
                "id": "accept-practice-context-fabric-current-operational-weave",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept exact scope narrowing, four-source composition, "
                    "cross-source coherence and atomic same-packet proofreading."
                ),
            }
        ],
        "claim_scope": [
            "Four authored-synthetic existing read shapes compose into one typed expiring frame set.",
            "Source identity, practice/session/location scope, field minimisation and freshness remain fail closed.",
            "The same-packet proofreader independently recomputes need, grant, source, weave and frame-set digests.",
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
                    "The weave consumes read shapes only and does not alter the "
                    "accepted combined-intent proposal or command path."
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
                    "Current source revisions remain bounded reads; no context "
                    "frame or event becomes current truth or command authority."
                ),
            },
        ],
        "evidence": {
            "plans": [PLAN, DESIGN, THREAT],
            "findings": [SCHEMA, EVIDENCE],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [REVIEW, RECONCILIATION],
            "tests": [
                "tests/test_bernie_reception_one_combined_scope.py",
                "tests/test_reception_one_availability_reconciliation.py",
                "tests/test_raisa_provider_free_practice_context_fabric_bureau_memory_contract.py",
                "tests/test_raisa_provider_free_practice_context_fabric_current_operational_weave.py",
                "tests/test_raisa_practice_context_fabric_direction.py",
                "tests/test_api_spine_artifacts.py",
                "tests/test_raisa_provider_free_practice_context_fabric_current_operational_weave_continuity.py",
            ],
        },
        "unresolved_gates": [
            "The patient-free temporal weave may use only authored-synthetic committed-event and historical-snapshot shapes under a separately frozen contract.",
            "Patient, clinical, product-derived, protected and production data; real databases, event transport and ordinary services remain closed.",
            "Persistence, operational retention, provider calls, external retrieval, product runtime and new routes remain closed.",
            "Commands, writes, deployment, production, release, Pages, protected refs and protected evidence remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 217 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 218
        graph["updated_at"] = UPDATED_AT
        _write(GRAPH, graph)
    elif graph["graph_revision"] == 218 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
    else:
        raise SystemExit("Unexpected Current operational weave Continuity predecessor")

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Current authorised operational read composition",
        "outcome": (
            "Four provider-free authored-synthetic current read families compose "
            "into one scoped, expiring and same-packet-proofread frame set."
        ),
        "evidence": [
            PLAN,
            DESIGN,
            THREAT,
            SCHEMA,
            EVIDENCE,
            REVIEW,
            RECONCILIATION,
            CLOSEOUT,
            ACCEPTANCE,
        ],
    }
    if (
        compass["map_revision"] == 199
        and compass["source_graph_revision"] == 217
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 200
        and compass["source_graph_revision"] == 218
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected Current operational weave Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "The provider-free authored-synthetic Fabric contract and Current operational weave are accepted at exact independently reviewed source HEADs.",
                "The patient-free temporal weave must freeze explicit tenancy, retention, replay and supersession semantics without opening persistence or product runtime.",
                "Separately gate patient, clinical or product data, real event transport, persistence, provider or external retrieval, commands, deployment, production and release.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Current operational weave accepted; patient-free temporal weave next",
        "why_now": (
            "Exact four-source composition, scope narrowing, coherence, expiry "
            "and same-packet proofreading pass deterministic and independent review."
        ),
        "outcome": (
            "The first current operational Context Fabric bundle is accepted "
            "without opening product data, persistence, runtime or commands."
        ),
        "unlocks": [
            "Define the provider-free patient-free temporal weave for bounded committed-event indexing and historical snapshot semantics.",
            "Preserve source distinctions, explicit expiry and the API Spine read/command boundary.",
        ],
        "does_not_solve": [
            "Patient, clinical or product-data access, real historical retention or external evidence retrieval.",
            "Provider-model memory, product runtime, persistence, commands, deployment or production.",
            "Release, Pages, protected evidence or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 218 / Compass 200. The provider-free Practice "
        "Context Fabric Current operational weave passes at an exact independently "
        "reviewed HEAD. The patient-free temporal weave is next."
    )
    limit = (
        "Current operational weave acceptance proves pure provider-free authored-"
        "synthetic composition only; it creates no patient, product, persistence, "
        "provider, runtime, command, deployment or protected authority."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 200
    compass["source_graph_revision"] = 218
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
