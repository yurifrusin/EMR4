"""Advance Continuity and Compass for the post-cancellation orientation."""

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
NODE_ID = "raisa-provider-free-read-only-post-cancellation-programme-orientation"
PARENT = "raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition"
SOURCE_HEAD = "74da22d5372299eb2d2e38bb2266b76c89a97035"
UPDATED_AT = "2026-08-17T18:57:36Z"
PLAN = "docs/raisa-provider-free-read-only-post-cancellation-programme-orientation-plan.md"
FINDING = "docs/raisa-provider-free-read-only-post-cancellation-programme-orientation.md"
THREAT = "docs/security/raisa-provider-free-read-only-post-cancellation-programme-orientation-threat-model-delta.md"
TEST = "tests/test_raisa_provider_free_read_only_post_cancellation_programme_orientation.py"
PLAN_TEST = "tests/test_raisa_provider_free_read_only_post_cancellation_programme_orientation_plan.py"
CLOSEOUT = "docs/raisa-provider-free-read-only-post-cancellation-programme-orientation-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-provider-free-read-only-post-cancellation-programme-orientation-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-18--post-cancellation-programme-orientation.md"
PACKET = "orchestration/agent_inbox/codex/raisa-provider-free-read-only-post-cancellation-programme-orientation-gemini37-review-packet.md"
REVIEW = "orchestration/agent_inbox/antigravity/raisa-provider-free-read-only-post-cancellation-programme-orientation-gemini37-review-receipt.json"
PREFLIGHT = "orchestration/agent_inbox/codex/raisa-provider-free-read-only-post-cancellation-programme-orientation-gemini37-review-worktree-preflight.json"
RECEIPT = "orchestration/agent_inbox/codex/raisa-provider-free-read-only-post-cancellation-programme-orientation-pre-verifier-acceptance-receipt.json"
UPDATER = "scripts/raisa_provider_free_read_only_post_cancellation_programme_orientation_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_provider_free_read_only_post_cancellation_programme_orientation_continuity.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        FINDING,
        THREAT,
        TEST,
        PLAN_TEST,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        PACKET,
        REVIEW,
        PREFLIGHT,
        RECEIPT,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free read-only post-cancellation programme orientation",
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
                "Repository-static read-only orientation; no product behavior or runtime changed.",
                "Arrival/check-in is an authority and lifecycle inconsistency, not a proved corrupt write path.",
                "No product-facing arrival meaning is selected before the successor convergence review.",
            ],
        },
        "decisions": [
            {
                "id": "select-arrival-check-in-command-family-convergence-review",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Select one provider-free read-only review of generic Arrived status, waiting-area composition, A5.1 check-in and static action-contract meaning before any product edit.",
            }
        ],
        "claim_scope": [
            "Create, update, general status and delete/cancel are complete for the current first-party reference-client scope.",
            "Generic Arrived status, specialized default-off A5.1 check-in and static action-contract meaning require convergence.",
            "Six unchanged endpoint-coverage failures are baseline negative evidence, not candidate regressions.",
            "Eleven new checks, 107 API/static checks, the 200-test canonical fast profile and one fresh Gemini 3.7 Flash/high veto pass.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [FINDING, THREAT],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [RECEIPT, PREFLIGHT, REVIEW],
            "tests": [TEST, PLAN_TEST, CONTINUITY_TEST],
            "artifacts": [PACKET, UPDATER],
        },
        "unresolved_gates": [
            "The selected arrival/check-in convergence review remains to choose canonical A5.1, explicit generic status binding or strict specialized non-overlap.",
            "A5.1 remains default-off, authored-synthetic-practice-only and uncalled.",
            "Product source, route/static-contract repair, patient linking, external channels, product data, providers, deployment and release remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 313 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 314
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 314 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected post-cancellation orientation Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Reconcile arrival/check-in command-family meaning before another first-party control",
        "outcome": "A provider-free read-only arrival/check-in convergence review is selected without choosing a product meaning.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 295
        and compass["source_graph_revision"] == 313
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 296
        and compass["source_graph_revision"] == 314
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected post-cancellation orientation Compass predecessor")
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Arrival/check-in meaning must converge across status, waiting-area, A5.1 and static contracts",
        "why_now": "The first-party cancellation family is complete and check-in is the narrowest remaining dependency-satisfied command-family inconsistency.",
        "outcome": "A provider-free read-only arrival/check-in command-family convergence review is next.",
        "unlocks": [
            "Compare exact general status, waiting-area and A5.1 contracts.",
            "Freeze one canonical product-facing arrival meaning or a strict justified non-overlap before implementation.",
        ],
        "does_not_solve": [
            "No A5.1 feature flag, route, action grammar, UI control or database behavior changed.",
            "Patient linking, external channels, product data, providers, deployment and release remain closed.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 314 / Compass 296. First-party cancellation is complete; "
        "arrival/check-in is the next bounded command-family convergence question, and no product meaning is selected yet."
    )
    limit = (
        "The post-cancellation orientation selects only a read-only arrival/check-in convergence review; "
        "it does not admit A5.1, bind generic status, repair static route contracts or add a control."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 314
    compass["map_revision"] = 296
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
