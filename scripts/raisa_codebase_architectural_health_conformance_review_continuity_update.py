"""Advance Continuity and Compass for the accepted architecture-health review."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts import ariadne_compass


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = "raisa-codebase-architectural-health-conformance-review"
PARENT = (
    "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-"
    "rehearsal"
)
SOURCE_HEAD = "95ce6b75723d57e672858619c3621d4a273c1f34"
UPDATED_AT = "2026-08-11T00:00:00Z"
PLAN = "docs/raisa-codebase-architectural-health-conformance-review-plan.md"
STATE_MAP = "docs/raisa-codebase-as-built-architectural-state-map.md"
FINDINGS = "docs/raisa-codebase-architectural-health-conformance-review.md"
CLOSEOUT = "docs/raisa-codebase-architectural-health-conformance-review-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-codebase-architectural-health-conformance-review-sol-acceptance.md"
)
RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-codebase-architectural-health-conformance-review-preplanning-receipt.json"
)
PRECOMMIT_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-codebase-architectural-health-conformance-review-precommit-receipt.json"
)
RESEARCH_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-codebase-architectural-health-review-research-predispatch-receipt.json"
)
RESEARCH_STATE = (
    "orchestration/agent_inbox/codex/"
    "raisa-codebase-architectural-health-review-research-predispatch-runtime-state.json"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-11--codebase-architectural-health-conformance-review.md"
)
TEST = "tests/test_raisa_codebase_architectural_health_conformance_review_continuity.py"
UPDATER = (
    "scripts/raisa_codebase_architectural_health_conformance_review_continuity_update.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        STATE_MAP,
        FINDINGS,
        CLOSEOUT,
        ACCEPTANCE,
        RECEIPT,
        PRECOMMIT_RECEIPT,
        RESEARCH_RECEIPT,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "EMR4 codebase architectural-health and conformance review",
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
                "The review is repository-local and findings-only; it opens no product, provider, data, runtime, migration, tool or command boundary.",
                "The mounted GraphQL read, REST command, event fresh-read and default-off boundaries remain sound at the reviewed source.",
                "A bounded provider-free CI and lifecycle conformance repair is required before AES-C0 begins.",
            ],
        },
        "decisions": [
            {
                "id": "accept-architecture-health-review-with-bounded-repair",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept the as-built review, fitness cadence and narrow conformance-repair successor without authorizing a broad refactor.",
            }
        ],
        "claim_scope": [
            "No P0 or current patient or clinical authority breach was found in the selected repository composition and focused checks.",
            "Runtime GraphQL remains authenticated, practice-scoped and Query-only; canonical commands remain REST/OpenAPI-owned.",
            "P1 protected-CI Python-target coverage and P2 API Spine lifecycle drift require a bounded corrective successor.",
            "The review proposes repository fitness functions and cadence; it does not prove exhaustive code quality or production health.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [STATE_MAP, FINDINGS],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [RESEARCH_RECEIPT, RECEIPT, PRECOMMIT_RECEIPT],
            "tests": [TEST],
            "artifacts": [RESEARCH_STATE, UPDATER],
        },
        "unresolved_gates": [
            "The protected Python workflow does not yet compile and bounded-test the full maintained Python 3.11 source selection.",
            "Historical/current API Spine lifecycle assertions still require explicit supersession repair.",
            "Patient, clinical, product-derived, financial, protected and historical-PHI data remain closed.",
            "Applied migration, operational database/source, watcher/listener, providers, tools, commands, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 234 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 235
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 235 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected architecture-health Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Inspect system composition before executable Bureau containment",
        "outcome": "The authority architecture is sound; bounded CI and lifecycle conformance repair is required before AES-C0.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 216
        and compass["source_graph_revision"] == 234
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 217
        and compass["source_graph_revision"] == 235
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected architecture-health Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Serial database durability and the intervening architecture-health review pass.",
                "Repair maintained-source Python 3.11 CI coverage and API Spine lifecycle supersession before AES-C0.",
                "Keep applied migration, operational sources, product/patient data, providers, tools and commands separately gated.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Architecture-health accepted; bounded conformance repair next",
        "why_now": "The review confirmed the authority shape but reproduced CI target-coverage and lifecycle drift that should be corrected before executable containment contracts are added.",
        "outcome": "No P0 is found; one remaining P1 and bounded P2 lifecycle defects define a narrow provider-free repair.",
        "unlocks": [
            "Implement the explicit maintained/protected/historical source-state and Python 3.11 CI conformance repair.",
            "Repair current versus historical API Spine assertions and add baton consistency checks.",
            "After the repair passes, begin AES-C0 architecture and contract with the new fitness constraints.",
        ],
        "does_not_solve": [
            "Exhaustive code quality, appointment-router decomposition or production readiness.",
            "Applied migration, operational database/source access, watcher/listener or persistence.",
            "Patient/product/clinical data, providers, work-cell tools, routes or commands.",
            "Deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 235 / Compass 217. The bounded architecture-health "
        "review confirms the live GraphQL-read/REST-command/event/default-off "
        "authority shape and finds no P0. A narrow provider-free Python 3.11 CI "
        "and API lifecycle conformance repair is next before AES-C0; product, "
        "provider, tool, command and protected boundaries remain closed."
    )
    limit = (
        "Architecture-health acceptance is a repository composition and focused-check review; it is not exhaustive assurance or production readiness."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 235
    compass["map_revision"] = 217
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
