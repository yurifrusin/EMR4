"""Advance Continuity and Compass for conditional-command admission rehearsal."""

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
NODE_ID = "raisa-provider-free-unmounted-conditional-command-admission-rehearsal"
PARENT = "raisa-context-fabric-source-owned-truth-conditional-command-reorientation"
SOURCE_HEAD = "f465d6a6536ea2e69eec8df2ed1c2f9f65c24f6c"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = "docs/raisa-provider-free-unmounted-conditional-command-admission-rehearsal-plan.md"
DESIGN = "docs/raisa-provider-free-unmounted-conditional-command-admission-rehearsal-design.md"
THREAT = "docs/security/raisa-provider-free-unmounted-conditional-command-admission-rehearsal-threat-model-delta.md"
PACKET_DIR = (
    "orchestration/continuity/"
    "raisa-provider-free-unmounted-conditional-command-admission-rehearsal/"
)
SCENARIOS = PACKET_DIR + "scenarios.json"
SCHEMA = PACKET_DIR + "scenarios.schema.json"
CLOSEOUT = "docs/raisa-provider-free-unmounted-conditional-command-admission-rehearsal-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-conditional-command-admission-rehearsal-sol-acceptance.md"
)
FAILURE = (
    "orchestration/agent_inbox/codex/"
    "raisa-conditional-command-admission-rehearsal-source-head-draft-failure-receipt.json"
)
REGISTER_REVISION = "docs/ariadne-agent-error-correction-register-revision-256.md"
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-12--provider-free-unmounted-conditional-command-admission-rehearsal.md"
)
TEST = "tests/test_raisa_provider_free_unmounted_conditional_command_admission_rehearsal_continuity.py"
UPDATER = "scripts/raisa_provider_free_unmounted_conditional_command_admission_rehearsal_continuity_update.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        DESIGN,
        THREAT,
        SCENARIOS,
        SCHEMA,
        CLOSEOUT,
        ACCEPTANCE,
        FAILURE,
        REGISTER_REVISION,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free unmounted conditional-command admission rehearsal",
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
                "This is a provider-free pure in-memory authored-synthetic rehearsal.",
                "It imports no route or database and performs no command, mutation, audit or receipt effect.",
                "The next descendant remains provider-free, unmounted and design-only.",
            ],
        },
        "decisions": [
            {
                "id": "accept-conditional-command-admission-rehearsal",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept exact packet admission and eight-outcome precedence with planned effects only.",
            }
        ],
        "claim_scope": [
            "Thirty-seven canonical cases cover four operations, eight outcomes and nineteen admission rejections.",
            "All thirty-two hostile mutations fail closed.",
            "Only committed plans a mutation; no effect is performed.",
            "Create requires schedule-domain fencing and event evidence cannot assert truth or success.",
            "Current authority precedes replay disclosure and other outcome evaluation.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [DESIGN, THREAT],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [FAILURE],
            "tests": [
                "tests/test_raisa_provider_free_unmounted_conditional_command_admission_rehearsal.py",
                TEST,
            ],
            "artifacts": [SCENARIOS, SCHEMA, UPDATER],
        },
        "unresolved_gates": [
            "No production token, cryptography, route, common kernel, database fence or persistent idempotency/audit is implemented.",
            "Legacy compatibility routes remain mounted and unchanged.",
            "Operational database/source/watcher access, real events, patient/product data, provider, commands, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 245 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 246
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 246 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected conditional-command rehearsal Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Mechanically admit conditional-command packets and typed outcomes without runtime effects",
        "outcome": "Rehearsal passes; the next safe tranche maps legacy and proposal/confirm routes onto one abstract backend kernel.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 227
        and compass["source_graph_revision"] == 245
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 228
        and compass["source_graph_revision"] == 246
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected conditional-command rehearsal Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Freeze the provider-free unmounted legacy-route convergence map and common kernel-interface design.",
                "Keep route/database behavior closed until a later implementation descendant has its own acceptance.",
                "Retain Durable Event and Cue Delivery as a later observability-first extension.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Conditional-command admission semantics proved; common kernel interface next",
        "why_now": "The accepted architecture required a mechanical proof that malformed packets stop and valid packets resolve to one non-ambiguous outcome before designing route convergence.",
        "outcome": "Thirty-seven authored-synthetic cases and thirty-two attacks pass without a route, database, event or mutation.",
        "unlocks": [
            "Map all four raw compatibility routes and proposal/confirm replacements onto one abstract backend conditional-command interface.",
            "Freeze route-specific confirmation and idempotency migration requirements without changing behavior.",
        ],
        "does_not_solve": [
            "Production tokens, route implementation, database fencing, persistent idempotency or audit.",
            "Durable cue delivery, CF-D2, patient/product data, provider tools, commands, deployment, Pages or protected refs.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 246 / Compass 228. The provider-free unmounted "
        "conditional-command admission rehearsal passes all 37 canonical cases and "
        "32 hostile mutations with zero effects. The next safe tranche is the legacy-route "
        "convergence map and common kernel-interface design."
    )
    limit = (
        "The conditional-command admission rehearsal is pure authored-synthetic evaluation; "
        "it does not prove route behavior, database serialization or persistent effects."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 246
    compass["map_revision"] = 228
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
