"""Idempotently accept Bureau C5 provider-free implementation readiness."""

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
NODE_ID = "model-required-bureau-c5-provider-free-implementation-readiness"
PARENT = "model-required-bureau-c4-allowlisted-actuator-simulator"
SOURCE_HEAD = "d82de54ba59071d231adbf45a3aae1bbc0642ff4"
UPDATED_AT = "2026-08-05T14:30:00Z"
PLAN = "docs/emr4-model-required-bureau-c5-disposable-live-development-recovery-plan.md"
THREAT = (
    "docs/security/emr4-model-required-bureau-c5-disposable-live-development-"
    "recovery-threat-model-delta.md"
)
OPENAPI = (
    "docs/api-spine/openapi/technical-control-live-development-recovery-commands.yaml"
)
EVIDENCE = (
    "orchestration/continuity/model-required-bureau-c5-disposable-live-development-"
    "recovery/provider-free-acceptance-evidence.json"
)
REGISTER = "orchestration/continuity/ariadne-agent-error-register/agent-error-register.json"
REVISION = "docs/ariadne-agent-error-correction-register-revision-23.md"
CLOSEOUT = (
    "docs/emr4-model-required-bureau-c5-provider-free-implementation-readiness-"
    "closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/model-required-bureau-c5-provider-free-"
    "implementation-readiness-sol-acceptance.md"
)
FIRST_REVIEW = (
    "orchestration/agent_inbox/antigravity/model-required-bureau-c5-sol-recovery-"
    "review-receipt.json"
)
FINAL_REVIEW = (
    "orchestration/agent_inbox/antigravity/model-required-bureau-c5-sol-recovery-"
    "review-2-receipt.json"
)
TESTS = [
    "scripts/model_required_bureau_c5_acceptance.py",
    "tests/test_bernie_reception_one_combined_scope.py",
    "tests/test_reception_one_availability_reconciliation.py",
    "tests/test_model_required_bureau_c5_contract.py",
    "tests/test_model_required_bureau_c5_rehearsal.py",
    "tests/test_model_required_bureau_c5_plan.py",
    "tests/test_model_required_bureau_c5_implementation_readiness_continuity.py",
]


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "C5 Provider-Free Implementation Readiness",
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
            "authorized_openings": [
                {
                    "boundary": "autonomous-action",
                    "source": CLOSEOUT,
                    "scope": (
                        "Prepare the distinct exact-head C5 pre-execution receipt; "
                        "this opening itself performs no live action."
                    ),
                }
            ],
            "notes": [
                "Only provider-free implementation readiness is accepted; no live C5 result exists.",
                "AER-0027 closes only through Sol recovery, two preserved veto outcomes and the corrected exact-head pass.",
                "The distinct pre-execution receipt must bind the frozen serial target/provider/cost/cleanup envelope before live action.",
                "Practice Context Fabric remains a separate unimplemented successor direction.",
            ],
        },
        "decisions": [
            {
                "id": "accept-model-required-bureau-c5-implementation-readiness",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept the recovered C5 provider-free source and controls only "
                    "as readiness for a distinct gated live rehearsal."
                ),
            }
        ],
        "claim_scope": [
            "All fourteen worker-audit findings and both first-veto evidence findings are closed by direct regressions.",
            "Fresh corrected Gemini review passed 269 tests on the exact clean unchanged candidate.",
            "No target process, socket, port, task directory or candidate-runtime provider call occurred.",
            "No product, database, ordinary-service, Context Fabric, deployment, production or release capability is established.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [
                    "tests/test_bernie_reception_one_combined_scope.py",
                    "tests/test_model_required_bureau_c5_contract.py",
                ],
                "note": (
                    "C5 uses patient-free technical frames and leaves the inherited "
                    "Diary combined-scope contract unchanged."
                ),
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [
                    "tests/test_reception_one_availability_reconciliation.py",
                    "tests/test_model_required_bureau_c5_rehearsal.py",
                    CLOSEOUT,
                ],
                "note": (
                    "C5 has no product event consumer and leaves the inherited "
                    "reschedule reconciliation contract unchanged."
                ),
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT, OPENAPI],
            "findings": [EVIDENCE, REGISTER, REVISION],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [FIRST_REVIEW, FINAL_REVIEW],
            "tests": TESTS,
        },
        "unresolved_gates": [
            "The distinct exact-head C5 pre-execution receipt must pass before any task-owned target, socket, port, temporary-directory or Sydney Vertex action.",
            "Only the frozen gemini-2.5-flash Sydney envelope, authored-synthetic technical frame, at most two calls and USD 0.50 may be considered in that serial rehearsal.",
            "A fresh live result must prove baseline, exact fault, admitted diagnosis, one-use authority, generation-2 readback, rollback semantics and complete cleanup.",
            "Patient, clinical, product-derived, protected and production data; real databases; ordinary services; product routes and Context Fabric runtime remain closed.",
            "Deployment, production, release, Pages, protected refs and protected evidence remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 214 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 215
        graph["updated_at"] = UPDATED_AT
        _write(GRAPH, graph)
    elif graph["graph_revision"] == 215 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
    else:
        raise SystemExit("Unexpected C5 implementation-readiness Continuity predecessor")

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Recovered C5 provider-free implementation readiness",
        "outcome": "C5 source gates pass; the distinct serial pre-execution gate is next.",
        "evidence": [
            PLAN,
            THREAT,
            OPENAPI,
            EVIDENCE,
            REGISTER,
            REVISION,
            CLOSEOUT,
            ACCEPTANCE,
            FIRST_REVIEW,
            FINAL_REVIEW,
        ],
    }
    if (
        compass["map_revision"] == 196
        and compass["source_graph_revision"] == 214
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 197
        and compass["source_graph_revision"] == 215
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected C5 implementation-readiness Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "C5 provider-free implementation ready for its exact live gate",
        "why_now": (
            "C4 and the frozen C5 plan made the provider-free controller/authority "
            "source dependency-complete; Sol recovery and fresh veto now pass."
        ),
        "outcome": (
            "The C5 source and safety controls are accepted, but no live recovery "
            "or provider result exists until the distinct serial rehearsal passes."
        ),
        "unlocks": [
            "Create the exact-head C5 pre-execution receipt and run only the frozen serial rehearsal.",
            "After C5 live acceptance, begin the provider-free Practice Context Fabric contract descendant.",
        ],
        "does_not_solve": [
            "A live model diagnosis, target lifecycle, recovery readback or cleanup result.",
            "Real database/service targets, product data, commands, cloud/IAM or production actuators.",
            "Context Fabric implementation, deployment, production, release, Pages or protected actions.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 215 / Compass 197. C5 provider-free implementation "
        "readiness passes after Sol recovery, one preserved revision veto and one "
        "fresh corrected exact-head pass. The distinct serial C5 pre-execution gate "
        "is next; no live C5 result exists yet."
    )
    limit = (
        "C5 implementation readiness proves provider-free source controls only; it "
        "does not prove a live target, provider diagnosis, recovery, cleanup, product "
        "runtime, Context Fabric, deployment, production or release."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 197
    compass["source_graph_revision"] = 215
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
