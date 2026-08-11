"""Advance Continuity and Compass for accepted CF-D1 concurrency evidence."""

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
NODE_ID = "raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal"
PARENT = "raisa-agent-execution-surface-containment-gate-aes-c5"
DURABILITY_PARENT = (
    "raisa-provider-free-disposable-postgresql-durability-"
    "behavior-transaction-rehearsal"
)
SOURCE_HEAD = "fed81847b4155d49cf997905e79cf31808ceb017"
UPDATED_AT = "2026-08-11T00:00:00Z"
PLAN = "docs/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-plan.md"
DESIGN = "docs/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-design.md"
THREAT = "docs/security/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-threat-model-delta.md"
CLOSEOUT = "docs/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-closeout.md"
BASE = (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "durability-concurrency-rehearsal/"
)
CONTRACT = BASE + "concurrency-rehearsal-contract.json"
CONTRACT_SCHEMA = BASE + "concurrency-rehearsal-contract.schema.json"
EVIDENCE_SCHEMA = BASE + "provider-free-durability-concurrency-evidence.schema.json"
ATTEMPT_002 = BASE + "provider-free-durability-concurrency-evidence-attempt-002.json"
ATTEMPT_003 = BASE + "provider-free-durability-concurrency-evidence-attempt-003.json"
PASS_EVIDENCE = BASE + "provider-free-durability-concurrency-evidence-attempt-004.json"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-context-fabric-durability-concurrency-rehearsal-sol-acceptance.md"
PREEXECUTION = "orchestration/agent_inbox/codex/raisa-context-fabric-durability-concurrency-attempt-004-preexecution-receipt.json"
PLANNING_REVIEW = "orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-concurrency-planning-review-receipt.json"
IMPLEMENTATION_REVIEW = "orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-concurrency-implementation-review-receipt.json"
LAUNCHER_REVIEW = "orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-concurrency-launcher-recovery-review-receipt.json"
TELEMETRY_REVIEW = "orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-concurrency-marker-telemetry-recovery-review-receipt.json"
VOCABULARY_REVIEW = "orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-concurrency-replay-vocabulary-recovery-review-receipt.json"
ATTEMPT_001_ANALYSIS = "docs/raisa-context-fabric-durability-concurrency-attempt-001-launcher-failure-analysis.md"
ATTEMPT_002_ANALYSIS = "docs/raisa-context-fabric-durability-concurrency-attempt-002-marker-telemetry-analysis.md"
ATTEMPT_003_ANALYSIS = "docs/raisa-context-fabric-durability-concurrency-attempt-003-replay-vocabulary-analysis.md"
ERROR_REVISION = "docs/ariadne-agent-error-correction-register-revision-239.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-11--context-fabric-durability-concurrency-rehearsal.md"
HARNESS = "scripts/raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py"
IMPLEMENTATION_TEST = "tests/test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py"
PLAN_TEST = "tests/test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_plan.py"
CONTINUITY_TEST = "tests/test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_continuity.py"
UPDATER = "scripts/raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_continuity_update.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        DESIGN,
        THREAT,
        CONTRACT,
        CONTRACT_SCHEMA,
        EVIDENCE_SCHEMA,
        ATTEMPT_002,
        ATTEMPT_003,
        PASS_EVIDENCE,
        ATTEMPT_001_ANALYSIS,
        ATTEMPT_002_ANALYSIS,
        ATTEMPT_003_ANALYSIS,
        PLANNING_REVIEW,
        IMPLEMENTATION_REVIEW,
        LAUNCHER_REVIEW,
        TELEMETRY_REVIEW,
        VOCABULARY_REVIEW,
        ERROR_REVISION,
        CLOSEOUT,
        ACCEPTANCE,
        PREEXECUTION,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Raisa Context Fabric CF-D1 disposable PostgreSQL concurrency rehearsal",
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
        "relationships": [
            {"node_id": PARENT, "relation": "builds_on"},
            {"node_id": DURABILITY_PARENT, "relation": "builds_on"},
        ],
        "authority": {
            "authorized_openings": [],
            "notes": [
                "CF-D1 consumed one local provider-free disposable PostgreSQL run over six fixed authored-synthetic two-session races.",
                "All overlap, outcomes, relation readbacks and forbidden-effect checks passed with zero automatic retries.",
                "The exact container is absent; no operational database, source, provider, product data, tool, command or reusable runtime authority remains open.",
            ],
        },
        "decisions": [
            {
                "id": "accept-context-fabric-durability-concurrency-rehearsal",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept six exact two-session PostgreSQL 16 concurrency outcomes, native replay, outer rollback and exact cleanup.",
            }
        ],
        "claim_scope": [
            "All six fixed races proved leader Timeout/PgSleep and contender Lock overlap before result admission.",
            "The result proves exact registration, position, admission and coordinator winner/loser behavior with 12 participants, 11 preconditions and zero retries.",
            "Attempt 004 passed whole-document evidence admission and exact container cleanup; attempts 001-003 remain immutable failures.",
            "The result does not prove crash/restart, unknown commit, arbitrary deadlock freedom, load, performance, more than two participants or operational availability.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [
                DESIGN,
                THREAT,
                EVIDENCE_SCHEMA,
                ATTEMPT_002,
                ATTEMPT_003,
                PASS_EVIDENCE,
                ATTEMPT_001_ANALYSIS,
                ATTEMPT_002_ANALYSIS,
                ATTEMPT_003_ANALYSIS,
            ],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                PLANNING_REVIEW,
                IMPLEMENTATION_REVIEW,
                LAUNCHER_REVIEW,
                TELEMETRY_REVIEW,
                VOCABULARY_REVIEW,
                PREEXECUTION,
            ],
            "tests": [IMPLEMENTATION_TEST, PLAN_TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER, HARNESS, ERROR_REVISION],
        },
        "unresolved_gates": [
            "CF-D2 restart and unknown-commit recovery needs its own fresh five-source rehydration, frozen fail-closed plan and separate disposable evidence.",
            "Key rotation, retention/purge, arbitrary retry/deadlock/load behavior, long-lived persistence and operational availability remain unproved.",
            "No operational database/source, watcher/listener, real/product/patient/clinical data, provider, tool, command, deployment, production, release, Pages or protected-ref movement is opened.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 242 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 243
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 243 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected CF-D1 Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove exact Context Fabric database behavior under six fixed two-session races",
        "outcome": "CF-D1 passes bounded overlap, exact winner/loser outcomes, native replay, outer rollback, whole-document evidence and cleanup without product or provider access.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 224
        and compass["source_graph_revision"] == 242
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 225
        and compass["source_graph_revision"] == 243
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected CF-D1 Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Serial durability, architecture-health repair, AES-C0 through AES-C5 and CF-D1 concurrency pass.",
                "CF-D2 restart/unknown-commit recovery requires a fresh five-source rehydration and its own narrow fail-closed plan.",
                "Keep operational database/source access, real data, providers, tools, commands, production and protected refs separately closed.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Context Fabric CF-D1 concurrency evidence accepted",
        "why_now": "Yuri selected the first post-AES programme descendant and standing authority continues through dependency-satisfied planned tranches.",
        "outcome": "Six exact authored-synthetic two-session PostgreSQL races passed with bounded overlap, exact outcomes, no retry and complete owned cleanup.",
        "unlocks": [
            "Freeze the narrowest CF-D2 provider-free disposable restart and unknown-commit recovery plan.",
            "Separate definitely committed, definitely rolled back and genuinely indeterminate client observations without guessing success.",
            "Require fresh five-source rehydration and a new evidence path before CF-D2 runtime.",
        ],
        "does_not_solve": [
            "Crash/restart or unknown-commit recovery, arbitrary retry/deadlock/load behavior, performance or operational availability.",
            "Key rotation, retention/purge, long-lived persistence, applied migration, application/API/Diary wiring or watchers/listeners.",
            "Operational database/source access, real/product/patient/clinical data, providers, tools or commands.",
            "Credential/IAM change, deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 243 / Compass 225. CF-D1 proves six exact "
        "provider-free authored-synthetic PostgreSQL 16 two-session races with "
        "bounded overlap, native replay, outer rollback, zero retry and exact "
        "cleanup. CF-D2 provider-free disposable restart and unknown-commit "
        "recovery is the next dependency-satisfied planned tranche under "
        "Yuri's standing authority."
    )
    limit = (
        "CF-D1 proves six fixed two-session database races, not crash/restart, "
        "unknown commit, arbitrary deadlock freedom, load, performance, more "
        "than two participants or operational availability."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 243
    compass["map_revision"] = 225
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
