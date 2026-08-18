"""Advance Continuity and Compass for the native Harness no-call rehearsal."""

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
NODE_ID = "deepseek-native-harness-authored-synthetic-traceability-micro-rehearsal"
PARENT = (
    "raisa-provider-free-default-off-canonical-check-in-route-adapter-"
    "convergence-rehearsal"
)
SOURCE_HEAD = "ed044625b6f1e59d323c21ced6ec6e2372a11d3f"
UPDATED_AT = "2026-08-18T04:37:03Z"
PLAN = "docs/deepseek-native-harness-authored-synthetic-traceability-micro-rehearsal-plan.md"
PREFLIGHT = "orchestration/agent_inbox/codex/deepseek-native-harness-traceability-package-preflight-evidence.json"
PREDISPATCH = "orchestration/agent_inbox/codex/deepseek-native-harness-traceability-pre-dispatch-receipt.json"
EVIDENCE = "orchestration/agent_inbox/codex/deepseek-native-harness-traceability-micro-rehearsal-evidence.json"
INCIDENTS = "orchestration/agent_inbox/codex/deepseek-native-harness-traceability-orchestrator-incidents.json"
REGISTER = "docs/ariadne-agent-error-correction-register-revision-391.md"
CLOSEOUT = "docs/deepseek-native-harness-authored-synthetic-traceability-micro-rehearsal-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/deepseek-native-harness-traceability-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-18--deepseek-native-harness-traceability-micro-rehearsal.md"
UPDATER = "scripts/deepseek_native_harness_traceability_micro_rehearsal_continuity_update.py"
TEST = "tests/test_deepseek_native_harness_traceability_micro_rehearsal_continuity.py"


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
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-closeout.md",
            ],
            "note": "The accepted first-party intent contract remains inherited; this isolated Harness measurement changes no client intent.",
        },
        {
            "contract_id": "committed-reschedule-availability-reconciliation",
            "status": "satisfied",
            "evidence": [
                "orchestration/continuity/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition/ordinary-diary-cancellation-canonical-consumer-convergence-composition-evidence.json",
                "review/test_ordinary_diary_cancellation_convergence.py",
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-closeout.md",
            ],
            "note": "The accepted reconciliation contract remains inherited; the Harness process read no product source and changed no projection.",
        },
    ]
    return {
        "id": NODE_ID,
        "title": "DeepSeek native Harness authored-synthetic traceability micro-rehearsal",
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
                "The result is a bounded pre-provider configuration failure, not a DeepSeek inference result.",
                "Default worker transport and every product/runtime authority remain unchanged.",
            ],
        },
        "decisions": [{
            "id": "accept-native-harness-bounded-no-call-traceability-result",
            "source": ACCEPTANCE,
            "status": "accepted",
            "summary": "Accept exact fail-fast local traceability evidence while declining every model-performance or transport-selection claim.",
        }],
        "claim_scope": [
            "Pinned rc.7 produced an exact configuration invariant and nonzero exit before provider I/O.",
            "Zero provider, retry, fallback, auxiliary-model, tool or subagent requests started.",
            "No session trace existed; sanitized terminal metadata and trace absence are preserved.",
            "No inference reliability, coding quality or Harness superiority claim is supported.",
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
            "No DeepSeek inference reliability or coding-performance comparison has occurred.",
            "Native Harness default-worker selection remains closed.",
            "Ordinary check-in admission and atomic client cutover remain closed.",
            "Product data, providers, deployment, production and protected integration remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 317 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 318
    elif graph["graph_revision"] == 318 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected native Harness Continuity predecessor")
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Measure native Harness terminal and trace evidence without changing product authority",
        "outcome": "Pinned rc.7 failed fast before provider I/O with an exact local invariant; no inference result exists.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 299
        and compass["source_graph_revision"] == 317
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 300
        and compass["source_graph_revision"] == 318
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected native Harness Compass predecessor")
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Native Harness traceability measured only through a bounded no-call failure",
        "why_now": "Yuri requested a tiny official-Harness rehearsal after repeated untraceable Claude Code failures.",
        "outcome": "Resume with a provider-free read-only orientation for later ordinary check-in admission and atomic two-client cutover.",
        "unlocks": [
            "Require credential-absent exact-profile boot validation before any future occupied Harness comparison.",
            "Map the next product admission and atomic client-cutover gates without opening either.",
        ],
        "does_not_solve": [
            "No DeepSeek inference reliability, coding quality or transport superiority was measured.",
            "No ordinary practice, client, generic-status Arrived or waiting-area action is enabled.",
            "Product/patient data, providers, deployment, production and protected integration remain closed.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 318 / Compass 300. The pinned native DeepSeek "
        "Harness produced a clear pre-provider configuration failure but no inference "
        "result; product work resumes through a read-only ordinary-admission and "
        "atomic-client-cutover orientation."
    )
    limit = (
        "The native Harness no-call result supports local launcher traceability only; "
        "it opens no model-performance, transport-selection, product or runtime authority."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 318
    compass["map_revision"] = 300
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
