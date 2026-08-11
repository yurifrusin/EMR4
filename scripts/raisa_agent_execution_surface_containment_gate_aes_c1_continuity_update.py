"""Advance Continuity and Compass for accepted AES-C1 admission rehearsal."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ariadne_compass


GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = "raisa-agent-execution-surface-containment-gate-aes-c1"
PARENT = "raisa-agent-execution-surface-containment-gate-aes-c0"
SOURCE_HEAD = "285e60216cf22907e8a0f5596ece11f74f455c81"
UPDATED_AT = "2026-08-11T00:00:00Z"
PLAN = "docs/raisa-agent-execution-surface-containment-gate-aes-c1-provider-free-admission-plan.md"
THREAT = "docs/security/raisa-agent-execution-surface-containment-gate-aes-c1-provider-free-admission-threat-model-delta.md"
CLOSEOUT = "docs/raisa-agent-execution-surface-containment-gate-aes-c1-provider-free-admission-closeout.md"
BASE = "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/"
CONTRACT = BASE + "admission-rehearsal-contract.json"
SCHEMA = BASE + "admission-rehearsal-contract.schema.json"
SCENARIOS = BASE + "authored-synthetic-admission-scenarios.json"
EVIDENCE = BASE + "provider-free-admission-evidence.json"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-aes-c1-provider-free-admission-sol-acceptance.md"
PREPLANNING = "orchestration/agent_inbox/codex/raisa-aes-c1-provider-free-admission-preplanning-receipt.json"
PREACCEPTANCE = "orchestration/agent_inbox/codex/raisa-aes-c1-preacceptance-receipt.json"
PRECOMMIT = "orchestration/agent_inbox/codex/raisa-aes-c1-precommit-receipt.json"
REVIEW = "orchestration/agent_inbox/antigravity/raisa-aes-c1-provider-free-admission-review-receipt.json"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-11--aes-c1-provider-free-admission.md"
TEST = "tests/test_raisa_agent_execution_surface_containment_gate_aes_c1.py"
CONTINUITY_TEST = "tests/test_raisa_agent_execution_surface_containment_gate_aes_c1_continuity.py"
UPDATER = "scripts/raisa_agent_execution_surface_containment_gate_aes_c1_continuity_update.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        CONTRACT,
        SCHEMA,
        SCENARIOS,
        EVIDENCE,
        CLOSEOUT,
        ACCEPTANCE,
        PREPLANNING,
        PREACCEPTANCE,
        PRECOMMIT,
        REVIEW,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Raisa Agent Execution Surface AES-C1 provider-free admission rehearsal",
        "kind": "foundation",
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
                "AES-C1 is authored-synthetic, provider-free and unmounted; an allow is an inert decision and executes nothing.",
                "The work cell receives no lease or credential and cannot select capability, adapter, destination, method or executable.",
                "GraphQL remains read-only, events signal fresh reads, and REST/OpenAPI commands remain separately authorized and human/policy gated.",
            ],
        },
        "decisions": [
            {
                "id": "accept-aes-c1-provider-free-admission",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept exact fail-closed manifest/grant/lease/current-authority admission over 45 unmounted authored-synthetic scenarios.",
            }
        ],
        "claim_scope": [
            "Two exact inert intersections allow, 25 scenarios deny and 18 scenarios stop; no admitted operation executes.",
            "All 24 hostile attempt mutations and eight hostile contract mutations reject with zero admission.",
            "Immutable generation, current authority, revocation, kill and all 19 cumulative budget counters are checked before admission.",
            "The result proves pure admission behavior, not runtime broker, adapter custody, provider behavior or product-data safety.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [THREAT, CONTRACT, SCHEMA, SCENARIOS, EVIDENCE],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING, PREACCEPTANCE, PRECOMMIT, REVIEW],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "AES-C2 provider-free broker simulator has not yet been frozen or executed.",
            "No runtime broker, work-cell process, real adapter, provider, product context, database/source, network, executable tool or command is opened.",
            "Protected evidence, patient/clinical/product data, credentials, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 237 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 238
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 238 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected AES-C1 Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove exact admission before mounting any broker or adapter",
        "outcome": "AES-C1 passes 45 authored-synthetic admission scenarios and 32 hostile mutations with zero execution; AES-C2 provider-free broker simulation is next.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 219
        and compass["source_graph_revision"] == 237
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 220
        and compass["source_graph_revision"] == 238
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected AES-C1 Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Serial database durability, architecture-health review, bounded conformance repair, AES-C0 architecture and AES-C1 admission pass.",
                "Freeze and execute AES-C2 provider-free broker simulation before hostile process containment or any occupied capability descendant.",
                "Keep product/patient data, providers, credentials, external adapters, operational persistence, tools and commands separately gated.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "AES-C1 exact admission accepted; AES-C2 inert broker simulation next",
        "why_now": "AES-C0 froze the authority grammar, allowing the smallest admission intersection to be rehearsed without mounting a runtime or adapter.",
        "outcome": "All 45 canonical scenarios and 32 hostile mutations pass fail-closed with zero execution, provider calls or product/patient data.",
        "unlocks": [
            "Freshly rehydrate and freeze AES-C2 provider-free broker simulation around exactly one inert allowlisted authored-synthetic adapter.",
            "Prove that the work cell never receives a credential or selects destination, method or executable.",
            "Preserve broker-owned operation identity and exact AES-C1 admission before any inert simulated dispatch.",
        ],
        "does_not_solve": [
            "Real runtime broker, hostile process isolation, container/kernel security or occupied work cells.",
            "Provider calls, patient/product/clinical data, database/source access, watcher/listener or operational persistence.",
            "Credentials, IAM, metadata, generic network, executable tools, routes or commands.",
            "Deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 238 / Compass 220. AES-C1 passes as an exact, "
        "provider-free and unmounted admission rehearsal: two inert allows, 25 "
        "denials, 18 terminal stops and 32 hostile mutations with zero execution. "
        "AES-C2 inert broker simulation is next; product, provider, data, credential, "
        "tool, command and protected boundaries remain closed."
    )
    limit = (
        "AES-C1 proves deterministic unmounted admission over authored-synthetic objects, not runtime broker containment, adapter custody or product-data safety."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 238
    compass["map_revision"] = 220
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
