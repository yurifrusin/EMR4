from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from scripts import ariadne_compass
except ModuleNotFoundError:
    import ariadne_compass  # type: ignore[no-redef]


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
UPDATED_AT = "2026-08-04T07:05:15Z"
BRANCH = "codex/ariadne-bernie-davida-parallel-seam"
SOURCE_HEAD = "ba6a96d55002ee7713c3a12867e57b41ce972150"
PARENT = "model-required-bureau-gate-minus-one"
NODE_ID = "model-required-bureau-standing-programme-authority"
AGENTS = "AGENTS.md"
PLAN = "docs/emr4-rayleen-davida-controlled-recovery-development-plan.md"
POLICY_DOC = "docs/ariadne-autonomous-continuation.md"
POLICY = "orchestration/harness_settings/autonomous_continuation.yaml"
OPERATING_MODEL = "orchestration/harness_settings/operating_model.yaml"
TEST = "tests/test_ariadne_autonomous_continuation.py"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "model-required-bureau-standing-programme-authority-sol-acceptance.md"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Standing Programme Continuation Authority",
        "kind": "maintenance",
        "status": "accepted",
        "created_at": UPDATED_AT,
        "updated_at": UPDATED_AT,
        "coordinates": {
            "git_ref": BRANCH,
            "source_head": SOURCE_HEAD,
            "thread_id": None,
            "worktree_role": "task",
        },
        "relationships": [{"node_id": PARENT, "relation": "builds_on"}],
        "authority": {
            "authorized_openings": [
                {
                    "boundary": "autonomous-action",
                    "source": AGENTS,
                    "scope": (
                        "Automatic movement through dependency-satisfied gates whose "
                        "complete material boundaries are frozen in the live Current "
                        "Baton or an accepted descendant plan"
                    ),
                }
            ],
            "notes": [
                "Yuri established the standing authority on 2026-08-04.",
                "Gate zero is authorised and is the active next gate.",
                "Generic future candidates and unresolved explicit closures are not self-authorising.",
                "No provider call, product or patient data, runtime wiring, write, deployment, release, Pages or protected-ref action occurred.",
                "The user-owned docs/branding directory and prior untracked receipts remained excluded.",
            ],
        },
        "decisions": [
            {
                "id": "activate-standing-programme-continuation",
                "source": AGENTS,
                "status": "accepted",
                "summary": (
                    "Proceed automatically across exact dependency-satisfied gates and "
                    "pause only for a genuine user-attention condition."
                ),
            }
        ],
        "claim_scope": [
            "Routine fresh-authority pauses between fully specified planned gates are superseded.",
            "The policy covers planning, bounded dispatch, implementation, testing, review, recovery, acceptance and task-branch publication inside the frozen plan.",
            "The policy cannot infer missing provider, data, clinical, write, deployment, release, protected or human-only authority.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [AGENTS, PLAN, POLICY_DOC],
            "findings": [POLICY, OPERATING_MODEL],
            "closeouts": [],
            "acceptances": [ACCEPTANCE],
            "receipts": [],
            "tests": [TEST],
        },
        "unresolved_gates": [
            "Gate zero must pass deterministic checks, a fresh Gemini 3.6 Flash/high veto and Sol Extra High acceptance before lanes A-D begin.",
            "A generic future candidate remains closed until an active accepted plan freezes its complete material boundary.",
            "User attention remains required for an unplanned fork, missing user-only input, conflicting evidence that changes acceptance meaning, exhausted bounded recovery or explicit user pause.",
        ],
    }


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 208:
        if graph["nodes"][-1]["id"] != NODE_ID:
            raise SystemExit("Revision 208 has an unexpected terminal node.")
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
        return
    if graph["graph_revision"] != 207 or graph["nodes"][-1]["id"] != PARENT:
        raise SystemExit("Unexpected standing-authority Continuity predecessor.")
    graph["nodes"].append(_node())
    graph["graph_revision"] = 208
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def _journey() -> dict[str, Any]:
    return {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Durable authority for uninterrupted planned gate progression",
        "outcome": (
            "Gate zero is active and every later exact dependency-satisfied gate may "
            "follow without a repeat permission pause."
        ),
        "evidence": [
            AGENTS,
            PLAN,
            POLICY_DOC,
            POLICY,
            OPERATING_MODEL,
            ACCEPTANCE,
            TEST,
        ],
    }


