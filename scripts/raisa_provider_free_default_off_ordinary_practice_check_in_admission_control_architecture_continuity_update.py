"""Advance Continuity and Compass for check-in admission-control architecture."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestration_harness.git_object_resolution import resolve_commit_source
from scripts import ariadne_compass


GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = (
    "raisa-provider-free-default-off-ordinary-practice-canonical-check-in-"
    "admission-control-architecture"
)
PARENT = (
    "ariadne-transactional-closeout-control-plane-consolidation-efficacy-"
    "rehearsal"
)
SOURCE_HEAD = "752b521c59f5b44bf46de0cf776a33ac74b8134d"
UPDATED_AT = "2026-08-18T17:24:22.2795586Z"
PLAN = (
    "docs/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-"
    "admission-control-architecture-plan.md"
)
ARCHITECTURE = (
    "docs/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-"
    "admission-control-architecture.md"
)
THREAT = (
    "docs/security/raisa-provider-free-default-off-ordinary-practice-canonical-"
    "check-in-admission-control-architecture-threat-model-delta.md"
)
BASE = (
    "orchestration/continuity/raisa-provider-free-default-off-ordinary-practice-"
    "canonical-check-in-admission-control-architecture/"
)
CONTRACT = BASE + "contract.json"
SCHEMA = BASE + "contract.schema.json"
EVIDENCE = BASE + "provider-free-architecture-evidence.json"
REPORT_ARTIFACT = BASE + "architecture-report.md"
VALIDATOR = (
    "scripts/raisa_provider_free_default_off_ordinary_practice_check_in_"
    "admission_control_architecture.py"
)
FOCUSED_TEST = (
    "tests/test_raisa_provider_free_default_off_ordinary_practice_check_in_"
    "admission_control_architecture.py"
)
PREPLAN_STATE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-default-off-ordinary-"
    "practice-canonical-check-in-admission-control-architecture-preplanning-"
    "runtime-state.json"
)
PREPLAN_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-provider-free-default-off-ordinary-"
    "practice-canonical-check-in-admission-control-architecture-preplanning-"
    "receipt.json"
)
MANIFEST = (
    "orchestration/agent_inbox/codex/raisa-check-in-admission-control-"
    "architecture-gemini37-command-manifest.json"
)
PREFLIGHT = (
    "orchestration/agent_inbox/codex/raisa-check-in-admission-control-"
    "architecture-gemini37-review-worktree-preflight.json"
)
PRE_VERIFIER_STATE = (
    "orchestration/agent_inbox/codex/raisa-check-in-admission-control-"
    "architecture-pre-verifier-acceptance-runtime-state.json"
)
PRE_VERIFIER_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-check-in-admission-control-"
    "architecture-pre-verifier-acceptance-receipt.json"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-check-in-admission-control-"
    "architecture-gemini37-review-receipt.json"
)
REGISTER = "docs/ariadne-agent-error-correction-register-revision-512.md"
CLOSEOUT = (
    "docs/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-"
    "admission-control-architecture-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-check-in-admission-control-"
    "architecture-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/2026-08-19--default-off-ordinary-practice-"
    "check-in-admission-control-architecture.md"
)
UPDATER = (
    "scripts/raisa_provider_free_default_off_ordinary_practice_check_in_"
    "admission_control_architecture_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_default_off_ordinary_practice_check_in_"
    "admission_control_architecture_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        ARCHITECTURE,
        THREAT,
        CONTRACT,
        SCHEMA,
        EVIDENCE,
        REPORT_ARTIFACT,
        VALIDATOR,
        FOCUSED_TEST,
        PREPLAN_STATE,
        PREPLAN_RECEIPT,
        MANIFEST,
        PREFLIGHT,
        PRE_VERIFIER_STATE,
        PRE_VERIFIER_RECEIPT,
        REVIEW,
        REGISTER,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        UPDATER,
        CONTINUITY_TEST,
    ]


def _node(*, source_head: str) -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": (
            "Provider-free default-off ordinary-practice canonical check-in "
            "admission-control architecture"
        ),
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
                "Ordinary-practice admission remains absent, default-off and denied.",
                "Synthetic and ordinary lanes are non-substitutable; lane overlap denies.",
                "The architecture authorizes no mounted product command or enablement.",
            ],
        },
        "decisions": [
            {
                "id": "accept-default-off-check-in-admission-control-architecture",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": (
                    "Accept four-state disable-biased admission control, dominant "
                    "kill switch and non-PHI observability without enablement."
                ),
            }
        ],
        "claim_scope": [
            "All 11 frozen source bindings match.",
            "The record has four states and exactly six allowed transitions with no resume.",
            "Five future commands remain unmounted and unauthorized now.",
            "All 390 hostile mutations fail closed with zero escapes.",
            "Five metric families and six non-actuating critical alerts are frozen.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, ARCHITECTURE, THREAT],
            "findings": [CONTRACT, SCHEMA, EVIDENCE, REPORT_ARTIFACT, REGISTER],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                PREPLAN_STATE,
                PREPLAN_RECEIPT,
                MANIFEST,
                PREFLIGHT,
                PRE_VERIFIER_STATE,
                PRE_VERIFIER_RECEIPT,
                REVIEW,
            ],
            "tests": [FOCUSED_TEST, CONTINUITY_TEST],
            "artifacts": [VALIDATOR, UPDATER],
        },
        "unresolved_gates": [
            "No ordinary-practice admission record is implemented or active.",
            "Tenant-role, unknown-commit and environment posture evidence remains absent.",
            "Control commands and read-only posture projection remain unmounted.",
            "The Ariadne and DeepSeek shared causal clock remains shadow-only.",
            "No product data, provider, runtime, deployment or protected integration is authorized.",
        ],
    }


def main() -> int:
    source_resolution = resolve_commit_source(repo_root=ROOT, source_head=SOURCE_HEAD)
    source_head = source_resolution["resolved_commit"]
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 324 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node(source_head=source_head))
        graph["graph_revision"] = 325
    elif graph["graph_revision"] == 325 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node(source_head=source_head)
    else:
        raise SystemExit("Unexpected check-in admission architecture predecessor")
    graph["updated_at"] = UPDATED_AT

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Freeze check-in admission control without enabling a practice",
        "outcome": "Architecture accepted; ordinary admission remains absent and denied.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 306
        and compass["source_graph_revision"] == 324
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 307
        and compass["source_graph_revision"] == 325
        and compass["journey"][-1]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected check-in admission architecture Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Rehearse the unmounted default-off check-in admission kernel",
        "why_now": (
            "The four-state, six-transition disable-biased architecture at "
            "752b521c59f5b44bf46de0cf776a33ac74b8134d is accepted with all "
            "operational-evidence gates still closed."
        ),
        "outcome": (
            "Prove the typed evaluator and transition kernel provider-free with zero "
            "active records, exact default denial and no mounted command."
        ),
        "unlocks": [
            "Freeze one unmounted kernel contract derived from the accepted architecture.",
            "Exercise allowed and forbidden transitions with zero active records.",
            "Prove kill-switch dominance and disable-only rollback without enablement.",
        ],
        "does_not_solve": [
            "No ordinary practice is enabled and no feature flag or allowlist changes.",
            "No product route, generic-status Arrived, grammar, client or waiting area changes.",
            "No live clockwork adoption, product data, provider, runtime, deployment or protected integration opens.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 325 / Compass 307. Default-off ordinary-practice "
        "canonical check-in admission-control architecture is accepted at exact "
        "source 752b521c59f5b44bf46de0cf776a33ac74b8134d; no practice is enabled. "
        "The next tranche is an unmounted zero-active-record kernel rehearsal."
    )
    compass["source_graph_revision"] = 325
    compass["map_revision"] = 307
    compass["updated_at"] = UPDATED_AT

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    _write(GRAPH, graph)
    _write(COMPASS, compass)
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
