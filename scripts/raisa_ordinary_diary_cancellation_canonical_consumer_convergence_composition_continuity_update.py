"""Advance Continuity and Compass for ordinary Diary cancellation convergence."""

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
NODE_ID = "raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition"
PARENT = "raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review"
SOURCE_HEAD = "bfac65298e1d4aaca85d1c9dcb20329ef298c485"
UPDATED_AT = "2026-08-17T15:54:51Z"

PLAN = "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-plan.md"
THREAT = (
    "docs/security/"
    "raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-"
    "threat-model-delta.md"
)
EVIDENCE_ROOT = (
    "orchestration/continuity/"
    "raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition/"
)
EVIDENCE_SCHEMA = EVIDENCE_ROOT + (
    "ordinary-diary-cancellation-canonical-consumer-convergence-composition-"
    "evidence.schema.json"
)
EVIDENCE = EVIDENCE_ROOT + (
    "ordinary-diary-cancellation-canonical-consumer-convergence-composition-"
    "evidence.json"
)
SOURCE_TEST = (
    "tests/test_raisa_ordinary_diary_cancellation_canonical_consumer_"
    "convergence_composition.py"
)
PLAN_TEST = (
    "tests/test_raisa_ordinary_diary_cancellation_canonical_consumer_"
    "convergence_composition_plan.py"
)
BROWSER_TEST = "review/test_ordinary_diary_cancellation_convergence.py"
RECEPTION_TEST = "review/test_reception_one_cancellation_action.py"
DIARY_TEST = "review/test_diary_smoke.py"
EVIDENCE_TEST = (
    "tests/test_raisa_ordinary_diary_cancellation_canonical_consumer_"
    "convergence_composition_evidence.py"
)
FIRST_PACKET = (
    "orchestration/agent_inbox/codex/"
    "raisa-ordinary-diary-cancellation-canonical-consumer-convergence-"
    "composition-gemini37-review-packet.md"
)
FIRST_MANIFEST = (
    "orchestration/agent_inbox/codex/"
    "raisa-ordinary-diary-cancellation-canonical-consumer-convergence-"
    "composition-gemini37-command-manifest.json"
)
FIRST_REVIEW = (
    "orchestration/agent_inbox/antigravity/"
    "raisa-ordinary-diary-cancellation-canonical-consumer-convergence-"
    "composition-gemini37-review-receipt.json"
)
REPAIR_PACKET = (
    "orchestration/agent_inbox/codex/"
    "raisa-ordinary-diary-cancellation-canonical-consumer-convergence-"
    "composition-gemini37-repair-review-packet.md"
)
REPAIR_MANIFEST = (
    "orchestration/agent_inbox/codex/"
    "raisa-ordinary-diary-cancellation-canonical-consumer-convergence-"
    "composition-gemini37-repair-review-command-manifest.json"
)
REPAIR_PREFLIGHT = (
    "orchestration/agent_inbox/codex/"
    "raisa-ordinary-diary-cancellation-canonical-consumer-convergence-"
    "composition-repair-review-worktree-preflight.json"
)
PREVERIFIER_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-ordinary-diary-cancellation-canonical-consumer-convergence-"
    "composition-repair-pre-verifier-receipt.json"
)
POSTCOMPACTION_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-ordinary-diary-cancellation-canonical-consumer-convergence-"
    "composition-postcompaction-receipt.json"
)
REPAIR_REVIEW = (
    "orchestration/agent_inbox/antigravity/"
    "raisa-ordinary-diary-cancellation-canonical-consumer-convergence-"
    "composition-gemini37-repair-review-receipt.json"
)
REGISTER = "docs/ariadne-agent-error-correction-register-revision-346.md"
CLOSEOUT = (
    "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-"
    "composition-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-ordinary-diary-cancellation-canonical-consumer-convergence-"
    "composition-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-18--ordinary-diary-cancellation-canonical-consumer-convergence.md"
)
UPDATER = (
    "scripts/raisa_ordinary_diary_cancellation_canonical_consumer_convergence_"
    "composition_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_ordinary_diary_cancellation_canonical_consumer_"
    "convergence_composition_continuity.py"
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _all_evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        EVIDENCE_SCHEMA,
        EVIDENCE,
        SOURCE_TEST,
        PLAN_TEST,
        BROWSER_TEST,
        RECEPTION_TEST,
        DIARY_TEST,
        EVIDENCE_TEST,
        FIRST_PACKET,
        FIRST_MANIFEST,
        FIRST_REVIEW,
        REPAIR_PACKET,
        REPAIR_MANIFEST,
        REPAIR_PREFLIGHT,
        PREVERIFIER_RECEIPT,
        POSTCOMPACTION_RECEIPT,
        REPAIR_REVIEW,
        REGISTER,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        UPDATER,
        CONTINUITY_TEST,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Ordinary Diary cancellation canonical consumer convergence composition",
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
        "relationships": [{"node_id": PARENT, "relation": "implements"}],
        "authority": {
            "authorized_openings": [],
            "notes": [
                "Provider-free first-party client composition and route-intercepted browser evidence only.",
                "The ordinary Diary and Reception One now consume one canonical delete proposal, confirmation, minimal receipt and fresh-truth contract.",
                "Backend/API/schema/database, product data, providers, deployment and protected refs remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-ordinary-diary-canonical-cancellation-convergence",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept the delete-only client convergence, strict minimal receipt and fail-closed fresh-truth reconciliation.",
            }
        ],
        "claim_scope": [
            "The ordinary Diary calls only the dedicated delete proposal and canonical delete-confirm command.",
            "One shared validator binds appointment, reason, optional note, issues, confirmation, autonomy tier and endpoint before confirm.",
            "Only the recursively closed minimal public delete receipt is admitted; no appointment read model is required.",
            "Every terminal or uncertain outcome is reconciled through fresh authorised Diary truth, and failed reconciliation disables cancellation as refresh-required.",
            "One fresh Gemini 3.7 Flash/high repaired-candidate veto passes all nine exact commands and leaves the worktree clean.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [PLAN, EVIDENCE, SOURCE_TEST, CLOSEOUT],
                "note": "Both first-party clients preserve the selected cancellation intent and cannot silently substitute a different command family.",
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [EVIDENCE, BROWSER_TEST, CLOSEOUT],
                "note": "Current Diary truth is reloaded after every terminal or uncertain cancellation outcome and defeats contradictory receipt claims.",
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [EVIDENCE_SCHEMA, EVIDENCE, REGISTER],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                FIRST_REVIEW,
                REPAIR_PREFLIGHT,
                PREVERIFIER_RECEIPT,
                REPAIR_REVIEW,
                POSTCOMPACTION_RECEIPT,
            ],
            "tests": [
                SOURCE_TEST,
                PLAN_TEST,
                BROWSER_TEST,
                RECEPTION_TEST,
                DIARY_TEST,
                EVIDENCE_TEST,
                CONTINUITY_TEST,
            ],
            "artifacts": [
                FIRST_PACKET,
                FIRST_MANIFEST,
                REPAIR_PACKET,
                REPAIR_MANIFEST,
                UPDATER,
            ],
        },
        "unresolved_gates": [
            "A read-only post-cancellation programme orientation must select and freeze the next command-family tranche.",
            "The stale pre-adapter route-contract suite remains contained test debt under AER-0387.",
            "Live backend/database behavior, external adapters, product data, providers, deployment and production remain closed.",
        ],
    }


