"""Advance Continuity and Compass for the shadow clockwork gear architecture."""

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
NODE_ID = "ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-architecture"
PARENT = (
    "raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-"
    "check-in-admission-control-kernel-rehearsal"
)
SOURCE_HEAD = "f6cbd33fd3322754e06ac6dafa1503f5200e0803"
UPDATED_AT = "2026-08-18T20:08:13.6850292Z"
BASE = (
    "orchestration/continuity/ariadne-provider-free-shadow-clockwork-deepseek-"
    "broker-gear-architecture/"
)
PLAN = "docs/ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-architecture-plan.md"
ARCHITECTURE = "docs/ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-architecture.md"
THREAT = (
    "docs/security/ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-"
    "architecture-threat-model-delta.md"
)
CONTRACT = BASE + "contract.json"
SCHEMA = BASE + "contract.schema.json"
EVIDENCE = BASE + "provider-free-architecture-evidence.json"
REPORT_ARTIFACT = BASE + "architecture-report.md"
RUNNER = (
    "scripts/ariadne_provider_free_shadow_clockwork_deepseek_broker_gear_"
    "architecture.py"
)
FOCUSED_TEST = (
    "tests/test_ariadne_provider_free_shadow_clockwork_deepseek_broker_gear_"
    "architecture.py"
)
PLAN_TEST = FOCUSED_TEST.removesuffix(".py") + "_plan.py"
TRANSACTIONAL_TEST = "tests/test_ariadne_transactional_closeout.py"
REGISTER_TEST = "tests/test_ariadne_agent_error_register.py"
PREPLAN_STATE = (
    "orchestration/agent_inbox/codex/ariadne-shadow-clockwork-deepseek-broker-"
    "gear-architecture-preplanning-runtime-state.json"
)
PREPLAN_RECEIPT = PREPLAN_STATE.replace("runtime-state", "receipt")
MANIFEST = (
    "orchestration/agent_inbox/codex/ariadne-clockwork-broker-gear-gemini37-"
    "command-manifest.json"
)
REVIEW_PACKET = MANIFEST.replace("command-manifest.json", "review-packet.md")
PREFLIGHT = MANIFEST.replace("command-manifest.json", "review-worktree-preflight.json")
PRE_VERIFIER_STATE = (
    "orchestration/agent_inbox/codex/ariadne-clockwork-broker-gear-pre-verifier-"
    "acceptance-runtime-state.json"
)
PRE_VERIFIER_RECEIPT = PRE_VERIFIER_STATE.replace("runtime-state", "receipt")
REVIEW = (
    "orchestration/agent_inbox/antigravity/ariadne-clockwork-broker-gear-"
    "gemini37-review-receipt.json"
)
REGISTER = "docs/ariadne-agent-error-correction-register-revision-531.md"
CLOSEOUT = (
    "docs/ariadne-provider-free-shadow-clockwork-deepseek-broker-gear-"
    "architecture-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/ariadne-shadow-clockwork-deepseek-broker-"
    "gear-architecture-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/2026-08-19--shadow-clockwork-deepseek-"
    "broker-gear-architecture.md"
)
UPDATER = (
    "scripts/ariadne_provider_free_shadow_clockwork_deepseek_broker_gear_"
    "architecture_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_ariadne_provider_free_shadow_clockwork_deepseek_broker_gear_"
    "architecture_continuity.py"
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
        RUNNER,
        FOCUSED_TEST,
        PLAN_TEST,
        TRANSACTIONAL_TEST,
        REGISTER_TEST,
        PREPLAN_STATE,
        PREPLAN_RECEIPT,
        MANIFEST,
        REVIEW_PACKET,
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
        "title": "Ariadne provider-free shadow clockwork and DeepSeek broker gear architecture",
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
                "Ariadne remains the sole source of causal bureaucratic time.",
                "A digest-bound WorkOrder transfers one sequence lease to the DeepSeek broker and exact terminal acknowledgement returns it.",
                "The result is architecture-only; no live control is replaced and no occupied Harness starts.",
            ],
        },
        "decisions": [
            {
                "id": "accept-shadow-clockwork-deepseek-broker-gear-architecture",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept the provider-free single-writer causal architecture without live adoption.",
            }
        ],
        "claim_scope": [
            "All ten canonical-LF predecessor bindings match.",
            "All 48 named architecture scenarios pass.",
            "All 256 hostile contract mutations and ten hostile gear traces fail closed with zero escapes.",
            "Caller-supplied binding fields are zero; fifteen field groups are engine-owned.",
            "The Gemini 3.7 Flash/high veto passes ten commands at unchanged clean reviewed HEAD.",
            "No efficacy reduction is claimed from architecture alone; fourteen conventional verification reruns are retained as baseline evidence.",
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
                REVIEW_PACKET,
                PREFLIGHT,
                PRE_VERIFIER_STATE,
                PRE_VERIFIER_RECEIPT,
                REVIEW,
            ],
            "tests": [FOCUSED_TEST, PLAN_TEST, TRANSACTIONAL_TEST, REGISTER_TEST, CONTINUITY_TEST],
            "artifacts": [RUNNER, UPDATER],
        },
        "unresolved_gates": [
            "Live clock adoption and retirement of any current control remain separately closed.",
            "The provider-free shadow gear rehearsal must prove measured efficacy before an adoption plan is considered.",
            "Occupied DeepSeek work remains behind the separate native-Harness HMR boot proof.",
            "No product, practice, provider, Git, runtime, deployment or protected integration authority is opened.",
        ],
    }


