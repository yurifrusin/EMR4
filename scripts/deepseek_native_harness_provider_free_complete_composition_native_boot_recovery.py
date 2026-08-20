"""Run one provider-free complete-composition native Harness recovery boot."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Iterator

import jsonschema
import yaml

import scripts.deepseek_native_harness_provider_free_preterminal_observable_composition_recovery_boot as base
from scripts.deepseek_native_harness_provider_free_effective_tool_composition_guard import (
    build_guard_source,
    validate_guard_source,
)
from scripts.deepseek_native_harness_provider_free_effective_tool_composition_native_boot_proof import (
    sentinel_source,
)
from scripts.deepseek_native_harness_provider_free_emr4_bounded_worker_preset_materialisation_recovery import (
    PRESET_BYTES,
    PRESET_ID,
    PRESET_RELATIVE_PATH,
    validate_preset_bytes,
)
from scripts.deepseek_native_harness_provider_free_required_service_injection_recovery import (
    REQUIRED_SERVICES,
    future_runner_source,
    validate_future_runner,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-complete-composition-native-boot-recovery"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "provider-free-complete-composition-native-boot-evidence.json"
REPORT_PATH = OPERATION_ROOT / "provider-free-complete-composition-native-boot-report.md"
EVIDENCE_SCHEMA = (
    "ariadne.deepseek_native_harness_provider_free_complete_composition_native_"
    "boot_recovery_evidence.v1"
)
CONTRACT_SCHEMA = (
    "ariadne.deepseek_native_harness_provider_free_complete_composition_native_"
    "boot_recovery_contract.v1"
)
ATTEMPT_ID = "complete-composition-native-boot-recovery-attempt-001"
HEX_40 = re.compile(r"^[0-9a-f]{40}$")

PLAN_PATH = (
    REPO_ROOT
    / "docs"
    / "deepseek-native-harness-provider-free-complete-composition-native-boot-recovery-plan.md"
)
FOCUSED_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_provider_free_complete_composition_native_boot_recovery.py"
)
REQUIRED_SERVICE_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-required-service-injection-recovery"
)
PRESET_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-emr4-bounded-worker-preset-materialisation-recovery"
)
GUARD_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-effective-tool-composition-and-terminal-coordinate-guard"
)
PRETERMINAL_BOOT_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-preterminal-observable-composition-recovery-boot"
)
FIRST_NATIVE_BOOT_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-effective-tool-composition-native-boot-proof"
)
OBSERVABILITY_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-preterminal-activation-observability-recovery"
)
HMR_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-stock-headless-to-custom-runner-hmr-boot-proof"
)
MATERIALISED_PRESET_PATH = (
    PRESET_ROOT / "materialised-home" / Path(PRESET_RELATIVE_PATH)
)

PREDECESSOR_FILES = {
    "frozen_plan_sha256": PLAN_PATH,
    "base_execution_controller_sha256": Path(base.__file__).resolve(),
    "required_service_controller_sha256": REPO_ROOT
    / "scripts"
    / "deepseek_native_harness_provider_free_required_service_injection_recovery.py",
    "required_service_contract_sha256": REQUIRED_SERVICE_ROOT / "contract.json",
    "required_service_evidence_sha256": REQUIRED_SERVICE_ROOT
    / "provider-free-required-service-injection-evidence.json",
    "preset_controller_sha256": REPO_ROOT
    / "scripts"
    / "deepseek_native_harness_provider_free_emr4_bounded_worker_preset_materialisation_recovery.py",
    "preset_contract_sha256": PRESET_ROOT / "contract.json",
    "preset_evidence_sha256": PRESET_ROOT
    / "provider-free-emr4-bounded-worker-preset-evidence.json",
    "materialised_preset_sha256": MATERIALISED_PRESET_PATH,
    "guard_controller_sha256": REPO_ROOT
    / "scripts"
    / "deepseek_native_harness_provider_free_effective_tool_composition_guard.py",
    "guard_contract_sha256": GUARD_ROOT / "contract.json",
    "guard_evidence_sha256": GUARD_ROOT / "provider-free-effective-tool-guard-evidence.json",
    "observability_controller_sha256": REPO_ROOT
    / "scripts"
    / "deepseek_native_harness_provider_free_preterminal_observability_recovery.py",
    "observability_contract_sha256": OBSERVABILITY_ROOT / "contract.json",
    "observability_evidence_sha256": OBSERVABILITY_ROOT
    / "provider-free-preterminal-observability-recovery-evidence.json",
    "preterminal_boot_controller_sha256": Path(base.__file__).resolve(),
    "preterminal_boot_contract_sha256": PRETERMINAL_BOOT_ROOT / "contract.json",
    "preterminal_boot_evidence_sha256": PRETERMINAL_BOOT_ROOT
    / "provider-free-preterminal-observable-native-boot-evidence.json",
    "first_native_boot_controller_sha256": REPO_ROOT
    / "scripts"
    / "deepseek_native_harness_provider_free_effective_tool_composition_native_boot_proof.py",
    "first_native_boot_contract_sha256": FIRST_NATIVE_BOOT_ROOT / "contract.json",
    "first_native_boot_evidence_sha256": FIRST_NATIVE_BOOT_ROOT
    / "provider-free-effective-tool-native-boot-evidence.json",
    "hmr_boot_controller_sha256": REPO_ROOT
    / "scripts"
    / "deepseek_native_harness_provider_free_hmr_boot_proof.py",
    "hmr_boot_contract_sha256": HMR_ROOT / "contract.json",
}
IMPLEMENTATION_FILES = {
    "controller_sha256": Path(__file__).resolve(),
    "focused_test_sha256": FOCUSED_TEST_PATH,
}


class CompleteCompositionError(RuntimeError):
    """A closed complete-composition admission rejection."""


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(CONTRACT_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(contract, schema)
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise CompleteCompositionError("contract_schema_mismatch")
    if contract.get("operation_id") != OPERATION_ID:
        raise CompleteCompositionError("contract_operation_mismatch")
    attempt = contract.get("attempt", {})
    if (
        attempt.get("attempt_id") != ATTEMPT_ID
        or attempt.get("native_process_count") != 1
        or attempt.get("automatic_retry") is not False
        or attempt.get("manual_retry") is not False
        or attempt.get("resume") is not False
    ):
        raise CompleteCompositionError("contract_one_process_latch_mismatch")
    if contract.get("required_services") != list(REQUIRED_SERVICES):
        raise CompleteCompositionError("contract_required_services_mismatch")
    preset = contract.get("preset", {})
    if (
        preset.get("id") != PRESET_ID
        or preset.get("install_relative_path") != PRESET_RELATIVE_PATH
        or preset.get("selected_tools") != ["edit", "glob", "read"]
    ):
        raise CompleteCompositionError("contract_preset_mismatch")
    return contract


def _git_object_is_ancestor(object_id: str) -> bool:
    if HEX_40.fullmatch(object_id) is None:
        return False
    exists = subprocess.run(
        ["git", "cat-file", "-e", f"{object_id}^{{commit}}"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    relation = subprocess.run(
        ["git", "merge-base", "--is-ancestor", object_id, "HEAD"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return exists.returncode == 0 and relation.returncode == 0


def _exact_preset(contract: dict[str, Any]) -> bytes:
    projection = validate_preset_bytes(PRESET_BYTES)
    if (
        projection["sha256"] != contract["preset"]["sha256"]
        or MATERIALISED_PRESET_PATH.read_bytes() != PRESET_BYTES
    ):
        raise CompleteCompositionError("accepted_preset_bytes_mismatch")
    return PRESET_BYTES


def validate_predecessors(contract: dict[str, Any]) -> dict[str, Any]:
    sources = {
        "planning_source": contract["planning_source"],
        "frozen_plan_source": contract["frozen_plan_source"],
        **contract["accepted_sources"],
    }
    if any(not _git_object_is_ancestor(value) for value in sources.values()):
        raise CompleteCompositionError("accepted_git_source_missing_or_not_ancestor")
    actual = {
        field: base.sha256_file(path) for field, path in PREDECESSOR_FILES.items()
    }
    if actual != contract["predecessor_bytes"]:
        raise CompleteCompositionError("predecessor_digest_mismatch")
    implementation = {
        field: base.sha256_file(path) for field, path in IMPLEMENTATION_FILES.items()
    }
    if implementation != contract["implementation_bytes"]:
        raise CompleteCompositionError("implementation_digest_mismatch")

    failed = json.loads(
        (PRETERMINAL_BOOT_ROOT / "provider-free-preterminal-observable-native-boot-evidence.json").read_text(
            encoding="utf-8"
        )
    )
    expected_failed = contract["immutable_predecessor_attempt"]
    if (
        failed.get("attempt_id") != expected_failed["attempt_id"]
        or failed.get("result") != "fail"
        or failed.get("failure_classification") != "SERVICES_UNAVAILABLE"
    ):
        raise CompleteCompositionError("immutable_failed_attempt_shape_mismatch")
    first_failed = json.loads(
        (FIRST_NATIVE_BOOT_ROOT / "provider-free-effective-tool-native-boot-evidence.json").read_text(
            encoding="utf-8"
        )
    )
    if (
        first_failed.get("attempt_id") != "native-composition-attempt-001"
        or first_failed.get("result") != "fail"
    ):
        raise CompleteCompositionError("first_immutable_failed_attempt_shape_mismatch")

    service_evidence = json.loads(
        (REQUIRED_SERVICE_ROOT / "provider-free-required-service-injection-evidence.json").read_text(
            encoding="utf-8"
        )
    )
    preset_evidence = json.loads(
        (PRESET_ROOT / "provider-free-emr4-bounded-worker-preset-evidence.json").read_text(
            encoding="utf-8"
        )
    )
    if (
        service_evidence.get("result") != "pass"
        or service_evidence.get("future_declaration", {}).get("required_services")
        != list(REQUIRED_SERVICES)
        or preset_evidence.get("result") != "pass"
        or preset_evidence.get("materialised_preset", {}).get("sha256")
        != contract["preset"]["sha256"]
    ):
        raise CompleteCompositionError("accepted_composition_evidence_mismatch")

    runner = validate_future_runner(future_runner_source())
    guard = validate_guard_source(build_guard_source())
    preset = validate_preset_bytes(PRESET_BYTES)
    sentinel = sentinel_source()
    generated = {
        "future_runner_sha256": base.sha256_bytes(future_runner_source()),
        "effective_tool_guard_sha256": base.sha256_bytes(build_guard_source()),
        "readiness_sentinel_sha256": base.sha256_bytes(sentinel),
        "materialised_preset_sha256": base.sha256_bytes(PRESET_BYTES),
    }
    if generated != contract["generated_bytes"]:
        raise CompleteCompositionError("generated_digest_mismatch")
    return {
        "accepted_sources": contract["accepted_sources"],
        "predecessor_sha256": actual,
        "generated_sha256": generated,
        "implementation_sha256": implementation,
        "required_services": list(REQUIRED_SERVICES),
        "service_dependency_gate": "cordis_inactive_until_all_declared_services_active",
        "future_runner": runner,
        "effective_tool_guard": guard,
        "materialised_preset": preset,
        "immutable_predecessor_unchanged": True,
    }


def _yaml_path(path: Path) -> str:
    return json.dumps(str(path.resolve()))


def build_patch_pair(
    profile_dir: Path,
    readiness_path: Path,
    activation_path: Path,
    terminal_path: Path,
    sentinel_path: Path,
    runner_path: Path,
) -> tuple[bytes, bytes]:
    profile_patch = profile_dir / "cordis.patch.yml"
    home_patch = profile_dir.parents[1] / "cordis.patch.yml"
    expected_modules = profile_dir.parents[2] / "installation" / "proof"
    if (
        sentinel_path != expected_modules / "sentinel.mjs"
        or runner_path != expected_modules / "runner.mjs"
    ):
        raise base.RecoveryBootError("proof_module_location_mismatch")
    common = f"""- id: headless-runner
  disabled: true
