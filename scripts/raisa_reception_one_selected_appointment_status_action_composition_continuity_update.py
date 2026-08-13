"""Advance Continuity and Compass for the Reception One status-action composition."""

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
NODE_ID = "raisa-reception-one-selected-appointment-status-action-composition"
PARENT = "raisa-post-cf-d2-compass-baton-orientation"
SOURCE_HEAD = "b6c6a983c4936c1f0bd5e9daf03924bbcd4ddd33"
UPDATED_AT = "2026-08-13T12:46:00Z"
PLAN = "docs/raisa-reception-one-selected-appointment-status-action-composition-plan.md"
THREAT = "docs/security/raisa-reception-one-selected-appointment-status-action-composition-threat-model-delta.md"
EVIDENCE_SCHEMA = (
    "orchestration/continuity/raisa-reception-one-selected-appointment-status-action-composition/"
    "selected-appointment-status-action-evidence.schema.json"
)
EVIDENCE = (
    "orchestration/continuity/raisa-reception-one-selected-appointment-status-action-composition/"
    "selected-appointment-status-action-evidence.json"
)
BROWSER_TEST = "review/test_reception_one_status_action.py"
PLAN_TEST = "tests/test_raisa_reception_one_selected_appointment_status_action_composition_plan.py"
EVIDENCE_TEST = "tests/test_raisa_reception_one_selected_appointment_status_action_composition_evidence.py"
UPDATER = "scripts/raisa_reception_one_selected_appointment_status_action_composition_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_reception_one_selected_appointment_status_action_composition_continuity.py"
CLOSEOUT = "docs/raisa-reception-one-selected-appointment-status-action-composition-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-reception-one-selected-appointment-status-action-composition-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-13--reception-one-selected-appointment-status-action-composition.md"
)
RECEIPTS = [
    "orchestration/agent_inbox/codex/raisa-reception-one-selected-appointment-status-action-composition-preplanning-receipt.json",
    "orchestration/agent_inbox/codex/raisa-reception-one-selected-appointment-status-action-composition-preacceptance-receipt.json",
]


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _all_evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        EVIDENCE_SCHEMA,
        EVIDENCE,
        BROWSER_TEST,
        PLAN_TEST,
        EVIDENCE_TEST,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        *RECEIPTS,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free Reception One selected-appointment status-action composition",
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
        "relationships": [{"node_id": PARENT, "relation": "implements"}],
        "authority": {
            "authorized_openings": [],
            "notes": [
                "Consumer-only authored-synthetic UI composition over the existing status proposal/confirm command family.",
                "GraphQL remains read-only; the bridge has no network or raw-write implementation.",
                "Backend current-authority, source-truth, idempotency, audit and receipt ownership are unchanged.",
            ],
        },
        "decisions": [
            {
                "id": "accept-reception-one-selected-appointment-status-action-composition",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept one selected current appointment status action with fail-closed feedback and fresh projection reconciliation.",
            }
        ],
        "claim_scope": [
            "One selected current Reception One appointment delegates one existing status through the existing setAppointmentStatus interaction.",
            "Safe, cancel, blocked, stale, interruption and responsive rendered scenarios pass without a duplicate command or raw fallback.",
            "Eight dedicated, 144 native Diary, 171 focused and 193 canonical-fast tests pass.",
            "No backend, database, provider, product/patient data, deployment, release or protected-ref activity occurred.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [PLAN, EVIDENCE, BROWSER_TEST, CLOSEOUT],
                "note": "The status-only interaction preserves the selected appointment identity, practitioner, time and duration while proposing and confirming only one existing status field.",
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [PLAN, EVIDENCE, BROWSER_TEST, CLOSEOUT],
                "note": "A committed status result triggers a fresh authoritative Diary projection rebuild; event cues remain optional acceleration hints and never become command truth.",
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [EVIDENCE_SCHEMA, EVIDENCE],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": RECEIPTS,
            "tests": [BROWSER_TEST, PLAN_TEST, EVIDENCE_TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "A fresh read-only orientation must select any successor from current repository evidence.",
            "Another command family, event family, representative cohort or patient channel still requires its recorded Yuri decision.",
            "Watcher/runtime, product data, providers, deployment, production and release remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 282 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 283
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 283 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected selected-status composition Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Compose one already-secured routine Diary command into the focused Reception One projection",
        "outcome": "One selected current appointment now uses the existing status proposal/confirm interaction with fail-closed feedback and fresh projection reconciliation.",
        "evidence": _all_evidence(),
    }
    if (
        compass["map_revision"] == 264
        and compass["source_graph_revision"] == 282
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 265
        and compass["source_graph_revision"] == 283
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected selected-status composition Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "The first post-durability visible Reception One command composition is accepted",
        "why_now": "The selected appointment/status seam is complete and the remaining candidate directions carry different value or authority gates.",
        "outcome": "Reception One can apply one existing appointment status safely through the canonical command path.",
        "unlocks": [
            "Run a fresh provider-free read-only Compass and baton orientation over the completed visible seam.",
            "Select the narrowest next dependency-satisfied product tranche without inferring another command, event, participant or patient-channel authority.",
        ],
        "does_not_solve": [
            "No additional appointment command family or Diary event family is authorised.",
            "Representative staff execution and the first external patient channel retain their recorded Yuri-owned gates.",
            "Watcher/runtime, product data, providers, deployment, production and release remain closed.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 283 / Compass 265. The provider-free Reception "
        "One selected-appointment status-action composition passes over the "
        "existing status proposal/confirm family. A fresh read-only orientation "
        "is next; no further command or event family is inferred."
    )
    limit = (
        "The selected-status composition proves authored-synthetic client and route-intercepted rendered behavior only; it adds no command family or backend, database, provider, deployment or production authority."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 283
    compass["map_revision"] = 265
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
