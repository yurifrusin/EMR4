"""Record the accepted provider-free clockwork single-owner migration rehearsal."""

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
NODE_ID = "ariadne-provider-free-clockwork-single-owner-migration-retirement-rehearsal"
PARENT = "ariadne-provider-free-clockwork-governance-projection-consolidation-repair"
SOURCE_HEAD = "d03cc6386fdf3e2714881089514380d93824e160"
UPDATED_AT = "2026-08-19T01:53:31.2243631Z"
BASE = "orchestration/continuity/ariadne-provider-free-clockwork-single-owner-migration-retirement-rehearsal/"
PLAN = "docs/ariadne-provider-free-clockwork-single-owner-migration-retirement-rehearsal-plan.md"
THREAT = "docs/security/ariadne-provider-free-clockwork-single-owner-migration-retirement-rehearsal-threat-model-delta.md"
CONTRACT = BASE + "contract.json"
INTENT = BASE + "closeout-intent.json"
EVIDENCE = BASE + "provider-free-migration-evidence.json"
MIRROR_RECEIPT = BASE + "canonical-mirror-receipt.json"
MIGRATION_REPORT = BASE + "migration-report.md"
ENGINE = "orchestration_harness/governance_migration.py"
RUNNER = "scripts/ariadne_provider_free_clockwork_single_owner_migration_retirement_rehearsal.py"
FOCUSED_TEST = "tests/test_ariadne_provider_free_clockwork_single_owner_migration_retirement_rehearsal.py"
PREDECESSOR_TEST = "tests/test_ariadne_provider_free_clockwork_governance_projection_consolidation_repair.py"
BATON_TEST = "tests/test_current_baton_consistency.py"
REGISTER_TEST = "tests/test_ariadne_agent_error_register.py"
REGISTER = "docs/ariadne-agent-error-correction-register-revision-566.md"
PREPLAN_STATE = "orchestration/agent_inbox/codex/ariadne-clockwork-single-owner-migration-retirement-rehearsal-preplanning-runtime-state.json"
PREPLAN_RECEIPT = PREPLAN_STATE.replace("runtime-state", "receipt")
FIRST_MANIFEST = "orchestration/agent_inbox/codex/ariadne-clockwork-single-owner-migration-retirement-rehearsal-gemini37-command-manifest.json"
FIRST_PACKET = FIRST_MANIFEST.replace("command-manifest.json", "review-packet.md")
FIRST_PREFLIGHT = FIRST_MANIFEST.replace("command-manifest.json", "review-worktree-preflight.json")
FIRST_REVIEW = "orchestration/agent_inbox/antigravity/ariadne-clockwork-single-owner-migration-retirement-rehearsal-gemini37-review-receipt.json"
CORRECTED_MANIFEST = FIRST_MANIFEST.replace("command-manifest", "corrected-command-manifest")
CORRECTED_PACKET = FIRST_PACKET.replace("review-packet", "corrected-review-packet")
CORRECTED_PREFLIGHT = FIRST_PREFLIGHT.replace("review-worktree-preflight", "corrected-review-worktree-preflight")
CORRECTED_STATE = "orchestration/agent_inbox/codex/ariadne-clockwork-single-owner-migration-retirement-rehearsal-corrected-pre-verifier-runtime-state.json"
CORRECTED_RECEIPT = CORRECTED_STATE.replace("runtime-state", "receipt")
CORRECTED_REVIEW = FIRST_REVIEW.replace("review-receipt", "corrected-review-receipt")
CLOSEOUT = "docs/ariadne-provider-free-clockwork-single-owner-migration-retirement-rehearsal-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/ariadne-clockwork-single-owner-migration-retirement-rehearsal-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-19--clockwork-single-owner-migration-retirement-rehearsal.md"
UPDATER = "scripts/ariadne_provider_free_clockwork_single_owner_migration_retirement_rehearsal_continuity_update.py"
CONTINUITY_TEST = "tests/test_ariadne_provider_free_clockwork_single_owner_migration_retirement_rehearsal_continuity.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _evidence() -> list[str]:
    return [
        PLAN, THREAT, CONTRACT, INTENT, EVIDENCE, MIRROR_RECEIPT,
        MIGRATION_REPORT, ENGINE, RUNNER, FOCUSED_TEST, PREDECESSOR_TEST,
        BATON_TEST, REGISTER_TEST, REGISTER, PREPLAN_STATE, PREPLAN_RECEIPT,
        FIRST_MANIFEST, FIRST_PACKET, FIRST_PREFLIGHT, FIRST_REVIEW,
        CORRECTED_MANIFEST, CORRECTED_PACKET, CORRECTED_PREFLIGHT,
        CORRECTED_STATE, CORRECTED_RECEIPT, CORRECTED_REVIEW, CLOSEOUT,
        ACCEPTANCE, MAILBOX, UPDATER, CONTINUITY_TEST,
    ]