- id: code-runtime
  disabled: true
- id: session-telemetry-otel
  disabled: true
- insert:
    - id: provider-free-effective-tool-hmr-sentinel
      name: ../../../installation/proof/sentinel.mjs
      config:
        eventPath: {_yaml_path(readiness_path)}
        watchedPaths:
          - {_yaml_path(profile_patch)}
          - {_yaml_path(home_patch)}
"""
    changed = (
        common
        + f"""    - id: agent-presets
      name: '@deepseek-ai/dsh-agent-presets'
      config:
        default: standard
    - id: provider-free-complete-composition-runner
      name: ../../../installation/proof/runner.mjs
      inject: [hmr, agentPresets, tools]
      config:
        activationPath: {_yaml_path(activation_path)}
        terminalPath: {_yaml_path(terminal_path)}
        watchedPaths:
          - {_yaml_path(profile_patch)}
          - {_yaml_path(home_patch)}
"""
    )
    initial, changed_bytes = common.encode(), changed.encode()
    validate_patch_pair(initial, changed_bytes)
    return initial, changed_bytes


def _patch_rows(payload: bytes) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = yaml.safe_load(payload)
    if not isinstance(rows, list):
        raise base.RecoveryBootError("patch_not_array")
    direct: list[dict[str, Any]] = []
    inserted: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise base.RecoveryBootError("patch_row_invalid")
        if "insert" in row:
            if set(row) != {"insert"} or not isinstance(row["insert"], list):
                raise base.RecoveryBootError("patch_insert_invalid")
            inserted.extend(row["insert"])
        else:
            direct.append(row)
    return direct, inserted


def validate_patch_pair(initial: bytes, changed: bytes) -> None:
    initial_direct, initial_inserted = _patch_rows(initial)
    changed_direct, changed_inserted = _patch_rows(changed)
    expected_direct = [
        {"id": "headless-runner", "disabled": True},
        {"id": "code-runtime", "disabled": True},
        {"id": "session-telemetry-otel", "disabled": True},
    ]
    if initial_direct != expected_direct or changed_direct != expected_direct:
        raise base.RecoveryBootError("patch_disabled_rows_mismatch")
    if [row.get("id") for row in initial_inserted] != [
        "provider-free-effective-tool-hmr-sentinel"
    ]:
        raise base.RecoveryBootError("initial_patch_composition_present")
    if [row.get("id") for row in changed_inserted] != [
        "provider-free-effective-tool-hmr-sentinel",
        "agent-presets",
        "provider-free-complete-composition-runner",
    ]:
        raise base.RecoveryBootError("changed_patch_rows_mismatch")
    if changed_inserted[:1] != initial_inserted:
        raise base.RecoveryBootError("changed_patch_mutates_initial")
    if changed_inserted[1] != {
        "id": "agent-presets",
        "name": "@deepseek-ai/dsh-agent-presets",
        "config": {"default": "standard"},
    }:
        raise base.RecoveryBootError("agent_presets_row_mismatch")
    runner = changed_inserted[2]
    if runner.get("inject") != list(REQUIRED_SERVICES):
        raise base.RecoveryBootError("runner_injection_mismatch")
    if runner.get("name") != "../../../installation/proof/runner.mjs":
        raise base.RecoveryBootError("runner_path_mismatch")
    sentinel_config = initial_inserted[0].get("config", {})
    runner_config = runner.get("config", {})
    if "eventPath" not in sentinel_config or "activationPath" in sentinel_config:
        raise base.RecoveryBootError("readiness_writer_config_mismatch")
    if "activationPath" not in runner_config or "eventPath" in runner_config:
        raise base.RecoveryBootError("activation_writer_config_mismatch")


def render_report(evidence: dict[str, Any]) -> str:
    terminal = evidence.get("terminal") or {}
    return f"""# Provider-free complete-composition native-boot recovery report

