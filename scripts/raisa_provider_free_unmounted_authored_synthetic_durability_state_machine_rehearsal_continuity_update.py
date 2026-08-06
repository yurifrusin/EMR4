"""Advance Continuity and Compass for the accepted durability rehearsal."""

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
    "raisa-provider-free-unmounted-authored-synthetic-durability-state-machine-"
    "rehearsal"
)
PARENT = "raisa-provider-free-unmounted-source-specific-durability-architecture"
SOURCE_HEAD = "95a2ed5e960c58686262b5e82ce2e89354a3860a"
UPDATED_AT = "2026-08-06T00:00:00Z"
PLAN = (
    "docs/raisa-provider-free-unmounted-authored-synthetic-durability-state-"
    "machine-rehearsal-plan.md"
)
DESIGN = PLAN.replace("-plan.md", "-design.md")
THREAT = (
    "docs/security/raisa-provider-free-unmounted-authored-synthetic-durability-"
    "state-machine-rehearsal-threat-model-delta.md"
)
MODULE = (
    "scripts/raisa_provider_free_unmounted_authored_synthetic_durability_state_"
    "machine_rehearsal.py"
)
GENERATOR = MODULE.replace(".py", "_acceptance.py")
TEST = (
    "tests/test_raisa_provider_free_unmounted_authored_synthetic_durability_"
    "state_machine_rehearsal.py"
)
CONTRACT_DIR = (
    "orchestration/continuity/raisa-provider-free-unmounted-authored-synthetic-"
    "durability-state-machine-rehearsal"
)
FIRST_VETO = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-durability-state-"
    "machine-rehearsal-independent-veto.md"
)
SECOND_VETO = FIRST_VETO.replace("independent-veto", "recovery-independent-veto")
THIRD_VETO = FIRST_VETO.replace(
    "independent-veto", "semantic-recovery-independent-veto"
)
FINAL_REVIEW = FIRST_VETO.replace(
    "independent-veto", "final-independent-review"
)
CLOSEOUT = PLAN.replace("-plan.md", "-closeout.md")
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-authored-"
    "synthetic-durability-state-machine-rehearsal-sol-acceptance.md"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_authored_synthetic_durability_state_"
    "machine_rehearsal_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_authored_synthetic_durability_"
    "state_machine_rehearsal_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Unmounted durability state-machine rehearsal",
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
                "The rehearsal is pure, provider-free, unmounted and authored-synthetic.",
                "Integrity sealing is deterministic test evidence, not a cryptographic MAC.",
                "No application, migration, database/source, product read, provider, command or runtime capability is opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-durability-state-machine-rehearsal",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept the pure atomic checkpoint, watermark, obligation, "
                    "audit, restart, rotation and retention transitions."
                ),
            }
        ],
        "claim_scope": [
            "Thirty-three closed authored-synthetic evidence cases pass.",
            "Exact cause cardinality and audit/rotation lifecycle chronology are deterministically rederived.",
            "The fresh fourth veto passed 29 attacks, 49 focused tests and 207 serial checks with no P0-P2 issue.",
            "No migration, database/source, operational persistence, product read, provider, command, runtime or protected capability is established.",
        ],
        "contract_evidence": [
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [PLAN, MODULE, TEST, CLOSEOUT],
                "note": (
                    "The committed signal remains patient-free and unmounted; no "
                    "live feed, read or command is added."
                ),
            },
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [DESIGN, TEST, CLOSEOUT],
                "note": "The rehearsal carries no patient or appointment payload.",
            },
        ],
        "evidence": {
            "plans": [PLAN, DESIGN, THREAT],
            "findings": [
                MODULE,
                FIRST_VETO,
                SECOND_VETO,
                THIRD_VETO,
                FINAL_REVIEW,
                "docs/ariadne-agent-error-correction-register-revision-45.md",
                "docs/ariadne-agent-error-correction-register-revision-46.md",
                "docs/ariadne-agent-error-correction-register-revision-47.md",
                "docs/ariadne-agent-error-correction-register-revision-48.md",
            ],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [],
            "tests": [
                TEST,
                "tests/test_raisa_provider_free_unmounted_authored_synthetic_durability_state_machine_rehearsal_plan.py",
                "tests/test_raisa_provider_free_unmounted_source_specific_durability_architecture.py",
                "tests/test_raisa_provider_free_unmounted_authored_synthetic_observation_to_temporal_signal_rehearsal_plan.py",
                "tests/test_api_spine_artifacts.py",
                "tests/test_api_spine_blueprint_first_boundary.py",
                "tests/test_ariadne_agent_error_register.py",
                CONTINUITY_TEST,
            ],
            "artifacts": [CONTRACT_DIR, MODULE, GENERATOR, UPDATER],
        },
        "unresolved_gates": [
            "Patient, clinical, product-derived, financial, protected and historical-PHI data remain closed.",
            "Migrations, database/outbox/feed/watcher/listener/source access and operational credentials remain closed.",
            "Operational persistence, product reads, providers and every route or command/write remain closed.",
            "Deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 227 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 228
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 228 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected durability-rehearsal Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove durability transitions before database design",
        "outcome": (
            "The pure state machine passes exact atomic, restart, rotation and "
            "retention transitions under fresh adversarial veto."
        ),
        "evidence": [PLAN, DESIGN, THREAT, FINAL_REVIEW, CLOSEOUT, ACCEPTANCE],
    }
    if (
        compass["map_revision"] == 209
        and compass["source_graph_revision"] == 227
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 210
        and compass["source_graph_revision"] == 228
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected durability-rehearsal Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "The source-specific durability architecture and pure durability state-machine rehearsal are accepted at exact reviewed HEADs.",
                "The next safe candidate is migration-and-transaction architecture only, without creating a migration or database object.",
                "Separately gate live database/source access, operational credentials, implementation, product reads, clinical data, commands, deployment and release.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": (
            "Pure durability state machine accepted; migration-and-transaction "
            "architecture is next"
        ),
        "why_now": (
            "The exact pure transition semantics are independently accepted before "
            "freezing their future PostgreSQL realization."
        ),
        "outcome": (
            "Thirty-three evidence cases and 29 adversarial attacks pass, with "
            "207 serial checks and no P0-P2 finding."
        ),
        "unlocks": [
            "Freeze the future PostgreSQL schema, isolation, locking, rollback, RLS/roles, credential binding and retention architecture.",
            "Design database-backed authored-synthetic acceptance without creating or mounting the database surfaces.",
        ],
        "does_not_solve": [
            "Migrations, live database/outbox/feed/watcher/listener/source access or operational credentials.",
            "Application/runtime implementation, persistence, product reads or real patient/product data.",
            "Provider cognition, routes, commands, deployment, production or release.",
            "Pages, protected evidence or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 228 / Compass 210. The provider-free unmounted "
        "durability state-machine rehearsal passes at exact reviewed HEAD. A pure "
        "migration-and-transaction architecture tranche is next; every live and "
        "real-data boundary remains closed."
    )
    limit = (
        "Durability state-machine acceptance proves deterministic pure transitions, "
        "not cryptographic authenticity, a migration, live database/source, "
        "persistence, product-read, provider, command, runtime or deployment safety."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 210
    compass["source_graph_revision"] = 228
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
