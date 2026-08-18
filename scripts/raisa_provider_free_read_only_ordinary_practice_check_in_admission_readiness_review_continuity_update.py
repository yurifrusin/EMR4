"""Advance Continuity and Compass for the ordinary check-in readiness review."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ariadne_compass
from orchestration_harness.git_object_resolution import resolve_commit_source


GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = (
    "raisa-provider-free-read-only-ordinary-practice-canonical-check-in-"
    "admission-readiness-review"
)
PARENT = "ariadne-post-native-harness-successor-resolution-repair"
SOURCE_HEAD = "27101faa86b5aa3850e90bc4ded8600e5f8d7dc9"
UPDATED_AT = "2026-08-18T13:19:10.6024156Z"
PLAN = (
    "docs/raisa-provider-free-read-only-ordinary-practice-canonical-check-in-"
    "admission-readiness-review-plan.md"
)
THREAT = (
    "docs/security/raisa-provider-free-read-only-ordinary-practice-canonical-"
    "check-in-admission-readiness-review-threat-model-delta.md"
)
BASE = (
    "orchestration/continuity/raisa-provider-free-read-only-ordinary-practice-"
    "canonical-check-in-admission-readiness-review/"
)
CONTRACT = BASE + "admission-readiness-review-contract.json"
SCHEMA = BASE + "admission-readiness-review-contract.schema.json"
EVIDENCE = BASE + "provider-free-read-only-evidence.json"
FINDING = BASE + "admission-readiness-review-report.md"
REVIEWER = (
    "scripts/raisa_provider_free_read_only_ordinary_practice_check_in_"
    "admission_readiness_review.py"
)
FOCUSED_TEST = (
    "tests/test_raisa_provider_free_read_only_ordinary_practice_check_in_"
    "admission_readiness_review.py"
)
PLAN_TEST = (
    "tests/test_raisa_provider_free_read_only_ordinary_practice_check_in_"
    "admission_readiness_review_plan.py"
)
RUNTIME = (
    "orchestration/agent_inbox/codex/raisa-provider-free-read-only-ordinary-"
    "practice-canonical-check-in-admission-readiness-review-preplanning-"
    "runtime-state.json"
)
RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-read-only-ordinary-"
    "practice-canonical-check-in-admission-readiness-review-preplanning-"
    "receipt.json"
)
REGISTER = "docs/ariadne-agent-error-correction-register-revision-487.md"
CLOSEOUT = (
    "docs/raisa-provider-free-read-only-ordinary-practice-canonical-check-in-"
    "admission-readiness-review-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-ordinary-practice-check-in-"
    "admission-readiness-review-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/2026-08-18--ordinary-practice-canonical-"
    "check-in-admission-readiness-review.md"
)
UPDATER = (
    "scripts/raisa_provider_free_read_only_ordinary_practice_check_in_"
    "admission_readiness_review_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_read_only_ordinary_practice_check_in_"
    "admission_readiness_review_continuity.py"
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
        FINDING,
        REVIEWER,
        FOCUSED_TEST,
        PLAN_TEST,
        RUNTIME,
        RECEIPT,
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
        "title": "Provider-free read-only ordinary-practice canonical check-in admission-readiness review",
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
                "The ordinary-practice admission verdict is fail-closed: not ready.",
                "Existing A5.1 remains default-off and exact authored-synthetic practice allowlisted.",
                "Yuri deferred the product successor behind one transactional closeout-control-plane consolidation and efficacy rehearsal.",
            ],
        },
        "decisions": [
            {
                "id": "accept-not-ready-ordinary-practice-check-in-admission-review",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept the 6/3/3 readiness matrix and continue only to default-off admission-control architecture.",
            }
        ],
        "claim_scope": [
            "All 28 frozen source hashes and canonical-LF bindings match.",
            "The exact matrix is six satisfied, three blocking gaps and three operational-evidence gaps.",
            "More than 120 hostile contract mutations fail closed.",
            "No product/configuration source, practice posture, route, database, provider or protected ref changed.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [CONTRACT, SCHEMA, EVIDENCE, FINDING, REGISTER],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [RUNTIME, RECEIPT],
            "tests": [FOCUSED_TEST, PLAN_TEST, CONTINUITY_TEST],
            "artifacts": [REVIEWER, UPDATER],
        },
        "unresolved_gates": [
            "Explicit ordinary-practice admission control is not designed or implemented.",
            "Ordinary rollout, kill-switch and rollback operations are not designed or exercised.",
            "Non-PHI A5.1 observability and alerting are not designed or implemented.",
            "Tenant-role, unknown-commit recovery and environment posture still require operational evidence.",
            "No enablement, product data, provider, runtime, deployment or protected integration is authorized.",
            "Default-off ordinary-practice admission-control architecture remains deferred, not discarded.",
        ],
    }


def main() -> int:
    source_resolution = resolve_commit_source(
        repo_root=ROOT,
        source_head=SOURCE_HEAD,
    )
    source_head = source_resolution["resolved_commit"]
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 322 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node(source_head=source_head))
        graph["graph_revision"] = 323
    elif graph["graph_revision"] == 323 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node(source_head=source_head)
    else:
        raise SystemExit("Unexpected ordinary check-in readiness Continuity predecessor")
    graph["updated_at"] = UPDATED_AT

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Decide ordinary-practice canonical check-in readiness without enabling it",
        "outcome": "Not ready: six dimensions pass, three blocking controls and three operational evidence obligations remain.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 304
        and compass["source_graph_revision"] == 322
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 305
        and compass["source_graph_revision"] == 323
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected ordinary check-in readiness Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Consolidate the closeout control plane and measure whether it reduces procedural weight",
        "why_now": "The read-only 6/3/3 matrix at 27101faa86b5aa3850e90bc4ded8600e5f8d7dc9 is accepted, and Yuri explicitly prioritized a measured transactional replacement for hand-authored closeout ceremony.",
        "outcome": "Shadow one typed closeout manifest against representative history and accept it only if retries, manual fields, wall time and maintained workflow surface fall without coverage loss.",
        "unlocks": [
            "Freeze one provider-free transactional closeout-control-plane consolidation and efficacy plan.",
            "Measure prevention, escapes, commands, reruns, wall time, files, lines and fixture count against the current baseline.",
            "Retire redundant controls only after shadow parity and explicit efficacy thresholds pass.",
        ],
        "does_not_solve": [
            "No ordinary practice is enabled and no feature flag or allowlist changes.",
            "No product/configuration source, route, database, client or waiting-area movement changes.",
            "No product data, provider, runtime, deployment, release, Pages or protected integration opens.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 323 / Compass 305. Ordinary-practice canonical "
        "check-in admission is not ready: six dimensions pass, three blocking "
        "controls and three operational-evidence obligations remain. Yuri has "
        "deferred its product successor behind a transactional closeout-control-"
        "plane consolidation and efficacy rehearsal."
    )
    compass["source_graph_revision"] = 323
    compass["map_revision"] = 305
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
