"""Advance Continuity and Compass for accepted AES-C4 provider proof."""

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
NODE_ID = "raisa-agent-execution-surface-containment-gate-aes-c4"
PARENT = "raisa-agent-execution-surface-containment-gate-aes-c3"
SOURCE_HEAD = "e569da0a9081117b799e9437d8b7025230e2162b"
UPDATED_AT = "2026-08-11T00:00:00Z"
PLAN = "docs/raisa-agent-execution-surface-containment-gate-aes-c4-bounded-occupied-provider-proof-plan.md"
REBIND = "docs/raisa-agent-execution-surface-containment-gate-aes-c4-preexecution-factual-rebind.md"
THREAT = "docs/security/raisa-agent-execution-surface-containment-gate-aes-c4-bounded-occupied-provider-proof-threat-model-delta.md"
CLOSEOUT = "docs/raisa-agent-execution-surface-containment-gate-aes-c4-bounded-occupied-provider-proof-closeout.md"
BASE = "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c4/"
ENVELOPE = BASE + "provider-envelope.json"
ENVELOPE_SCHEMA = BASE + "provider-envelope.schema.json"
PREFLIGHT = BASE + "live-preexecution-cloud-preflight.json"
EVIDENCE = BASE + "occupied-provider-proof-evidence.json"
LEDGER = BASE + "occupied-provider-proof-ledger.json"
DRY_EVIDENCE = BASE + "provider-free-factual-rebind-evidence.json"
DRY_LEDGER = BASE + "provider-free-factual-rebind-ledger.json"
INVALID_EVIDENCE = BASE + "provider-free-factual-rebind-invalid-source-evidence.json"
INVALID_LEDGER = BASE + "provider-free-factual-rebind-invalid-source-ledger.json"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-aes-c4-bounded-occupied-provider-proof-sol-acceptance.md"
POSTCOMPACTION = "orchestration/agent_inbox/codex/raisa-aes-c4-provider-proof-postcompaction-3-receipt.json"
PRECOMMIT = "orchestration/agent_inbox/codex/raisa-aes-c4-factual-rebind-evidence-precommit-receipt.json"
WORKTREE_PREFLIGHT = "orchestration/agent_inbox/codex/raisa-aes-c4-provider-proof-rebind-review-worktree-preflight.json"
PREDISPATCH = "orchestration/agent_inbox/codex/raisa-aes-c4-provider-proof-rebind-review-predispatch-receipt.json"
PREVERIFIER = "orchestration/agent_inbox/codex/raisa-aes-c4-provider-proof-rebind-pre-verifier-acceptance-receipt.json"
REVIEW = "orchestration/agent_inbox/antigravity/raisa-aes-c4-provider-proof-rebind-review-receipt.json"
PACKET = "orchestration/agent_inbox/codex/raisa-aes-c4-provider-proof-rebind-review-packet.md"
ERROR_REVISION = "docs/ariadne-agent-error-correction-register-revision-227.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-11--aes-c4-bounded-occupied-provider-proof.md"
TEST = "tests/test_raisa_agent_execution_surface_containment_gate_aes_c4.py"
CONTINUITY_TEST = (
    "tests/test_raisa_agent_execution_surface_containment_gate_aes_c4_continuity.py"
)
UPDATER = (
    "scripts/raisa_agent_execution_surface_containment_gate_aes_c4_continuity_update.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        REBIND,
        THREAT,
        ENVELOPE,
        ENVELOPE_SCHEMA,
        DRY_EVIDENCE,
        DRY_LEDGER,
        INVALID_EVIDENCE,
        INVALID_LEDGER,
        PREFLIGHT,
        EVIDENCE,
        LEDGER,
        CLOSEOUT,
        ACCEPTANCE,
        POSTCOMPACTION,
        PRECOMMIT,
        WORKTREE_PREFLIGHT,
        PREDISPATCH,
        PREVERIFIER,
        REVIEW,
        PACKET,
        ERROR_REVISION,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Raisa Agent Execution Surface AES-C4 bounded occupied provider proof",
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
                "AES-C4 consumed exactly one newly authored-synthetic Sydney Vertex call; its ledger is terminal and grants no continuing provider authority.",
                "The model received no product/patient context, credential, provider tool, database/source, filesystem capability or command authority.",
                "GraphQL remained read-only and unused; product mutations remain separately authorized and human/policy-gated REST/OpenAPI commands.",
            ],
        },
        "decisions": [
            {
                "id": "accept-aes-c4-bounded-occupied-provider-proof",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept one exact broker-admitted authored-synthetic Sydney Vertex call, deterministic four-field release, terminal accounting and complete cleanup.",
            }
        ],
        "claim_scope": [
            "Exactly one gemini-2.5-flash call reached the Australia Southeast 1 hostname with HTTP 200/STOP and no retry, redirect, fallback or provider tool.",
            "The deterministic proofreader released exactly four nonce-bound fields with command_authority false.",
            "The one-call ledger is consumed; every lease, alias and token is revoked; no broker listener/process, temporary runtime or reusable capability remains.",
            "The result proves the configured and observed Sydney path and exact authored-synthetic containment only, not physical or sovereign processing, product-data safety, reusable runtime or command safety.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, REBIND],
            "findings": [
                THREAT,
                ENVELOPE,
                ENVELOPE_SCHEMA,
                DRY_EVIDENCE,
                DRY_LEDGER,
                INVALID_EVIDENCE,
                INVALID_LEDGER,
                PREFLIGHT,
                EVIDENCE,
                LEDGER,
            ],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                POSTCOMPACTION,
                PRECOMMIT,
                WORKTREE_PREFLIGHT,
                PREDISPATCH,
                PREVERIFIER,
                REVIEW,
            ],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER, PACKET, ERROR_REVISION],
        },
        "unresolved_gates": [
            "AES-C5 product-runtime admission requires a separately frozen privacy, identity, retention and product-data authority plus one exact source and one exact purpose.",
            "No continuing provider call, product read, database/source adapter, filesystem capability, provider tool, generic network, command/write or reusable runtime is opened.",
            "Protected evidence, patient/clinical/product-derived data, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 240 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 241
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 241 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected AES-C4 Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove one exact occupied provider crossing under the external capability broker before any product-derived Bureau context",
        "outcome": "AES-C4 passes one authored-synthetic Sydney Vertex call with exact typed release, terminal accounting and complete cleanup; AES-C5 remains closed at its product-data/source/purpose fork.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 222
        and compass["source_graph_revision"] == 240
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 223
        and compass["source_graph_revision"] == 241
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected AES-C4 Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Serial durability, architecture-health repair and AES-C0 through AES-C4 pass.",
                "Before AES-C5, Yuri must select or authorize one exact product source and purpose and freeze privacy, identity, retention and product-data boundaries.",
                "Keep every command/write, broader product context, reusable runtime, deployment and production surface separately gated.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "AES-C4 occupied authored-synthetic provider containment accepted; AES-C5 awaits its first product-data choice",
        "why_now": "AES-C3 proved hostile containment, and Yuri supplied the exact Sydney Vertex authored-synthetic envelope needed for one consumed provider crossing.",
        "outcome": "One exact provider call returned HTTP 200/STOP, released four deterministic no-command fields, consumed its ledger and left no reusable capability or runtime residue.",
        "unlocks": [
            "Ask Yuri to nominate one exact real product source and one exact purpose for AES-C5, or request bounded alternatives.",
            "Freeze AES-C5 privacy, principal/identity, tenant, field, freshness, retention, proofreader, provider, cost, cleanup and no-command boundaries before any product read.",
            "Preserve AES-C0/C1/C2/C3/C4 authority, custody, current-state, egress, hostile-containment and terminal-ledger controls in any later product-runtime proof.",
        ],
        "does_not_solve": [
            "Patient, clinical, product-derived, practice, licensed or external-corpus data safety.",
            "Reusable provider/broker runtime, database/source adapters, watcher/listener, filesystem capability or provider-executed tools.",
            "Command/write safety, concurrency, general model safety, semantic prompt-injection detection or Australian physical/sovereign processing.",
            "Deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 241 / Compass 223. AES-C4 passes one exact, "
        "broker-admitted authored-synthetic Sydney Vertex call: HTTP 200/STOP, "
        "one deterministic four-field no-command release, a consumed no-retry "
        "ledger and complete cleanup. AES-C5 remains closed until Yuri selects "
        "or authorizes its first real product source, purpose and privacy boundary."
    )
    limit = "AES-C4 proves one exact authored-synthetic brokered provider crossing and cleanup, not physical or sovereign processing, product-data safety, reusable runtime or command safety."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 241
    compass["map_revision"] = 223
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
