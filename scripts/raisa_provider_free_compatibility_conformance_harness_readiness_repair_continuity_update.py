"""Advance Continuity and Compass for compatibility harness readiness."""

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
NODE_ID = "raisa-provider-free-compatibility-conformance-harness-temporal-idempotency-readiness-repair"
PARENT = "raisa-provider-free-compatibility-consumer-kernel-convergence-admission-review"
SOURCE_HEAD = "48c1821af79f9d22b7c029fdbba8c4f984d239e5"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = "docs/raisa-provider-free-compatibility-conformance-harness-temporal-idempotency-readiness-repair-plan.md"
THREAT = "docs/security/raisa-provider-free-compatibility-conformance-harness-temporal-idempotency-readiness-repair-threat-model-delta.md"
CLOSEOUT = "docs/raisa-provider-free-compatibility-conformance-harness-temporal-idempotency-readiness-repair-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-compatibility-conformance-harness-readiness-repair-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-12--compatibility-conformance-harness-readiness-repair.md"
STRUCTURAL = "orchestration/continuity/raisa-provider-free-compatibility-conformance-harness-readiness-repair/structural-repair-evidence.json"
PREPLANNING = "orchestration/agent_inbox/codex/raisa-compatibility-conformance-harness-readiness-repair-preplanning-receipt.json"
PRECOMMIT = "orchestration/agent_inbox/codex/raisa-compatibility-conformance-harness-readiness-repair-precommit-receipt.json"
TEST = "tests/test_raisa_provider_free_compatibility_conformance_harness_readiness_repair_continuity.py"
UPDATER = "scripts/raisa_provider_free_compatibility_conformance_harness_readiness_repair_continuity_update.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        STRUCTURAL,
        CLOSEOUT,
        ACCEPTANCE,
        PREPLANNING,
        PRECOMMIT,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free compatibility conformance-harness temporal/idempotency readiness repair",
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
                "This is provider-free test-only conformance evidence.",
                "The application tree and status-code assertion set are unchanged.",
                "All raw compatibility routes remain mounted and unchanged.",
            ],
        },
        "decisions": [
            {
                "id": "accept-compatibility-conformance-harness-readiness-repair",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept the exact 311/311 current compatibility baseline without an application change.",
            }
        ],
        "claim_scope": [
            "The exact pre-repair collection reproduced 266 pass and 45 fail with 33 temporal and 12 header cases.",
            "The same ordinary compatibility collection now passes 311 of 311 tests.",
            "Two structural tests prove exactly eight changed test files, an unchanged application tree and unchanged status-code assertions.",
            "The source-bound combined run passes 313 of 313 and the canonical 191-test fast profile passes.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [THREAT],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING, PRECOMMIT],
            "tests": [
                "tests/test_raisa_provider_free_compatibility_conformance_harness_readiness_repair.py",
                TEST,
            ],
            "artifacts": [STRUCTURAL, UPDATER],
        },
        "unresolved_gates": [
            "The provider-free unmounted status transaction-kernel protocol rehearsal is next.",
            "No status route imports or executes a kernel yet.",
            "External consumer readiness, raw-route convergence and create schedule fencing remain unproved.",
            "Operational data, providers, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 254 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 255
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 255 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected compatibility harness Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Restore a trustworthy compatibility baseline before status-kernel protocol work",
        "outcome": "All 311 ordinary compatibility tests pass without application or assertion weakening.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 236
        and compass["source_graph_revision"] == 254
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 237
        and compass["source_graph_revision"] == 255
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected compatibility harness Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Rehearse the provider-free unmounted status transaction-kernel protocol.",
                "Keep every application route outside the protocol rehearsal.",
                "Retain raw status until precondition, confirmation and idempotency ingress is accepted.",
                "Select and prove a database-owned create schedule fence before create convergence.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Compatibility baseline trustworthy; status protocol next",
        "why_now": "The exact ordinary suite is current, so transaction-kernel semantics can be evaluated against a clean behavioral baseline.",
        "outcome": "The same 311 tests move from 45 classified harness failures to 311/311 without an application change.",
        "unlocks": [
            "Rehearse authority-first status transaction-kernel schedules in an unmounted authored-synthetic protocol.",
            "Freeze atomic mutation, audit and completed-receipt behavior plus typed loser outcomes.",
        ],
        "does_not_solve": [
            "Status route integration, raw-route convergence, external consumers or create schedule fencing.",
            "Operational data, providers, commands, deployment, Pages or protected refs.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 255 / Compass 237. The provider-free compatibility "
        "conformance-harness repair restores the exact 311/311 baseline without an application "
        "change; the unmounted status transaction-kernel protocol rehearsal is next."
    )
    for limit in (
        "A green compatibility suite does not prove external-consumer readiness or route-convergence safety.",
        "Test-only clock and header repair grants no application or command authority.",
    ):
        if limit not in compass["map_limits"]:
            compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 255
    compass["map_revision"] = 237
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
