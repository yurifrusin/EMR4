"""Advance Continuity and Compass for accepted AES-C0 architecture."""

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
NODE_ID = "raisa-agent-execution-surface-containment-gate-aes-c0"
PARENT = "raisa-codebase-conformance-repair"
SOURCE_HEAD = "01d355f42df5981341196f3aa0caec2cccce7a2d"
UPDATED_AT = "2026-08-11T00:00:00Z"
PLAN = "docs/raisa-agent-execution-surface-containment-gate-aes-c0-plan.md"
ARCHITECTURE = (
    "docs/raisa-agent-execution-surface-containment-gate-aes-c0-architecture.md"
)
THREAT = (
    "docs/security/"
    "raisa-agent-execution-surface-containment-gate-aes-c0-threat-model-delta.md"
)
CLOSEOUT = "docs/raisa-agent-execution-surface-containment-gate-aes-c0-closeout.md"
BASE = (
    "orchestration/continuity/"
    "raisa-agent-execution-surface-containment-gate-aes-c0/"
)
CONTRACT = BASE + "architecture-contract.json"
SCHEMA = BASE + "architecture-contract.schema.json"
EXAMPLES = BASE + "authored-synthetic-contract-examples.json"
EVIDENCE = BASE + "provider-free-acceptance-evidence.json"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-aes-c0-architecture-contract-sol-acceptance.md"
)
PREPLANNING = (
    "orchestration/agent_inbox/codex/"
    "raisa-aes-c0-architecture-contract-preplanning-receipt.json"
)
PREACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-aes-c0-architecture-contract-preacceptance-receipt.json"
)
PRECOMMIT = (
    "orchestration/agent_inbox/codex/"
    "raisa-aes-c0-architecture-contract-precommit-receipt.json"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-11--aes-c0-architecture-contract.md"
)
TEST = "tests/test_raisa_agent_execution_surface_containment_gate_aes_c0.py"
CONTINUITY_TEST = (
    "tests/"
    "test_raisa_agent_execution_surface_containment_gate_aes_c0_continuity.py"
)
UPDATER = (
    "scripts/"
    "raisa_agent_execution_surface_containment_gate_aes_c0_continuity_update.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        ARCHITECTURE,
        THREAT,
        CONTRACT,
        SCHEMA,
        EXAMPLES,
        EVIDENCE,
        CLOSEOUT,
        ACCEPTANCE,
        PREPLANNING,
        PREACCEPTANCE,
        PRECOMMIT,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Raisa Agent Execution Surface AES-C0 architecture contract",
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
                "AES-C0 is declarative, provider-free and unmounted; it opens no runtime or product surface.",
                "The work cell receives no capability lease, reusable credential, generic egress, database/source, tool or command authority.",
                "GraphQL remains read-only, events signal fresh reads, and REST/OpenAPI commands remain separately authorized and human/policy gated.",
            ],
        },
        "decisions": [
            {
                "id": "accept-aes-c0-architecture-contract",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept six closed containment messages and 37 hostile fail-closed mutations before any AES runtime descendant.",
            }
        ],
        "claim_scope": [
            "Six closed typed records bind immutable generation authority, broker-side leases, cumulative budgets, deterministic decisions, external revocation and minimized evidence.",
            "Only provider inference, authoritative read and inert authored-synthetic adapter are representable as future leaseable classes.",
            "Provider failure is explicit intelligence_unavailable with no silent provider, model or deterministic-equivalent fallback.",
            "The result is contract coherence and authored-synthetic hostile testing, not runtime containment or product-data safety.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [ARCHITECTURE, THREAT, CONTRACT, SCHEMA, EXAMPLES, EVIDENCE],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING, PREACCEPTANCE, PRECOMMIT],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "AES-C1 provider-free admission rehearsal has not yet been frozen or executed.",
            "No capability broker, work-cell process, adapter, provider, product context, tool or command is implemented or opened.",
            "Protected evidence, patient/clinical/product data, credentials, database/source access, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 236 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 237
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 237 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected AES-C0 Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Freeze deterministic authority before executable Bureau capability",
        "outcome": "AES-C0 closed messages and hostile contract tests pass; AES-C1 provider-free admission rehearsal is next after the requested fresh-window pause.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 218
        and compass["source_graph_revision"] == 236
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 219
        and compass["source_graph_revision"] == 237
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected AES-C0 Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Serial database durability, architecture-health review, bounded conformance repair and AES-C0 architecture pass.",
                "Freeze and execute AES-C1 provider-free admission before any broker simulation or occupied capability descendant.",
                "Keep product/patient data, providers, operational persistence, tools and commands separately gated.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "AES-C0 authority grammar accepted; fresh-window pause before AES-C1",
        "why_now": "The prerequisite durability, architectural-health and conformance work passed, allowing the selected containment boundary to be frozen without opening runtime capability.",
        "outcome": "Six closed containment records and all 37 hostile mutations now pass as provider-free architecture evidence.",
        "unlocks": [
            "In a fresh task window, freeze AES-C1 authored-synthetic admission scenarios against the exact AES-C0 contract.",
            "Prove manifest/grant/lease intersection, immutable generation and default denial without implementing a runtime broker.",
            "Continue the planned containment sequence under standing authority after the requested context handoff.",
        ],
        "does_not_solve": [
            "Capability-broker implementation, hostile process isolation or occupied work cells.",
            "Applied migration, operational database/source access, watcher/listener or persistence.",
            "Patient/product/clinical data, providers, tools, routes or commands.",
            "Deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 237 / Compass 219. AES-C0 passes as a closed, "
        "provider-free and unmounted Agent Execution Surface authority contract. "
        "Work is explicitly paused for a fresh task window before AES-C1; product, "
        "provider, data, runtime, tool, command and protected boundaries remain closed."
    )
    limit = (
        "AES-C0 proves closed contract coherence and finite hostile mutations, not runtime containment, broker correctness or product-data safety."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 237
    compass["map_revision"] = 219
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
