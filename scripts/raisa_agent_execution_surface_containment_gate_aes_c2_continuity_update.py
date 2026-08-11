"""Advance Continuity and Compass for accepted AES-C2 broker simulation."""

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
NODE_ID = "raisa-agent-execution-surface-containment-gate-aes-c2"
PARENT = "raisa-agent-execution-surface-containment-gate-aes-c1"
SOURCE_HEAD = "d54f0476448f1218cd55477d42b958721359eae8"
UPDATED_AT = "2026-08-11T00:00:00Z"
PLAN = "docs/raisa-agent-execution-surface-containment-gate-aes-c2-provider-free-broker-simulator-plan.md"
THREAT = "docs/security/raisa-agent-execution-surface-containment-gate-aes-c2-provider-free-broker-simulator-threat-model-delta.md"
CLOSEOUT = "docs/raisa-agent-execution-surface-containment-gate-aes-c2-provider-free-broker-simulator-closeout.md"
BASE = "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/"
CONTRACT = BASE + "broker-simulator-contract.json"
SCHEMA = BASE + "broker-simulator-contract.schema.json"
SCENARIOS = BASE + "authored-synthetic-broker-simulator-scenarios.json"
EVIDENCE = BASE + "provider-free-broker-simulator-evidence.json"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-aes-c2-provider-free-broker-simulator-sol-acceptance.md"
PREPLANNING = "orchestration/agent_inbox/codex/raisa-aes-c2-provider-free-broker-simulator-preplanning-receipt.json"
PREVERIFIER = "orchestration/agent_inbox/codex/raisa-aes-c2-pre-verifier-acceptance-receipt.json"
PRECOMMIT = "orchestration/agent_inbox/codex/raisa-aes-c2-precommit-receipt.json"
REVIEW = "orchestration/agent_inbox/antigravity/raisa-aes-c2-provider-free-broker-simulator-review-receipt.json"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-11--aes-c2-provider-free-broker-simulator.md"
TEST = "tests/test_raisa_agent_execution_surface_containment_gate_aes_c2.py"
CONTINUITY_TEST = "tests/test_raisa_agent_execution_surface_containment_gate_aes_c2_continuity.py"
UPDATER = "scripts/raisa_agent_execution_surface_containment_gate_aes_c2_continuity_update.py"


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
        PREVERIFIER,
        PRECOMMIT,
        REVIEW,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Raisa Agent Execution Surface AES-C2 provider-free inert broker simulator",
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
                "AES-C2 is authored-synthetic and provider-free; its only adapter is one statically selected pure in-process function with no external effect.",
                "The work cell receives no lease, registry or credential fixture and cannot select capability, adapter, destination, method, implementation or executable.",
                "GraphQL remains read-only, events signal fresh reads, and REST/OpenAPI commands remain separately authorized and human/policy gated.",
            ],
        },
        "decisions": [
            {
                "id": "accept-aes-c2-provider-free-broker-simulator",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept exact broker-owned identity, custody, control-state recheck and budget commit over one pure inert function and 26 authored-synthetic scenarios.",
            }
        ],
        "claim_scope": [
            "Two exact simulations release, four attempts are not dispatched and 20 stop; the pure function is actually called exactly three times.",
            "All 18 hostile attempt/result mutations and 14 hostile contract mutations reject without a released simulation.",
            "The broker owns operation identity, current-control recheck, cumulative budget commit and the private synthetic noncredential fixture.",
            "The result proves in-process inert simulation, not a real runtime broker, process/container isolation, real credential custody, provider behavior, product-data safety or command safety.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [THREAT, CONTRACT, SCHEMA, SCENARIOS, EVIDENCE],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING, PREVERIFIER, PRECOMMIT, REVIEW],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "AES-C3 provider-free hostile containment rehearsal has not yet been frozen or executed.",
            "No real runtime broker, work-cell process, container, adapter, provider, product context, database/source, filesystem, network, executable tool or command is opened.",
            "Protected evidence, patient/clinical/product data, credentials, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 238 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 239
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 239 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected AES-C2 Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove broker-owned inert dispatch before hostile containment or any occupied capability",
        "outcome": "AES-C2 passes 26 authored-synthetic scenarios and 32 hostile mutations with exactly three pure calls and zero external effect; AES-C3 hostile containment is next.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 220
        and compass["source_graph_revision"] == 238
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 221
        and compass["source_graph_revision"] == 239
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected AES-C2 Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Serial database durability, architecture-health review, bounded conformance repair, AES-C0 architecture, AES-C1 admission and AES-C2 inert broker simulation pass.",
                "Freeze and execute AES-C3 provider-free hostile containment before process isolation or any occupied capability descendant.",
                "Keep product/patient data, providers, real credentials, external adapters, operational persistence, tools and commands separately gated.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "AES-C2 inert broker simulation accepted; AES-C3 hostile containment next",
        "why_now": "AES-C1 proved exact admission, allowing the smallest broker-owned pure dispatch and custody boundary to be rehearsed before adversarial containment.",
        "outcome": "All 26 canonical scenarios and 32 hostile mutations pass fail-closed; exactly three pure calls occur with zero external effect, provider call or product/patient data.",
        "unlocks": [
            "Freshly rehydrate and freeze AES-C3 provider-free hostile containment against the exact AES-C0/C1/C2 contracts.",
            "Challenge local-file, template/deserialization, metadata/credential probing, arbitrary or encoded egress, cumulative probing, stale lease and cross-generation replay surfaces.",
            "Preserve broker-owned operation identity, current-state recheck, budget commit and zero external effect throughout the hostile rehearsal.",
        ],
        "does_not_solve": [
            "Real runtime broker, process/container/kernel isolation, real adapters or occupied work cells.",
            "Provider calls, patient/product/clinical data, database/source access, watcher/listener or operational persistence.",
            "Real credentials, IAM, metadata, generic network, filesystem capability, executable tools, routes or commands.",
            "Deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 239 / Compass 221. AES-C2 passes as an exact, "
        "provider-free inert broker simulation: two released simulations, four "
        "non-dispatches, 20 terminal stops and 32 hostile mutations with exactly "
        "three pure calls and zero external effect. AES-C3 hostile containment is "
        "next; product, provider, data, credential, filesystem, tool, command and "
        "protected boundaries remain closed."
    )
    limit = (
        "AES-C2 proves broker-owned in-process inert dispatch over authored-synthetic objects, not real runtime containment, credential custody, adapter safety or product-data safety."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 239
    compass["map_revision"] = 221
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
