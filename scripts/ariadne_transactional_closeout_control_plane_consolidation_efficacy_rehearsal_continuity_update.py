"""Advance Continuity and Compass for the transactional closeout rehearsal."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestration_harness.git_object_resolution import resolve_commit_source
from scripts import ariadne_compass


GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = (
    "ariadne-transactional-closeout-control-plane-consolidation-efficacy-rehearsal"
)
PARENT = (
    "raisa-provider-free-read-only-ordinary-practice-canonical-check-in-"
    "admission-readiness-review"
)
SOURCE_HEAD = "762cd8fd1a6493f4d4b82e24f97d851531b6f7f0"
UPDATED_AT = "2026-08-18T16:22:38.3870606Z"
PLAN = "docs/ariadne-transactional-closeout-control-plane-consolidation-efficacy-rehearsal-plan.md"
THREAT = "docs/security/ariadne-transactional-closeout-control-plane-consolidation-efficacy-rehearsal-threat-model-delta.md"
BASE = (
    "orchestration/continuity/ariadne-transactional-closeout-control-plane-"
    "consolidation-efficacy-rehearsal/"
)
SCHEMA = BASE + "control-plane.schema.json"
FIXTURES = BASE + "historical-shadow-fixtures.json"
EVIDENCE = BASE + "provider-free-efficacy-evidence.json"
FINDING = BASE + "provider-free-efficacy-report.md"
ENGINE = "orchestration_harness/transactional_closeout.py"
BROKER = "scripts/ariadne_deepseek_native_harness_broker.mjs"
ENGINE_TEST = "tests/test_ariadne_transactional_closeout.py"
BROKER_TEST = "tests/test_ariadne_deepseek_native_harness_broker.py"
PREPLAN_STATE = (
    "orchestration/agent_inbox/codex/ariadne-transactional-closeout-control-"
    "plane-consolidation-efficacy-rehearsal-preplanning-runtime-state.json"
)
PREPLAN_RECEIPT = (
    "orchestration/agent_inbox/codex/ariadne-transactional-closeout-control-"
    "plane-consolidation-efficacy-rehearsal-preplanning-receipt.json"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/ariadne-transactional-closeout-"
    "control-plane-gemini37-corrected-review-receipt.json"
)
REGISTER = "docs/ariadne-agent-error-correction-register-revision-509.md"
CLOSEOUT = (
    "docs/ariadne-transactional-closeout-control-plane-consolidation-efficacy-"
    "rehearsal-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/ariadne-transactional-closeout-control-"
    "plane-consolidation-efficacy-rehearsal-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/2026-08-19--ariadne-transactional-"
    "closeout-control-plane-consolidation-efficacy-rehearsal.md"
)
UPDATER = (
    "scripts/ariadne_transactional_closeout_control_plane_consolidation_"
    "efficacy_rehearsal_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_ariadne_transactional_closeout_control_plane_consolidation_"
    "efficacy_rehearsal_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        SCHEMA,
        FIXTURES,
        EVIDENCE,
        FINDING,
        ENGINE,
        BROKER,
        ENGINE_TEST,
        BROKER_TEST,
        PREPLAN_STATE,
        PREPLAN_RECEIPT,
        REVIEW,
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
        "title": "Ariadne transactional closeout control-plane consolidation efficacy rehearsal",
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
                "One typed journal and reducer pass the provider-free historical shadow efficacy thresholds.",
                "A digest-bound DeepSeek broker WorkOrder continues the same causal clock provider-free.",
                "The result is shadow-only; no live closeout control is replaced or retired.",
            ],
        },
        "decisions": [
            {
                "id": "accept-shadow-transactional-closeout-clock",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept measured shadow efficacy and broker-clock conformance without live adoption.",
            }
        ],
        "claim_scope": [
            "Maintained comparison surface falls from six files and 1,002 lines to five files and 981 changed-or-new lines.",
            "Manual constants fall from 72 to 54 typed leaves and publication calls from 12 to one atomic rename.",
            "The frozen controlled retry sample falls from seven to zero without coverage loss.",
            "Candidate timing is slower and is not an acceptance benefit.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [SCHEMA, FIXTURES, EVIDENCE, FINDING, REGISTER],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLAN_STATE, PREPLAN_RECEIPT, REVIEW],
            "tests": [ENGINE_TEST, BROKER_TEST, CONTINUITY_TEST],
            "artifacts": [ENGINE, BROKER, UPDATER],
        },
        "unresolved_gates": [
            "Live control-plane adoption or retirement requires a separate transactional migration gate.",
            "Canonical historical evidence-file presence remains mandatory before live adoption.",
            "DeepSeek occupied EMR4 work remains blocked by the separate native-Harness HMR boot proof.",
            "No ordinary-practice check-in admission, product runtime, deployment or protected integration is authorized.",
        ],
    }


def main() -> int:
    source_resolution = resolve_commit_source(repo_root=ROOT, source_head=SOURCE_HEAD)
    source_head = source_resolution["resolved_commit"]
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 323 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node(source_head=source_head))
        graph["graph_revision"] = 324
    elif graph["graph_revision"] == 324 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node(source_head=source_head)
    else:
        raise SystemExit("Unexpected transactional closeout Continuity predecessor")
    graph["updated_at"] = UPDATED_AT

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove a smaller typed closeout clock and DeepSeek broker coupling in shadow",
        "outcome": "Shadow efficacy passes; live control replacement remains closed.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 305
        and compass["source_graph_revision"] == 323
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 306
        and compass["source_graph_revision"] == 324
        and compass["journey"][-1]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected transactional closeout Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Design default-off ordinary-practice canonical check-in admission control",
        "why_now": "The 6/3/3 readiness review identified three blocking controls, and the prerequisite clockwork efficacy rehearsal now passes in shadow without opening live adoption.",
        "outcome": "Freeze the narrowest provider-free architecture for explicit admission, kill-switch and rollback operations, and non-PHI observability while default denial remains exact.",
        "unlocks": [
            "Freeze one admission-control architecture with explicit default denial.",
            "Separate authored-synthetic practice allowlisting from future ordinary-practice admission.",
            "Specify rollout, kill-switch, rollback and non-PHI observability without enablement.",
        ],
        "does_not_solve": [
            "No ordinary practice is enabled and no feature flag or allowlist changes.",
            "No product route, status grammar, client or waiting-area movement changes.",
            "No live clockwork adoption, product data, provider, runtime, deployment or protected integration opens.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 324 / Compass 306. The typed transactional "
        "closeout clock and DeepSeek broker coupling pass provider-free shadow "
        "efficacy, while live control replacement remains closed. The next "
        "tranche is default-off ordinary-practice canonical check-in admission-"
        "control architecture."
    )
    compass["source_graph_revision"] = 324
    compass["map_revision"] = 306
    compass["updated_at"] = UPDATED_AT

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    _write(GRAPH, graph)
    _write(COMPASS, compass)
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
