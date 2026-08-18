"""Advance Continuity and Compass for the exact-tool-view second admission."""

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
NODE_ID = (
    "deepseek-native-harness-exact-tool-view-recovery-and-second-monitored-"
    "development-admission"
)
PARENT = (
    "deepseek-native-harness-emr4-worker-profile-and-first-monitored-"
    "development-admission"
)
SOURCE_HEAD = "00d4f8d6065ab09b5faf5501c979edd2fa59943c"
UPDATED_AT = "2026-08-18T10:37:23.2818490Z"
PLAN = (
    "docs/deepseek-native-harness-exact-tool-view-recovery-and-second-"
    "monitored-development-admission-plan.md"
)
THREAT = (
    "docs/security/deepseek-native-harness-exact-tool-view-recovery-and-"
    "second-monitored-development-admission-threat-model-delta.md"
)
PROOF = (
    "orchestration/agent_inbox/codex/deepseek-native-harness-exact-tool-view-"
    "provider-free-composed-request-evidence.json"
)
NEGATIVE = (
    "orchestration/agent_inbox/codex/deepseek-native-harness-exact-tool-view-"
    "second-monitored-development-occupied-negative-evidence.json"
)
REGISTER = "docs/ariadne-agent-error-correction-register-revision-445.md"
CLOSEOUT = (
    "docs/deepseek-native-harness-exact-tool-view-recovery-and-second-"
    "monitored-development-admission-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/deepseek-native-harness-exact-tool-view-"
    "second-monitored-development-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/2026-08-18--deepseek-native-harness-"
    "exact-tool-view-second-monitored-development.md"
)
UPDATER = (
    "scripts/deepseek_native_harness_exact_tool_view_second_admission_"
    "continuity_update.py"
)
TEST = (
    "tests/test_deepseek_native_harness_exact_tool_view_second_admission_"
    "continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        PROOF,
        NEGATIVE,
        "orchestration/continuity/deepseek-native-harness-emr4-worker-profile-and-first-monitored-development-admission/profile-family.yaml",
        "orchestration/continuity/deepseek-native-harness-emr4-worker-profile-and-first-monitored-development-admission/profile-family.schema.json",
        "scripts/ariadne_deepseek_native_harness_broker.mjs",
        "tests/test_deepseek_native_harness_emr4_profile_contract.py",
        "tests/test_ariadne_deepseek_native_harness_broker.py",
        REGISTER,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        UPDATER,
        TEST,
    ]


