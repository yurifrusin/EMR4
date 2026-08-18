"""Advance Continuity and Compass for canonical check-in adapter extraction."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ariadne_compass


GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = (
    "raisa-provider-free-unmounted-canonical-check-in-product-adapter-"
    "extraction-rehearsal"
)
PARENT = (
    "raisa-provider-free-read-only-arrival-check-in-command-family-"
    "convergence-review"
)
SOURCE_HEAD = "8de886c5148b3259428c8c517674f10ea92d937e"
UPDATED_AT = "2026-08-18T00:22:21Z"
PLAN = (
    "docs/raisa-provider-free-unmounted-canonical-check-in-product-adapter-"
    "extraction-rehearsal-plan.md"
)
THREAT = (
    "docs/security/raisa-provider-free-unmounted-canonical-check-in-product-"
    "adapter-extraction-rehearsal-threat-model-delta.md"
)
ADAPTER = "app/services/appointment_check_in_product_adapter.py"
TEST = (
    "tests/test_raisa_provider_free_unmounted_canonical_check_in_product_"
    "adapter.py"
)
PLAN_TEST = (
    "tests/test_raisa_provider_free_unmounted_canonical_check_in_product_"
    "adapter_extraction_rehearsal_plan.py"
)
CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-canonical-check-in-product-adapter-"
    "extraction-rehearsal-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-canonical-check-in-product-adapter-"
    "sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/2026-08-18--canonical-check-in-product-"
    "adapter-extraction-rehearsal.md"
)
PACKET = (
    "orchestration/agent_inbox/codex/raisa-canonical-check-in-product-adapter-"
    "gemini37-review-packet.md"
)
MANIFEST = (
    "orchestration/agent_inbox/codex/raisa-canonical-check-in-product-adapter-"
    "gemini37-command-manifest.json"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-canonical-check-in-product-"
    "adapter-gemini37-final-review-receipt.json"
)
PREFLIGHT = (
    "orchestration/agent_inbox/codex/raisa-canonical-check-in-product-adapter-"
    "gemini37-worktree-preflight.json"
)
RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-canonical-check-in-product-adapter-"
    "pre-verifier-corrected-manifest-receipt.json"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_canonical_check_in_product_adapter_"
    "extraction_rehearsal_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_canonical_check_in_product_"
    "adapter_extraction_rehearsal_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        ADAPTER,
        TEST,
        PLAN_TEST,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        PACKET,
        MANIFEST,
        REVIEW,
        PREFLIGHT,
        RECEIPT,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free unmounted canonical check-in product-adapter extraction rehearsal",
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
                "Provider-free authored-synthetic in-process adapter over injected fakes only.",
                "Existing A5.1 route and default-off practice gate remain unchanged.",
                "General-status Arrived, action grammar and both first-party clients remain unchanged.",
            ],
        },
        "decisions": [
            {
                "id": "accept-reusable-unmounted-canonical-check-in-adapter",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept one reusable deterministic check-in adapter while keeping route admission and client convergence closed.",
            }
        ],
        "claim_scope": [
            "Current Receptionist authority, locked truth, one-use evidence and idempotent replay are composed in one unmounted adapter seam.",
            "Waiting-area behavior permits only compatible assignment or preservation; move/removal remain separate.",
            "Audit, committed event, private receipt, commit and readback remain ordered and patient-free.",
            "85 focused tests including 68 hostile mutations, 101 plan/convergence checks, wider 152/590 packets, the 200-test canonical profile and final Gemini 3.7 veto pass.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [
                    "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-plan.md",
                    "orchestration/continuity/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition/ordinary-diary-cancellation-canonical-consumer-convergence-composition-evidence.json",
                    "tests/test_raisa_ordinary_diary_cancellation_canonical_consumer_convergence_composition.py",
                    "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-closeout.md",
                ],
                "note": "The accepted first-party intent contract remains inherited and is not changed by this unmounted check-in adapter.",
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [
                    "orchestration/continuity/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition/ordinary-diary-cancellation-canonical-consumer-convergence-composition-evidence.json",
                    "review/test_ordinary_diary_cancellation_convergence.py",
                    "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-closeout.md",
                ],
                "note": "The accepted fresh-read reconciliation contract remains inherited; the unmounted adapter creates no competing client projection.",
            },
        ],
        "evidence": {
            "plans": [
                PLAN,
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-plan.md",
            ],
            "findings": [
                THREAT,
                "orchestration/continuity/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition/ordinary-diary-cancellation-canonical-consumer-convergence-composition-evidence.json",
            ],
            "closeouts": [
                CLOSEOUT,
                MAILBOX,
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-closeout.md",
            ],
            "acceptances": [ACCEPTANCE],
            "receipts": [RECEIPT, PREFLIGHT, REVIEW],
            "tests": [
                TEST,
                PLAN_TEST,
                CONTINUITY_TEST,
                "tests/test_raisa_ordinary_diary_cancellation_canonical_consumer_convergence_composition.py",
                "review/test_ordinary_diary_cancellation_convergence.py",
            ],
            "artifacts": [
                ADAPTER,
                PACKET,
                MANIFEST,
                UPDATER,
            ],
        },
        "unresolved_gates": [
            "The existing default-off A5.1 route does not yet delegate to the adapter.",
            "Practice enablement, general-status Arrived closure, action grammar and both client cutovers remain closed.",
            "PostgreSQL/RLS/concurrency, product data, providers, deployment and production remain unproved.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 315 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 316
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 316 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected check-in adapter Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Extract reusable check-in authority from default-off A5.1 route-local composition",
        "outcome": "One unmounted deterministic check-in adapter is accepted without route or practice admission.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 297
        and compass["source_graph_revision"] == 315
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 298
        and compass["source_graph_revision"] == 316
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected check-in adapter Compass predecessor")
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Reusable deterministic check-in adapter exists while admission stays route-owned and default-off",
        "why_now": "The predecessor selected check-in as canonical ordinary-arrival meaning and this tranche extracts that exact meaning without opening runtime authority.",
        "outcome": "In a fresh task, converge the unchanged default-off A5.1 route onto the accepted adapter without enabling it.",
        "unlocks": [
            "Remove duplicated route-local check-in composition behind the existing closed gate.",
            "Prepare later atomic general-status, grammar and two-client convergence as distinct gates.",
        ],
        "does_not_solve": [
            "No practice, route call, general-status Arrived, action grammar or client changed.",
            "Real PostgreSQL, product/patient data, providers, deployment and production remain closed.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 316 / Compass 298. The canonical check-in adapter is "
        "accepted unmounted; the next product step is default-off route-adapter convergence "
        "after fresh-task rehydration."
    )
    limit = (
        "The adapter extraction is in-process authored-synthetic evidence only; it opens no route, "
        "practice, database, provider, client, deployment or production authority."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 316
    compass["map_revision"] = 298
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
