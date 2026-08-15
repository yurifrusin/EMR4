"""Advance Continuity and Compass for Ariadne continuity safeguards."""

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
NODE_ID = "ariadne-provider-free-continuity-journal-and-refinement-promotion-safeguards"
PARENT = "ariadne-postcompaction-active-operation-latch"
PRODUCT_POSITION = (
    "raisa-provider-free-unmounted-delete-confirm-physical-design-architecture"
)
SOURCE_HEAD = "79f5d6cf1cbe4ca9ad4893f257e92eccfd2ac2ce"
UPDATED_AT = "2026-08-15T09:47:44Z"
PLAN = "docs/ariadne-provider-free-continuity-journal-and-refinement-promotion-plan.md"
THREAT = "docs/security/ariadne-provider-free-continuity-journal-and-refinement-promotion-threat-model-delta.md"
SETTINGS = "orchestration/harness_settings/continuity_and_refinement_safeguards.yaml"
BASE = "orchestration/continuity/ariadne-continuity-and-refinement-safeguards/"
JOURNAL_SCHEMA = BASE + "operation-journal.schema.json"
GATE_SCHEMA = BASE + "gate-attempt.schema.json"
PROPOSAL_SCHEMA = BASE + "refinement-proposal.schema.json"
PROMOTION_SCHEMA = BASE + "refinement-promotion.schema.json"
EVIDENCE = BASE + "provider-free-authored-synthetic-evidence.json"
MODULE = "orchestration_harness/continuity_and_refinement.py"
CLI = "scripts/ariadne_continuity_and_refinement.py"
TEST = "tests/test_ariadne_continuity_and_refinement.py"
CLOSEOUT = (
    "docs/ariadne-provider-free-continuity-journal-and-refinement-promotion-closeout.md"
)
ACCEPTANCE = "orchestration/agent_inbox/codex/ariadne-prime-derived-harness-adaptations-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-15--ariadne-continuity-journal-and-refinement-safeguards.md"
REVIEW = "orchestration/agent_inbox/antigravity/ariadne-prime-derived-harness-adaptations-gemini37-review-receipt.json"
PREFLIGHT = "orchestration/agent_inbox/codex/ariadne-prime-derived-harness-adaptations-review-worktree-preflight.json"
POSTFLIGHT = "orchestration/agent_inbox/codex/ariadne-prime-derived-harness-adaptations-review-worktree-postflight.json"
AER = "docs/ariadne-agent-error-correction-register-revision-294.md"
UPDATER = "scripts/ariadne_continuity_and_refinement_safeguards_continuity_update.py"
CONTINUITY_TEST = (
    "tests/test_ariadne_continuity_and_refinement_safeguards_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        SETTINGS,
        JOURNAL_SCHEMA,
        GATE_SCHEMA,
        PROPOSAL_SCHEMA,
        PROMOTION_SCHEMA,
        EVIDENCE,
        MODULE,
        CLI,
        TEST,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        REVIEW,
        PREFLIGHT,
        POSTFLIGHT,
        AER,
        UPDATER,
        CONTINUITY_TEST,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Ariadne provider-free continuity journal and refinement-promotion safeguards",
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
            "authorized_openings": [],
            "notes": [
                "The accepted sidecar emits deterministic harness decisions and does not execute or replay commands.",
                "Refinement content remains inert and quarantined; promotion and rollback emit immutable decisions only.",
                "Prime Agent is neither installed nor executed, and no Raisa product authority is opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-continuity-journal-and-refinement-safeguards",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept append-only operation continuity, exact unchanged-gate decisions and explicitly promoted or rolled-back inert refinements as Ariadne-only safeguards.",
            }
        ],
        "claim_scope": [
            "Exact completed request/result bindings may replay; conflicts, live work and uncertain or failed work never silently execute.",
            "One exact composite gate fingerprint may reuse a pass, preserve a deterministic failure for diagnosis or preserve uncertainty for resolution.",
            "Refinement promotion binds exact source/evidence/base/validation and separated Sol/reviewer authority; rollback derives from immutable history.",
            "Two hundred focused tests, 167 hostile mutations, the canonical fast profile and one fresh Gemini 3.7 Flash/high veto pass.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [
                SETTINGS,
                JOURNAL_SCHEMA,
                GATE_SCHEMA,
                PROPOSAL_SCHEMA,
                PROMOTION_SCHEMA,
                EVIDENCE,
                AER,
            ],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [REVIEW, PREFLIGHT, POSTFLIGHT],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [MODULE, CLI, UPDATER],
        },
        "unresolved_gates": [
            "No crash-safe journal store, supervisor, distributed coordination or command-completion claim is proved.",
            "No refinement applies itself; source, policy, prompt and skill changes remain ordinary explicitly reviewed work.",
            "No Prime runtime or Raisa application/API/database/provider/data authority is opened.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 298:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 299
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 299 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected Ariadne continuity-safeguards predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if compass["map_revision"] == 280 and compass["source_graph_revision"] == 298:
        pass
    elif compass["map_revision"] == 281 and compass["source_graph_revision"] == 299:
        pass
    else:
        raise SystemExit("Unexpected Ariadne continuity-safeguards Compass predecessor")
    if compass["current_position"]["node_id"] != PRODUCT_POSITION:
        raise SystemExit("Product current position changed unexpectedly")

    current = compass["current_position"]
    current["why_now"] = (
        "The delete-confirm physical design passes, the bounded Prime assessment is complete, "
        "and Yuri has resumed the planned unmounted scaffold sequence."
    )
    current["unlocks"] = [
        "Freeze and implement the provider-free unmounted delete-confirm physical schema-and-transaction scaffold.",
        "Verify static representability against the accepted authority, receipt, audit, transaction and readback contract.",
        "Keep executable DDL, database behavior, mounted routes and product data behind later evidence gates.",
    ]
    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "ariadne-workflow-executive":
            for item in _evidence():
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Ariadne workflow horizon item missing")

    compass["orientation_statement"] = (
        "EMR4 is at Continuity 299 / Compass 281. Ariadne's provider-free continuity "
        "journal, unchanged-gate and quarantined-refinement safeguards pass without "
        "runtime authority. Product position remains the accepted delete-confirm "
        "physical design, and the unmounted scaffold is now the next active candidate."
    )
    limit = (
        "The Ariadne continuity sidecar proves deterministic decision logic only, not "
        "durable supervision, command completion, autonomous refinement or Raisa runtime capability."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 299
    compass["map_revision"] = 281
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
