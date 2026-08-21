"""Run one provider-free rc.7 boot with one inert task and no runner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile as stdlib_tempfile
from typing import Any

import jsonschema


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import (  # noqa: E402
    deepseek_native_harness_provider_free_inert_task_sentinel_readiness_native_boot_engine
    as engine,
)


OPERATION_ID = (
    "deepseek-native-harness-provider-free-inert-task-sentinel-readiness-native-boot-proof"
)
ATTEMPT_ID = "inert-task-sentinel-readiness-native-boot-attempt-001"
TASK_ARGUMENT = "EMR4_PROVIDER_FREE_SENTINEL_READINESS_PROBE"
CONTINUITY_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = CONTINUITY_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = CONTINUITY_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = CONTINUITY_ROOT / "evidence.schema.json"
CONSUMED_PATH = CONTINUITY_ROOT / "native-attempt-consumed.json"
EVIDENCE_PATH = (
    CONTINUITY_ROOT
    / "provider-free-inert-task-sentinel-readiness-native-boot-terminal.json"
)
REPORT_PATH = (
    CONTINUITY_ROOT
    / "provider-free-inert-task-sentinel-readiness-native-boot-report.md"
)
CONTRACT_SCHEMA = (
    "ariadne.deepseek_native_harness_inert_task_sentinel_readiness_boot_contract.v1"
)
EVIDENCE_SCHEMA = (
    "ariadne.deepseek_native_harness_inert_task_sentinel_readiness_boot_evidence.v1"
)
DISPOSABLE_PREFIX = "dsh-inert-task-sentinel-readiness-"
_STDLIB_MKDTEMP = stdlib_tempfile.mkdtemp


def _load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = engine._load_json(path)
    jsonschema.validate(contract, engine._load_json(CONTRACT_SCHEMA_PATH))
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise engine.RepairedSentinelBootError("contract_schema_mismatch")
    if contract.get("operation_id") != OPERATION_ID:
        raise engine.RepairedSentinelBootError("contract_operation_mismatch")
    if contract.get("attempt") != {
        "attempt_id": ATTEMPT_ID,
        "native_process_limit": 1,
        "automatic_retry": False,
        "manual_retry": False,
        "resume": False,
        "fallback": False,
        "reclassification": False,
    }:
        raise engine.RepairedSentinelBootError("contract_attempt_latch_mismatch")
    if contract.get("profile") != {
        "profile": "headless",
        "changed": False,
        "sentinel_id": "synthetic-worker-hmr-sentinel",
        "sentinel_name": "../../../installation/proof/sentinel.mjs",
        "expected_events": engine.EXPECTED_EVENTS,
        "runner_row_count": 0,
        "runner_file_count": 0,
        "changed_profile_write_count": 0,
    }:
        raise engine.RepairedSentinelBootError("contract_initial_profile_mismatch")
    if contract.get("launch") != {
        "node_flag": "--expose-internals",
        "profile_flag": "--profile",
        "profile": "headless",
        "task_arguments": [TASK_ARGUMENT],
        "argument_count": 6,
        "timeout_seconds": 45,
        "termination_owner": "controller_after_readiness",
    }:
        raise engine.RepairedSentinelBootError("contract_launch_mismatch")
    return contract


def _fresh_mkdtemp(*, prefix: str, dir: Path) -> str:
    if prefix != "dsh-repaired-sentinel-boot-":
        raise engine.RepairedSentinelBootError("disposable_prefix_call_mismatch")
    return _STDLIB_MKDTEMP(prefix=DISPOSABLE_PREFIX, dir=dir)


class _FreshTempfileProxy:
    mkdtemp = staticmethod(_fresh_mkdtemp)


def _validate_lineage(contract: dict[str, Any]) -> dict[str, Any]:
    sources = [contract["planning_source"], *contract["accepted_sources"].values()]
    if any(not engine._git_commit_is_ancestor(source) for source in sources):
        raise engine.RepairedSentinelBootError("git_source_missing_or_not_ancestor")
    observed: list[dict[str, Any]] = []
    roles: set[str] = set()
    for row in contract["components"]:
        role = row["role"]
        path = REPO_ROOT / row["path"]
        if role in roles or not path.is_file() or path.is_symlink():
            raise engine.RepairedSentinelBootError("component_path_invalid:" + role)
        roles.add(role)
        digest = engine._file_sha256(path)
        if digest != row["sha256"]:
            raise engine.RepairedSentinelBootError("component_digest_mismatch:" + role)
        observed.append({"role": role, "sha256": digest})

    diagnosis = engine._load_json(
        REPO_ROOT
        / "orchestration/continuity/deepseek-native-harness-provider-free-post-sentinel-pre-stock-readiness-exit-coordinate-diagnosis/diagnosis-evidence.json"
    )
    prior_terminal = engine._load_json(
        REPO_ROOT
        / "orchestration/continuity/deepseek-native-harness-provider-free-source-repaired-sentinel-native-boot-proof/provider-free-source-repaired-sentinel-native-boot-terminal.json"
    )
    if (
        diagnosis.get("result") != "pass"
        or diagnosis.get("narrowest_supported_coordinate")
        != "headless_startup.apply.missing_task_program_error_to_app_exit_one"
        or diagnosis.get("terminal", {}).get("retry_count") != 0
        or any(diagnosis.get("zero_activity", {}).values())
    ):
        raise engine.RepairedSentinelBootError("accepted_diagnosis_mismatch")
    if (
        prior_terminal.get("result") != "failed_closed"
        or prior_terminal.get("hmr_events") != ["sentinel_activated"]
        or prior_terminal.get("launch", {}).get("task_argument_count") != 0
        or prior_terminal.get("launch", {}).get("retry_count") != 0
        or prior_terminal.get("cleanup", {}).get("process_absent") is not True
        or prior_terminal.get("cleanup", {}).get("disposable_root_absent") is not True
    ):
        raise engine.RepairedSentinelBootError("consumed_predecessor_terminal_mismatch")
    return {"sources": sources, "components": observed}


def _report(evidence: dict[str, Any]) -> str:
    outcome = (
        "The inert task was accepted and stock-headless HMR reached readiness."
        if evidence["result"] == "pass"
        else "The one-process inert-task boot failed closed before readiness."
    )
    return f"""# Provider-free inert-task sentinel-readiness native boot report

