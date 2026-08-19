"""Record the accepted provider-free governance projection repair."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestration_harness.git_object_resolution import resolve_commit_source
from scripts import ariadne_compass


GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = "ariadne-provider-free-clockwork-governance-projection-consolidation-repair"
PARENT = "ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-rehearsal"
SOURCE_HEAD = "a0bb86b78bfc011066142740c82d5c25cab7b9c8"
UPDATED_AT = "2026-08-18T23:49:44.1443944Z"
BASE = (
    "orchestration/continuity/ariadne-provider-free-clockwork-governance-"
    "projection-consolidation-repair/"
)
PLAN = "docs/ariadne-provider-free-clockwork-governance-projection-consolidation-repair-plan.md"
THREAT = (
    "docs/security/ariadne-provider-free-clockwork-governance-projection-"
    "consolidation-repair-threat-model-delta.md"
)
CONTRACT = BASE + "contract.json"
PROBES = BASE + "rerun-probes.json"
EVIDENCE = BASE + "provider-free-repair-evidence.json"
REPORT_ARTIFACT = BASE + "repair-report.md"
ENGINE = "orchestration_harness/governance_clockwork.py"
RUNNER = (
    "scripts/ariadne_provider_free_clockwork_governance_projection_"
    "consolidation_repair.py"
)
FOCUSED_TEST = (
    "tests/test_ariadne_provider_free_clockwork_governance_projection_"
    "consolidation_repair.py"
)
REGISTER_TEST = "tests/test_ariadne_agent_error_register.py"
REGISTER = "docs/ariadne-agent-error-correction-register-revision-561.md"
FIRST_REVIEW = (
    "orchestration/agent_inbox/antigravity/ariadne-clockwork-governance-"
    "projection-consolidation-repair-gemini37-review-receipt.json"
)
RETRY_REVIEW = FIRST_REVIEW.replace("review-receipt", "retry-review-receipt")
PREPLAN_STATE = (
    "orchestration/agent_inbox/codex/ariadne-clockwork-governance-projection-"
    "consolidation-repair-preplanning-runtime-state.json"
)
PREPLAN_RECEIPT = PREPLAN_STATE.replace("runtime-state", "receipt")
PREVERIFY_STATE = (
    "orchestration/agent_inbox/codex/ariadne-clockwork-governance-projection-"
    "consolidation-repair-retry-pre-verifier-runtime-state.json"
)
PREVERIFY_RECEIPT = PREVERIFY_STATE.replace("runtime-state", "receipt")
MANIFEST = (
    "orchestration/agent_inbox/codex/ariadne-clockwork-governance-projection-"
    "consolidation-repair-gemini37-retry-command-manifest.json"
)
PACKET = MANIFEST.replace("command-manifest.json", "review-packet.md")
PREFLIGHT = MANIFEST.replace("command-manifest.json", "review-worktree-preflight.json")
CLOSEOUT = (
    "docs/ariadne-provider-free-clockwork-governance-projection-"
    "consolidation-repair-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/ariadne-clockwork-governance-projection-"
    "consolidation-repair-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/2026-08-19--clockwork-governance-"
    "projection-consolidation-repair.md"
)
UPDATER = (
    "scripts/ariadne_provider_free_clockwork_governance_projection_"
    "consolidation_repair_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_ariadne_provider_free_clockwork_governance_projection_"
    "consolidation_repair_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        CONTRACT,
        PROBES,
        EVIDENCE,
        REPORT_ARTIFACT,
        ENGINE,
        RUNNER,
        FOCUSED_TEST,
        REGISTER_TEST,
        REGISTER,
        PREPLAN_STATE,
        PREPLAN_RECEIPT,
        FIRST_REVIEW,
        MANIFEST,
        PACKET,
        PREFLIGHT,
        PREVERIFY_STATE,
        PREVERIFY_RECEIPT,
        RETRY_REVIEW,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        UPDATER,
        CONTINUITY_TEST,
    ]


def _node(*, source_head: str) -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Ariadne provider-free clockwork governance projection consolidation repair",
        "kind": "foundation",
        "status": "accepted",
        "created_at": UPDATED_AT,
        "updated_at": UPDATED_AT,
        "coordinates": {
            "git_ref": "codex/ariadne-bernie-davida-parallel-seam",
            "source_head": source_head,
            "thread_id": None,
            "worktree_role": "task",
        },
        "relationships": [{"node_id": PARENT, "relation": "builds_on"}],
        "authority": {
            "authorized_openings": [],
            "notes": [
                "The provider-free private-shadow repair is accepted; live adoption remains closed.",
                "Current governance controls remain authoritative pending a separate migration-and-retirement decision.",
                "No product, provider, runtime, deployment or protected-ref authority opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-clockwork-governance-projection-consolidation-repair",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept the measured private-shadow mechanism and keep live adoption behind Yuri's separate choice.",
            }
        ],
        "claim_scope": [
            "All thirteen preserved rerun probes and nine surrounding-workflow probes reject before publication.",
            "Maintained governance surfaces reduce from ten to four, a sixty-percent reduction.",
            "The exact reviewed five-file implementation occupied 850 lines; final closeout occupies 849 against the frozen 850-line ceiling.",
            "Twenty-one end-to-end reruns yield three-closeout repair-only and four-closeout cumulative break-even.",
            "Default runner execution is byte-preserving; all persistent outputs require explicit publish authority.",
            "Fresh Gemini 3.7 Flash/high review passes at exact clean candidate a0bb86b78bfc011066142740c82d5c25cab7b9c8.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [CONTRACT, PROBES, EVIDENCE, REPORT_ARTIFACT, REGISTER],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                PREPLAN_STATE,
                PREPLAN_RECEIPT,
                FIRST_REVIEW,
                MANIFEST,
                PACKET,
                PREFLIGHT,
                PREVERIFY_STATE,
                PREVERIFY_RECEIPT,
                RETRY_REVIEW,
            ],
            "tests": [FOCUSED_TEST, REGISTER_TEST, CONTINUITY_TEST],
            "artifacts": [ENGINE, RUNNER, UPDATER],
        },
        "unresolved_gates": [
            "Yuri must choose whether to authorize a separately frozen live migration-and-retirement rehearsal or retain shadow-only use.",
            "No current control may be retired and no dual live control plane may be created without that choice.",
            "Occupied DeepSeek remains behind the separate native-Harness HMR boot proof.",
            "No product, practice, provider, Git, runtime, deployment or protected integration authority is opened.",
        ],
    }


def main() -> int:
    source_head = resolve_commit_source(repo_root=ROOT, source_head=SOURCE_HEAD)[
        "resolved_commit"
    ]
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 328 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node(source_head=source_head))
        graph["graph_revision"] = 329
    elif graph["graph_revision"] == 329 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node(source_head=source_head)
    else:
        raise SystemExit("Unexpected governance repair Continuity predecessor")
    graph["updated_at"] = UPDATED_AT

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Replace repeated hand-authored governance bindings with one measured private-shadow clock reading",
        "outcome": "Private-shadow repair accepted; live adoption remains a separate user-attention gate.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 310
        and compass["source_graph_revision"] == 328
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 311
        and compass["source_graph_revision"] == 329
        and compass["journey"][-1]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected governance repair Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Choose whether the accepted clockwork should enter a separately controlled live migration",
        "why_now": (
            "Exact reviewed candidate a0bb86b78bfc011066142740c82d5c25cab7b9c8 covers all twenty-two "
            "representative probes, reduces maintained surfaces sixty percent and pays back in two repair-only closeouts."
        ),
        "outcome": (
            "Yuri chooses either a separately frozen migration-and-retirement rehearsal with no dual live control plane, "
            "or retains this mechanism in private shadow while product work resumes."
        ),
        "unlocks": [
            "A deliberate adoption decision based on measured construction cost and projected savings.",
            "If selected, one fail-closed migration plan that makes the clockwork the sole owner before retiring duplicates.",
            "If deferred, continued use of all existing controls with the accepted shadow mechanism retained as evidence.",
        ],
        "does_not_solve": [
            "Private-shadow acceptance does not authorize live adoption or current-control retirement.",
            "No DeepSeek Harness reliability or HMR boot proof was tested.",
            "No product, practice, data, Git, runtime, deployment or protected integration opens.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 329 / Compass 311. The provider-free clockwork governance projection repair is "
        "accepted in private shadow at exact candidate a0bb86b78bfc011066142740c82d5c25cab7b9c8: twenty-two "
        "representative probes pass, maintained surfaces fall sixty percent and honest repair-only payback is three "
        "closeouts. Yuri's choice is required before live migration or control retirement."
    )
    compass["source_graph_revision"] = 329
    compass["map_revision"] = 311
    compass["updated_at"] = UPDATED_AT

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    _write(GRAPH, graph)
    _write(COMPASS, compass)
    REPORT.write_text(
        ariadne_compass.render_markdown(report),
        encoding="utf-8",
        newline="\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
