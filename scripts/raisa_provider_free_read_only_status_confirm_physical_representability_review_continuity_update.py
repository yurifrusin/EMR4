"""Advance Continuity and Compass for status-confirm representability review."""

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
NODE_ID = "raisa-provider-free-read-only-status-confirm-physical-representability-review"
PARENT = "raisa-provider-free-unmounted-status-confirm-runtime-convergence-rehearsal"
SOURCE_HEAD = "530a1d479a48242df6985886acdbb796550e9093"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = (
    "docs/raisa-provider-free-read-only-status-confirm-physical-"
    "representability-review-plan.md"
)
THREAT = (
    "docs/security/raisa-provider-free-read-only-status-confirm-physical-"
    "representability-review-threat-model-delta.md"
)
CLOSEOUT = (
    "docs/raisa-provider-free-read-only-status-confirm-physical-"
    "representability-review-closeout.md"
)
BASE = (
    "orchestration/continuity/raisa-provider-free-read-only-status-confirm-"
    "physical-representability-review/"
)
CONTRACT = BASE + "physical-representability-review-contract.json"
SCHEMA = BASE + "physical-representability-review-contract.schema.json"
EVIDENCE = BASE + "provider-free-read-only-review-evidence.json"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-status-confirm-physical-"
    "representability-review-sol-acceptance.md"
)
PREPLANNING = (
    "orchestration/agent_inbox/codex/raisa-provider-free-read-only-status-"
    "confirm-physical-representability-review-preplanning-receipt.json"
)
PRECOMMIT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-read-only-status-"
    "confirm-physical-representability-review-precommit-receipt.json"
)
INCIDENT = (
    "orchestration/agent_inbox/codex/raisa-status-confirm-physical-"
    "representability-protected-metadata-scope-incident.json"
)
AER_REVISION = "docs/ariadne-agent-error-correction-register-revision-259.md"
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-12--status-confirm-physical-representability-review.md"
)
TEST = (
    "tests/test_raisa_provider_free_read_only_status_confirm_physical_"
    "representability_review.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_read_only_status_confirm_physical_"
    "representability_review_continuity.py"
)
UPDATER = (
    "scripts/raisa_provider_free_read_only_status_confirm_physical_"
    "representability_review_continuity_update.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        CONTRACT,
        SCHEMA,
        EVIDENCE,
        CLOSEOUT,
        ACCEPTANCE,
        PREPLANNING,
        PRECOMMIT,
        INCIDENT,
        AER_REVISION,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free read-only status-confirm physical representability review",
        "kind": "review",
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
                "The review is provider-free, exact-file and read-only; overall_verdict is implementation_not_admitted.",
                "State version, private receipt and ordered locks are representable only with additive change.",
                "Physical design, migration, source edits, database execution, providers, product data and commands remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-status-confirm-physical-representability-review",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept three additive representability verdicts and hand off only to an unmounted physical-design architecture.",
            }
        ],
        "claim_scope": [
            "The appointment model has no admissible monotonic state version; timestamp substitution is rejected.",
            "The receipt model has thirteen useful primitives and four additive gaps; private correlation need not alter the public envelope.",
            "The current service inserts then locks only the idempotency row; it does not implement the accepted three-lock order.",
            "All eleven hashes, 46 hostile mutations and exact source observations pass; no implementation is admitted.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [THREAT, CONTRACT, SCHEMA, EVIDENCE, INCIDENT, AER_REVISION],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING, PRECOMMIT],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "The exact additive state-version, private-receipt and ordered transaction design has not been selected.",
            "Migration/backfill, ORM/service composition, mounted-route parity and PostgreSQL behavior remain unproved.",
            "Providers, credentials, product/patient data, watchers/events, commands, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 260 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 261
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 261 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected representability-review Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Establish physical feasibility before selecting any additive schema or transaction design",
        "outcome": "All three domains are representable with additive change; implementation remains unadmitted and an unmounted physical-design architecture is next.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 242
        and compass["source_graph_revision"] == 260
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 243
        and compass["source_graph_revision"] == 261
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected representability-review Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve the accepted source-owned-truth, status protocol, adapter, convergence architecture and rehearsal contracts.",
                "Freeze the provider-free unmounted physical-design architecture before any model, migration, service or route edit.",
                "Keep database execution, raw-route change, create schedule fencing, providers, product data, commands and protected integration separately gated.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "The status safety kernel is physically feasible but its additive design remains unselected",
        "why_now": "The pure rehearsal proved semantic behavior, allowing exact source inspection to separate existing primitives from physical gaps.",
        "outcome": "State version, private receipt and ordered locks are each representable with additive change; no current end-to-end implementation is claimed.",
        "unlocks": [
            "Freeze a provider-free unmounted status-confirm physical-design architecture.",
            "Select the exact additive state-version, private receipt and ordered transaction contract without editing source.",
            "Keep implementation and database execution behind later evidence gates.",
        ],
        "does_not_solve": [
            "Column type/default/backfill, migration revision, constraint form or byte storage.",
            "Practice query, lock strength/wait policy, isolation level, deadlock recovery or exception mapping.",
            "ORM/service composition, mounted-route behavior, PostgreSQL execution or restart/unknown-commit recovery.",
            "Provider/credential activity, patient/product data, watchers/events, product commands, deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 261 / Compass 243. The exact-file status-confirm "
        "physical representability review passes: all three domains are feasible only "
        "through additive change. An unmounted physical-design architecture is next; "
        "implementation, database execution and product authority remain closed."
    )
    limit = (
        "The status-confirm physical representability review proves additive feasibility, not a selected schema, transaction design, migration or mounted implementation."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 261
    compass["map_revision"] = 243
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