def main() -> int:
    source_resolution = resolve_commit_source(repo_root=ROOT, source_head=SOURCE_HEAD)
    source_head = source_resolution["resolved_commit"]
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 326 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node(source_head=source_head))
        graph["graph_revision"] = 327
    elif graph["graph_revision"] == 327 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node(source_head=source_head)
    else:
        raise SystemExit("Unexpected shadow clockwork architecture predecessor")
    graph["updated_at"] = UPDATED_AT

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Freeze one causal clock and single-writer broker gear before implementation",
        "outcome": "Architecture accepted; live controls and occupied Harness remain closed.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 308
        and compass["source_graph_revision"] == 326
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 309
        and compass["source_graph_revision"] == 327
        and compass["journey"][-1]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected shadow clockwork architecture Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Rehearse the provider-free shadow clockwork and DeepSeek broker gear",
        "why_now": (
            "The accepted architecture at f6cbd33fd3322754e06ac6dafa1503f5200e0803 "
            "defines one causal lease and freezes an honest fourteen-rerun conventional baseline."
        ),
        "outcome": (
            "Implement only a private shadow request, lease, terminal-result and acknowledgement "
            "engine and compare four efficacy readings against frozen fixtures."
        ),
        "unlocks": [
            "Derive zero caller binding fields from one validated reading.",
            "Measure failure-induced reruns against the frozen conventional baseline.",
            "Prove no new mutable-current fixture, partial publication or uncaught escape.",
            "Report shared-engine growth and clean-run overhead before any adoption proposal.",
        ],
        "does_not_solve": [
            "No live control is replaced and no canonical projection adopts the clock.",
            "No native Harness starts and no DeepSeek or other provider call occurs.",
            "No product, practice, data, Git, runtime, deployment or protected integration opens.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 327 / Compass 309. The provider-free shadow "
        "Ariadne/DeepSeek broker gear architecture is accepted at exact source "
        "f6cbd33fd3322754e06ac6dafa1503f5200e0803 with one causal lease, zero "
        "caller binding fields and no live adoption. The next tranche is a "
        "provider-free private-shadow efficacy rehearsal."
    )
    compass["source_graph_revision"] = 327
    compass["map_revision"] = 309
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
