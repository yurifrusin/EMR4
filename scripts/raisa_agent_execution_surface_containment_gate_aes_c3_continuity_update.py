"""Advance Continuity and Compass for accepted AES-C3 hostile containment."""

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
NODE_ID = "raisa-agent-execution-surface-containment-gate-aes-c3"
PARENT = "raisa-agent-execution-surface-containment-gate-aes-c2"
SOURCE_HEAD = "c45ff191af420b801e9917a7efc69c17aeb5698b"
UPDATED_AT = "2026-08-11T00:00:00Z"
PLAN = "docs/raisa-agent-execution-surface-containment-gate-aes-c3-provider-free-hostile-containment-plan.md"
THREAT = "docs/security/raisa-agent-execution-surface-containment-gate-aes-c3-provider-free-hostile-containment-threat-model-delta.md"
CLOSEOUT = "docs/raisa-agent-execution-surface-containment-gate-aes-c3-provider-free-hostile-containment-closeout.md"
BASE = "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c3/"
CONTRACT = BASE + "containment-rehearsal-contract.json"
SCHEMA = BASE + "containment-rehearsal-contract.schema.json"
SCENARIOS = BASE + "authored-synthetic-hostile-containment-scenarios.json"
EVIDENCE = BASE + "provider-free-hostile-containment-evidence.json"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-aes-c3-provider-free-hostile-containment-sol-acceptance.md"
PREPLANNING = "orchestration/agent_inbox/codex/raisa-aes-c3-hostile-containment-preplanning-receipt.json"
POSTCOMPACTION = "orchestration/agent_inbox/codex/raisa-aes-c3-pre-verifier-postcompaction-receipt.json"
PREVERIFIER = (
    "orchestration/agent_inbox/codex/raisa-aes-c3-pre-verifier-acceptance-receipt.json"
)
PRECOMMIT = "orchestration/agent_inbox/codex/raisa-aes-c3-precommit-receipt.json"
REVIEW = "orchestration/agent_inbox/antigravity/raisa-aes-c3-provider-free-hostile-containment-review-receipt.json"
RECOVERY = "orchestration/agent_inbox/codex/raisa-aes-c3-sol-recovery.md"
ERROR_REVISION = "docs/ariadne-agent-error-correction-register-revision-224.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-11--aes-c3-provider-free-hostile-containment.md"
TEST = "tests/test_raisa_agent_execution_surface_containment_gate_aes_c3.py"
CONTINUITY_TEST = (
    "tests/test_raisa_agent_execution_surface_containment_gate_aes_c3_continuity.py"
)
UPDATER = (
    "scripts/raisa_agent_execution_surface_containment_gate_aes_c3_continuity_update.py"
)


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
        POSTCOMPACTION,
        PREVERIFIER,
        PRECOMMIT,
        REVIEW,
        RECOVERY,
        ERROR_REVISION,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Raisa Agent Execution Surface AES-C3 provider-free hostile containment",
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
                "AES-C3 is authored-synthetic, provider-free and pure; hostile references remain inert strings and no referenced resource is opened.",
                "The only executed adapter is one statically selected pure Python function; no real runtime, provider, credential, network, filesystem capability, database/source, tool or command is opened.",
                "GraphQL remains read-only, events signal fresh reads, and REST/OpenAPI commands remain separately authorized and human/policy gated.",
            ],
        },
        "decisions": [
            {
                "id": "accept-aes-c3-provider-free-hostile-containment",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept exact hostile-content inertness, structural rejection, output non-release, cumulative latching and stale-authority binding over 61 pure authored-synthetic scenarios.",
            }
        ],
        "claim_scope": [
            "Exactly 21 scenarios are contained, 15 reject and 25 stop; 28 pure calls make 21 digest-only releases.",
            "All 33 hostile attempt mutations and 18 contract mutations fail closed with zero released result.",
            "Opaque content has no decoder, interpreter, dereference, transport or operation-selection path; structural command-shaped content rejects before a call.",
            "The result proves only the pure authored-synthetic rehearsal, not semantic injection detection, real runtime/process/container isolation, credential/provider behaviour, product-data safety or command safety.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [THREAT, CONTRACT, SCHEMA, SCENARIOS, EVIDENCE],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING, POSTCOMPACTION, PREVERIFIER, PRECOMMIT, REVIEW],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER, RECOVERY, ERROR_REVISION],
        },
        "unresolved_gates": [
            "AES-C4 occupied authored-synthetic provider proof requires a newly frozen exact provider/model, region, identity, data, call, cost, isolation, proofreader, cleanup and no-fallback envelope; no current authority supplies it.",
            "No real runtime broker, work-cell process, container, adapter, provider, product context, database/source, filesystem, network, credential, executable tool or command is opened.",
            "Protected evidence, patient/clinical/product data, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 239 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 240
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 240 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected AES-C3 Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove hostile-content, cumulative-stop and stale-authority containment before any occupied provider capability",
        "outcome": "AES-C3 passes 61 authored-synthetic scenarios and 51 hostile mutations with 28 pure calls, 21 digest-only releases and zero external effect; AES-C4 is closed pending a new exact occupied-provider envelope.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 221
        and compass["source_graph_revision"] == 239
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 222
        and compass["source_graph_revision"] == 240
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected AES-C3 Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Serial database durability, architecture-health review, bounded conformance repair and AES-C0 through AES-C3 pass.",
                "Obtain Yuri's exact provider/model, region, identity, authored-synthetic data, call, cost, isolation, proofreader, cleanup and no-fallback envelope before AES-C4.",
                "Keep product/patient data, real credentials, external adapters, operational persistence, tools and commands separately gated.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "AES-C3 hostile containment accepted; AES-C4 occupied-provider envelope requires Yuri",
        "why_now": "AES-C2 proved exact inert dispatch, allowing the hostile-content, cumulative-stop and replay boundary to be tested before any occupied provider capability.",
        "outcome": "All 61 canonical scenarios and 51 hostile mutations pass fail closed; exactly 28 pure calls and 21 digest-only releases occur with zero external effect.",
        "unlocks": [
            "Ask Yuri to choose or authorize the exact current AES-C4 occupied-provider envelope before planning or dispatch.",
            "If authorized, freeze the narrowest authored-synthetic provider proof with exact provider/model, region, identity, data, call, cost, isolation, proofreader, cleanup and no-fallback controls.",
            "Preserve AES-C0/C1/C2/C3 authority, custody, current-state, egress and hostile-containment controls throughout any later occupied proof.",
        ],
        "does_not_solve": [
            "Semantic prompt-injection detection or real runtime/process/container/kernel isolation.",
            "Provider behaviour, patient/product/clinical data safety, database/source access, watcher/listener or operational persistence.",
            "Real credentials, IAM, metadata, generic network, filesystem capability, executable tools, routes or commands.",
            "Deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 240 / Compass 222. AES-C3 passes as an exact, "
        "provider-free pure hostile-containment rehearsal: 21 contained, 15 "
        "rejected and 25 stopped scenarios, 51 hostile mutations, 28 pure calls "
        "and 21 digest-only releases with zero external effect. AES-C4 remains "
        "closed until Yuri supplies a new exact occupied-provider envelope."
    )
    limit = "AES-C3 proves pure authored-synthetic structural and stale-authority containment, not semantic injection detection, real runtime isolation, provider behaviour or product-data safety."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 240
    compass["map_revision"] = 222
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
