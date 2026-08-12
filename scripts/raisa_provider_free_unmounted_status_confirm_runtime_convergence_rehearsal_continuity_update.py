"""Advance Continuity and Compass for status-confirm convergence rehearsal."""

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
NODE_ID = "raisa-provider-free-unmounted-status-confirm-runtime-convergence-rehearsal"
PARENT = "raisa-provider-free-unmounted-status-confirm-runtime-convergence-architecture"
SOURCE_HEAD = "a1629f2441e2bdb350d00c6d6016e94123ff0d8d"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = (
    "docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-"
    "rehearsal-plan.md"
)
THREAT = (
    "docs/security/raisa-provider-free-unmounted-status-confirm-runtime-"
    "convergence-rehearsal-threat-model-delta.md"
)
CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-status-confirm-runtime-convergence-"
    "rehearsal-closeout.md"
)
BASE = (
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-"
    "runtime-convergence-rehearsal/"
)
PACKET = BASE + "rehearsal-packet.json"
SCHEMA = BASE + "rehearsal-packet.schema.json"
EVIDENCE = BASE + "provider-free-rehearsal-evidence.json"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-status-confirm-runtime-"
    "convergence-rehearsal-sol-acceptance.md"
)
PREPLANNING = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-"
    "confirm-runtime-convergence-rehearsal-preplanning-receipt.json"
)
POSTCOMPACTION = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-"
    "confirm-runtime-convergence-rehearsal-postcompaction-receipt.json"
)
PRECOMMIT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-status-"
    "confirm-runtime-convergence-rehearsal-precommit-receipt.json"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-12--status-confirm-runtime-convergence-rehearsal.md"
)
TEST = (
    "tests/test_raisa_provider_free_unmounted_status_confirm_runtime_"
    "convergence_rehearsal.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_status_confirm_runtime_"
    "convergence_rehearsal_continuity.py"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_status_confirm_runtime_"
    "convergence_rehearsal_continuity_update.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        PACKET,
        SCHEMA,
        EVIDENCE,
        CLOSEOUT,
        ACCEPTANCE,
        PREPLANNING,
        POSTCOMPACTION,
        PRECOMMIT,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free unmounted status-confirm runtime convergence rehearsal",
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
                "The rehearsal is provider-free, authored-synthetic, pure in-memory and unmounted; implementation_authorized is false.",
                "Twenty-four schedules prove ordered decisions, rollback, authority-first disclosure and stored receipt retry.",
                "Physical storage, migration, application/database execution, providers, product data and commands remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-status-confirm-runtime-convergence-rehearsal",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept 24 exact schedules and hand off only to a read-only physical representability review.",
            }
        ],
        "claim_scope": [
            "All 24 authored-synthetic schedules reproduce their frozen outcomes and durable/disclosure counts.",
            "Current authority and target validity precede idempotency inspection or stored receipt disclosure.",
            "Three failure points roll back the mutation, audit and receipt together; response loss leaves one effect and an exact stored retry.",
            "All 88 hostile mutations are rejected; this proves in-memory coherence, not PostgreSQL or mounted-route behavior.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [THREAT, PACKET, SCHEMA, EVIDENCE],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING, POSTCOMPACTION, PRECOMMIT],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "The physical representability of appointment_state_version, private receipts and the ordered lock boundary has not been reviewed.",
            "Migration/backfill, ORM/service composition, mounted-route parity and PostgreSQL behavior remain unselected and unproved.",
            "Raw-route change, create schedule fencing, providers, product/patient data, commands, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 259 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 260
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 260 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected convergence-rehearsal Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove the status command safety order before selecting physical representation",
        "outcome": "Twenty-four schedules and 88 hostile mutations pass in pure memory; a read-only physical representability review is next.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 241
        and compass["source_graph_revision"] == 259
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 242
        and compass["source_graph_revision"] == 260
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected convergence-rehearsal Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve the accepted source-owned-truth, status protocol, adapter, runtime-gap and convergence contracts.",
                "Run the provider-free read-only physical representability review before any model, migration, service or route edit.",
                "Keep raw-route change, create schedule fencing, providers, product data, commands and protected integration separately gated.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "The status safety order executes coherently in memory but remains physically unrepresented",
        "why_now": "The accepted architecture was exact enough to challenge races, rollbacks and lost responses without opening runtime authority.",
        "outcome": "All 24 schedules and 88 hostile mutations pass with authority-first disclosure, atomic effects and stored receipt retry.",
        "unlocks": [
            "Freeze exact non-protected sources for a provider-free read-only physical representability review.",
            "Determine whether state version, private receipt correlation and ordered locks can be represented without weakening the contract.",
            "Keep all source edits and execution behind a later evidence gate.",
        ],
        "does_not_solve": [
            "Physical appointment-state version or private completed-receipt storage.",
            "Migration/backfill, ORM/service composition, mounted-route behavior or PostgreSQL locking/concurrency.",
            "Restart/unknown-commit operational recovery or waiting-area regression behavior.",
            "Provider/credential activity, patient/product data, product commands, deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 260 / Compass 242. The provider-free unmounted "
        "status-confirm convergence rehearsal passes all 24 schedules and 88 hostile "
        "mutations. A read-only physical representability review is next; source edits, "
        "database execution and product authority remain closed."
    )
    limit = (
        "The status-confirm convergence rehearsal proves pure in-memory state-machine behavior, not physical storage, mounted routes or PostgreSQL semantics."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 260
    compass["map_revision"] = 242
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
