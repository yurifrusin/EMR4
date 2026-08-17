"""Advance Continuity and Compass for the arrival/check-in convergence review."""

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
    "raisa-provider-free-read-only-arrival-check-in-command-family-convergence-review"
)
PARENT = "raisa-provider-free-read-only-post-cancellation-programme-orientation"
SOURCE_HEAD = "3bed3eb32dd1b8723bf5aa6218963b757ebc0e3d"
UPDATED_AT = "2026-08-17T21:20:15Z"
PLAN = (
    "docs/raisa-provider-free-read-only-arrival-check-in-command-family-"
    "convergence-review-plan.md"
)
FINDING = (
    "docs/raisa-provider-free-read-only-arrival-check-in-command-family-"
    "convergence-review.md"
)
THREAT = (
    "docs/security/raisa-provider-free-read-only-arrival-check-in-command-family-"
    "convergence-review-threat-model-delta.md"
)
TEST = (
    "tests/test_raisa_provider_free_read_only_arrival_check_in_command_family_"
    "convergence_review.py"
)
PLAN_TEST = (
    "tests/test_raisa_provider_free_read_only_arrival_check_in_command_family_"
    "convergence_review_plan.py"
)
CLOSEOUT = (
    "docs/raisa-provider-free-read-only-arrival-check-in-command-family-"
    "convergence-review-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-read-only-arrival-"
    "check-in-command-family-convergence-review-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/2026-08-18--arrival-check-in-command-family-"
    "convergence-review.md"
)
PACKET = (
    "orchestration/agent_inbox/codex/raisa-provider-free-read-only-arrival-"
    "check-in-command-family-convergence-review-gemini37-review-packet.md"
)
MANIFEST = (
    "orchestration/agent_inbox/codex/raisa-provider-free-read-only-arrival-"
    "check-in-command-family-convergence-review-gemini37-command-manifest.json"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-provider-free-read-only-arrival-"
    "check-in-command-family-convergence-review-gemini37-review-receipt.json"
)
PREFLIGHT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-read-only-arrival-"
    "check-in-command-family-convergence-review-gemini37-review-worktree-"
    "preflight.json"
)
RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-read-only-arrival-"
    "check-in-command-family-convergence-review-pre-verifier-acceptance-receipt.json"
)
POSTCOMPACTION = (
    "orchestration/agent_inbox/codex/raisa-provider-free-read-only-arrival-"
    "check-in-command-family-convergence-review-closeout-postcompaction-"
    "receipt.json"
)
UPDATER = (
    "scripts/raisa_provider_free_read_only_arrival_check_in_command_family_"
    "convergence_review_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_read_only_arrival_check_in_command_family_"
    "convergence_review_continuity.py"
)


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
        MANIFEST,
        REVIEW,
        PREFLIGHT,
        RECEIPT,
        POSTCOMPACTION,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free read-only arrival/check-in command-family convergence review",
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
                "Repository-static semantic review; no product behavior or runtime changed.",
                "Dedicated check-in is selected as the future canonical ordinary arrival command.",
                "A5.1 remains default-off, uncalled and unmodified.",
            ],
        },
        "decisions": [
            {
                "id": "select-dedicated-check-in-as-future-canonical-arrival-command",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Treat check-in as the authoritative domain command and Arrived as its resulting state; preserve general status for other transitions and require a later atomic two-client cutover.",
            }
        ],
        "claim_scope": [
            "Dedicated check-in has stronger authority, evidence, waiting-area, event and receipt meaning than bare Arrived assignment.",
            "The reusable deterministic kernel is separated from the Rayleen-named default-off A5.1 gate.",
            "Waiting-area movement or removal remains a separate command family.",
            "Eleven new checks, 118 focused checks, the 200-test canonical fast profile and one fresh Gemini 3.7 Flash/high veto pass.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [FINDING, THREAT],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [RECEIPT, POSTCOMPACTION, PREFLIGHT, REVIEW],
            "tests": [TEST, PLAN_TEST, CONTINUITY_TEST],
            "artifacts": [PACKET, MANIFEST, UPDATER],
        },
        "unresolved_gates": [
            "The unmounted canonical check-in product-adapter extraction rehearsal remains next.",
            "Mounted route, general-status Arrived admission, grammar action and both first-party clients remain unchanged.",
            "Product data, providers, deployment, production and release remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 314 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 315
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 315 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected arrival/check-in convergence Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Select one authoritative ordinary appointment-arrival command meaning",
        "outcome": "Dedicated check-in is the future canonical product-facing arrival command; Arrived is its resulting state.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 296
        and compass["source_graph_revision"] == 314
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 297
        and compass["source_graph_revision"] == 315
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected arrival/check-in convergence Compass predecessor")
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Dedicated check-in owns ordinary arrival meaning while general status retains other transitions",
        "why_now": "The repository-static convergence review proves that bare Arrived assignment does not preserve the full check-in contract.",
        "outcome": "Extract the deterministic check-in kernel into one provider-free unmounted product adapter next.",
        "unlocks": [
            "Separate reusable check-in behavior from A5.1-only admission scaffolding.",
            "Prepare a later atomic route, grammar and two-client convergence without opening it now.",
        ],
        "does_not_solve": [
            "No A5.1 feature flag, route, general-status policy, action grammar or client changed.",
            "Patient linking, external channels, product data, providers, deployment and release remain closed.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 315 / Compass 297. Dedicated check-in is the future canonical "
        "ordinary arrival command; the next bounded step is its provider-free unmounted adapter extraction."
    )
    limit = (
        "The convergence review selects future command meaning only; A5.1 remains default-off and "
        "no route, status admission, grammar, client, database or runtime authority is opened."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 315
    compass["map_revision"] = 297
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
