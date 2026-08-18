"""Advance Continuity and Compass for the occupied native Harness rehearsal."""

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
NODE_ID = (
    "deepseek-native-harness-authored-synthetic-agentic-coding-"
    "traceability-rehearsal"
)
PARENT = "deepseek-native-harness-authored-synthetic-traceability-micro-rehearsal"
SOURCE_HEAD = "25067e7d633eae597929d6969a35b22b735b253e"
UPDATED_AT = "2026-08-18T05:32:45.5157558Z"
PLAN = (
    "docs/deepseek-native-harness-authored-synthetic-agentic-coding-"
    "traceability-rehearsal-plan.md"
)
PREFLIGHT = (
    "orchestration/agent_inbox/codex/deepseek-native-harness-agentic-coding-"
    "package-preflight-evidence.json"
)
PREDISPATCH = (
    "orchestration/agent_inbox/codex/deepseek-native-harness-agentic-coding-"
    "pre-dispatch-receipt.json"
)
EVIDENCE = (
    "orchestration/agent_inbox/codex/deepseek-native-harness-agentic-coding-"
    "rehearsal-evidence.json"
)
INCIDENTS = (
    "orchestration/agent_inbox/codex/deepseek-native-harness-agentic-coding-"
    "orchestrator-incidents.json"
)
REGISTER = "docs/ariadne-agent-error-correction-register-revision-392.md"
CLOSEOUT = (
    "docs/deepseek-native-harness-authored-synthetic-agentic-coding-"
    "traceability-rehearsal-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/deepseek-native-harness-agentic-coding-"
    "sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/2026-08-18--deepseek-native-harness-"
    "agentic-coding-traceability-rehearsal.md"
)
UPDATER = (
    "scripts/deepseek_native_harness_agentic_coding_traceability_rehearsal_"
    "continuity_update.py"
)
TEST = (
    "tests/test_deepseek_native_harness_agentic_coding_traceability_"
    "rehearsal_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        PREFLIGHT,
        PREDISPATCH,
        EVIDENCE,
        INCIDENTS,
        REGISTER,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        UPDATER,
        TEST,
    ]


def _node() -> dict[str, Any]:
    inherited_contracts = [
        {
            "contract_id": "combined-patient-practitioner-time-duration-intent",
            "status": "satisfied",
            "evidence": [
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-plan.md",
                "orchestration/continuity/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition/ordinary-diary-cancellation-canonical-consumer-convergence-composition-evidence.json",
                "tests/test_raisa_ordinary_diary_cancellation_canonical_consumer_convergence_composition.py",
            ],
            "note": "The accepted product intent remains inherited; the Harness saw only a generic synthetic fixture.",
        },
        {
            "contract_id": "committed-reschedule-availability-reconciliation",
            "status": "satisfied",
            "evidence": [
                "orchestration/continuity/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition/ordinary-diary-cancellation-canonical-consumer-convergence-composition-evidence.json",
                "review/test_ordinary_diary_cancellation_convergence.py",
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-closeout.md",
            ],
            "note": "The accepted reconciliation contract remains unchanged; no EMR4 source or projection entered the rehearsal.",
        },
    ]
    return {
        "id": NODE_ID,
        "title": "DeepSeek native Harness authored-synthetic agentic-coding traceability rehearsal",
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
                "The result accepts occupied native-Harness traceability, not complete worker reliability.",
                "A monitored low-risk EMR4 trial may follow only through a separately frozen profile-and-work package.",
                "Product data, live runtime, deployment and protected integration remain closed.",
            ],
        },
        "decisions": [{
            "id": "accept-occupied-native-harness-traceability-not-worker-completion",
            "source": ACCEPTANCE,
            "status": "accepted",
            "summary": "Accept materially strong attributable session/tool/usage evidence and the correct partial repair while declining a complete task or default-transport claim.",
        }],
        "claim_scope": [
            "Pinned rc.7 produced six attributable successful model steps and eight ordered tool calls/results.",
            "The worker recovered a stale-version edit, correctly repaired one synthetic source file and left 4/4 tests passing.",
            "The worker omitted the required regression test and successful terminal summary before local request ordinal seven was denied.",
            "No retry, fallback, auxiliary route, telemetry, web or subagent activity occurred.",
            "The result supports monitored low-risk EMR4 trial use after profile codification, not unrestricted default promotion.",
        ],
        "contract_evidence": inherited_contracts,
        "evidence": {
            "plans": [
                PLAN,
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-plan.md",
            ],
            "findings": [
                PREFLIGHT,
                EVIDENCE,
                INCIDENTS,
                REGISTER,
                "orchestration/continuity/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition/ordinary-diary-cancellation-canonical-consumer-convergence-composition-evidence.json",
            ],
            "closeouts": [
                CLOSEOUT,
                MAILBOX,
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-closeout.md",
            ],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREDISPATCH],
            "tests": [
                TEST,
                "tests/test_raisa_ordinary_diary_cancellation_canonical_consumer_convergence_composition.py",
                "review/test_ordinary_diary_cancellation_convergence.py",
            ],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "Complete native-Harness worker reliability on real EMR4 work remains unproved.",
            "The versioned EMR4 profile family and first monitored work package remain to be frozen.",
            "Unrestricted default-worker promotion remains closed.",
            "Ordinary-practice admission, product data, providers, deployment, production and protected integration remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 318 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 319
    elif graph["graph_revision"] == 319 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected occupied native Harness Continuity predecessor")
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Measure attributable native-Harness multi-step coding control before monitored EMR4 use",
        "outcome": "Occupied traceability and a correct partial repair passed; complete worker-task reliability did not.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 300
        and compass["source_graph_revision"] == 318
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 301
        and compass["source_graph_revision"] == 319
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected occupied native Harness Compass predecessor")
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Native Harness ready for versioned-profile codification and one monitored low-risk EMR4 trial",
        "why_now": "The broader synthetic run exposed every model/tool step and terminal cause, enough to replace further broad rehearsal with representative work.",
        "outcome": "Freeze the minimal profile family, then admit one exact-path provider-free EMR4 development package under Sol review.",
        "unlocks": [
            "Codify emr4-readonly-review, emr4-bounded-worker and emr4-provider-free profiles with pinned package/profile identities.",
            "Use the bounded profile for one real low-risk EMR4 package and compare planned work, trace and candidate admission.",
        ],
        "does_not_solve": [
            "Complete worker reliability and lower failure frequency remain unproved.",
            "The native Harness is not an unrestricted default worker transport.",
            "No ordinary practice, product/patient data, live runtime, deployment, Pages or protected integration is enabled.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 319 / Compass 301. The pinned native DeepSeek "
        "Harness now has materially strong occupied traceability evidence and a "
        "correct partial coding result, while complete task reliability remains "
        "unproved; the next step is profile codification followed by one monitored "
        "low-risk provider-free EMR4 development package."
    )
    limit = (
        "The occupied native-Harness result supports a monitored exact-path EMR4 "
        "trial after profile codification; it is not unrestricted default-worker, "
        "product-data, live-runtime or protected-integration authority."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 319
    compass["map_revision"] = 301
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
