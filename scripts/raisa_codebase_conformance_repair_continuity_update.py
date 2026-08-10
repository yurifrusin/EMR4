"""Advance Continuity and Compass for the accepted conformance repair."""

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
NODE_ID = "raisa-codebase-conformance-repair"
PARENT = "raisa-codebase-architectural-health-conformance-review"
SOURCE_HEAD = "8ce3a591fa0e63ad2d68bf95a8d7e24369dd872f"
UPDATED_AT = "2026-08-11T00:00:00Z"
PLAN = "docs/raisa-codebase-conformance-repair-plan.md"
CLOSEOUT = "docs/raisa-codebase-conformance-repair-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-codebase-conformance-repair-sol-acceptance.md"
)
PREPLANNING_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-codebase-conformance-repair-preplanning-receipt.json"
)
POSTCOMPACTION_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-codebase-conformance-repair-postcompaction-receipt.json"
)
PREACCEPTANCE_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-codebase-conformance-repair-preacceptance-receipt.json"
)
PREACCEPTANCE_STATE = (
    "orchestration/agent_inbox/codex/"
    "raisa-codebase-conformance-repair-preacceptance-runtime-state.json"
)
PRECOMMIT_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-codebase-conformance-repair-precommit-receipt.json"
)
PRECOMMIT_STATE = (
    "orchestration/agent_inbox/codex/"
    "raisa-codebase-conformance-repair-precommit-runtime-state.json"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/2026-08-11--codebase-conformance-repair.md"
)
SOURCE_STATE = "orchestration/harness_settings/python_source_state.json"
API_STATUS = "docs/api-spine/external-read-model-current-surface-status.json"
API_SCHEMA = "docs/api-spine/external-read-model-current-surface-status.schema.json"
TEST = "tests/test_raisa_codebase_conformance_repair_continuity.py"
UPDATER = "scripts/raisa_codebase_conformance_repair_continuity_update.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        SOURCE_STATE,
        API_STATUS,
        API_SCHEMA,
        CLOSEOUT,
        ACCEPTANCE,
        PREPLANNING_RECEIPT,
        POSTCOMPACTION_RECEIPT,
        PREACCEPTANCE_RECEIPT,
        PRECOMMIT_RECEIPT,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "EMR4 bounded codebase conformance repair",
        "kind": "maintenance",
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
                "The repair changes repository verification and lifecycle declarations only; it opens no product or runtime surface.",
                "The source-state validator does not enumerate protected evidence and compiles selected maintained source in memory.",
                "GraphQL remains read-only and product mutations remain REST/OpenAPI command-owned under the API Spine.",
            ],
        },
        "decisions": [
            {
                "id": "accept-bounded-codebase-conformance-repair",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept the exact Python 3.11 CI, API lifecycle and baton-consistency repair before AES-C0.",
            }
        ],
        "claim_scope": [
            "Protected CI now requires exact Python 3.11, in-memory maintained-source compilation, Ruff/leakage and bounded static conformance tests.",
            "The practitioner directory is currently implemented and mounted as read-only REST and GraphQL, not deployment or production ready.",
            "Patient reminder/message and RACGP/Cochrane read surfaces remain explicit gaps.",
            "The repair changes no route behavior, database state, product workflow or authority.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [SOURCE_STATE, API_STATUS, API_SCHEMA],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                PREPLANNING_RECEIPT,
                POSTCOMPACTION_RECEIPT,
                PREACCEPTANCE_RECEIPT,
                PRECOMMIT_RECEIPT,
            ],
            "tests": [
                "tests/test_python_source_state.py",
                "tests/test_api_spine_external_read_model_current_surface_status.py",
                "tests/test_api_spine_external_read_model_gap_inventory.py",
                "tests/test_current_baton_consistency.py",
                TEST,
            ],
            "artifacts": [PREACCEPTANCE_STATE, PRECOMMIT_STATE, UPDATER],
        },
        "unresolved_gates": [
            "AES-C0 architecture and contract has not yet been frozen or accepted.",
            "No capability broker, work-cell process, provider, product context, tool or command is implemented or opened.",
            "Protected evidence, patient/clinical/product data, database/source access, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 235 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 236
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 236 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected conformance-repair Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Repair repository fitness before executable Bureau containment",
        "outcome": "Maintained Python 3.11 CI, API lifecycle supersession and baton consistency now pass; AES-C0 architecture is next.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 217
        and compass["source_graph_revision"] == 235
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 218
        and compass["source_graph_revision"] == 236
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected conformance-repair Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Serial database durability, architecture-health review and bounded codebase conformance repair pass.",
                "Freeze and accept AES-C0 architecture and contract before any executable capability descendant.",
                "Keep product/patient data, providers, operational persistence, tools and commands separately gated.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Repository conformance repaired; AES-C0 architecture next",
        "why_now": "The prerequisite database slice, architecture-health review and narrow CI/lifecycle repair pass, so the selected containment programme can begin without opening runtime capability.",
        "outcome": "The maintained source, current API lifecycle and live baton now have executable consistency checks.",
        "unlocks": [
            "Freeze AES-C0 capability classes, external broker trust boundary and immutable generation manifest.",
            "Bind no-fallback state, route classification, command separation and exact denial behavior into AES-C0 acceptance.",
            "Continue the planned provider-free containment sequence after architecture acceptance.",
        ],
        "does_not_solve": [
            "Capability-broker implementation, hostile execution rehearsal or occupied work cells.",
            "Applied migration, operational database/source access, watcher/listener or persistence.",
            "Patient/product/clinical data, providers, tools, routes or commands.",
            "Deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 236 / Compass 218. The bounded Python 3.11 CI, "
        "API lifecycle and baton-consistency repair passes without product "
        "behavior change. AES-C0 architecture and contract is next; product, "
        "provider, data, tool, command and protected boundaries remain closed."
    )
    limit = (
        "Codebase conformance repair proves the selected maintained-source and lifecycle checks, not exhaustive code quality or production readiness."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 236
    compass["map_revision"] = 218
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
