"""Idempotently accept provider-free Bureau successor lanes."""

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
NODE_ID = "model-required-bureau-provider-free-successor-lanes"
PARENT = "model-required-bureau-gate-zero"
SOURCE_HEAD = "fc25d30b698944e9c8a792fb0a0a3467cf080c39"
UPDATED_AT = "2026-08-04T09:00:00Z"
PLAN = "docs/emr4-rayleen-davida-controlled-recovery-development-plan.md"
DESIGN = "docs/emr4-model-required-bureau-provider-free-successor-lanes.md"
THREAT = "docs/security/emr4-model-required-bureau-provider-free-successor-lanes-threat-model-delta.md"
EVIDENCE = "orchestration/continuity/model-required-bureau-provider-free-successor-lanes/provider-free-acceptance-evidence.json"
CLOSEOUT = "docs/emr4-model-required-bureau-provider-free-successor-lanes-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/model-required-bureau-provider-free-successor-lanes-sol-acceptance.md"
REVIEW = "orchestration/agent_inbox/antigravity/model-required-bureau-successor-lanes-review-receipt.json"
TEST = "tests/test_model_required_bureau_successor_lanes.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID, "title": "Provider-Free Bureau Successor Lanes", "kind": "foundation", "status": "accepted",
        "created_at": UPDATED_AT, "updated_at": UPDATED_AT,
        "coordinates": {"git_ref":"codex/ariadne-bernie-davida-parallel-seam","source_head":SOURCE_HEAD,"thread_id":None,"worktree_role":"task"},
        "relationships":[{"node_id":PARENT,"relation":"builds_on"}],
        "authority":{"authorized_openings":[{"boundary":"autonomous-action","source":PLAN,"scope":"Provider-free C3 recovery risk/authority policy and D3 staged-promotion/rollback architecture"}],"notes":["A1/A2, B1/B2, C1/C2 and D1/D2 passed provider-free deterministic and independent review.","C1 froze the technical observation/provenance vocabulary required by D1/D2.","Candidate-runtime side effects were zero; source-only Gemini review transport was non-zero.","No provider, live read, write, actuator, deployment, release, Pages or protected boundary opened."]},
        "decisions":[{"id":"accept-provider-free-successor-lanes","source":CLOSEOUT,"status":"accepted","summary":"Accept Rayleen and Davida language/context foundations, technical anatomy/diagnosis proof, and separated update provenance/delta contracts."}],
        "claim_scope":["Five closed schemas, four examples and 22 authored cases pass.","Fresh Gemini source review passed 261 tests with no findings.","No intelligent end-to-end model path, live read, effect or release is established."],
        "contract_evidence":[],
        "evidence":{"plans":[PLAN,DESIGN,THREAT],"findings":[EVIDENCE],"closeouts":[CLOSEOUT],"acceptances":[ACCEPTANCE],"receipts":[REVIEW],"tests":["scripts/model_required_bureau_successor_lanes_acceptance.py",TEST]},
        "unresolved_gates":["A3/B3 occupied model paths require exact provider/data/identity/region/cost authority.","A4 product read, A5/B4 writes, C4 actuator rehearsal and actual update/migration activation remain closed.","Deployment, production, release, Pages, protected refs and protected evidence remain closed."]
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 209 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node()); graph["graph_revision"] = 210; graph["updated_at"] = UPDATED_AT; _write(GRAPH, graph)
    elif graph["graph_revision"] == 210 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node(); _write(GRAPH, graph)
    else:
        raise SystemExit("Unexpected successor-lane Continuity predecessor")

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {"node_id":NODE_ID,"lineage_parent":PARENT,"strategic_role":"Provider-free Bureau-specific foundations","outcome":"A1/A2, B1/B2, C1/C2 and D1/D2 pass; C3/D3 are active.","evidence":[PLAN,DESIGN,THREAT,EVIDENCE,CLOSEOUT,ACCEPTANCE,REVIEW,TEST]}
    if compass["map_revision"] == 190 and compass["source_graph_revision"] == 209 and compass["current_position"]["node_id"] == PARENT:
        compass["journey"].append(journey)
    elif compass["map_revision"] == 191 and compass["source_graph_revision"] == 210 and compass["current_position"]["node_id"] == NODE_ID:
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected successor-lane Compass predecessor")
    compass["current_position"] = {"node_id":NODE_ID,"strategic_role":"Provider-free successor foundations accepted; C3/D3 active","why_now":"Gate zero allowed Bureau-specific contracts and C1 supplied D-lane provenance vocabulary.","outcome":"Deterministic and independent review pass with zero candidate-runtime side effects.","unlocks":["C3 deterministic recovery risk and authority policy.","D3 staged promotion and rollback architecture."],"does_not_solve":["Occupied models or intelligent end-to-end behavior.","Live product reads, commands, writes, actuators or update activation.","Deployment, production, release, Pages or protected actions."],"evidence":journey["evidence"]}
    compass["orientation_statement"] = "EMR4 is at Continuity 210 / Compass 191. Provider-free A1/A2, B1/B2, C1/C2 and D1/D2 pass; C3/D3 proceed under standing authority. Occupied models, live reads, writes/actuators and deployment/release remain closed."
    limit = "Provider-free language fixtures prove schemas, grounding and policy only; they do not prove model NLU or an intelligent end-to-end path."
    if limit not in compass["map_limits"]: compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 191; compass["source_graph_revision"] = 210; compass["updated_at"] = UPDATED_AT; _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed": raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
