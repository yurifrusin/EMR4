"""Advance Continuity and Compass for the unmounted check-in admission kernel."""

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
    "raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-"
    "check-in-admission-control-kernel-rehearsal"
)
PARENT = (
    "raisa-provider-free-default-off-ordinary-practice-canonical-check-in-"
    "admission-control-architecture"
)
SOURCE_HEAD = "4204ec6348abb0f92b1a30314699d4a469fa860a"
UPDATED_AT = "2026-08-18T18:37:32.9752761Z"
BASE = (
    "orchestration/continuity/raisa-provider-free-unmounted-default-off-ordinary-"
    "practice-canonical-check-in-admission-control-kernel-rehearsal/"
)
PLAN = (
    "docs/raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-"
    "check-in-admission-control-kernel-rehearsal-plan.md"
)
THREAT = (
    "docs/security/raisa-provider-free-unmounted-default-off-ordinary-practice-"
    "canonical-check-in-admission-control-kernel-rehearsal-threat-model-delta.md"
)
CONTRACT = BASE + "contract.json"
SCHEMA = BASE + "contract.schema.json"
EVIDENCE = BASE + "provider-free-kernel-rehearsal-evidence.json"
REPORT_ARTIFACT = BASE + "kernel-rehearsal-report.md"
KERNEL = "orchestration_harness/check_in_admission_control.py"
RUNNER = (
    "scripts/raisa_provider_free_unmounted_default_off_ordinary_practice_check_"
    "in_admission_control_kernel_rehearsal.py"
)
FOCUSED_TEST = (
    "tests/test_raisa_provider_free_unmounted_default_off_ordinary_practice_"
    "check_in_admission_control_kernel_rehearsal.py"
)
PLAN_TEST = FOCUSED_TEST.removesuffix(".py") + "_plan.py"
PREPLAN_STATE = (
    "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-default-off-"
    "ordinary-practice-canonical-check-in-admission-control-kernel-rehearsal-"
    "preplanning-runtime-state.json"
)
PREPLAN_RECEIPT = PREPLAN_STATE.replace("runtime-state", "receipt")
MANIFEST = (
    "orchestration/agent_inbox/codex/raisa-check-in-admission-control-kernel-"
    "gemini37-command-manifest.json"
)
PREFLIGHT = (
    "orchestration/agent_inbox/codex/raisa-check-in-admission-control-kernel-"
    "gemini37-review-worktree-preflight.json"
)
FIRST_FAILURE = (
    "orchestration/agent_inbox/antigravity/raisa-check-in-admission-control-"
    "kernel-gemini37-first-worktree-postcondition-failure.json"
)
PRE_VERIFIER_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-check-in-admission-control-kernel-"
    "pre-verifier-acceptance-attempt-003-receipt.json"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-check-in-admission-control-"
    "kernel-gemini37-corrected-review-receipt.json"
)
REGISTER = "docs/ariadne-agent-error-correction-register-revision-521.md"
CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-"
    "check-in-admission-control-kernel-rehearsal-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-check-in-admission-control-kernel-"
    "sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/2026-08-19--unmounted-check-in-admission-"
    "control-kernel-rehearsal.md"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_default_off_ordinary_practice_check_"
    "in_admission_control_kernel_rehearsal_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_default_off_ordinary_practice_"
    "check_in_admission_control_kernel_rehearsal_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        CONTRACT,
        SCHEMA,
        EVIDENCE,
        REPORT_ARTIFACT,
        KERNEL,
        RUNNER,
        FOCUSED_TEST,
        PLAN_TEST,
        PREPLAN_STATE,
        PREPLAN_RECEIPT,
        MANIFEST,
        PREFLIGHT,
        FIRST_FAILURE,
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
            "Provider-free unmounted default-off ordinary-practice canonical "
            "check-in admission-control kernel rehearsal"
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
                "The kernel is unmounted, provider-free and has zero active ordinary records.",
                "Ordinary activation authority is false and no accepted transition produces active.",
                "The shared Ariadne and DeepSeek clock remains shadow-only.",
            ],
        },
        "decisions": [
            {
                "id": "accept-unmounted-check-in-admission-control-kernel",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": (
                    "Accept the pure zero-active-record evaluator and disable-biased "
                    "transition kernel without product mounting or enablement."
                ),
            }
        ],
        "claim_scope": [
            "All seven frozen source bindings match.",
            "All 63 named scenarios pass.",
            "All 341 hostile mutations fail closed with zero escapes.",
            "Canonical active ordinary records and ordinary releases are both zero.",
            "The corrected Gemini veto passes 9/9 commands at unchanged clean HEAD.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [CONTRACT, SCHEMA, EVIDENCE, REPORT_ARTIFACT, REGISTER],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                PREPLAN_STATE,
                PREPLAN_RECEIPT,
                MANIFEST,
                PREFLIGHT,
                FIRST_FAILURE,
                PRE_VERIFIER_RECEIPT,
                REVIEW,
            ],
            "tests": [FOCUSED_TEST, PLAN_TEST, CONTINUITY_TEST],
            "artifacts": [KERNEL, RUNNER, UPDATER],
        },
        "unresolved_gates": [
            "No ordinary-practice admission record is active and activation remains closed.",
            "Tenant-role, unknown-commit and environment posture evidence remains absent.",
            "No admission-control command or product route is mounted.",
            "The shared causal clock and DeepSeek broker gear remain shadow-only.",
            "No product data, provider, runtime, deployment or protected integration is authorized.",
        ],
    }


def main() -> int:
    source_resolution = resolve_commit_source(repo_root=ROOT, source_head=SOURCE_HEAD)
    source_head = source_resolution["resolved_commit"]
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 325 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node(source_head=source_head))
        graph["graph_revision"] = 326
    elif graph["graph_revision"] == 326 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node(source_head=source_head)
    else:
        raise SystemExit("Unexpected check-in admission kernel predecessor")
    graph["updated_at"] = UPDATED_AT

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove the default-off check-in admission evaluator without mounting it",
        "outcome": "Pure kernel accepted; ordinary admission remains impossible.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 307
        and compass["source_graph_revision"] == 325
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 308
        and compass["source_graph_revision"] == 326
        and compass["journey"][-1]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected check-in admission kernel Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Freeze the shadow Ariadne and DeepSeek broker clockwork gear",
        "why_now": (
            "The kernel at 4204ec6348abb0f92b1a30314699d4a469fa860a and its "
            "contained review failures expose exact typed clock requirements."
        ),
        "outcome": (
            "Specify one digest-linked causal tick/result protocol and measurable "
            "shadow efficacy boundary without live adoption or provider use."
        ),
        "unlocks": [
            "Derive full Git, stage, disposition, side-effect and attempt identity from one event.",
            "Bind DeepSeek WorkOrders and results to one exact Ariadne parent tick.",
            "Require atomic projections and exhaustive admitted-or-rejected receipts.",
            "Measure manual fields, reruns, maintained fixtures and escapes before adoption.",
        ],
        "does_not_solve": [
            "No current control is retired and no live clock is adopted.",
            "No occupied DeepSeek or other provider call is authorized.",
            "No product, patient, clinical, runtime, deployment or protected integration opens.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 326 / Compass 308. The provider-free unmounted "
        "default-off check-in admission kernel is accepted at exact source "
        "4204ec6348abb0f92b1a30314699d4a469fa860a with zero active ordinary "
        "records and zero ordinary releases. The next tranche freezes a shadow "
        "Ariadne/DeepSeek broker clockwork gear architecture."
    )
    compass["source_graph_revision"] = 326
    compass["map_revision"] = 308
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
