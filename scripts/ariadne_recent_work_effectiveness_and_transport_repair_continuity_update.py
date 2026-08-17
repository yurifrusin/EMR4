"""Advance Continuity and Compass for the Ariadne effectiveness review."""

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
NODE_ID = "ariadne-recent-work-effectiveness-and-transport-repair"
PARENT = (
    "raisa-provider-free-disposable-postgresql-delete-confirm-http-"
    "integration-rehearsal"
)
SOURCE_HEAD = "73bea42b37424ca3f53240d52f8e5c10120a5ce7"
UPDATED_AT = "2026-08-17T02:40:11Z"

PLAN = "docs/ariadne-recent-work-effectiveness-and-deepseek-harness-adaptation-plan.md"
THREAT = "docs/security/ariadne-recent-work-effectiveness-and-deepseek-harness-adaptation-threat-model-delta.md"
ASSESSMENT = "docs/ariadne-recent-work-effectiveness-and-deepseek-harness-assessment.md"
DIAGNOSIS = "docs/ariadne-antigravity-transport-timeout-diagnosis.md"
REGISTER = "docs/ariadne-agent-error-correction-register-revision-334.md"
REPLAY = "orchestration/agent_inbox/codex/ariadne-effectiveness-and-deepseek-harness-review-transport-diagnosis-exact-manifest-validation-receipt.json"
VALIDATION = "orchestration/agent_inbox/codex/ariadne-effectiveness-and-deepseek-harness-review-transport-repair-validation-v2-receipt.json"
PREDISPATCH = "orchestration/agent_inbox/codex/ariadne-effectiveness-and-deepseek-harness-review-gemini37-fresh-predispatch-receipt.json"
PACKET = "orchestration/agent_inbox/codex/ariadne-effectiveness-and-deepseek-harness-review-gemini37-fresh-review-packet.md"
MANIFEST = "orchestration/agent_inbox/codex/ariadne-effectiveness-and-deepseek-harness-review-gemini37-fresh-command-manifest.json"
PREFLIGHT = "orchestration/agent_inbox/codex/ariadne-effectiveness-and-deepseek-harness-review-gemini37-fresh-worktree-preflight.json"
REVIEW = "orchestration/agent_inbox/antigravity/ariadne-effectiveness-and-deepseek-harness-review-gemini37-fresh-review-receipt.json"
CLOSEOUT = "docs/ariadne-recent-work-effectiveness-and-deepseek-harness-adaptation-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/ariadne-effectiveness-and-deepseek-harness-adaptation-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-17--ariadne-effectiveness-and-deepseek-harness-adaptation.md"
UPDATER = "scripts/ariadne_recent_work_effectiveness_and_transport_repair_continuity_update.py"
CONTINUITY_TEST = "tests/test_ariadne_recent_work_effectiveness_and_transport_repair_continuity.py"


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
        ASSESSMENT,
        DIAGNOSIS,
        REGISTER,
        REPLAY,
        VALIDATION,
        PREDISPATCH,
        PACKET,
        MANIFEST,
        PREFLIGHT,
        REVIEW,
        "orchestration_harness/git_refs_snapshot.py",
        "orchestration_harness/orchestrator_preflight.py",
        "scripts/ariadne_validation_runner.py",
        "scripts/ariadne_serial_pytest.py",
        "scripts/ariadne_deepseek_claude.py",
        "scripts/ariadne_antigravity.py",
        "tests/test_ariadne_git_refs_snapshot.py",
        "tests/test_ariadne_orchestrator_preflight.py",
        "tests/test_ariadne_validation_runner.py",
        "tests/test_ariadne_serial_pytest.py",
        "tests/test_ariadne_deepseek_claude.py",
        "tests/test_ariadne_antigravity.py",
        "tests/test_ariadne_agent_error_register.py",
        "tests/test_current_baton_consistency.py",
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        UPDATER,
        CONTINUITY_TEST,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Ariadne recent-work effectiveness and transport repair",
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
                "Repository-only Ariadne development-harness review and repair.",
                "Codex remains conductor; DeepSeek Harness migration is rejected.",
                "No Raisa product, data, database, provider, deployment or protected-ref authority is opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-ariadne-effectiveness-and-transport-repair",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept five evidence-backed workflow repairs and resume the narrow provider-free Reception One cancellation composition.",
            }
        ],
        "claim_scope": [
            "The sampled median candidate-to-closeout tail is 38.5 minutes; 40.3 percent of sampled time was tail, not necessarily waste.",
            "Machine Git snapshots, durable validation, pytest admission, worker hardening and terminal-latch non-dispatch pass.",
            "The exact historical command manifest passes provider-free in 150.578 seconds.",
            "Antigravity now has a bounded 45-minute deadline and digest-only nonzero failure evidence.",
            "One fresh eight-command Gemini 3.7 Flash/high veto passes at unchanged exact source HEAD.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [ASSESSMENT, DIAGNOSIS, REGISTER],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [REPLAY, VALIDATION, PREDISPATCH, PREFLIGHT, REVIEW],
            "tests": [
                "tests/test_ariadne_antigravity.py",
                "tests/test_ariadne_agent_error_register.py",
                "tests/test_current_baton_consistency.py",
                CONTINUITY_TEST,
            ],
            "artifacts": [
                "orchestration_harness/git_refs_snapshot.py",
                "orchestration_harness/orchestrator_preflight.py",
                "scripts/ariadne_validation_runner.py",
                "scripts/ariadne_serial_pytest.py",
                "scripts/ariadne_deepseek_claude.py",
                "scripts/ariadne_antigravity.py",
                PACKET,
                MANIFEST,
                UPDATER,
            ],
        },
        "unresolved_gates": [
            "The sub-25-minute ordinary closeout-tail target needs several later samples.",
            "DeepSeek worker hardening is defence in depth, not hostile-process containment.",
            "Raw compatibility DELETE, real/product data, provider product calls, deployment and protected integration remain closed.",
        ],
    }


