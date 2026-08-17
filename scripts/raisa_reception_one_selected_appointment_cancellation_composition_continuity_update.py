"""Advance Continuity and Compass for Reception One cancellation composition."""

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
NODE_ID = "raisa-reception-one-selected-appointment-cancellation-composition"
PARENT = "ariadne-recent-work-effectiveness-and-transport-repair"
SOURCE_HEAD = "856ebc3d832d5b64ce65c2e0732eaa63d926c600"
UPDATED_AT = "2026-08-17T05:49:00Z"

PLAN = "docs/raisa-reception-one-selected-appointment-cancellation-composition-plan.md"
THREAT = (
    "docs/security/"
    "raisa-reception-one-selected-appointment-cancellation-composition-threat-model-delta.md"
)
EVIDENCE_SCHEMA = (
    "orchestration/continuity/"
    "raisa-reception-one-selected-appointment-cancellation-composition/"
    "selected-appointment-cancellation-composition-evidence.schema.json"
)
EVIDENCE = (
    "orchestration/continuity/"
    "raisa-reception-one-selected-appointment-cancellation-composition/"
    "selected-appointment-cancellation-composition-evidence.json"
)
BROWSER_TEST = "review/test_reception_one_cancellation_action.py"
SOURCE_TEST = "tests/test_raisa_reception_one_selected_appointment_cancellation_composition_evidence.py"
DEEPSEEK_PACKET = (
    "orchestration/agent_inbox/codex/"
    "raisa-reception-one-selected-appointment-cancellation-composition-"
    "deepseek-test-worker-packet.md"
)
DEEPSEEK_RESULT = (
    "orchestration/agent_inbox/deepseek/"
    "raisa-reception-one-selected-appointment-cancellation-composition-test-worker-result.json"
)
GEMINI_PACKET = (
    "orchestration/agent_inbox/codex/"
    "raisa-reception-one-selected-appointment-cancellation-composition-"
    "gemini37-review-packet.md"
)
GEMINI_MANIFEST = (
    "orchestration/agent_inbox/codex/"
    "raisa-reception-one-selected-appointment-cancellation-composition-"
    "gemini37-command-manifest.json"
)
GEMINI_PREFLIGHT = (
    "orchestration/agent_inbox/codex/"
    "raisa-reception-one-selected-appointment-cancellation-composition-"
    "gemini37-worktree-preflight.json"
)
GEMINI_REVIEW = (
    "orchestration/agent_inbox/antigravity/"
    "raisa-reception-one-selected-appointment-cancellation-composition-"
    "gemini37-review-receipt.json"
)
REGISTER = "docs/ariadne-agent-error-correction-register-revision-337.md"
CLOSEOUT = (
    "docs/raisa-reception-one-selected-appointment-cancellation-composition-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-reception-one-selected-appointment-cancellation-composition-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-17--reception-one-selected-appointment-cancellation-composition.md"
)
POSTCOMPACTION_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-reception-one-selected-appointment-cancellation-composition-"
    "closeout-postcompaction-receipt.json"
)
PREVERIFIER_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-reception-one-selected-appointment-cancellation-composition-"
    "pre-verifier-v3-receipt.json"
)
UPDATER = (
    "scripts/"
    "raisa_reception_one_selected_appointment_cancellation_composition_"
    "continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/"
    "test_raisa_reception_one_selected_appointment_cancellation_composition_"
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
        EVIDENCE_SCHEMA,
        EVIDENCE,
        "docs/diary/diary.js",
        "docs/diary/meta-grid.js",
        "docs/diary/meta-grid.css",
        "docs/diary/diary.html",
        BROWSER_TEST,
        SOURCE_TEST,
        DEEPSEEK_PACKET,
        DEEPSEEK_RESULT,
        GEMINI_PACKET,
        GEMINI_MANIFEST,
        GEMINI_PREFLIGHT,
        PREVERIFIER_RECEIPT,
        GEMINI_REVIEW,
        REGISTER,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        POSTCOMPACTION_RECEIPT,
        UPDATER,
        CONTINUITY_TEST,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Reception One selected-appointment cancellation composition",
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
                "Provider-free authored-synthetic first-party client composition over the accepted delete proposal/confirm family.",
                "Reception One is a reference renderer; adapter presentation freedom remains below immutable typed facts, actions, confirmation, authority and receipt semantics.",
                "No raw compatibility DELETE, status-cancel fallback, product data, provider, database execution, deployment or protected-ref authority is opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-reception-one-selected-appointment-cancellation-composition",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept one explicit-confirmation cancellation action with strict public receipt admission and fresh truth reconciliation.",
            }
        ],
        "claim_scope": [
            "One selected current appointment can use one dedicated delete proposal and canonical delete-confirm interaction after explicit staff confirmation.",
            "Fifteen dedicated and 84 combined route-intercepted browser cases pass, alongside 43 focused and 200 canonical-fast tests.",
            "Malformed, stale, blocked, cancelled, interrupted and uncertain outcomes fail closed and reconcile from a fresh scoped read.",
            "One fresh Gemini 3.7 Flash/high exact-candidate veto passes at unchanged source HEAD.",
            "Creative or external renderers may vary presentation but cannot vary facts, consequences, warnings, confirmation, authority checks or receipts.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [PLAN, EVIDENCE, BROWSER_TEST, CLOSEOUT],
                "note": "Cancellation remains one separately typed selected-appointment action and does not create a generic command dispatcher.",
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [PLAN, EVIDENCE, BROWSER_TEST, CLOSEOUT],
                "note": "The display accepts terminal truth only after a fresh scoped Diary read; event cues remain acceleration hints.",
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [EVIDENCE_SCHEMA, EVIDENCE, REGISTER],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                DEEPSEEK_RESULT,
                PREVERIFIER_RECEIPT,
                GEMINI_PREFLIGHT,
                GEMINI_REVIEW,
                POSTCOMPACTION_RECEIPT,
            ],
            "tests": [BROWSER_TEST, SOURCE_TEST, CONTINUITY_TEST],
            "artifacts": [
                "docs/diary/diary.js",
                "docs/diary/meta-grid.js",
                "docs/diary/meta-grid.css",
                "docs/diary/diary.html",
                DEEPSEEK_PACKET,
                GEMINI_PACKET,
                GEMINI_MANIFEST,
                UPDATER,
            ],
        },
        "unresolved_gates": [
            "The ordinary Diary deleteBooking and applySignedDeleteProposal compatibility consumer still retains a separately unaccepted dual-family fallback.",
            "Route-intercepted browser evidence does not prove live backend or PostgreSQL behavior.",
            "External-adapter interoperability, product data, providers, deployment, production and release remain closed.",
        ],
    }


