"""Idempotently accept the bounded Bureau C5 occupied live rehearsal."""

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
NODE_ID = "model-required-bureau-c5-occupied-live-rehearsal"
PARENT = "model-required-bureau-c5-provider-free-implementation-readiness"
SOURCE_HEAD = "dff672049ab5ce47058d7340525e63589fefc5c1"
UPDATED_AT = "2026-08-06T00:25:00Z"
PLAN = "docs/emr4-model-required-bureau-c5-disposable-live-development-recovery-plan.md"
BOUNDARY = "docs/emr4-model-required-bureau-c5-live-preexecution-orchestration-boundary.md"
THREAT = (
    "docs/security/emr4-model-required-bureau-c5-disposable-live-development-"
    "recovery-threat-model-delta.md"
)
PREEXEC_THREAT = (
    "docs/security/emr4-model-required-bureau-c5-live-preexecution-"
    "orchestration-threat-model-delta.md"
)
EVIDENCE = (
    "orchestration/continuity/model-required-bureau-c5-disposable-live-"
    "development-recovery/occupied-rehearsal-interpreter-binding-evidence.json"
)
LEDGER = (
    "orchestration/continuity/model-required-bureau-c5-disposable-live-"
    "development-recovery/occupied-rehearsal-interpreter-binding-cost-ledger.json"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/model-required-bureau-c5-"
    "interpreter-binding-review-receipt.json"
)
PREEXECUTION = (
    "orchestration/agent_inbox/codex/model-required-bureau-c5-interpreter-"
    "binding-live-preexecution-receipt.json"
)
CLOSEOUT = "docs/emr4-model-required-bureau-c5-occupied-live-rehearsal-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/model-required-bureau-c5-occupied-live-"
    "rehearsal-sol-acceptance.md"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "C5 Occupied Authored-Synthetic Live Rehearsal",
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
                    "boundary": "api-change",
                    "source": CLOSEOUT,
                    "scope": (
                        "Define the first provider-free, authored-synthetic, "
                        "unmounted Practice Context Fabric and Bureau Memory Bank "
                        "read contract; no product route, persistence or runtime."
                    ),
                }
            ],
            "notes": [
                "C5 acceptance is limited to one disposable authored-synthetic development loop.",
                "One Gemini 2.5 Flash call was deterministically admitted; no correction call followed.",
                "Final cleanup proves no owned process, listener, task directory, open ledger or reusable capability.",
                "Practice Context Fabric remains provider-free and unmounted in its first descendant.",
            ],
        },
        "decisions": [
            {
                "id": "accept-model-required-bureau-c5-occupied-live-rehearsal",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept the exact authored-synthetic C5 diagnosis, one-use "
                    "recovery, generation-2 readback and complete cleanup result."
                ),
            }
        ],
        "claim_scope": [
            "One exact Sydney Vertex gemini-2.5-flash call was admitted under the bounded diagnosis-only envelope.",
            "One disposable loopback target recovered from generation 1 to generation 2 with fresh readback.",
            "The closed ledger consumed one provider call and at most USD 0.25 of the USD 0.50 reservation ceiling.",
            "No patient, product, database, ordinary-service, production, deployment or release capability is established.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [
                    "tests/test_bernie_reception_one_combined_scope.py",
                    EVIDENCE,
                ],
                "note": (
                    "C5 used only patient-free technical frames and did not alter "
                    "the Diary combined-scope contract."
                ),
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [
                    "tests/test_reception_one_availability_reconciliation.py",
                    EVIDENCE,
                    CLOSEOUT,
                ],
                "note": (
                    "C5 introduced no product event consumer and left committed "
                    "reschedule reconciliation unchanged."
                ),
            },
        ],
        "evidence": {
            "plans": [PLAN, BOUNDARY, THREAT, PREEXEC_THREAT],
            "findings": [EVIDENCE, LEDGER],
            "closeouts": [CLOSEOUT],
            "acceptances": [ACCEPTANCE],
            "receipts": [REVIEW, PREEXECUTION],
            "tests": [
                "tests/test_bernie_reception_one_combined_scope.py",
                "tests/test_reception_one_availability_reconciliation.py",
                "tests/test_model_required_bureau_c5_live.py",
                "tests/test_model_required_bureau_c5_rehearsal.py",
                "tests/test_model_required_bureau_c5_contract.py",
                "tests/test_model_required_bureau_c5_occupied_live_continuity.py",
            ],
        },
        "unresolved_gates": [
            "Practice Context Fabric and Bureau Memory Bank may begin only as provider-free authored-synthetic unmounted read contracts.",
            "Product routes, persistence, temporal retention, provider calls and external retrieval remain closed.",
            "Patient, clinical, product-derived, protected and production data; real databases and ordinary services remain closed.",
            "Commands, writes, deployment, production, release, Pages, protected refs and protected evidence remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 215 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 216
        graph["updated_at"] = UPDATED_AT
        _write(GRAPH, graph)
    elif graph["graph_revision"] == 216 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
        _write(GRAPH, graph)
    else:
        raise SystemExit("Unexpected C5 occupied-live Continuity predecessor")

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Bounded occupied model-required recovery proof",
        "outcome": (
            "C5 passes one source-bound authored-synthetic diagnosis, one-use "
            "recovery, generation-2 readback and complete cleanup loop."
        ),
        "evidence": [PLAN, BOUNDARY, THREAT, PREEXEC_THREAT, EVIDENCE, LEDGER, REVIEW, CLOSEOUT, ACCEPTANCE],
    }
    if (
        compass["map_revision"] == 197
        and compass["source_graph_revision"] == 215
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 198
        and compass["source_graph_revision"] == 216
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected C5 occupied-live Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "C5 live proof accepted; Context Fabric contract is next",
        "why_now": (
            "Provider-free source gates, Windows endpoint ownership, active-interpreter "
            "binding, fresh independent veto and the exact occupied run all pass."
        ),
        "outcome": (
            "One bounded authored-synthetic model-required recovery loop passed "
            "with fresh readback, closed accounting and complete cleanup."
        ),
        "unlocks": [
            "Begin the provider-free Practice Context Fabric and Bureau Memory Bank contract descendant.",
            "Keep product routes, persistence, real data, provider retrieval and commands separately gated.",
        ],
        "does_not_solve": [
            "General autonomous repair, production operations or arbitrary model correctness.",
            "Patient, clinical, product, database, ordinary-service or provider-memory access.",
            "Context Fabric runtime, persistence, commands, deployment, release, Pages or protected actions.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 216 / Compass 198. The bounded C5 occupied "
        "authored-synthetic live rehearsal passes with one admitted Sydney Vertex "
        "call, generation-2 readback and complete cleanup. The provider-free "
        "Practice Context Fabric and Bureau Memory Bank contract is now next."
    )
    limit = (
        "C5 occupied acceptance proves one disposable authored-synthetic development "
        "loop only; it does not establish production repair, product/runtime/data "
        "authority, provider-model memory or Context Fabric implementation."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["map_revision"] = 198
    compass["source_graph_revision"] = 216
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