def main() -> int:
    graph = _read(GRAPH)
    if graph["graph_revision"] == 309 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 310
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 310 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected Ariadne effectiveness Continuity predecessor")
    _write(GRAPH, graph)

    compass = _read(COMPASS)
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Reduce avoidable workflow tail without weakening safety gates",
        "outcome": "Five evidence-backed Ariadne repairs pass and the product sequence can resume with clearer durable evidence.",
        "evidence": _all_evidence(),
    }
    if (
        compass["map_revision"] == 291
        and compass["source_graph_revision"] == 309
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 292
        and compass["source_graph_revision"] == 310
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected Ariadne effectiveness Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["prerequisites"] = [
                "Preserve the accepted delete-confirm HTTP/PostgreSQL truth envelope.",
                "Use machine-derived Git state and durable sequential validation for later tranches.",
                "Keep raw DELETE, product data, providers, deployment and protected integration separately closed.",
            ]
            for path in journey["evidence"]:
                if path not in horizon["evidence"]:
                    horizon["evidence"].append(path)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Ariadne effectiveness repair accepted; visible cancellation composition is next",
        "why_now": "The workflow review and independent correction gate pass, so the next dependency-satisfied product step can reuse the accepted delete-confirm truth envelope.",
        "outcome": "Ariadne now removes repeated evidence friction and preserves useful failure diagnostics without relaxing authority or acceptance.",
        "unlocks": [
            "Freeze the narrow provider-free visible selected-appointment cancellation composition.",
            "Reuse the selected-action console and explicit human confirmation pattern.",
            "Project strict delete-confirm success and failure receipts without opening raw DELETE.",
        ],
        "does_not_solve": [
            "Visible Reception One cancellation behavior itself.",
            "Concurrent crash/restart or unknown-commit behavior.",
            "Product/patient data, provider access, deployment, release, Pages or protected refs.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 310 / Compass 292. Five evidence-backed Ariadne "
        "effectiveness and transport repairs pass without weakening the truth "
        "kernel. The narrow provider-free visible Reception One selected-"
        "appointment cancellation composition is next."
    )
    limit = (
        "The Ariadne effectiveness result improves development evidence and "
        "transport handling; it changes no Raisa product behavior."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 310
    compass["map_revision"] = 292
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