Date: 2026-08-20

Result: **{evidence['result']}**

- Attempt: `{evidence['attempt_id']}`
- Failure classification: `{evidence['failure_classification']}`
- Readiness: `{', '.join(evidence['readiness']['events'])}`
- Required services: `hmr, agentPresets, tools`
- Activation: `{', '.join(evidence['activation']['coordinates'])}`
- Terminal: `{terminal.get('code')}`
- Effective tools: `{', '.join(terminal.get('effective_tool_names', []))}`
- Native process / retry count: `{evidence['launch']['native_process_count']} / {evidence['launch']['retry_count']}`
- Network / agent-session / broker / model / provider counts: `0 / 0 / 0 / 0 / 0`
- Exit code / duration: `{evidence['launch']['exit_code']} / {evidence['launch']['duration_ms']} ms`
- Process absent: `{str(evidence['cleanup']['process_absent']).lower()}`
- Disposable root absent: `{str(evidence['cleanup']['disposable_root_absent']).lower()}`

This proves only one pinned local rc.7 provider-free pre-provider composition
path. It is not an occupied DeepSeek worker, model/provider call or product
runtime result.
"""


_PATCHED_NAMES = (
    "OPERATION_ID",
    "OPERATION_ROOT",
    "CONTRACT_PATH",
    "CONTRACT_SCHEMA_PATH",
    "EVIDENCE_SCHEMA_PATH",
    "EVIDENCE_PATH",
    "REPORT_PATH",
    "EVIDENCE_SCHEMA",
    "PLAN_PATH",
    "PREDECESSOR_FILES",
    "IMPLEMENTATION_FILES",
    "load_contract",
    "validate_predecessors",
    "build_preset_source",
    "corrected_runner_source",
    "validate_corrected_runner",
    "build_patch_pair",
    "validate_patch_pair",
    "render_report",
)


@contextmanager
def configured_base() -> Iterator[None]:
    replacements: dict[str, Any] = {
        "OPERATION_ID": OPERATION_ID,
        "OPERATION_ROOT": OPERATION_ROOT,
        "CONTRACT_PATH": CONTRACT_PATH,
        "CONTRACT_SCHEMA_PATH": CONTRACT_SCHEMA_PATH,
        "EVIDENCE_SCHEMA_PATH": EVIDENCE_SCHEMA_PATH,
        "EVIDENCE_PATH": EVIDENCE_PATH,
        "REPORT_PATH": REPORT_PATH,
        "EVIDENCE_SCHEMA": EVIDENCE_SCHEMA,
        "PLAN_PATH": PLAN_PATH,
        "PREDECESSOR_FILES": PREDECESSOR_FILES,
        "IMPLEMENTATION_FILES": IMPLEMENTATION_FILES,
        "load_contract": load_contract,
        "validate_predecessors": validate_predecessors,
        "build_preset_source": _exact_preset,
        "corrected_runner_source": future_runner_source,
        "validate_corrected_runner": validate_future_runner,
        "build_patch_pair": build_patch_pair,
        "validate_patch_pair": validate_patch_pair,
        "render_report": render_report,
    }
    original = {name: getattr(base, name) for name in _PATCHED_NAMES}
    try:
        for name, value in replacements.items():
            setattr(base, name, value)
        yield
    finally:
        for name, value in original.items():
            setattr(base, name, value)


def deterministic_check(cache_root: Path | None = None) -> dict[str, Any]:
    with configured_base():
        projection = base.deterministic_check(cache_root)
    return projection


def execute_boot(cache_root: Path | None = None) -> dict[str, Any]:
    with configured_base():
        return base.execute_boot(cache_root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--execute", action="store_true")
    parser.add_argument("--cache-root", type=Path)
    args = parser.parse_args()
    try:
        if args.check:
            projection = deterministic_check(args.cache_root)
            print(
                json.dumps(
                    {
                        "status": "passed",
                        "attempt_id": projection["contract"]["attempt"]["attempt_id"],
                        "required_services": list(REQUIRED_SERVICES),
                        "effective_tools": projection["contract"]["preset"]["selected_tools"],
                        "native_processes": 0,
                    },
                    sort_keys=True,
                )
            )
        else:
            evidence = execute_boot(args.cache_root)
            print(
                json.dumps(
                    {
                        "status": evidence["result"],
                        "attempt_id": evidence["attempt_id"],
                        "terminal": (evidence.get("terminal") or {}).get("code"),
                        "exit_code": evidence["launch"]["exit_code"],
                        "cleanup": evidence["cleanup"],
                    },
                    sort_keys=True,
                )
            )
    except (CompleteCompositionError, base.RecoveryBootError, OSError, ValueError) as error:
        raise SystemExit(str(error)) from error
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