def _contract_evidence() -> list[dict[str, Any]]:
    return [
        {
            "contract_id": "combined-patient-practitioner-time-duration-intent",
            "status": "satisfied",
            "evidence": [
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-plan.md",
                "orchestration/continuity/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition/ordinary-diary-cancellation-canonical-consumer-convergence-composition-evidence.json",
                "tests/test_raisa_ordinary_diary_cancellation_canonical_consumer_convergence_composition.py",
            ],
            "note": "The accepted product intent remains inherited; no product source or data entered this Harness tranche.",
        },
        {
            "contract_id": "committed-reschedule-availability-reconciliation",
            "status": "satisfied",
            "evidence": [
                "orchestration/continuity/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition/ordinary-diary-cancellation-canonical-consumer-convergence-composition-evidence.json",
                "review/test_ordinary_diary_cancellation_convergence.py",
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-closeout.md",
            ],
            "note": "The accepted reconciliation contract remains unchanged; no product source or projection entered the Harness tranche.",
        },
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "DeepSeek native Harness exact-tool-view recovery and second monitored development admission",
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
        "relationships": [{"node_id": PARENT, "relation": "builds_on"}],
        "authority": {
            "authorized_openings": [],
            "notes": [
                "The provider-free exact three-tool view is accepted.",
                "The occupied HMR startup terminal is accepted as negative evidence; no candidate, retry or resume is admitted.",
                "Future occupied native-Harness work requires a separate provider-free stock-headless-to-custom-runner startup proof.",
                "Product data, application runtime, deployment and protected integration remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-exact-tool-view-and-contained-hmr-startup-terminal",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept exact provider-free edit/glob/read composition and the attributable pre-provider HMR startup failure while admitting no worker candidate or retry.",
            }
        ],
        "claim_scope": [
            "The pinned rc.7 package-native preset mount and tools.restrict mechanism removed every unselected model schema.",
            "A provider-free request declared exactly edit, glob and read with zero external/provider calls.",
            "The occupied worker failed before its custom runner or provider boundary because stock headless HMR requires Node --expose-internals.",
            "The broker observed zero requests/provider calls/responses and the candidate changed zero paths.",
            "All disposable resources are absent and the attempt was not retried or resumed.",
        ],
        "contract_evidence": _contract_evidence(),
        "evidence": {
            "plans": [
                PLAN,
                THREAT,
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-plan.md",
            ],
            "findings": [
                PROOF,
                NEGATIVE,
                REGISTER,
                "orchestration/continuity/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition/ordinary-diary-cancellation-canonical-consumer-convergence-composition-evidence.json",
            ],
            "closeouts": [
                CLOSEOUT,
                MAILBOX,
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-closeout.md",
            ],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                "orchestration/agent_inbox/codex/deepseek-native-harness-exact-tool-view-second-monitored-development-register-426-corrected-predispatch-receipt.json"
            ],
            "tests": [
                "tests/test_deepseek_native_harness_emr4_profile_contract.py",
                "tests/test_ariadne_deepseek_native_harness_broker.py",
                "tests/test_ariadne_agent_error_register.py",
                "tests/test_raisa_ordinary_diary_cancellation_canonical_consumer_convergence_composition.py",
                "review/test_ordinary_diary_cancellation_convergence.py",
                TEST,
            ],
            "artifacts": [
                "orchestration/continuity/deepseek-native-harness-emr4-worker-profile-and-first-monitored-development-admission/profile-family.yaml",
                "orchestration/continuity/deepseek-native-harness-emr4-worker-profile-and-first-monitored-development-admission/profile-family.schema.json",
                "scripts/ariadne_deepseek_native_harness_broker.mjs",
                UPDATER,
            ],
        },
        "unresolved_gates": [
            "A provider-free stock-headless-to-custom-runner HMR startup proof is required before any future occupied native-Harness worker.",
            "A useful real-EMR4 native-Harness candidate remains unproved.",
            "The native Harness is not an unrestricted default worker transport.",
            "Product data, application runtime, deployment, release and protected integration remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 320 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 321
    elif graph["graph_revision"] == 321 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected exact-tool-view second admission predecessor")
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove the exact native-Harness tool view and attribute the second monitored EMR4 admission",
        "outcome": "Provider-free exact edit/glob/read composition passed; the occupied worker then failed deterministically before provider I/O at the stock headless HMR startup prerequisite.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 302
        and compass["source_graph_revision"] == 320
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 303
        and compass["source_graph_revision"] == 321
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected exact-tool-view second admission Compass predecessor")
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Review ordinary-practice canonical check-in admission readiness without enabling it",
        "why_now": "The additive Harness trial is closed with exact traceability evidence, and the default-off check-in route convergence already passed at c82c3a741053a9c8da260aa62e1a968af22bb54e; repeating that accepted tranche would be invalid.",
        "outcome": "Inventory the current default-off and empty-allowlist posture plus API Spine command, authorization, tenant, idempotency, audit, rollback, rollout and observability prerequisites without changing product source, configuration, route behavior or data.",
        "unlocks": [
            "Freeze a bounded evidence-backed readiness inventory for a later explicit ordinary-practice admission gate.",
            "Identify every unmet prerequisite and preserve default denial until a separately authorised implementation tranche.",
            "Reassess DeepSeek, Gemini and native-subagent lanes only when a future candidate has an independently owned work package.",
        ],
        "does_not_solve": [
            "The native Harness has not produced a useful real-EMR4 candidate and is not a default transport.",
            "No practice is enabled and no product code, configuration, route behavior or product data is changed.",
            "No generic-status Arrived transition, grammar/client change or waiting-area movement is admitted.",
            "No product/patient data, live provider, production runtime, deployment, Pages or protected integration is enabled.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 321 / Compass 303. The native Harness now has an "
        "exact provider-free edit/glob/read proof and an attributable pre-provider "
        "HMR startup terminal with no candidate. Default-off route convergence already "
        "passed at c82c3a741053a9c8da260aa62e1a968af22bb54e; next is the provider-free "
        "read-only ordinary-practice canonical check-in admission-readiness review."
    )
    limit = (
        "The second native-Harness admission proves exact provider-free tool scoping "
        "and traceable HMR startup failure only; it admits no candidate, retry, "
        "default-transport promotion or broader product/runtime authority."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 321
    compass["map_revision"] = 303
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
