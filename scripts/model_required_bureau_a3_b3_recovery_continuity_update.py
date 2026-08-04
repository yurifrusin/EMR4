"""Idempotently accept the occupied A3/B3 request-contract recovery."""

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
NODE_ID = "model-required-bureau-a3-b3-request-contract-recovery"
PARENT = "model-required-bureau-c3-d3"
SOURCE_HEAD = "a70d06fd047733bac9a72921d0fd2f81e1b946db"
UPDATED_AT = "2026-08-04T14:00:00Z"
PLAN = "docs/emr4-model-required-bureau-a3-b3-request-contract-recovery-plan.md"
PROGRAMME = "docs/emr4-rayleen-davida-controlled-recovery-development-plan.md"
THREAT = (
    "docs/security/"
    "emr4-model-required-bureau-a3-b3-request-contract-recovery-threat-model-delta.md"
)
EVIDENCE = (
    "orchestration/continuity/model-required-bureau-a3-b3-request-contract-recovery/"
    "occupied-rehearsal-evidence.json"
)
ACCEPTANCE_EVIDENCE = (
    "orchestration/continuity/model-required-bureau-a3-b3-request-contract-recovery/"
    "occupied-acceptance-evidence.json"
)
COST = (
    "orchestration/continuity/model-required-bureau-a3-b3-request-contract-recovery/"
    "occupied-rehearsal-cost-ledger.json"
)
CLOSEOUT = "docs/emr4-model-required-bureau-a3-b3-request-contract-recovery-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "model-required-bureau-a3-b3-request-contract-recovery-sol-acceptance.md"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/"
    "model-required-bureau-a3-b3-request-contract-recovery-review-2-receipt.json"
)
TEST = "tests/test_model_required_bureau_a3_b3_request_contract_recovery.py"
CONSUMED_DECISION_ID = "select-model-required-bureau-next-material-gate"
NEXT_DECISION_ID = "select-model-required-bureau-post-a3-b3-material-gate"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Occupied Rayleen and Davida Advisory Recovery",
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
                "The exact Gemini 2.5 Flash Sydney authored-synthetic call boundary is consumed.",
                "Rayleen admitted before Davida; each lane used exactly one single-use call.",
                "Positive bounded reasoning and deterministic proofreading both remained active.",
                "No product read, command, write, actuator or release authority opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-a3-b3-request-contract-recovery",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept one proofreader-admitted authored-synthetic occupied "
                    "advisory result for Rayleen and Davida in strict sequence."
                ),
            }
        ],
        "claim_scope": [
            "Two occupied candidate-runtime calls produced two advisory-only releases.",
            "Provider-reported thinking tokens were non-zero in both lanes.",
            "The configured and observed Sydney request path does not prove sovereign processing.",
            "Zero patient, clinical, product, database, command, write, actuator, deployment or protected-ref effect occurred.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, PROGRAMME, THREAT],
            "findings": [EVIDENCE, COST, ACCEPTANCE_EVIDENCE],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [REVIEW],
            "tests": [
                "scripts/model_required_bureau_a3_b3_recovery_acceptance.py",
                TEST,
            ],
        },
        "unresolved_gates": [
            "A4 live product read and UI projection require a separate exact material boundary.",
            "A5 and B4 commands and writes require separate exact material boundaries.",
            "C4 actuator rehearsal and any live recovery action require separate exact authority.",
            "External update ingestion, licence acceptance, import, migration and activation remain closed.",
            "Patient, clinical, product-derived and production data remain closed.",
            "Deployment, production, release, Pages, protected refs and protected evidence remain closed.",
        ],
    }


def _decision() -> dict[str, Any]:
    return {
        "id": NEXT_DECISION_ID,
        "question": (
            "Which material Bureau boundary, if any, should be frozen next: "
            "A4 product read/UI projection, A5/B4 write commands, C4 actuator "
            "rehearsal, or a separately scoped update/import lane?"
        ),
        "required_before": (
            "Yuri must select and freeze the exact data, product/runtime, write/"
            "actuator, cost, side-effect and acceptance boundary before execution."
        ),
        "evidence": [
            PLAN,
            PROGRAMME,
            THREAT,
            EVIDENCE,
            COST,
            ACCEPTANCE_EVIDENCE,
            CLOSEOUT,
            ACCEPTANCE,
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 211 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 212
        graph["updated_at"] = UPDATED_AT
        _write(GRAPH, graph)
    elif graph["graph_revision"] == 212 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
    else:
        raise SystemExit("Unexpected A3/B3 recovery Continuity predecessor")

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Occupied provider-model advisory proof for Rayleen and Davida",
        "outcome": "A3/B3 pass; no dependency-satisfied non-material successor remains.",
        "evidence": [
            PLAN,
            PROGRAMME,
            THREAT,
            EVIDENCE,
            COST,
            ACCEPTANCE_EVIDENCE,
            CLOSEOUT,
            ACCEPTANCE,
            REVIEW,
            TEST,
        ],
    }
    if (
        compass["map_revision"] == 192
        and compass["source_graph_revision"] == 211
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 193
        and compass["source_graph_revision"] == 212
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected A3/B3 recovery Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Occupied Rayleen/Davida advisory rehearsal accepted",
        "why_now": (
            "The previous Rayleen response-shape rejection required a distinct "
            "positive-bounded-reasoning request-contract recovery."
        ),
        "outcome": (
            "Rayleen and Davida each admitted one authored-synthetic advisory "
            "with deterministic proofreading and zero product authority."
        ),
        "unlocks": [
            "A decision-ready A4 product-read/UI-projection boundary.",
            "Separately decidable A5/B4 write, C4 actuator or update/import boundaries.",
        ],
        "does_not_solve": [
            "Product or real-data model runtime.",
            "Commands, confirmations, writes, actuators or clinical decisions.",
            "Deployment, production, release, Pages or protected actions.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 212 / Compass 193. The positive-bounded-reasoning "
        "A3/B3 recovery passes with one proofreader-admitted occupied authored-"
        "synthetic advisory per lane. The current planned block is complete; the "
        "next implementation lane requires a separately frozen material boundary."
    )
    limit = (
        "A3/B3 prove bounded authored-synthetic occupied advisory formation only; "
        "they do not prove product data, commands, writes, actuators, clinical "
        "decisions, production suitability or sovereign processing."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    decisions = [
        item
        for item in compass["user_owned_decisions"]
        if item["id"] not in {CONSUMED_DECISION_ID, NEXT_DECISION_ID}
    ]
    decisions.append(_decision())
    compass["user_owned_decisions"] = decisions
    compass["map_revision"] = 193
    compass["source_graph_revision"] = 212
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