def main() -> int:
    graph = _read(GRAPH)
    if graph["graph_revision"] == 310 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 311
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 311 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected cancellation-composition Continuity predecessor")
    _write(GRAPH, graph)

    compass = _read(COMPASS)
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Complete the first-party selected-action console with canonical explicit-confirmation cancellation",
        "outcome": "Reception One can cancel one selected appointment through the delete-only truth kernel and can serve as one reference rendering of an adapter-neutral contract.",
        "evidence": _all_evidence(),
    }
    if (
        compass["map_revision"] == 292
        and compass["source_graph_revision"] == 310
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 293
        and compass["source_graph_revision"] == 311
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected cancellation-composition Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "The native selected-action console now spans routine edits and destructive cancellation over one truth kernel",
        "why_now": "The visible cancellation composition passed over the accepted delete-confirm envelope, leaving the ordinary Diary compatibility consumer as the narrowest same-family inconsistency.",
        "outcome": "Reception One is a stronger reference client, while adapter presentation remains decoupled from deterministic facts, authority and effects.",
        "unlocks": [
            "Run one provider-free read-only ordinary Diary cancellation compatibility-consumer convergence review.",
            "Map deleteBooking and applySignedDeleteProposal against the now-proven canonical delete-only consumer contract.",
            "Freeze the smallest later source convergence without calling or authorizing raw compatibility DELETE.",
        ],
        "does_not_solve": [
            "The ordinary Diary dual-family cancellation fallback itself.",
            "External-adapter conformance or representative human usability.",
            "Product/patient data, providers, database execution, deployment, release, Pages or protected refs.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 311 / Compass 293. Reception One selected-"
        "appointment cancellation passes through the canonical delete-only "
        "truth kernel with explicit confirmation and fresh reconciliation. "
        "A provider-free read-only ordinary Diary cancellation compatibility-"
        "consumer convergence review is next."
    )
    limit = (
        "The Reception One cancellation result proves authored-synthetic "
        "first-party rendering over a typed adapter-neutral contract; it does "
        "not prove live backend/database or external-adapter operation."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 311
    compass["map_revision"] = 293
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
