"""Advance Continuity and Compass for accepted AES-C5 product-runtime admission."""

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
NODE_ID = "raisa-agent-execution-surface-containment-gate-aes-c5"
PARENT = "raisa-agent-execution-surface-containment-gate-aes-c4"
SOURCE_HEAD = "4e5d96ada19c51432fa4db46c76e23c952147c52"
UPDATED_AT = "2026-08-11T00:00:00Z"
PLAN = "docs/raisa-agent-execution-surface-containment-gate-aes-c5-product-runtime-admission-plan.md"
THREAT = "docs/security/raisa-agent-execution-surface-containment-gate-aes-c5-product-runtime-admission-threat-model-delta.md"
CLOSEOUT = "docs/raisa-agent-execution-surface-containment-gate-aes-c5-product-runtime-admission-closeout.md"
BASE = "orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c5/"
ENVELOPE = BASE + "product-runtime-envelope.json"
ENVELOPE_SCHEMA = BASE + "product-runtime-envelope.schema.json"
LOCAL_CORE = BASE + "local-fake-core-evidence.json"
LOCAL_LIFECYCLE = BASE + "local-fake-lifecycle-evidence.json"
LOCAL_SOURCE_LEDGER = BASE + "local-fake-ledgers/source-ledger.json"
LOCAL_PROVIDER_LEDGER = BASE + "local-fake-ledgers/provider-ledger.json"
FACTS = BASE + "live-preexecution-factual-and-cli-check.json"
PREFLIGHT = BASE + "live-preexecution-cloud-preflight.json"
OCCUPIED_CORE = BASE + "occupied-core-evidence.json"
OCCUPIED_LIFECYCLE = BASE + "occupied-lifecycle-evidence.json"
OCCUPIED_SOURCE_LEDGER = BASE + "occupied-ledgers/source-ledger.json"
OCCUPIED_PROVIDER_LEDGER = BASE + "occupied-ledgers/provider-ledger.json"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-aes-c5-product-runtime-admission-sol-acceptance.md"
POSTCOMPACTION = "orchestration/agent_inbox/codex/raisa-aes-c5-postcompaction-2-receipt.json"
PREINTEGRATION = "orchestration/agent_inbox/codex/raisa-aes-c5-occupied-preintegration-receipt.json"
WORKER = "orchestration/agent_inbox/codex/raisa-aes-c5-deepseek-implementation-receipt.json"
CONFLICT = "orchestration/agent_inbox/codex/raisa-aes-c5-single-generation-destination-conflict-analysis.md"
WORKTREE_PREFLIGHT = "orchestration/agent_inbox/codex/raisa-aes-c5-gemini-review-worktree-preflight.json"
PREDISPATCH = "orchestration/agent_inbox/codex/raisa-aes-c5-gemini-veto-predispatch-receipt.json"
PREVERIFIER = "orchestration/agent_inbox/codex/raisa-aes-c5-pre-verifier-acceptance-receipt.json"
REVIEW = "orchestration/agent_inbox/antigravity/raisa-aes-c5-gemini-36-high-review-receipt.json"
PACKET = "orchestration/agent_inbox/codex/raisa-aes-c5-gemini-review-packet.md"
ERROR_REVISION = "docs/ariadne-agent-error-correction-register-revision-233.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-11--aes-c5-product-runtime-admission.md"
CORE = "scripts/raisa_agent_execution_surface_containment_gate_aes_c5_product_runtime_admission.py"
LOCAL = "scripts/raisa_agent_execution_surface_containment_gate_aes_c5_local_route.py"
TEST = "tests/test_raisa_agent_execution_surface_containment_gate_aes_c5.py"
LOCAL_TEST = "tests/test_raisa_agent_execution_surface_containment_gate_aes_c5_local_route.py"
PLAN_TEST = "tests/test_raisa_agent_execution_surface_containment_gate_aes_c5_plan.py"
CONTINUITY_TEST = "tests/test_raisa_agent_execution_surface_containment_gate_aes_c5_continuity.py"
UPDATER = "scripts/raisa_agent_execution_surface_containment_gate_aes_c5_continuity_update.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        ENVELOPE,
        ENVELOPE_SCHEMA,
        LOCAL_CORE,
        LOCAL_LIFECYCLE,
        LOCAL_SOURCE_LEDGER,
        LOCAL_PROVIDER_LEDGER,
        FACTS,
        PREFLIGHT,
        OCCUPIED_CORE,
        OCCUPIED_LIFECYCLE,
        OCCUPIED_SOURCE_LEDGER,
        OCCUPIED_PROVIDER_LEDGER,
        CLOSEOUT,
        ACCEPTANCE,
        POSTCOMPACTION,
        PREINTEGRATION,
        WORKER,
        CONFLICT,
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
        "title": "Raisa Agent Execution Surface AES-C5 product-runtime admission",
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
                "AES-C5 consumed exactly one authenticated authored-synthetic application-route read and exactly one Sydney Vertex call; both ledgers are terminal.",
                "The source and provider operations used separate one-grant, one-destination immutable generations with no lease or budget transfer.",
                "The released booking-context match is inert with command_authority false; no continuing product, database, provider, tool, command or runtime authority is opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-aes-c5-product-runtime-admission",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept one exact authenticated authored-synthetic practitioner-directory read, minimized provider crossing, deterministic no-command release, terminal accounting and exact cleanup.",
            }
        ],
        "claim_scope": [
            "Exactly one practice-scoped product route read returned three active authored-synthetic rows with unchanged database counts and exact disposable-schema cleanup.",
            "Exactly one gemini-2.5-flash call reached the Australia Southeast 1 hostname with HTTP 200/STOP and no retry, redirect, fallback or provider tool.",
            "Both generations exhausted and both ledgers are consumed; every lease, alias and token is revoked and no reusable process, listener or capability remains.",
            "The result proves the exact authored-synthetic application-route containment path, not real-person or patient-data safety, production identity/RLS, physical or sovereign processing, reusable runtime or command safety.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [
                THREAT,
                ENVELOPE,
                ENVELOPE_SCHEMA,
                LOCAL_CORE,
                LOCAL_LIFECYCLE,
                LOCAL_SOURCE_LEDGER,
                LOCAL_PROVIDER_LEDGER,
                FACTS,
                PREFLIGHT,
                OCCUPIED_CORE,
                OCCUPIED_LIFECYCLE,
                OCCUPIED_SOURCE_LEDGER,
                OCCUPIED_PROVIDER_LEDGER,
            ],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                POSTCOMPACTION,
                PREINTEGRATION,
                WORKER,
                WORKTREE_PREFLIGHT,
                PREDISPATCH,
                PREVERIFIER,
                REVIEW,
            ],
            "tests": [TEST, LOCAL_TEST, PLAN_TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER, CORE, LOCAL, PACKET, CONFLICT, ERROR_REVISION],
        },
        "unresolved_gates": [
            "No AES-C6 or later Agent Execution Surface tranche is planned or authorized.",
            "Any real practice population, patient/clinical data, new product-data class, reusable runtime, tool or command requires a new Yuri-owned programme choice and exact fail-closed plan.",
            "No continuing provider call, product/database read, watcher, filesystem capability, provider tool, generic network, credential/IAM change, command/write, deployment, production, release, Pages or protected-ref movement is opened.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 241 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 242
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 242 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected AES-C5 Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Complete the finite AES sequence with one exact authenticated authored-synthetic application-route and provider crossing",
        "outcome": "AES-C5 passes one practice-scoped route read, one minimized Sydney Vertex call, deterministic no-command release, terminal accounting and complete cleanup; no AES-C6 is planned or authorized.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 223
        and compass["source_graph_revision"] == 241
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 224
        and compass["source_graph_revision"] == 242
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected AES-C5 Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Serial durability, architecture-health repair and AES-C0 through AES-C5 pass.",
                "Any future real practice population, new product-data class, reusable runtime, tool, command, deployment or production descendant requires a new Yuri-owned programme choice and exact fail-closed plan.",
                "Keep patient/clinical data, continuing source/provider access, credentials, commands, production and protected refs separately closed.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Finite AES-C0 through AES-C5 containment sequence complete",
        "why_now": "Yuri selected the exact practitioner-directory source and Reception One booking-context purpose needed for the final planned authored-synthetic product-runtime proof.",
        "outcome": "One authenticated application-route read and one Sydney Vertex call released one deterministic inert booking-context match, consumed both ledgers and left the database unchanged with exact cleanup.",
        "unlocks": [
            "Use the accepted AES-C0 through AES-C5 evidence as the containment baseline when Yuri selects a future programme descendant.",
            "Require a new exact source, data, principal, purpose, retention, provider/cost, proofreader, cleanup and authority plan before any broader or reusable runtime.",
            "No AES-C6 exists in the accepted sequence; the next direction is a Yuri-owned programme choice rather than an automatic tranche.",
        ],
        "does_not_solve": [
            "Real-person, patient, clinical, appointment or operational-practice data safety, production identity or RLS.",
            "Continuing product/database/provider access, watcher/listener, reusable broker/runtime, filesystem capability, generic network or provider-executed tools.",
            "Command/write safety, concurrency, general model safety, semantic prompt-injection detection or Australian physical/sovereign processing.",
            "Credential/IAM change, deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 242 / Compass 224. AES-C5 completes the finite "
        "AES-C0 through AES-C5 sequence with one authenticated practice-scoped "
        "authored-synthetic route read, one minimized Sydney Vertex call, one "
        "deterministic no-command release, consumed ledgers and exact cleanup. "
        "No AES-C6 is planned or authorized; any further product-data, reusable-"
        "runtime, tool, command, deployment or production direction is a new "
        "Yuri-owned programme choice."
    )
    limit = "AES-C5 proves one exact authored-synthetic application-route and brokered provider crossing with cleanup, not real-person or patient-data safety, production identity/RLS, reusable runtime, command safety or physical/sovereign processing."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 242
    compass["map_revision"] = 224
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
