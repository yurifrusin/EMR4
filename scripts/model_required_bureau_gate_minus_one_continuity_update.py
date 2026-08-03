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
UPDATED_AT = "2026-08-03T22:15:35Z"
BRANCH = "codex/ariadne-bernie-davida-parallel-seam"
SOURCE_HEAD = "2b62f040bcc1c300dca6fb730e0f986d22f3be85"
PARENT = "raisa-provider-free-default-off-office-consumer-adapter"
NODE_ID = "model-required-bureau-gate-minus-one"
PLAN = "docs/emr4-rayleen-davida-controlled-recovery-development-plan.md"
ARCHITECTURE = "docs/emr4-model-required-deterministic-authority-bureau-architecture.md"
PARENT_THREAT = (
    "docs/security/emr4-model-required-bureaus-controlled-recovery-threat-model-delta.md"
)
THREAT = (
    "docs/security/emr4-model-required-bureaus-gate-minus-one-threat-model-delta.md"
)
HARDENING = (
    "docs/security/hardening/model-required-bureau-gate-minus-one/hardening.json"
)
HARDENING_MD = (
    "docs/security/hardening/model-required-bureau-gate-minus-one/hardening.md"
)
EVIDENCE = (
    "orchestration/continuity/model-required-bureau-gate-minus-one/"
    "provider-free-acceptance-evidence.json"
)
CLOSEOUT = "docs/emr4-model-required-bureau-gate-minus-one-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "model-required-bureau-gate-minus-one-sol-acceptance.md"
)
PREPLAN = (
    "orchestration/agent_inbox/codex/"
    "model-required-bureau-gate-minus-one-preplan-receipt.json"
)
PREVERIFIER = (
    "orchestration/agent_inbox/codex/"
    "model-required-bureau-gate-minus-one-pre-verifier-receipt-2.json"
)
POSTCOMPACTION = (
    "orchestration/agent_inbox/codex/"
    "model-required-bureau-gate-minus-one-postcompaction-pre-verifier-receipt-2.json"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/"
    "model-required-bureau-gate-minus-one-review-2-receipt.json"
)
RUNNER = "scripts/model_required_bureau_gate_minus_one_acceptance.py"
TEST = "tests/test_model_required_bureau_gate_minus_one.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Model-Required Bureau Gate -1 Adversarial Architecture Review",
        "kind": "review",
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
                    "boundary": "security-review",
                    "source": PLAN,
                    "scope": (
                        "Architecture-only adversarial containment review before "
                        "the shared model-required Bureau contract"
                    ),
                }
            ],
            "notes": [
                "Yuri explicitly authorised Gate -1.",
                "The external Gemini review received bounded source-only development context and no product data or runtime authority.",
                "No implementation, product read/write, provider product runtime, actuator, deployment, production, release or protected-ref authority opened.",
                "The user-owned docs/branding directory remained excluded.",
            ],
        },
        "decisions": [
            {
                "id": "select-bureau-gate-minus-one-controls",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Require a deterministic labeled capability envelope and one-shot "
                    "brokered cognitive cell as Gate-zero inputs."
                ),
            }
        ],
        "claim_scope": [
            "The research-backed architecture review and deterministic artifacts passed a fresh Gemini 3.6 Flash/high veto.",
            "The model remains mandatory for intelligent dialogue but is an untrusted candidate generator with no authority.",
            "The selected controls are requirements only; no runtime implementation or prompt-injection immunity is established.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [ARCHITECTURE, PLAN, PARENT_THREAT, THREAT],
            "findings": [HARDENING, HARDENING_MD, EVIDENCE],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLAN, PREVERIFIER, POSTCOMPACTION, REVIEW],
            "tests": [RUNNER, TEST],
        },
        "unresolved_gates": [
            "Gate zero requires fresh Yuri authority before architecture/schema/test work begins.",
            "Every model/provider/data/cost/runtime decision and every product lane remains closed.",
            "Real identity, patient/clinical/product data, tools, actuators, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 207:
        if graph["nodes"][-1]["id"] != NODE_ID:
            raise SystemExit("Revision 207 has an unexpected terminal node.")
        boundaries = graph["governance"]["closed_boundaries"]
        if "security-review" not in boundaries:
            boundaries.append("security-review")
            boundaries.sort()
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
        return
    if graph["graph_revision"] != 206 or graph["nodes"][-1]["id"] != PARENT:
        raise SystemExit("Unexpected Gate -1 Continuity predecessor.")
    graph["nodes"].append(_node())
    graph["governance"]["closed_boundaries"].append("security-review")
    graph["governance"]["closed_boundaries"].sort()
    graph["graph_revision"] = 207
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] == 188
        and compass["source_graph_revision"] == 207
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        return
    if (
        compass["map_revision"] != 187
        or compass["source_graph_revision"] != 206
        or compass["current_position"]["node_id"] != PARENT
    ):
        raise SystemExit("Unexpected Gate -1 Compass predecessor.")
    compass["journey"].append(
        {
            "node_id": NODE_ID,
            "lineage_parent": PARENT,
            "strategic_role": (
                "Adversarial containment gate before the shared model-required Bureau contract"
            ),
            "outcome": (
                "Gate -1 selects deterministic information-flow labels and a one-shot "
                "brokered cognitive cell while leaving every runtime and product lane closed."
            ),
            "evidence": [PLAN, THREAT, HARDENING, EVIDENCE, CLOSEOUT, REVIEW],
        }
    )
    evidence = [PLAN, THREAT, HARDENING, EVIDENCE, CLOSEOUT, ACCEPTANCE, REVIEW]
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Accepted adversarial architecture gate before Gate zero",
        "why_now": (
            "Mandatory provider-model participation creates a high-consequence prompt-"
            "injection and wrapper-compromise boundary that must be frozen before lane work."
        ),
        "outcome": (
            "The shared Bureau direction now requires deterministic labeled capability "
            "flows and a fresh brokered no-ambient-bridge cell for every attempt."
        ),
        "unlocks": [
            "With fresh Yuri authority, begin Gate zero architecture, closed schemas and deterministic tests only."
        ],
        "does_not_solve": [
            "Implementation or runtime enforcement of the selected controls.",
            "Prompt-injection immunity, sandbox invulnerability or provider trustworthiness.",
            "Real identity/data, product reads/writes, patient/clinical use, deployment, production or release.",
        ],
        "evidence": evidence,
    }
    decision_id = "authorize-model-required-bureau-gate-zero"
    decisions = {item["id"]: item for item in compass["user_owned_decisions"]}
    decision = {
        "id": decision_id,
        "question": (
            "Should EMR4 freeze the shared model-required Bureau contract and closed "
            "Gate-zero schemas and deterministic tests?"
        ),
        "required_before": (
            "Fresh Yuri authority is required because Gate -1 is consumed and the earlier "
            "pause on further development remains in force."
        ),
        "evidence": evidence,
    }
    if decision_id in decisions:
        compass["user_owned_decisions"] = [
            decision if item["id"] == decision_id else item
            for item in compass["user_owned_decisions"]
        ]
    else:
        compass["user_owned_decisions"].append(decision)
    limit = (
        "Gate -1 is accepted architecture evidence only; its selected controls are not "
        "implemented and establish no model or product runtime, prompt-injection immunity, "
        "data access, actuator, deployment, production or release posture."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["orientation_statement"] = (
        "EMR4's model-required Bureau programme has passed Gate -1 at Continuity 207 / "
        "Compass 188. The next safe candidate is Gate zero only: freeze the shared "
        "four-plane contract, label/capability and source/sink schemas, one-attempt cell "
        "and deterministic tests after fresh Yuri authority. All product/runtime lanes "
        "remain closed."
    )
    compass["map_revision"] = 188
    compass["source_graph_revision"] = 207
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
