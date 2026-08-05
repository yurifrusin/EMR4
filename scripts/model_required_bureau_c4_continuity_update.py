"""Idempotently accept the provider-free Bureau C4 simulator descendant."""

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
NODE_ID = "model-required-bureau-c4-allowlisted-actuator-simulator"
PARENT = "model-required-bureau-a5-b4-command-runtime"
SOURCE_HEAD = "955b6a566f7097f58929dcb2fa9c4ed0aaad8b29"
UPDATED_AT = "2026-08-05T12:00:00Z"
PLAN = "docs/emr4-model-required-bureau-c4-allowlisted-actuator-simulator-plan.md"
PROGRAMME = "docs/emr4-rayleen-davida-controlled-recovery-development-plan.md"
THREAT = (
    "docs/security/emr4-model-required-bureau-c4-allowlisted-actuator-"
    "simulator-threat-model-delta.md"
)
OPENAPI = "docs/api-spine/openapi/technical-control-simulator-commands.yaml"
EVIDENCE = (
    "orchestration/continuity/model-required-bureau-c4-allowlisted-actuator-"
    "simulator/provider-free-acceptance-evidence.json"
)
REGISTER = (
    "orchestration/continuity/ariadne-agent-error-register/agent-error-register.json"
)
CLOSEOUT = (
    "docs/emr4-model-required-bureau-c4-allowlisted-actuator-simulator-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/model-required-bureau-c4-sol-acceptance.md"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/"
    "model-required-bureau-c4-code-review-receipt.json"
)
TESTS = [
    "scripts/model_required_bureau_c4_acceptance.py",
    "tests/test_bernie_reception_one_combined_scope.py",
    "tests/test_reception_one_availability_reconciliation.py",
    "tests/test_model_required_bureau_c4_simulator.py",
    "tests/test_model_required_bureau_c4_plan.py",
    "tests/test_model_required_bureau_c4_continuity.py",
]


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-Free Allowlisted-Actuator Simulator",
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
                "C4 passes only as local provider-free authored-synthetic simulation.",
                "One shared store owns evidence, idempotency, supersession and attempt transaction semantics.",
                "AER-0025 and AER-0026 close only through Sol's named recovery lease and fresh veto.",
                "Standing authority opens exact C5 planning, not a live recovery action.",
            ],
        },
        "decisions": [
            {
                "id": "accept-model-required-bureau-c4-simulator",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept one fixed provider-free authored-synthetic forward "
                    "transition and exact rollback behind typed one-use evidence."
                ),
            }
        ],
        "claim_scope": [
            "Exact scalar admission, current authority, one-use evidence and cross-runtime transaction regressions pass.",
            "Fresh readback and exact rollback distinguish verified success from every terminal denial.",
            "Fresh Gemini source veto passed 389 tests on the exact unchanged clean candidate.",
            "No provider, live target, product data, real database, route or external actuator is established.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [
                    "tests/test_bernie_reception_one_combined_scope.py",
                    "tests/test_model_required_bureau_c4_simulator.py",
                ],
                "note": (
                    "C4 has no Diary intent surface and leaves the inherited "
                    "combined-scope contract unchanged."
                ),
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [
                    "tests/test_reception_one_availability_reconciliation.py",
                    "tests/test_model_required_bureau_c4_simulator.py",
                    CLOSEOUT,
                ],
                "note": (
                    "C4 has no product event consumer and leaves the inherited "
                    "reschedule reconciliation contract unchanged."
                ),
            },
        ],
        "evidence": {
            "plans": [PLAN, PROGRAMME, THREAT, OPENAPI],
            "findings": [EVIDENCE, REGISTER],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [REVIEW],
            "tests": TESTS,
        },
        "unresolved_gates": [
            "C5 requires a separately frozen exact disposable non-PHI target, provider/model boundary, human authority, rollback, audit and cleanup before any live development action.",
            "Real databases, ordinary services, cloud/IAM operations, product routes and external actuators remain closed.",
            "Patient, clinical, product-derived or protected data and patient-facing Rayleen remain closed.",
            "Update download/import/migration/activation and external event delivery remain closed.",
            "Production, deployment, release, Pages, protected refs and protected evidence remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 213 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 214
        graph["updated_at"] = UPDATED_AT
        _write(GRAPH, graph)
    elif graph["graph_revision"] == 214 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
    else:
        raise SystemExit("Unexpected C4 Continuity predecessor")

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "First one-use deterministic technical action simulator",
        "outcome": "C4 passes; exact disposable C5 planning is next.",
        "evidence": [
            PLAN,
            PROGRAMME,
            THREAT,
            OPENAPI,
            EVIDENCE,
            REGISTER,
            CLOSEOUT,
            ACCEPTANCE,
            REVIEW,
        ],
    }
    if (
        compass["map_revision"] == 195
        and compass["source_graph_revision"] == 213
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 196
        and compass["source_graph_revision"] == 214
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected C4 Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Provider-free allowlisted-actuator simulator accepted",
        "why_now": (
            "C3 authority policy and the accepted A5/B4 backend command foundations "
            "made one exact zero-external-effect technical simulator dependency-complete."
        ),
        "outcome": (
            "One fixed authored-synthetic recovery transition now passes deterministic, "
            "Sol recovery and independent source veto."
        ),
        "unlocks": [
            "Freeze C5's narrowest disposable non-PHI live-development-recovery plan.",
            "Use C4's typed authority and readback lessons in the later Context Fabric technical thread.",
        ],
        "does_not_solve": [
            "A live provider diagnosis or any live development recovery action.",
            "Real database/service targets, product data, commands, cloud/IAM or production actuators.",
            "Deployment, production, release, Pages or protected actions.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 214 / Compass 196. C4's provider-free "
        "authored-synthetic allowlisted-actuator simulator passes after Sol recovery "
        "and a fresh exact-head veto. Standing authority opens exact C5 planning next, "
        "but no live target or recovery action is yet authorised by C4."
    )
    limit = (
        "C4 proves one in-memory authored-synthetic technical transition only; it does "
        "not prove a live model diagnosis, real target, database, external actuator, "
        "development recovery, deployment, production or release."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 196
    compass["source_graph_revision"] = 214
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
