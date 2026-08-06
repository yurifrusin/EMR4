"""Idempotently accept the unmounted observation-to-signal rehearsal."""

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
NODE_ID = (
    "raisa-provider-free-unmounted-authored-synthetic-observation-to-"
    "temporal-signal-rehearsal"
)
PARENT = "raisa-provider-free-default-off-live-source-observation-boundary"
SOURCE_HEAD = "c0502c398df4a56c9558bc68eddedb2adf20d12d"
UPDATED_AT = "2026-08-06T18:00:00Z"
PLAN = (
    "docs/raisa-provider-free-unmounted-authored-synthetic-observation-to-"
    "temporal-signal-rehearsal-plan.md"
)
DESIGN = (
    "docs/raisa-provider-free-unmounted-authored-synthetic-observation-to-"
    "temporal-signal-rehearsal-design.md"
)
THREAT = (
    "docs/security/raisa-provider-free-unmounted-authored-synthetic-"
    "observation-to-temporal-signal-rehearsal-threat-model-delta.md"
)
SOURCE = (
    "scripts/raisa_provider_free_unmounted_authored_synthetic_observation_to_"
    "temporal_signal_rehearsal.py"
)
GENERATOR = (
    "scripts/raisa_provider_free_unmounted_authored_synthetic_observation_to_"
    "temporal_signal_rehearsal_acceptance.py"
)
TEST = (
    "tests/test_raisa_provider_free_unmounted_authored_synthetic_observation_"
    "to_temporal_signal_rehearsal.py"
)
FIRST_VETO = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-observation-to-"
    "temporal-signal-independent-veto.md"
)
SECOND_VETO = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-observation-to-"
    "temporal-signal-sol-recovery-independent-veto.md"
)
FINAL_REVIEW = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-observation-to-"
    "temporal-signal-final-independent-review.md"
)
PREACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-context-fabric-observation-to-"
    "temporal-signal-pre-verifier-acceptance-receipt.json"
)
CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-authored-synthetic-observation-to-"
    "temporal-signal-rehearsal-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-authored-"
    "synthetic-observation-to-temporal-signal-rehearsal-sol-acceptance.md"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_authored_synthetic_observation_to_"
    "temporal_signal_rehearsal_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_authored_synthetic_observation_"
    "to_temporal_signal_rehearsal_continuity.py"
)
CONTINUITY_DIR = (
    "orchestration/continuity/raisa-provider-free-unmounted-authored-"
    "synthetic-observation-to-temporal-signal-rehearsal/"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Unmounted authored-synthetic observation-to-signal rehearsal",
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
                "The rehearsal is pure, provider-free, authored-synthetic and unmounted.",
                "The observer emits no truth and receives no read, provider, persistence or command authority.",
                "Admission and mapping are internal; public signal egress requires same-packet proofreader RELEASE.",
                "Live source, database, watcher, durable checkpoint, product read and runtime capabilities remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-unmounted-observation-to-temporal-signal-rehearsal",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept the full-domain synthetic observation admission, "
                    "backend-owned mapping and proofreader-gated temporal handoff."
                ),
            }
        ],
        "claim_scope": [
            "Exact scope-bound HMAC identity, prior continuity, registered aliases and backend impact floors pass.",
            "Every admitted raw-id, prior and two-sided clock coordinate maps from actual trusted inputs.",
            "The final fresh veto found no P0-P2 issue and passed 227 checks.",
            "No live source, persistence, product read, provider, command, runtime, deployment or protected capability is established.",
        ],
        "contract_evidence": [
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [
                    PLAN,
                    "docs/api-spine/async/integration-events.yaml",
                    "docs/api-spine/openapi/diary-committed-events.yaml",
                    TEST,
                    CLOSEOUT,
                ],
                "note": (
                    "The patient-free reschedule event is admitted only as an "
                    "invalidation signal and creates no source read or write."
                ),
            },
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [
                    "docs/api-spine/graphql/practice-context-fabric-read.graphql",
                    TEST,
                    CLOSEOUT,
                ],
                "note": (
                    "The temporal handoff adds no read or command surface and "
                    "cannot become command evidence."
                ),
            },
        ],
        "evidence": {
            "plans": [PLAN, DESIGN, THREAT],
            "findings": [
                FIRST_VETO,
                SECOND_VETO,
                FINAL_REVIEW,
                "docs/ariadne-agent-error-correction-register-revision-38.md",
                "docs/ariadne-agent-error-correction-register-revision-39.md",
                "docs/ariadne-agent-error-correction-register-revision-40.md",
                "docs/api-spine/async/integration-events.yaml",
                "docs/api-spine/openapi/diary-committed-events.yaml",
                "docs/api-spine/graphql/practice-context-fabric-read.graphql",
            ],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREACCEPTANCE],
            "tests": [
                TEST,
                "tests/test_raisa_provider_free_unmounted_authored_synthetic_observation_to_temporal_signal_rehearsal_plan.py",
                "tests/test_raisa_provider_free_practice_context_fabric_patient_free_temporal_weave.py",
                "tests/test_api_spine_artifacts.py",
                "tests/test_ariadne_agent_error_register.py",
                "tests/test_agents_acceptance_index.py",
                CONTINUITY_TEST,
            ],
            "artifacts": [SOURCE, GENERATOR, CONTINUITY_DIR, UPDATER],
        },
        "unresolved_gates": [
            "Patient, clinical, product-derived, financial, protected and historical-PHI data remain closed.",
            "Live database/outbox/feed/watcher/listener delivery, operational credentials and source access remain closed.",
            "Durable transaction position, checkpoint persistence, restart recovery, retention and live audit remain closed.",
            "Product reads, external evidence, provider calls, cross-Bureau clinical sources and every command/write remain closed.",
            "Deployment, production, release, Pages, protected refs and protected evidence remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 225 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 226
        graph["updated_at"] = UPDATED_AT
        _write(GRAPH, graph)
    elif graph["graph_revision"] == 226 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
    else:
        raise SystemExit("Unexpected observation-to-signal Continuity predecessor")

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove full-domain observation admission and temporal handoff",
        "outcome": (
            "One pure authored-synthetic committed change maps through backend "
            "impact and proofreader gates into the accepted temporal processor."
        ),
        "evidence": [
            PLAN,
            DESIGN,
            THREAT,
            FIRST_VETO,
            SECOND_VETO,
            FINAL_REVIEW,
            PREACCEPTANCE,
            CLOSEOUT,
            ACCEPTANCE,
        ],
    }
    if (
        compass["map_revision"] == 207
        and compass["source_graph_revision"] == 225
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 208
        and compass["source_graph_revision"] == 226
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected observation-to-signal Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "The default-off live-source architecture and full-domain unmounted observation-to-signal rehearsal are accepted at exact reviewed HEADs.",
                "The next safe candidate is a provider-free unmounted source-specific durability architecture for diary.appointment_rescheduled.v1.",
                "Separately gate live database/outbox/feed access, operational credentials, persistence, product reads, clinical data, commands, deployment and release.",
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
            "Unmounted observation-to-signal rehearsal accepted; source-specific "
            "durability architecture is next"
        ),
        "why_now": (
            "The full admitted identity, prior and two-sided clock domain plus "
            "proofreader-only public egress are independently accepted."
        ),
        "outcome": (
            "The repaired exact candidate passed 227 checks and a fresh "
            "no-finding independent veto."
        ),
        "unlocks": [
            "Freeze an architecture-only integration principal and durable monotonic outbox/transaction coordinate for diary.appointment_rescheduled.v1.",
            "Specify atomic decision-invalidation-checkpoint, restart, retention and key-rotation contracts without mounting a source.",
        ],
        "does_not_solve": [
            "Real patient/product data, live database/outbox/feed/watcher/listener access or product source reads.",
            "Operational credentials, checkpoint persistence, restart execution or runtime retention.",
            "Provider cognition, cross-Bureau clinical sources, commands, deployment or production.",
            "Release, Pages, protected evidence or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 226 / Compass 208. The provider-free unmounted "
        "observation-to-temporal-signal rehearsal passes at exact reviewed HEAD. "
        "A source-specific durability architecture is next; every live and "
        "real-data boundary remains closed."
    )
    limit = (
        "Unmounted observation-to-signal acceptance proves only pure authored-"
        "synthetic admission, mapping and proofreading; it creates no live "
        "source, database, persistence, product-read, provider, command, runtime, "
        "deployment or protected authority."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 208
    compass["source_graph_revision"] = 226
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
