"""Record the revision-required shadow clockwork efficacy rehearsal."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestration_harness.git_object_resolution import resolve_commit_source
from scripts import ariadne_compass


GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = "ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-rehearsal"
PARENT = "ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-architecture"
SOURCE_HEAD = "a4044010e9f9319e149660ad889141a32cc8d000"
UPDATED_AT = "2026-08-18T21:39:24.5770151Z"
BASE = (
    "orchestration/continuity/ariadne-provider-free-shadow-clockwork-deepseek-"
    "broker-gear-rehearsal/"
)
PLAN = "docs/ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-rehearsal-plan.md"
THREAT = (
    "docs/security/ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-"
    "rehearsal-threat-model-delta.md"
)
CONTRACT = BASE + "contract.json"
SCHEMA = BASE + "contract.schema.json"
GAUGES = BASE + "frozen-failure-gauges.json"
EVIDENCE = BASE + "provider-free-rehearsal-evidence.json"
REPORT_ARTIFACT = BASE + "rehearsal-report.md"
REJECTED = [
    BASE + f"rejected-attempt-{ordinal:03d}.json" for ordinal in range(1, 4)
]
ENGINE = "orchestration_harness/shadow_clockwork.py"
RUNNER = (
    "scripts/ariadne_provider_free_shadow_clockwork_deepseek_broker_gear_"
    "rehearsal.py"
)
FOCUSED_TEST = (
    "tests/test_ariadne_provider_free_shadow_clockwork_deepseek_broker_gear_"
    "rehearsal.py"
)
PLAN_TEST = FOCUSED_TEST.removesuffix(".py") + "_plan.py"
REGISTER_TEST = "tests/test_ariadne_agent_error_register.py"
PREPLAN_STATE = (
    "orchestration/agent_inbox/codex/ariadne-shadow-clockwork-deepseek-broker-"
    "gear-rehearsal-preplanning-runtime-state.json"
)
PREPLAN_RECEIPT = PREPLAN_STATE.replace("runtime-state", "receipt")
REGISTER = "docs/ariadne-agent-error-correction-register-revision-543.md"
CLOSEOUT = (
    "docs/ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-"
    "rehearsal-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/ariadne-shadow-clockwork-deepseek-broker-"
    "gear-rehearsal-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/2026-08-19--shadow-clockwork-deepseek-"
    "broker-gear-rehearsal.md"
)
UPDATER = (
    "scripts/ariadne_provider_free_shadow_clockwork_deepseek_broker_gear_"
    "rehearsal_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_ariadne_provider_free_shadow_clockwork_deepseek_broker_gear_"
    "rehearsal_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        CONTRACT,
        SCHEMA,
        GAUGES,
        EVIDENCE,
        REPORT_ARTIFACT,
        *REJECTED,
        ENGINE,
        RUNNER,
        FOCUSED_TEST,
        PLAN_TEST,
        REGISTER_TEST,
        PREPLAN_STATE,
        PREPLAN_RECEIPT,
        REGISTER,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        UPDATER,
        CONTINUITY_TEST,
    ]


def _node(*, source_head: str) -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Ariadne provider-free shadow clockwork and DeepSeek broker gear efficacy rehearsal",
        "kind": "foundation",
        "status": "accepted",
        "created_at": UPDATED_AT,
        "updated_at": UPDATED_AT,
        "coordinates": {
            "git_ref": "codex/ariadne-bernie-davida-parallel-seam",
            "source_head": source_head,
            "thread_id": None,
            "worktree_role": "task",
        },
        "relationships": [{"node_id": PARENT, "relation": "builds_on"}],
        "authority": {
            "authorized_openings": [],
            "notes": [
                "The factual provider-free evaluation is accepted; the clockwork candidate is revision-required.",
                "Thirteen reruns versus fourteen is below the frozen fifty-percent efficacy gate.",
                "No accepted generation, provider call, live adoption or current-control retirement occurred.",
            ],
        },
        "decisions": [
            {
                "id": "reject-shadow-clockwork-efficacy-candidate",
                "source": ACCEPTANCE,
                "status": "rejected",
                "summary": "Retain the corrected engine as negative evidence; do not adopt or expand without Yuri's choice.",
            }
        ],
        "claim_scope": [
            "All fourteen frozen gauges reject before publication with zero corrected-candidate escapes.",
            "Caller-supplied binding fields and new mutable-current fixtures are zero.",
            "Thirteen reruns reduce the fourteen-rerun comparator by only 7.143 percent; acceptance required at least 50 percent.",
            "Shared engine growth is 1,552 lines and clean-run median overhead is 112.089 ms, informational only.",
            "DeepSeek, Gemini and every provider remained uncalled because deterministic admission failed.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [CONTRACT, SCHEMA, GAUGES, EVIDENCE, REPORT_ARTIFACT, REGISTER],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLAN_STATE, PREPLAN_RECEIPT, *REJECTED],
            "tests": [FOCUSED_TEST, PLAN_TEST, REGISTER_TEST, CONTINUITY_TEST],
            "artifacts": [ENGINE, RUNNER, UPDATER],
        },
        "unresolved_gates": [
            "Yuri must choose between one bounded governance-projection repair and freezing the clockwork as research evidence.",
            "No repair, live adoption or current-control retirement is implied by this factual closeout.",
            "Occupied DeepSeek remains behind the separate native-Harness HMR boot proof.",
            "No product, practice, provider, Git, runtime, deployment or protected integration authority is opened.",
        ],
    }


def main() -> int:
    source_head = resolve_commit_source(
        repo_root=ROOT,
        source_head=SOURCE_HEAD,
    )["resolved_commit"]
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 327 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node(source_head=source_head))
        graph["graph_revision"] = 328
    elif graph["graph_revision"] == 328 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node(source_head=source_head)
    else:
        raise SystemExit("Unexpected shadow clockwork rehearsal predecessor")
    graph["updated_at"] = UPDATED_AT

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Measure the complete provider-free gear rather than assume it reduces bureaucracy",
        "outcome": "Evaluation retained; candidate revision-required at thirteen reruns versus a maximum seven.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 309
        and compass["source_graph_revision"] == 327
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 310
        and compass["source_graph_revision"] == 328
        and compass["journey"][-1]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected shadow clockwork rehearsal Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Choose whether the failed-efficacy clockwork merits one bounded repair",
        "why_now": (
            "The exact candidate a4044010e9f9319e149660ad889141a32cc8d000 covers all fourteen gauges "
            "but caused thirteen reruns and failed its maximum-seven gate."
        ),
        "outcome": (
            "Yuri chooses either a bounded generated-register/command-manifest repair with fresh cumulative "
            "efficacy measurement, or freezes the clockwork and returns to product work."
        ),
        "unlocks": [
            "A deliberate decision based on measured cost rather than architectural enthusiasm.",
            "If selected, a separately frozen repair with an explicit line budget and no live adoption.",
            "If declined, preservation of the corrected engine as negative research evidence without further process weight.",
        ],
        "does_not_solve": [
            "The failed rehearsal authorizes no automatic repair or live clockwork adoption.",
            "No DeepSeek Harness or provider reliability claim was tested.",
            "No product, practice, data, Git, runtime, deployment or protected integration opens.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 328 / Compass 310. The provider-free shadow clockwork rehearsal is "
        "factually closed but revision-required: thirteen reruns versus fourteen is only a 7.143 percent "
        "reduction, below the frozen fifty-percent gate. Yuri's choice is required before repair or abandonment."
    )
    compass["source_graph_revision"] = 328
    compass["map_revision"] = 310
    compass["updated_at"] = UPDATED_AT

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    _write(GRAPH, graph)
    _write(COMPASS, compass)
    REPORT.write_text(
        ariadne_compass.render_markdown(report),
        encoding="utf-8",
        newline="\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
