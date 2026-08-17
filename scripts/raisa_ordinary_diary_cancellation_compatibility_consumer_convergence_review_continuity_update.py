"""Advance Continuity and Compass for the ordinary Diary cancellation review."""

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
NODE_ID = "raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review"
PARENT = "raisa-reception-one-selected-appointment-cancellation-composition"
SOURCE_HEAD = "0f3b0c73fef0a2a52186a8f86bae8cf351d1a8df"
UPDATED_AT = "2026-08-17T08:41:05Z"

PLAN = "docs/raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review-plan.md"
THREAT = (
    "docs/security/"
    "raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review-threat-model-delta.md"
)
REPORT_DOC = "docs/raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review.md"
EVIDENCE_ROOT = (
    "orchestration/continuity/"
    "raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review/"
)
EVIDENCE_SCHEMA = (
    EVIDENCE_ROOT
    + "ordinary-diary-cancellation-compatibility-consumer-convergence-review-evidence.schema.json"
)
EVIDENCE = (
    EVIDENCE_ROOT
    + "ordinary-diary-cancellation-compatibility-consumer-convergence-review-evidence.json"
)
STATIC_TEST = "tests/test_raisa_ordinary_diary_cancellation_compatibility_consumer_convergence_review.py"
EVIDENCE_TEST = "tests/test_raisa_ordinary_diary_cancellation_compatibility_consumer_convergence_review_evidence.py"
GEMINI_PACKET = (
    "orchestration/agent_inbox/codex/"
    "raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review-"
    "gemini37-review-packet.md"
)
GEMINI_MANIFEST = (
    "orchestration/agent_inbox/codex/"
    "raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review-"
    "gemini37-command-manifest.json"
)
GEMINI_PREFLIGHT = (
    "orchestration/agent_inbox/codex/"
    "raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review-"
    "gemini37-worktree-preflight.json"
)
PREVERIFIER_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review-"
    "pre-verifier-receipt.json"
)
POSTCOMPACTION_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review-"
    "post-compaction-receipt.json"
)
GEMINI_REVIEW = (
    "orchestration/agent_inbox/antigravity/"
    "raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review-"
    "gemini37-receipt.json"
)
REGISTER = "docs/ariadne-agent-error-correction-register-revision-343.md"
CLOSEOUT = "docs/raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-ordinary-diary-cancellation-compatibility-consumer-convergence-review-"
    "sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-17--ordinary-diary-cancellation-compatibility-consumer-convergence-review.md"
)
UPDATER = (
    "scripts/"
    "raisa_ordinary_diary_cancellation_compatibility_consumer_convergence_review_"
    "continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/"
    "test_raisa_ordinary_diary_cancellation_compatibility_consumer_convergence_review_"
    "continuity.py"
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
        REPORT_DOC,
        EVIDENCE_SCHEMA,
        EVIDENCE,
        STATIC_TEST,
        EVIDENCE_TEST,
        GEMINI_PACKET,
        GEMINI_MANIFEST,
        GEMINI_PREFLIGHT,
        PREVERIFIER_RECEIPT,
        POSTCOMPACTION_RECEIPT,
        GEMINI_REVIEW,
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
        "title": "Ordinary Diary cancellation compatibility-consumer convergence review",
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
        "relationships": [{"node_id": PARENT, "relation": "validates"}],
        "authority": {
            "authorized_openings": [],
            "notes": [
                "Repository-static provider-free review only; no product source or command path changed.",
                "The review freezes one later client-only dedicated-delete and canonical-confirm convergence.",
                "Product data, providers, database execution, deployment and protected refs remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-ordinary-diary-cancellation-compatibility-review",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept the five source-grounded client gaps and freeze one delete-only fail-closed convergence.",
            }
        ],
        "claim_scope": [
            "The ordinary Diary can report failure after a valid canonical delete commit because it still requires an appointment read model absent from the strict public envelope.",
            "Its 404-to-status fallback changes command meaning and drops the free-text reason while retaining human confirmation.",
            "Its cancellation-specific proposal/endpoint admission and terminal-outcome reconciliation are weaker than Reception One.",
            "The smallest later fix is client-only and requires no backend, API, schema, migration or database change.",
            "One fresh Gemini 3.7 Flash/high exact-candidate veto passes after eight zero-exit commands and leaves its worktree clean.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "gap",
                "evidence": [PLAN, REPORT_DOC, EVIDENCE, CLOSEOUT],
                "note": "The ordinary Diary cancellation consumer remains a separately typed action but has not yet converged on the canonical delete-only response contract.",
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "gap",
                "evidence": [REPORT_DOC, EVIDENCE, CLOSEOUT],
                "note": "Fresh source-truth reconciliation is currently success-only and must cover every terminal or uncertain cancellation outcome.",
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [REPORT_DOC, EVIDENCE_SCHEMA, EVIDENCE, REGISTER],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                PREVERIFIER_RECEIPT,
                GEMINI_PREFLIGHT,
                GEMINI_REVIEW,
                POSTCOMPACTION_RECEIPT,
            ],
            "tests": [STATIC_TEST, EVIDENCE_TEST, CONTINUITY_TEST],
            "artifacts": [GEMINI_PACKET, GEMINI_MANIFEST, UPDATER],
        },
        "unresolved_gates": [
            "The ordinary Diary client-only canonical cancellation convergence is frozen but not yet implemented.",
            "The stale pre-adapter route-contract suite remains contained test debt under AER-0387.",
            "Live backend/database behavior, external adapters, product data, providers, deployment and production remain closed.",
        ],
    }


def main() -> int:
    graph = _read(GRAPH)
    if graph["graph_revision"] == 311 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 312
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 312 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit(
            "Unexpected ordinary Diary cancellation review Continuity predecessor"
        )
    _write(GRAPH, graph)

    compass = _read(COMPASS)
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Locate the remaining native cancellation-consumer divergence and freeze its narrowest source convergence",
        "outcome": "The ordinary Diary client gap is source-proved and one provider-free delete-only client correction is ready to implement.",
        "evidence": _all_evidence(),
    }
    if (
        compass["map_revision"] == 293
        and compass["source_graph_revision"] == 311
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 294
        and compass["source_graph_revision"] == 312
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit(
            "Unexpected ordinary Diary cancellation review Compass predecessor"
        )

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "The cancellation truth kernel is accepted and the remaining ordinary Diary consumer divergence is now exactly bounded",
        "why_now": "Reception One proved the canonical interaction; this read-only review showed the older consumer still expects the wrong response and may change command families on failure.",
        "outcome": "A client-only canonical delete convergence can now remove false failure, semantic fallback and stale-outcome ambiguity without backend change.",
        "unlocks": [
            "Implement the provider-free ordinary Diary client-only canonical cancellation convergence.",
            "Remove delete-to-status fallback while preserving visible destructive intent and human confirmation.",
            "Admit the strict minimal receipt and reconcile fresh Diary truth after every terminal or uncertain outcome.",
        ],
        "does_not_solve": [
            "The client source gap itself until the next composition is accepted.",
            "The contained stale pre-adapter route-contract test debt.",
            "Live backend/database, external-adapter, product-data, provider, deployment or production operation.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 312 / Compass 294. The ordinary Diary cancellation "
        "consumer divergence is source-proved: it can reject the accepted minimal "
        "receipt, change to status semantics and fail to reconcile uncertain outcomes. "
        "The provider-free client-only canonical delete convergence is next."
    )
    limit = (
        "The ordinary Diary cancellation review proves repository facts and one "
        "later source boundary; it changes no product behavior and proves no live "
        "route, database or external-adapter outcome."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 312
    compass["map_revision"] = 294
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