def _node(*, source_head: str) -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Ariadne provider-free clockwork single-owner migration and retirement rehearsal",
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
                "The provider-free canonical-mirror rehearsal is accepted; live canonical adoption remains closed.",
                "Existing canonical controls remain authoritative until Yuri makes the explicit adoption choice.",
                "No product, provider, runtime, deployment or protected-ref authority opened.",
            ],
        },
        "decisions": [{
            "id": "accept-clockwork-single-owner-migration-retirement-rehearsal",
            "source": ACCEPTANCE,
            "status": "accepted",
            "summary": "Accept exclusive mirror ownership, fault safety and rollback evidence without activating the clockwork live.",
        }],
        "claim_scope": [
            "All ten mirror surfaces have exclusive clockwork ownership; dual-owned surfaces are zero and four legacy writers are retired in the mirror.",
            "All twenty-three fault checkpoints, byte-exact rollback and exact restore pass.",
            "All thirteen predecessor and nine surrounding probes pass with zero caller-authored derived fields.",
            "The exact reviewed package occupies 892 of 950 lines; immutable closeout-fixture binding leaves the final package at 914 of 950.",
            "Final end-to-end cost is twenty-five reruns; projected representative steady-state corrective reruns are zero.",
            "Fresh corrected Gemini 3.7 Flash/high review passes eleven of eleven commands at exact clean candidate d03cc6386fdf3e2714881089514380d93824e160.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [CONTRACT, INTENT, EVIDENCE, MIRROR_RECEIPT, MIGRATION_REPORT, REGISTER],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                PREPLAN_STATE, PREPLAN_RECEIPT, FIRST_MANIFEST, FIRST_PACKET,
                FIRST_PREFLIGHT, FIRST_REVIEW, CORRECTED_MANIFEST,
                CORRECTED_PACKET, CORRECTED_PREFLIGHT, CORRECTED_STATE,
                CORRECTED_RECEIPT, CORRECTED_REVIEW,
            ],
            "tests": [FOCUSED_TEST, PREDECESSOR_TEST, BATON_TEST, REGISTER_TEST, CONTINUITY_TEST],
            "artifacts": [ENGINE, RUNNER, UPDATER],
        },
        "unresolved_gates": [
            "Yuri must explicitly choose live canonical adoption/retirement or shadow retention plus product resumption.",
            "No actual canonical writer or control may be changed before that choice.",
            "Occupied DeepSeek remains behind the separate native-Harness HMR boot proof.",
            "No product, practice, provider, Git, runtime, deployment or protected integration authority is opened.",
        ],
    }


def main() -> int:
    source_head = resolve_commit_source(repo_root=ROOT, source_head=SOURCE_HEAD)["resolved_commit"]
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 329 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node(source_head=source_head))
        graph["graph_revision"] = 330
    elif graph["graph_revision"] == 330 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node(source_head=source_head)
    else:
        raise SystemExit("Unexpected clockwork migration Continuity predecessor")
    graph["updated_at"] = UPDATED_AT

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove exclusive clockwork ownership, retirement safety and exact rollback in an isolated canonical mirror",
        "outcome": "Canonical-mirror rehearsal accepted; live adoption remains an explicit user-attention fork.",
        "evidence": _evidence(),
    }
    if compass["map_revision"] == 311 and compass["source_graph_revision"] == 329 and compass["current_position"]["node_id"] == PARENT:
        compass["journey"].append(journey)
    elif compass["map_revision"] == 312 and compass["source_graph_revision"] == 330 and compass["journey"][-1]["node_id"] == NODE_ID:
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected clockwork migration Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Choose live canonical adoption or retain shadow-only clockwork and resume product work",
        "why_now": "Exact candidate d03cc6386fdf3e2714881089514380d93824e160 proves exclusive ownership, all twenty-three fault boundaries and byte-exact rollback with zero projected representative steady-state corrective reruns.",
        "outcome": "Yuri explicitly authorizes one separately frozen live adoption/retirement tranche or retains existing controls and resumes the default-off check-in route-adapter plan.",
        "unlocks": [
            "A controlled live adoption plan with no dual writer and exact rollback, if explicitly selected.",
            "Otherwise, immediate product-track resumption with existing governance controls unchanged.",
        ],
        "does_not_solve": [
            "Mirror acceptance does not activate the clockwork or retire any actual control.",
            "No DeepSeek Harness reliability or HMR boot proof was tested.",
            "No product, practice, data, Git, runtime, deployment or protected integration opens.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 330 / Compass 312. The provider-free clockwork single-owner migration and retirement rehearsal is accepted at exact candidate d03cc6386fdf3e2714881089514380d93824e160: ten surfaces have one clockwork owner, all twenty-three fault checkpoints and byte-exact rollback pass, and projected representative steady-state corrective reruns are zero. Live canonical adoption remains Yuri's explicit choice."
    )
    compass["source_graph_revision"] = 330
    compass["map_revision"] = 312
    compass["updated_at"] = UPDATED_AT

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    _write(GRAPH, graph)
    _write(COMPASS, compass)
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
