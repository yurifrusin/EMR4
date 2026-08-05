"""Idempotently accept the A5.1/B4.1 command-runtime descendant."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ariadne_compass


GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = "model-required-bureau-a5-b4-command-runtime"
PARENT = "model-required-bureau-a3-b3-request-contract-recovery"
SOURCE_HEAD = "c93bbfa7e656a97a85c5b4532525caa362c6c781"
UPDATED_AT = "2026-08-05T10:00:00Z"
PLAN = "docs/emr4-model-required-bureau-a5-b4-command-runtime-plan.md"
PROGRAMME = "docs/emr4-rayleen-davida-controlled-recovery-development-plan.md"
THREAT = (
    "docs/security/emr4-model-required-bureau-a5-b4-command-runtime-"
    "threat-model-delta.md"
)
RECOVERY = "docs/model-required-bureau-a5-b4-a5-worker-recovery-lease.md"
CLOSEOUT = "docs/emr4-model-required-bureau-a5-b4-command-runtime-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/model-required-bureau-a5-b4-sol-acceptance.md"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/"
    "model-required-bureau-a5-b4-code-review-receipt.json"
)
REGISTER = (
    "orchestration/continuity/ariadne-agent-error-register/"
    "agent-error-register.json"
)
TESTS = [
    "tests/test_bernie_reception_one_combined_scope.py",
    "tests/test_reception_one_availability_reconciliation.py",
    "tests/test_model_required_bureau_a5_1_check_in_runtime.py",
    "tests/test_model_required_bureau_b4_1_default_location_runtime.py",
]
CONSUMED_DECISION_ID = "select-model-required-bureau-post-a3-b3-material-gate"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Rayleen Check-In and Davida Default-Location Commands",
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
                "A5.1 and B4.1 pass only for default-off authored-synthetic practices.",
                "Backend-owned human confirmation, idempotency and atomic audit/event-or-outbox remain mandatory.",
                "AER-0021 closed through the named recovery lease; AER-0022 preserves the corrected auth transport timeout.",
                "Standing programme authority opens provider-free C4 planning, not a live actuator.",
            ],
        },
        "decisions": [
            {
                "id": "accept-model-required-bureau-a5-b4-command-runtime",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept one Rayleen check-in and one Davida default-location "
                    "command runtime at their separate default-off synthetic boundaries."
                ),
            }
        ],
        "claim_scope": [
            "A5.1 Receptionist check-in truth, audit and patient-free event commit atomically.",
            "B4.1 human-confirmed default-location truth, audit and unpublished patient-free outbox commit atomically.",
            "Fresh Gemini code veto passed 261 tests on the exact unchanged clean candidate.",
            "No product-runtime provider, patient/product data, autonomous or external effect is established.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [
                    "tests/test_bernie_reception_one_combined_scope.py",
                    "tests/test_model_required_bureau_a5_1_check_in_runtime.py",
                ],
                "note": (
                    "The dedicated check-in command adds no private intent grammar "
                    "and preserves the inherited combined-scope Diary contract."
                ),
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [
                    "tests/test_reception_one_availability_reconciliation.py",
                    "tests/test_model_required_bureau_a5_1_check_in_runtime.py",
                    CLOSEOUT,
                ],
                "note": (
                    "The new event family is isolated by exact event type; the "
                    "existing reschedule feed and availability reconciliation remain green."
                ),
            },
        ],
        "evidence": {
            "plans": [PLAN, PROGRAMME, THREAT, RECOVERY],
            "findings": [REGISTER],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [REVIEW],
            "tests": TESTS,
        },
        "unresolved_gates": [
            "C4 remains provider-free authored-synthetic simulation with no real target or external actuator.",
            "C5 live development recovery requires a separately exact target and authority.",
            "Patient-facing Rayleen, product/clinical data and ordinary-practice enablement remain closed.",
            "External event delivery, further command families and update activation remain closed.",
            "Production, deployment, release, Pages, protected refs and protected evidence remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 212 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 213
        graph["updated_at"] = UPDATED_AT
        _write(GRAPH, graph)
    elif graph["graph_revision"] == 213 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
    else:
        raise SystemExit("Unexpected A5.1/B4.1 Continuity predecessor")

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Backend-owned Rayleen and Davida command foundations",
        "outcome": "A5.1/B4.1 pass; provider-free C4 planning is next.",
        "evidence": [PLAN, PROGRAMME, THREAT, RECOVERY, CLOSEOUT, ACCEPTANCE, REVIEW],
    }
    if (
        compass["map_revision"] == 193
        and compass["source_graph_revision"] == 212
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 194
        and compass["source_graph_revision"] == 213
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected A5.1/B4.1 Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Rayleen and Davida bounded command runtimes accepted",
        "why_now": (
            "A4 product read and the prior Davida command design supplied the "
            "dependency-complete boundaries for the first two human-confirmed commands."
        ),
        "outcome": (
            "Two separate default-off authored-synthetic command paths pass "
            "deterministic, migration and independent review."
        ),
        "unlocks": [
            "Immediate provider-free C4 allowlisted-actuator simulator planning.",
            "Later separately frozen A5/B4 command descendants.",
        ],
        "does_not_solve": [
            "Ordinary-practice, patient-facing or clinical product use.",
            "Live recovery, real-database or external actuator execution.",
            "Deployment, production, release, Pages or protected actions.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 213 / Compass 194. A5.1 Rayleen check-in and "
        "B4.1 Davida default-location command runtimes pass at default-off "
        "authored-synthetic boundaries. Standing authority opens the provider-"
        "free C4 allowlisted-actuator simulator next."
    )
    limit = (
        "A5.1/B4.1 prove bounded authored-synthetic command semantics only; "
        "they do not prove ordinary-practice, patient-facing, live-recovery, "
        "production, deployment or release suitability."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["user_owned_decisions"] = [
        item
        for item in compass["user_owned_decisions"]
        if item["id"] != CONSUMED_DECISION_ID
    ]
    compass["map_revision"] = 194
    compass["source_graph_revision"] = 213
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
