"""Idempotently accept Gate zero in the EMR4 Continuity graph and Compass."""

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
NODE_ID = "model-required-bureau-gate-zero"
PARENT = "model-required-bureau-standing-programme-authority"
SOURCE_HEAD = "3727ee83d03d310bbb2f0d52c2ce70d0430ab65d"
UPDATED_AT = "2026-08-04T08:45:00Z"

PLAN = "docs/emr4-rayleen-davida-controlled-recovery-development-plan.md"
DESIGN = "docs/emr4-model-required-bureau-gate-zero-shared-contract.md"
THREAT = "docs/security/emr4-model-required-bureau-gate-zero-threat-model-delta.md"
CONTRACT = (
    "orchestration/continuity/model-required-bureau-gate-zero/shared-contract.json"
)
EVIDENCE = (
    "orchestration/continuity/model-required-bureau-gate-zero/"
    "provider-free-acceptance-evidence.json"
)
CLOSEOUT = "docs/emr4-model-required-bureau-gate-zero-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "model-required-bureau-gate-zero-sol-acceptance.md"
)
PRE_VERIFIER = (
    "orchestration/agent_inbox/codex/"
    "model-required-bureau-gate-zero-pre-verifier-receipt.json"
)
WORKTREE_PREFLIGHT = (
    "orchestration/agent_inbox/codex/"
    "model-required-bureau-gate-zero-verifier-worktree-preflight.json"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/"
    "model-required-bureau-gate-zero-review-receipt.json"
)
TEST = "tests/test_model_required_bureau_gate_zero.py"


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Model-Required Bureau Gate Zero Shared Contract",
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
            "authorized_openings": [
                {
                    "boundary": "autonomous-action",
                    "source": PLAN,
                    "scope": (
                        "Provider-free A1/A2, B1/B2 and C1/C2 architecture/test "
                        "lanes within the frozen successor boundary"
                    ),
                }
            ],
            "notes": [
                "Yuri explicitly authorised Gate zero and standing planned-gate continuation.",
                "Fresh Gemini 3.6 Flash/high source review passed the exact unchanged clean candidate with zero findings.",
                "The review transport was non-zero; candidate product/runtime provider calls and side effects were zero.",
                "No live product, patient/clinical data, write, actuator, deployment, release, Pages or protected-ref boundary opened.",
                "The user-owned docs/branding directory remained excluded.",
            ],
        },
        "decisions": [
            {
                "id": "freeze-model-required-bureau-shared-contract",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Freeze the four-plane, domain, label/sink, outage, one-attempt "
                    "cell, API Spine, human-authority and evidence contract as the "
                    "mandatory parent for provider-free successor lanes."
                ),
            }
        ],
        "claim_scope": [
            "Six closed schemas and five authored-synthetic examples pass deterministic and independent review.",
            "Provider-free A1/A2, B1/B2 and C1/C2 architecture/test lanes are now active under standing authority.",
            "No operating isolation runtime, occupied Bureau model, live product path, command, actuator or release is established.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, DESIGN, THREAT],
            "findings": [CONTRACT, EVIDENCE],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [PRE_VERIFIER, WORKTREE_PREFLIGHT, REVIEW],
            "tests": [
                "scripts/model_required_bureau_gate_zero_acceptance.py",
                TEST,
                "tests/test_api_spine_artifacts.py",
            ],
        },
        "unresolved_gates": [
            "D1/D2 waits until C1 freezes the shared technical context and provenance vocabulary it requires.",
            "A3/B3 and every occupied model path require an exact accepted provider/data/region/identity/cost call boundary.",
            "Live product reads, patient-facing Rayleen, writes, actuators, migrations/update activation, deployment, production, release, Pages, protected refs and protected evidence remain closed.",
        ],
    }


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 209:
        if graph["nodes"][-1]["id"] != NODE_ID:
            raise SystemExit("Revision 209 has an unexpected terminal node.")
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
        return
    if graph["graph_revision"] != 208 or graph["nodes"][-1]["id"] != PARENT:
        raise SystemExit("Unexpected Gate-zero Continuity predecessor.")
    graph["nodes"].append(_node())
    graph["graph_revision"] = 209
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def _journey() -> dict[str, Any]:
    return {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Shared foundation for the model-required Bureau lanes",
        "outcome": (
            "Gate zero passes and activates the exact provider-free A1/A2, B1/B2 "
            "and C1/C2 architecture/test lanes."
        ),
        "evidence": [PLAN, DESIGN, THREAT, CONTRACT, EVIDENCE, CLOSEOUT, ACCEPTANCE, REVIEW, TEST],
    }


def _current_position() -> dict[str, Any]:
    return {
        "node_id": NODE_ID,
        "strategic_role": "Gate zero accepted; provider-free successor lanes active",
        "why_now": (
            "The common four-plane, label/sink, one-attempt cell and API Spine "
            "contract had to be frozen before Bureau-specific lanes diverged."
        ),
        "outcome": (
            "Deterministic and fresh independent review pass the exact architecture "
            "candidate with no product/runtime side effects."
        ),
        "unlocks": [
            "A1/A2 Rayleen provider-free read/projection and language foundations.",
            "B1/B2 Davida practice-administration grammar and authored-synthetic evaluator.",
            "C1/C2 controlled-recovery anatomy, observation, diagnosis and proofreader contracts.",
            "D1/D2 after C1 freezes the shared technical context/provenance vocabulary.",
        ],
        "does_not_solve": [
            "An occupied provider-model path or proof that a cell isolation runtime now exists.",
            "A live product read, patient-facing surface, command/write, actuator or update activation.",
            "Deployment, production, release, Pages, protected refs or protected evidence.",
        ],
        "evidence": [PLAN, DESIGN, THREAT, CONTRACT, EVIDENCE, CLOSEOUT, ACCEPTANCE, REVIEW, TEST],
    }


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if compass["map_revision"] == 190:
        if (
            compass["source_graph_revision"] != 209
            or compass["current_position"]["node_id"] != NODE_ID
            or compass["journey"][-1]["node_id"] != NODE_ID
        ):
            raise SystemExit("Revision 190 has unexpected Gate-zero state.")
        compass["journey"][-1] = _journey()
    elif (
        compass["map_revision"] == 189
        and compass["source_graph_revision"] == 208
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(_journey())
    else:
        raise SystemExit("Unexpected Gate-zero Compass predecessor.")

    compass["current_position"] = _current_position()
    for decision in compass["user_owned_decisions"]:
        if decision["id"] == "authorize-model-required-bureau-gate-zero":
            decision["required_before"] = (
                "Satisfied and consumed on 2026-08-04: Gate zero passes at "
                "Continuity 209 / Compass 190."
            )
            decision["evidence"] = list(
                dict.fromkeys(
                    decision["evidence"]
                    + [DESIGN, THREAT, EVIDENCE, CLOSEOUT, ACCEPTANCE, REVIEW]
                )
            )
            break

    limit = (
        "Gate-zero schemas specify required containment and authority behavior; "
        "they do not prove an operating cell, provider or product runtime."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 209 / Compass 190. Gate zero passes. Under the "
        "standing programme authority, A1/A2, B1/B2 and C1/C2 are active now; "
        "D1/D2 follows the C1 technical-context/provenance freeze. Occupied model, "
        "live product, write/actuator and deployment/release boundaries remain closed."
    )
    compass["map_revision"] = 190
    compass["source_graph_revision"] = 209
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)


def render_report() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")


def main() -> int:
    update_graph()
    update_compass()
    render_report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
