"""Advance Continuity and Compass for the post-Harness successor repair."""

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
NODE_ID = "ariadne-post-native-harness-successor-resolution-repair"
PARENT = (
    "deepseek-native-harness-exact-tool-view-recovery-and-second-monitored-"
    "development-admission"
)
SOURCE_HEAD = "2a31437f6da0defa2dc9247491f04d5b23c97608"
UPDATED_AT = "2026-08-18T12:06:43.5937197Z"
PLAN = "docs/ariadne-post-native-harness-successor-resolution-repair-plan.md"
THREAT = (
    "docs/security/ariadne-post-native-harness-successor-resolution-repair-"
    "threat-model-delta.md"
)
REGISTER = "docs/ariadne-agent-error-correction-register-revision-459.md"
CLOSEOUT = "docs/ariadne-post-native-harness-successor-resolution-repair-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/ariadne-post-native-harness-successor-"
    "resolution-repair-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/2026-08-18--post-native-harness-"
    "successor-resolution-repair.md"
)
RUNTIME = (
    "orchestration/agent_inbox/codex/ariadne-post-native-harness-successor-"
    "resolution-preplanning-runtime-state.json"
)
FAILED_RECEIPT = (
    "orchestration/agent_inbox/codex/ariadne-post-native-harness-successor-"
    "resolution-preplanning-receipt.json"
)
CORRECTED_RECEIPT = (
    "orchestration/agent_inbox/codex/ariadne-post-native-harness-successor-"
    "resolution-preplanning-corrected-receipt.json"
)
UPDATER = (
    "scripts/ariadne_post_native_harness_successor_resolution_repair_"
    "continuity_update.py"
)
TEST = (
    "tests/test_ariadne_post_native_harness_successor_resolution_repair_"
    "continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _contract_evidence() -> list[dict[str, Any]]:
    return [
        {
            "contract_id": "combined-patient-practitioner-time-duration-intent",
            "status": "satisfied",
            "evidence": [
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-plan.md",
                "orchestration/continuity/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition/ordinary-diary-cancellation-canonical-consumer-convergence-composition-evidence.json",
                "tests/test_raisa_ordinary_diary_cancellation_canonical_consumer_convergence_composition.py",
            ],
            "note": "The accepted product intent remains inherited; this repair changed continuity metadata only.",
        },
        {
            "contract_id": "committed-reschedule-availability-reconciliation",
            "status": "satisfied",
            "evidence": [
                "orchestration/continuity/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition/ordinary-diary-cancellation-canonical-consumer-convergence-composition-evidence.json",
                "review/test_ordinary_diary_cancellation_convergence.py",
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-closeout.md",
            ],
            "note": "The accepted reconciliation contract remains unchanged; no product source or projection entered this repair.",
        },
    ]


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        RUNTIME,
        FAILED_RECEIPT,
        CORRECTED_RECEIPT,
        REGISTER,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        UPDATER,
        TEST,
        "tests/test_ariadne_post_native_harness_successor_resolution_repair_plan.py",
        "tests/test_current_baton_consistency.py",
        "tests/test_ariadne_agent_error_register.py",
        "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-plan.md",
        "orchestration/continuity/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition/ordinary-diary-cancellation-canonical-consumer-convergence-composition-evidence.json",
        "tests/test_raisa_ordinary_diary_cancellation_canonical_consumer_convergence_composition.py",
        "review/test_ordinary_diary_cancellation_convergence.py",
        "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-closeout.md",
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Post-native-Harness successor resolution repair",
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
                "The already accepted default-off check-in route convergence remains exact and is not repeated.",
                "The successor is a provider-free read-only readiness review with no practice enablement or product edit authority.",
                "DeepSeek native-Harness occupied work remains paused and Claude Code is not a silent fallback.",
                "Product data, providers, deployment and protected integration remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-corrected-post-harness-successor",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept the continuity-only successor correction and continue with the no-enable read-only admission-readiness review.",
            }
        ],
        "claim_scope": [
            "The default-off check-in route convergence already passed at c82c3a741053a9c8da260aa62e1a968af22bb54e.",
            "Every stale post-Harness successor pointer now names the read-only ordinary-practice admission-readiness review.",
            "A deterministic guard rejects an exact accepted plan name in the live Next row.",
            "No product source, configuration, behavior, data, provider or protected ref changed.",
        ],
        "contract_evidence": _contract_evidence(),
        "evidence": {
            "plans": [
                PLAN,
                THREAT,
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-plan.md",
            ],
            "findings": [
                REGISTER,
                "orchestration/continuity/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition/ordinary-diary-cancellation-canonical-consumer-convergence-composition-evidence.json",
            ],
            "closeouts": [
                CLOSEOUT,
                MAILBOX,
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-closeout.md",
            ],
            "acceptances": [ACCEPTANCE],
            "receipts": [RUNTIME, FAILED_RECEIPT, CORRECTED_RECEIPT],
            "tests": [
                "tests/test_ariadne_post_native_harness_successor_resolution_repair_plan.py",
                "tests/test_current_baton_consistency.py",
                "tests/test_ariadne_agent_error_register.py",
                "tests/test_ariadne_active_operation_latch.py",
                "tests/test_ariadne_active_operation_latch_continuity.py",
                "tests/test_api_spine_artifacts.py",
                "tests/test_raisa_ordinary_diary_cancellation_canonical_consumer_convergence_composition.py",
                "review/test_ordinary_diary_cancellation_convergence.py",
                TEST,
            ],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "No ordinary practice is admitted to canonical check-in.",
            "No product code, configuration, live route or product data is authorized by the readiness review.",
            "Future native-Harness occupied work requires a separate provider-free HMR startup proof.",
            "Provider, runtime, deployment, release, Pages and protected integration remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 321 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 322
    elif graph["graph_revision"] == 322 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected successor repair Continuity predecessor")
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Correct the stale post-Harness successor without reopening accepted product work",
        "outcome": "Every live pointer now advances to a no-enable read-only ordinary-practice check-in admission-readiness review.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 303
        and compass["source_graph_revision"] == 321
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 304
        and compass["source_graph_revision"] == 322
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected successor repair Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Review ordinary-practice canonical check-in admission readiness without enabling it",
        "why_now": "Route convergence already passed at c82c3a741053a9c8da260aa62e1a968af22bb54e and the stale post-Harness pointer is corrected at 2a31437f6da0defa2dc9247491f04d5b23c97608.",
        "outcome": "Inventory the unchanged default-off and empty-allowlist posture plus API Spine, authorization, tenant, idempotency, audit, rollback, rollout and observability prerequisites with no product or data change.",
        "unlocks": [
            "Produce an evidence-backed readiness inventory for a later explicit admission decision.",
            "Name every unmet prerequisite while preserving default denial.",
            "Reassess worker and verifier lanes only if a later candidate creates an independently owned work package.",
        ],
        "does_not_solve": [
            "No practice is enabled and no product code, configuration, live route or product data is changed.",
            "No generic-status Arrived, grammar/client or waiting-area movement is admitted.",
            "No provider, runtime, deployment, release, Pages or protected integration is enabled.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 322 / Compass 304. The stale post-Harness "
        "successor is corrected without repeating accepted route work or changing "
        "the product. Next is the provider-free read-only ordinary-practice "
        "canonical check-in admission-readiness review; default denial remains."
    )
    compass["source_graph_revision"] = 322
    compass["map_revision"] = 304
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
