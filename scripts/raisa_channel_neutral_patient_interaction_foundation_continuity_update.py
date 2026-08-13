"""Advance Continuity and Compass for the patient interaction foundation."""

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
NODE_ID = "raisa-channel-neutral-patient-interaction-foundation"
PARENT = "raisa-provider-free-status-confirm-http-route-convergence"
SOURCE_HEAD = "17d9da1844e59406eecda44b5029e839b2e8a573"
UPDATED_AT = "2026-08-13T04:54:31Z"
PLAN = "docs/raisa-channel-neutral-patient-interaction-foundation-plan.md"
ARCHITECTURE = (
    "docs/raisa-channel-neutral-patient-interaction-foundation-architecture.md"
)
THREAT = (
    "docs/security/"
    "raisa-channel-neutral-patient-interaction-foundation-threat-model-delta.md"
)
CLOSEOUT = "docs/raisa-channel-neutral-patient-interaction-foundation-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-channel-neutral-patient-interaction-foundation-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-13--channel-neutral-patient-interaction-foundation.md"
)
BASE = "orchestration/continuity/raisa-channel-neutral-patient-interaction-foundation/"
CONTRACT = BASE + "foundation-contract.json"
CONTRACT_SCHEMA = BASE + "foundation-contract.schema.json"
EXAMPLES = BASE + "authored-synthetic-contract-examples.json"
EVIDENCE = BASE + "provider-free-acceptance-evidence.json"
SCRIPT = "scripts/raisa_channel_neutral_patient_interaction_foundation_acceptance.py"
TEST = "tests/test_raisa_channel_neutral_patient_interaction_foundation.py"
PLAN_TEST = "tests/test_raisa_channel_neutral_patient_interaction_foundation_plan.py"
CONTINUITY_TEST = (
    "tests/test_raisa_channel_neutral_patient_interaction_foundation_continuity.py"
)
UPDATER = (
    "scripts/raisa_channel_neutral_patient_interaction_foundation_continuity_update.py"
)
RECEIPTS = [
    "orchestration/agent_inbox/codex/raisa-channel-neutral-patient-interaction-foundation-preplanning-receipt.json",
    "orchestration/agent_inbox/codex/raisa-channel-neutral-patient-interaction-foundation-precommit-receipt.json",
    "orchestration/agent_inbox/codex/raisa-channel-neutral-patient-interaction-foundation-postcompaction-receipt.json",
]


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
        CONTRACT_SCHEMA,
        EXAMPLES,
        EVIDENCE,
        SCRIPT,
        TEST,
        PLAN_TEST,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        *RECEIPTS,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Channel-neutral patient interaction foundation",
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
                "The external-patient-client, identity-provider and channel gates remain closed.",
                "No runtime, patient/product data, database/source, provider, command, deployment or protected-ref authority was opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-channel-neutral-patient-interaction-foundation",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept passkey-first-not-passkey-only identity, recovery and channel-neutral projection/confirmation architecture.",
            }
        ],
        "claim_scope": [
            "Record resolution, proofing, binding, authentication, authorisation, delegation and recovery remain distinct.",
            "Eight closed message families, five assurance states and six future-closed untrusted channels are fixed.",
            "Projection is not current truth or reservation; selection is proposal-only; command authority remains in REST/OpenAPI.",
            "Twelve scenarios, 143 hostile rejections, 100 combined tests and the 193-test canonical fast profile pass.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, ARCHITECTURE, THREAT],
            "findings": [CONTRACT, EXAMPLES, EVIDENCE],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": RECEIPTS,
            "tests": [TEST, PLAN_TEST, CONTINUITY_TEST],
            "artifacts": [CONTRACT_SCHEMA, SCRIPT, UPDATER],
        },
        "unresolved_gates": [
            "Identity topology, proofing/federation provider, action-assurance mapping and recovery service levels remain unselected.",
            "Real identity, patient clients, SMS, email, WhatsApp, voice and delegated assistants remain closed.",
            "Visible native Diary status-confirm behavior remains unproved and is the next staff-only tranche.",
            "CF-D2 durability remains deferred to a fresh observability-first event/cue delivery plan.",
            "Patient/product data, providers, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 273 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 274
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 274 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected patient interaction Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Preserve channel-minimal patient access without weakening backend authority",
        "outcome": "The static identity, assurance, recovery, projection and confirmation foundation passes; staff-visible Diary wiring is next.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 255
        and compass["source_graph_revision"] == 273
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 256
        and compass["source_graph_revision"] == 274
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected patient interaction Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve accepted conditional-command and status-confirm route correctness.",
                "Wire and prove bounded visible native Diary status-confirm behavior for staff.",
                "Keep future patient channels behind the accepted identity, assurance, recovery, projection and confirmation foundation.",
                "Return to durable event/cue delivery only through a fresh observability-first CF-D2 plan informed by the visible consumer boundary.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Patient interaction foundation complete; staff-visible Diary wiring next",
        "why_now": "A small static slab prevents future channel or identity choices from splitting the backend authority model before visible UI work resumes.",
        "outcome": "Passkey-first-not-passkey-only identity, restricted recovery and channel-neutral proposal/confirmation semantics are frozen without enabling a patient client.",
        "unlocks": [
            "Freeze bounded visible native Diary status-confirm wiring for staff against the accepted backend route and interaction principles.",
            "Prove staff proposal review, confirmation, stale/current-truth reconciliation and responsive interaction without raw fallback.",
            "Preserve a later external-patient-client programme without requiring a dedicated application or duplicating command authority.",
        ],
        "does_not_solve": [
            "Real patient identity, authentication, recovery or channel delivery.",
            "Visible Diary interaction, another command family or patient self-service policy.",
            "CF-D2 restart/unknown-commit durability, watcher operations or cue recovery.",
            "Product/patient data, provider access, deployment, production or release.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 274 / Compass 256. The provider-free channel-neutral "
        "patient interaction foundation fixes passkey-first-not-passkey-only identity, "
        "restricted recovery and backend-owned projection/proposal/confirmation "
        "semantics without enabling any patient client or channel. Bounded visible "
        "native Diary status-confirm wiring for staff is next; CF-D2 remains a later "
        "observability-first durable event/cue extension."
    )
    limit = (
        "The patient interaction foundation is static architecture evidence, not real identity, channel delivery, patient self-service or command runtime."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 274
    compass["map_revision"] = 256
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
