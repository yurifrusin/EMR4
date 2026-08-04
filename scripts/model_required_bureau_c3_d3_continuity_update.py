"""Idempotently accept provider-free Bureau C3/D3 architecture."""

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
NODE_ID = "model-required-bureau-c3-d3"
PARENT = "model-required-bureau-provider-free-successor-lanes"
SOURCE_HEAD = "07ab07ed5e5e9d6cae5445de8538f428d6697d52"
UPDATED_AT = "2026-08-04T11:00:00Z"
PLAN = "docs/emr4-rayleen-davida-controlled-recovery-development-plan.md"
DESIGN = "docs/emr4-model-required-bureau-c3-d3-provider-free-architecture.md"
THREAT = "docs/security/emr4-model-required-bureau-c3-d3-threat-model-delta.md"
EVIDENCE = (
    "orchestration/continuity/model-required-bureau-c3-d3/"
    "provider-free-acceptance-evidence.json"
)
CLOSEOUT = "docs/emr4-model-required-bureau-c3-d3-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "model-required-bureau-c3-d3-sol-acceptance.md"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/"
    "model-required-bureau-c3-d3-review-receipt.json"
)
TEST = "tests/test_model_required_bureau_c3_d3.py"
DECISION_ID = "select-model-required-bureau-next-material-gate"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-Free Recovery and Update Authority Architecture",
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
                "C3 and D3 passed provider-free deterministic and independent review.",
                "Two bounded native workers supplied non-accepting advisory analysis.",
                "Candidate-runtime side effects were zero; source-only Gemini review transport was non-zero.",
                "No further dependency-satisfied provider-free implementation gate remains in the active sequence.",
            ],
        },
        "decisions": [
            {
                "id": "accept-provider-free-c3-d3",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept deterministic recovery risk/authority and staged "
                    "promotion/rollback architecture without an executor."
                ),
            }
        ],
        "claim_scope": [
            "Four closed schemas and three examples pass.",
            "Fresh Gemini source review passed 194 tests with no findings.",
            "No provider, live observer, reviewer runtime, effect or release is established.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, DESIGN, THREAT],
            "findings": [EVIDENCE],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [REVIEW],
            "tests": [
                "scripts/model_required_bureau_c3_d3_acceptance.py",
                TEST,
            ],
        },
        "unresolved_gates": [
            "A3/B3 occupied advisory rehearsals require an exact provider/model/region/identity/authored-synthetic-data/cost/call boundary.",
            "A4 live product read, A5/B4 writes and C4 actuator simulation require separate material authority.",
            "Actual downloads, licence acceptance, imports, migrations, activation, deployment, production and release remain closed.",
            "Pages, protected refs and protected evidence remain closed.",
        ],
    }


def _decision() -> dict[str, Any]:
    return {
        "id": DECISION_ID,
        "question": (
            "Which material Bureau lane should open next, with the recommended "
            "first option being a paired A3/B3 authored-synthetic occupied advisory rehearsal?"
        ),
        "required_before": (
            "Yuri must select and freeze the exact provider/model/region/identity/"
            "data/cost/call boundary, or choose a different material lane."
        ),
        "evidence": [PLAN, DESIGN, THREAT, EVIDENCE, CLOSEOUT, ACCEPTANCE, REVIEW],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 210 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 211
        graph["updated_at"] = UPDATED_AT
        _write(GRAPH, graph)
    elif graph["graph_revision"] == 211 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
    else:
        raise SystemExit("Unexpected C3/D3 Continuity predecessor")

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Provider-free recovery/update authority foundation",
        "outcome": (
            "C3/D3 pass; the next lanes require a selected material boundary."
        ),
        "evidence": [PLAN, DESIGN, THREAT, EVIDENCE, CLOSEOUT, ACCEPTANCE, REVIEW, TEST],
    }
    if (
        compass["map_revision"] == 191
        and compass["source_graph_revision"] == 210
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 192
        and compass["source_graph_revision"] == 211
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected C3/D3 Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": (
            "Provider-free recovery/update architecture accepted; material fork pending"
        ),
        "why_now": (
            "C1/C2 and D1/D2 supplied the exact evidence vocabulary and C3/D3 "
            "completed the remaining provider-free planned architecture."
        ),
        "outcome": (
            "Deterministic, Sol and independent review pass with zero candidate-runtime side effects."
        ),
        "unlocks": [
            "A decision-ready paired A3/B3 authored-synthetic provider rehearsal boundary.",
            "Separately decidable C4 actuator-simulator or live product read/write gates.",
        ],
        "does_not_solve": [
            "Occupied model intelligence or provider admission.",
            "Live product/technical reads, reviewer runtime, commands, writes or actuators.",
            "Update ingestion/activation, deployment, production, release or protected actions.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 211 / Compass 192. Provider-free C3/D3 pass and "
        "complete the dependency-satisfied provider-free Bureau sequence. The "
        "next lane is a genuine material choice; paired A3/B3 is recommended "
        "but no provider or effect boundary is open."
    )
    limit = (
        "C3/D3 prove provider-free risk, authority, staged-promotion and rollback "
        "contracts only; they do not prove a provider, observer, reviewer, command, "
        "actuator, updater, migration or activation runtime."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    decisions = [
        item
        for item in compass["user_owned_decisions"]
        if item["id"] != DECISION_ID
    ]
    decisions.append(_decision())
    compass["user_owned_decisions"] = decisions
    compass["map_revision"] = 192
    compass["source_graph_revision"] = 211
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