Date: 2026-08-21

Result: **{evidence['result']}**

- Attempt: `{evidence['attempt_id']}`
- Candidate: `{evidence['candidate_source']}`
- Native processes / retries: `{evidence['launch']['native_process_count']}` / `0`
- Command arguments / task arguments: `{evidence['launch']['argument_count']}` / `{evidence['launch']['task_argument_count']}`
- HMR events: `{', '.join(evidence['hmr_events'])}`
- Failure coordinate: `{evidence['failure_coordinate']}`
- Network / model / provider requests: `{evidence['provider_boundary']['network_attempts']}` / `0` / `0`
- Process absent: `{str(evidence['cleanup']['process_absent']).lower()}`
- Disposable root absent: `{str(evidence['cleanup']['disposable_root_absent']).lower()}`
- Raw streams retained: `false`

{outcome} This proves only pre-worker rc.7 Harness readiness with one inert
authored-synthetic task. It is not a runner, worker, model/provider,
product-runtime or reliability result.
"""


def configure_engine() -> None:
    engine.OPERATION_ID = OPERATION_ID
    engine.ATTEMPT_ID = ATTEMPT_ID
    engine.CONTINUITY_ROOT = CONTINUITY_ROOT
    engine.CONTRACT_PATH = CONTRACT_PATH
    engine.CONTRACT_SCHEMA_PATH = CONTRACT_SCHEMA_PATH
    engine.EVIDENCE_SCHEMA_PATH = EVIDENCE_SCHEMA_PATH
    engine.CONSUMED_PATH = CONSUMED_PATH
    engine.EVIDENCE_PATH = EVIDENCE_PATH
    engine.REPORT_PATH = REPORT_PATH
    engine.CONTRACT_SCHEMA = CONTRACT_SCHEMA
    engine.EVIDENCE_SCHEMA = EVIDENCE_SCHEMA
    engine.load_contract = _load_contract
    engine.tempfile = _FreshTempfileProxy
    engine.validate_lineage = _validate_lineage
    engine._render_report = _report


def deterministic_check(candidate_source: str | None = None) -> dict[str, Any]:
    configure_engine()
    projection = engine.deterministic_check(candidate_source)
    expected = [
        "node.exe",
        "--expose-internals",
        "C:/deterministic/installation/node_modules/@deepseek-ai/dsh/lib/bin.js",
        "--profile",
        "headless",
        TASK_ARGUMENT,
    ]
    normalized = [value.replace("\\", "/") for value in projection["command"]]
    if normalized != expected:
        raise engine.RepairedSentinelBootError("inert_task_launch_command_mismatch")
    if engine.tempfile.mkdtemp is not _fresh_mkdtemp:
        raise engine.RepairedSentinelBootError("disposable_prefix_binding_missing")
    projection["disposable_root_prefix"] = DISPOSABLE_PREFIX
    projection["task_argument_count"] = 1
    return projection


def execute_boot(candidate_source: str) -> dict[str, Any]:
    configure_engine()
    return engine.execute_boot(candidate_source)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--execute", action="store_true")
    parser.add_argument("--candidate-source")
    args = parser.parse_args()
    try:
        if args.check:
            projection = deterministic_check(args.candidate_source)
            output = {
                "status": "passed",
                "attempt_id": ATTEMPT_ID,
                "profile_sha256": projection["profile"]["sha256"],
                "native_processes": 0,
                "task_arguments": projection["task_argument_count"],
            }
        else:
            if args.candidate_source is None:
                raise engine.RepairedSentinelBootError("candidate_source_required")
            evidence = execute_boot(args.candidate_source)
            output = {
                "status": evidence["result"],
                "attempt_id": ATTEMPT_ID,
                "hmr_events": evidence["hmr_events"],
                "cleanup": evidence["cleanup"],
            }
        print(json.dumps(output, sort_keys=True))
    except (
        engine.RepairedSentinelBootError,
        engine.materializer.PresetMountProjectionError,
        engine.ProofError,
        jsonschema.ValidationError,
    ) as error:
        print(json.dumps({"status": "revision_required", "reason": str(error)}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