def _current_position() -> dict[str, Any]:
    return {
        "node_id": NODE_ID,
        "strategic_role": "Standing programme authority with Gate zero active",
        "why_now": (
            "The earlier sprint-local continuation rule and newer gate-specific fresh-"
            "authority clauses conflicted and caused unnecessary pauses."
        ),
        "outcome": (
            "The live handover, active plan and machine policy now require automatic "
            "movement across fully specified dependency-satisfied gates."
        ),
        "unlocks": [
            "Begin Gate zero now, then continue into each qualifying successor after its acceptance gates pass."
        ],
        "does_not_solve": [
            "A generic future candidate or unresolved explicit closure.",
            "A missing provider, model, data, clinical, cost, licence, write, deployment, release or protected-boundary choice.",
            "Any user-only credential, identity, participant, console or external-coordination action.",
        ],
        "evidence": [
            AGENTS,
            PLAN,
            POLICY_DOC,
            POLICY,
            OPERATING_MODEL,
            ACCEPTANCE,
            TEST,
        ],
    }


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if compass["map_revision"] == 189:
        if (
            compass["source_graph_revision"] != 208
            or compass["current_position"]["node_id"] != NODE_ID
            or compass["journey"][-1]["node_id"] != NODE_ID
        ):
            raise SystemExit("Revision 189 has unexpected standing-authority state.")
        compass["journey"][-1] = _journey()
    elif (
        compass["map_revision"] == 188
        and compass["source_graph_revision"] == 207
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(_journey())
    else:
        raise SystemExit("Unexpected standing-authority Compass predecessor.")

    compass["current_position"] = _current_position()
    decisions = {item["id"]: item for item in compass["user_owned_decisions"]}
    gate_zero = decisions["authorize-model-required-bureau-gate-zero"]
    gate_zero["required_before"] = (
        "Satisfied on 2026-08-04: Yuri authorised Gate zero and standing "
        "continuation through later fully specified dependency-satisfied gates."
    )
    gate_zero["evidence"] = list(
        dict.fromkeys(gate_zero["evidence"] + [AGENTS, PLAN, POLICY_DOC, POLICY])
    )
    standing_decision = {
        "id": "authorize-standing-programme-continuation",
        "question": (
            "May EMR4 move without repeat permission pauses through every fully "
            "specified dependency-satisfied gate?"
        ),
        "required_before": (
            "Satisfied on 2026-08-04 by Yuri's standing programme authority."
        ),
        "evidence": [
            AGENTS,
            PLAN,
            POLICY_DOC,
            POLICY,
            OPERATING_MODEL,
            ACCEPTANCE,
            TEST,
        ],
    }
    if standing_decision["id"] in decisions:
        compass["user_owned_decisions"] = [
            standing_decision if item["id"] == standing_decision["id"] else item
            for item in compass["user_owned_decisions"]
        ]
    else:
        compass["user_owned_decisions"].append(standing_decision)

    limit = (
        "Standing programme authority removes repeat permission pauses only for "
        "fully specified dependency-satisfied gates; it does not infer or erase an "
        "unresolved material boundary."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["orientation_statement"] = (
        "EMR4's standing programme authority is active at Continuity 208 / Compass "
        "189. Gate zero is the active next gate. After each gate passes its exact "
        "acceptance, Ariadne continues automatically into the next fully specified "
        "dependency-satisfied gate; only a genuine user-attention condition pauses "
        "the sequence."
    )
    compass["map_revision"] = 189
    compass["source_graph_revision"] = 208
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