def main() -> int:
    graph = _read(GRAPH)
    if graph["graph_revision"] == 312 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 313
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 313 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected ordinary Diary convergence Continuity predecessor")
    _write(GRAPH, graph)

    compass = _read(COMPASS)
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Converge both first-party cancellation clients on one deterministic command and fresh-truth contract",
        "outcome": "Reception One and the ordinary Diary now preserve identical cancellation meaning across different visual projections.",
        "evidence": _all_evidence(),
    }
    if (
        compass["map_revision"] == 294
        and compass["source_graph_revision"] == 312
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 295
        and compass["source_graph_revision"] == 313
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected ordinary Diary convergence Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Two first-party Diary projections now share one cancellation truth kernel",
        "why_now": "The earlier review located a false-failure and semantic-fallback gap in the ordinary Diary after Reception One had already proven the canonical interaction.",
        "outcome": "Cancellation presentation may vary across adapters while proposal, confirmation, receipt and fresh source truth retain one deterministic meaning.",
        "unlocks": [
            "Run a provider-free read-only post-cancellation programme orientation.",
            "Compare the complete cancellation chain with remaining Reception One and API Spine command families.",
            "Freeze the narrowest next architecture-strengthening tranche before another product edit.",
        ],
        "does_not_solve": [
            "Selection of the next command family until the read-only orientation completes.",
            "The contained stale pre-adapter route-contract test debt.",
            "Live backend/database, external-adapter, product-data, provider, deployment or production operation.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 313 / Compass 295. Reception One and the ordinary "
        "Diary now consume one canonical cancellation command and fresh-truth "
        "contract. A provider-free read-only post-cancellation programme orientation is next."
    )
    limit = (
        "The ordinary Diary cancellation convergence proves authored-synthetic "
        "route-intercepted client behavior, not live backend/database, external-adapter, "
        "representative usability, deployment or production behavior."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 313
    compass["map_revision"] = 295
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
