"""Advance Continuity and Compass for the first monitored EMR4 Harness worker."""

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
    "deepseek-native-harness-emr4-worker-profile-and-first-monitored-"
    "development-admission"
)
PARENT = (
    "deepseek-native-harness-authored-synthetic-agentic-coding-"
    "traceability-rehearsal"
)
SOURCE_HEAD = "af1a79f93024a7186849e550b4d529c8c601c93f"
UPDATED_AT = "2026-08-18T07:41:39.5012901Z"
PLAN = (
    "docs/deepseek-native-harness-emr4-worker-profile-and-first-monitored-"
    "development-admission-plan.md"
)
THREAT = (
    "docs/security/deepseek-native-harness-emr4-worker-profile-and-first-"
    "monitored-development-admission-threat-model-delta.md"
)
RECOVERY = (
    "docs/deepseek-native-harness-emr4-worker-profile-and-first-monitored-"
    "development-admission-enclosure-recovery.md"
)
PROFILE = (
    "orchestration/continuity/deepseek-native-harness-emr4-worker-profile-and-"
    "first-monitored-development-admission/profile-family.yaml"
)
SCHEMA = (
    "orchestration/continuity/deepseek-native-harness-emr4-worker-profile-and-"
    "first-monitored-development-admission/profile-family.schema.json"
)
MAPPING = (
    "orchestration/agent_inbox/codex/deepseek-native-harness-emr4-worker-"
    "profile-package-mapping-evidence.json"
)
PREFLIGHT = (
    "orchestration/agent_inbox/codex/deepseek-native-harness-emr4-worker-"
    "predispatch-evidence.json"
)
TERMINAL = (
    "orchestration/agent_inbox/codex/deepseek-native-harness-emr4-profile-"
    "validator-worker-terminal-evidence.json"
)
REGISTER = "docs/ariadne-agent-error-correction-register-revision-402.md"
CLOSEOUT = (
    "docs/deepseek-native-harness-emr4-worker-profile-and-first-monitored-"
    "development-admission-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/deepseek-native-harness-emr4-worker-"
    "profile-first-admission-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/2026-08-18--deepseek-native-harness-emr4-"
    "first-monitored-worker-admission.md"
)
UPDATER = (
    "scripts/deepseek_native_harness_emr4_worker_profile_first_admission_"
    "continuity_update.py"
)
TEST = (
    "tests/test_deepseek_native_harness_emr4_worker_profile_first_admission_"
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
        RECOVERY,
        PROFILE,
        SCHEMA,
        MAPPING,
        PREFLIGHT,
        TERMINAL,
        "scripts/ariadne_deepseek_native_harness_broker.mjs",
        "tests/test_ariadne_deepseek_native_harness_broker.py",
        REGISTER,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        UPDATER,
        TEST,
    ]


def _node() -> dict[str, Any]:
    inherited_contracts = [
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
            "note": "The accepted reconciliation contract remains unchanged; the worker candidate never started.",
        },
    ]
    return {
        "id": NODE_ID,
        "title": "DeepSeek native Harness EMR4 worker profile and first monitored development admission",
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
                "The result accepts attributable pre-provider negative worker evidence, not a worker candidate.",
                "A second monitored attempt requires a separately frozen exact-tool-view recovery and provider-free request-header proof.",
                "Product data, application behavior, live runtime, deployment and protected integration remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-broker-rejected-worker-terminal-without-candidate",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept the exact seven-tool broker rejection as useful fail-closed traceability evidence while rejecting the mapping claim and admitting no candidate or retry.",
            }
        ],
        "claim_scope": [
            "The isolated broker rejected the seven-tool declaration before provider I/O.",
            "The exact session had four frames, 17 rows, one request, zero provider calls, zero successful model steps, zero tool calls and no candidate change.",
            "The broker allowlist stayed at edit, glob and read; surplus schemas were not silently admitted.",
            "All disposable runtime and raw-session resources were cleaned and the single attempt was not retried.",
            "The result proves fail-closed control and attribution, not successful real-EMR4 worker completion or unrestricted default transport.",
        ],
        "contract_evidence": inherited_contracts,
        "evidence": {
            "plans": [
                PLAN,
                THREAT,
                RECOVERY,
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-plan.md",
            ],
            "findings": [
                MAPPING,
                PREFLIGHT,
                TERMINAL,
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
                "orchestration/agent_inbox/codex/deepseek-native-harness-emr4-profile-validator-worker-predispatch-corrected-receipt.json",
                "orchestration/agent_inbox/codex/deepseek-native-harness-emr4-profile-validator-terminal-evidence-precommit-corrected-receipt.json",
            ],
            "tests": [
                "tests/test_deepseek_native_harness_emr4_profile_contract.py",
                "tests/test_ariadne_deepseek_native_harness_broker.py",
                "tests/test_ariadne_agent_error_register.py",
                "tests/test_raisa_ordinary_diary_cancellation_canonical_consumer_convergence_composition.py",
                "review/test_ordinary_diary_cancellation_convergence.py",
                TEST,
            ],
            "artifacts": [PROFILE, SCHEMA, "scripts/ariadne_deepseek_native_harness_broker.mjs", UPDATER],
        },
        "unresolved_gates": [
            "An exact package-native scoped model tool view has not been demonstrated.",
            "A useful real-EMR4 native-Harness worker candidate remains unproved.",
            "The native Harness is not an unrestricted default worker transport.",
            "Product data, application runtime, deployment, release and protected integration remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 319 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 320
    elif graph["graph_revision"] == 320 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected first monitored Harness worker predecessor")
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove fail-closed native-Harness control on the first monitored EMR4 worker admission",
        "outcome": "The broker attributed and rejected an over-broad seven-tool request before provider I/O; no candidate was admitted.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 301
        and compass["source_graph_revision"] == 319
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 302
        and compass["source_graph_revision"] == 320
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected first monitored Harness worker Compass predecessor")
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Recover an exact native-Harness model tool view before one second monitored EMR4 worker attempt",
        "why_now": "The broker proved containment and the session trace identified four surplus model-facing schemas, so the narrow defect is package-native tool scoping rather than provider or model behavior.",
        "outcome": "Prove provider-free that the composed request exposes exactly read, glob and edit, then permit one fresh second monitored attempt over the same two-path package.",
        "unlocks": [
            "Identify and pin the rc.7 scoped-tool restriction that hides surplus model schemas.",
            "Add a provider-free composed-request admission gate comparing exact tool inventory with profile and broker allowlist.",
            "Run one fresh monitored worker only after that deterministic proof passes.",
        ],
        "does_not_solve": [
            "No useful real-EMR4 worker candidate has yet been produced by the native Harness.",
            "The native Harness is not an unrestricted default worker transport.",
            "No product/patient data, application behavior, runtime, deployment, Pages or protected integration is enabled.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 320 / Compass 302. The first monitored native-Harness "
        "EMR4 worker attempt failed closed before provider I/O because its composed "
        "request exposed seven tools against a three-tool broker allowlist; the next "
        "step is exact package-native tool-view recovery followed by at most one fresh "
        "second monitored attempt."
    )
    limit = (
        "The first monitored native-Harness EMR4 attempt is attributable pre-provider "
        "negative evidence only; no candidate, retry, default-transport promotion or "
        "broader product/runtime authority is accepted."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 320
    compass["map_revision"] = 302
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
