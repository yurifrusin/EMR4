"""Advance Continuity and Compass for the accepted PostgreSQL catalogue rehearsal."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts import ariadne_compass


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = (
    "raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal"
)
PARENT = "raisa-provider-free-unmounted-durability-inert-ddl-rehearsal"
SOURCE_HEAD = "c3ca2515b9f2c4b20cb7230364de7417f48eab54"
UPDATED_AT = "2026-08-08T00:00:00Z"
PLAN = (
    "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-"
    "rehearsal-plan.md"
)
DESIGN = PLAN.replace("-plan.md", "-design.md")
RECOVERY = PLAN.replace("-plan.md", "-plan-recovery.md")
THREAT = (
    "docs/security/raisa-provider-free-disposable-postgresql-durability-parse-"
    "catalogue-rehearsal-threat-model-delta.md"
)
CONTRACT_DIR = (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "durability-parse-catalogue-rehearsal"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-"
    "exact-catalogue-binding-review-receipt.json"
)
CLOSEOUT_REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-"
    "parse-catalogue-closeout-retry-review-receipt.json"
)
REJECTED_CLOSEOUT_REVIEW = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-durability-parse-"
    "catalogue-closeout-review-sol-rejection.json"
)
AER_REVISION = "docs/ariadne-agent-error-correction-register-revision-91.md"
EVIDENCE = CONTRACT_DIR + "/provider-free-disposable-postgresql-evidence.json"
CHARACTERIZATION = (
    CONTRACT_DIR
    + "/provider-free-disposable-postgresql-evidence-catalogue-characterization.json"
)
CLOSEOUT = PLAN.replace("-plan.md", "-closeout.md")
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-durability-parse-"
    "catalogue-sol-acceptance.md"
)
UPDATER = (
    "scripts/raisa_provider_free_disposable_postgresql_durability_parse_"
    "catalogue_rehearsal_continuity_update.py"
)
IMPLEMENTATION_TEST = (
    "tests/test_raisa_provider_free_disposable_postgresql_durability_parse_"
    "catalogue_rehearsal.py"
)
PLAN_TEST = IMPLEMENTATION_TEST.replace(".py", "_plan.py")
CONTINUITY_TEST = IMPLEMENTATION_TEST.replace(".py", "_continuity.py")


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Disposable PostgreSQL durability parse/catalogue rehearsal",
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
            "authorized_openings": [],
            "notes": [
                "The accepted runtime used one owned networkless tmpfs-only local PostgreSQL 16 container and authored-synthetic empty shapes.",
                "It proved parse, atomic installation/rollback and exact catalogue shape only; no function, trigger, RLS or application behavior was invoked.",
                "No migration, operational database/source, product read, provider product path, command, deployment or protected capability is opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-disposable-postgresql-durability-parse-catalogue-rehearsal",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept exact PostgreSQL-16 atomic admission and catalogue "
                    "shape with exact-ID cleanup, without behavioral or operational authority."
                ),
            }
        ],
        "claim_scope": [
            "The terminal exact-bound attempt reproduces all fifteen value-bearing catalogue digests.",
            "The exact 1,404,433-byte 412-statement artifact and fixed late-suffix rollback proof pass.",
            "The complete focused packet passes 109 tests and a fresh Gemini 3.6 Flash/high exact-HEAD veto reports zero P0-P3 findings.",
            "The first final closeout review was rejected for reporting 214 tests; fresh r71 at the same exact clean HEAD passed the complete 217-test closeout packet with zero P0-P3 findings.",
            "The owned networkless container is removed by exact ID and exact inspection proves absence.",
            "No behavioral, migration, operational source, product, command, deployment or protected capability is established.",
        ],
        "contract_evidence": [
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [
                    PLAN,
                    DESIGN,
                    RECOVERY,
                    REVIEW,
                    EVIDENCE,
                    IMPLEMENTATION_TEST,
                    CLOSEOUT,
                ],
                "note": (
                    "The server proof remains authored-synthetic and does not open "
                    "a live event, read, watcher or command path."
                ),
            },
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [DESIGN, EVIDENCE, PLAN_TEST, CLOSEOUT],
                "note": "The disposable relations are empty and carry no patient or appointment payload.",
            },
        ],
        "evidence": {
            "plans": [PLAN, DESIGN, RECOVERY, THREAT],
            "findings": [
                REVIEW,
                CLOSEOUT_REVIEW,
                CHARACTERIZATION,
                EVIDENCE,
                REJECTED_CLOSEOUT_REVIEW,
                AER_REVISION,
            ],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                "orchestration/agent_inbox/codex/raisa-context-fabric-durability-exact-catalogue-terminal-preexecution-receipt.json"
            ],
            "tests": [
                IMPLEMENTATION_TEST,
                PLAN_TEST,
                "tests/test_ariadne_agent_error_register.py",
                "tests/test_ariadne_continuity_engine.py",
                "tests/test_ariadne_compass.py",
                "tests/test_agents_acceptance_index.py",
                CONTINUITY_TEST,
            ],
            "artifacts": [CONTRACT_DIR + "/rehearsal-contract.json", UPDATER],
        },
        "unresolved_gates": [
            "Patient, clinical, product-derived, financial, protected and historical-PHI data remain closed.",
            "Function/trigger/RLS behavior, concurrency, application rollback and idempotency remain separate gates.",
            "Applied migration, operational database/outbox/feed/watcher/listener/source access, persistence and credentials remain closed.",
            "Product reads, providers, routes, commands, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 231 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 232
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 232 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected disposable-PostgreSQL Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove exact durability DDL against an isolated PostgreSQL 16 server",
        "outcome": (
            "Atomic admission, rollback, exact catalogue shape and exact-ID cleanup "
            "pass while every behavioral and operational boundary remains closed."
        ),
        "evidence": [
            PLAN,
            DESIGN,
            RECOVERY,
            THREAT,
            REVIEW,
            CLOSEOUT_REVIEW,
            REJECTED_CLOSEOUT_REVIEW,
            AER_REVISION,
            CHARACTERIZATION,
            EVIDENCE,
            CLOSEOUT,
            ACCEPTANCE,
        ],
    }
    if (
        compass["map_revision"] == 213
        and compass["source_graph_revision"] == 231
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 214
        and compass["source_graph_revision"] == 232
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected disposable-PostgreSQL Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Exact durability structure, bodies, inert lowering and isolated PostgreSQL-16 catalogue admission are accepted at fresh reviewed HEADs.",
                "The next safe descendant is a separately bounded provider-free database-backed authored-synthetic behavior/transaction rehearsal.",
                "Separately gate applied migration, application wiring, operational sources, product/patient data, commands, deployment and production.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Durability catalogue admission accepted; bounded behavior planning is next",
        "why_now": (
            "The exact artifact now parses and installs atomically with a closed "
            "catalogue, so selected behavior can be isolated as a later finite gate."
        ),
        "outcome": (
            "All fifteen exact value-bearing catalogue digests, rollback proof and "
            "owned cleanup pass with 109 runtime checks; the corrected final closeout "
            "veto passes all 217 tests with zero P0-P3 findings."
        ),
        "unlocks": [
            "Freeze the smallest database-backed authored-synthetic behavior/transaction rehearsal plan.",
            "Select finite entry-point, trigger, RLS and rollback scenarios without application wiring or operational data.",
        ],
        "does_not_solve": [
            "Function/trigger/RLS behavior, concurrency, idempotency or application transaction safety.",
            "Applied migration, operational database/outbox/feed/watcher/listener/source access, credentials or persistence.",
            "Application/runtime implementation, product reads, patient/product data, providers, routes or commands.",
            "Deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 232 / Compass 214. The provider-free disposable "
        "PostgreSQL-16 durability parse/catalogue rehearsal passes at exact reviewed "
        "runtime source HEAD. A separately bounded database-backed authored-synthetic "
        "behavior/transaction rehearsal is next; application and operational boundaries remain closed."
    )
    limit = (
        "Disposable PostgreSQL catalogue acceptance proves exact parse, atomic "
        "installation/rollback and metadata shape only; it does not prove function, "
        "trigger or RLS behavior, concurrency, applied migration, application runtime, "
        "operational source access, persistence, command or deployment safety."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 214
    compass["source_graph_revision"] = 232
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
