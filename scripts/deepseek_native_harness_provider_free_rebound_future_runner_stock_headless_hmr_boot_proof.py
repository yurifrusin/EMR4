"""Run one provider-free native boot of the exact rebound future runner."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any

import jsonschema
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from orchestration_harness import native_post_hmr_future_attempt_materialisation as base_bundle
from orchestration_harness import native_post_hmr_future_attempt_rebinding as rebinding
from orchestration_harness import native_post_hmr_pre_request_controller as joined_controller
from orchestration_harness import native_post_hmr_pre_request_diagnostic as diagnostic
from scripts import (
    deepseek_native_harness_provider_free_future_attempt_identity_and_target_rebinding_rehearsal as accepted_rebinding,
)
from scripts.deepseek_native_harness_provider_free_effective_tool_composition_guard import (
    _default_cache_root,
    build_guard_source,
    validate_guard_source,
)
from scripts.deepseek_native_harness_provider_free_effective_tool_composition_native_boot_proof import (
    sentinel_source,
    validate_installed_packages,
    verify_cached_packages,
)
from scripts.deepseek_native_harness_provider_free_hmr_boot_proof import (
    DISPOSABLE_PARENT,
    POLL_SECONDS,
    ProofError,
    _network_attempts,
    _offline_install,
    _terminate_process,
    _verify_installed_source,
    atomic_write,
    build_child_environment,
    network_guard_source,
    sha256_bytes,
    sha256_file,
    verify_tarball,
)
from scripts import (
    deepseek_native_harness_provider_free_preterminal_observable_composition_recovery_boot as native_base,
)


OPERATION_ID = (
    "deepseek-native-harness-provider-free-rebound-future-runner-stock-headless-"
    "hmr-boot-proof"
)
EXECUTION_ATTEMPT_ID = "rebound-stock-headless-hmr-boot-attempt-001"
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT_PATH = REPO_ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "native-boot-evidence.json"
REPORT_PATH = OPERATION_ROOT / "native-boot-report.md"
EFFICACY_PATH = OPERATION_ROOT / "efficacy-reading.json"
FOCUSED_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_provider_free_rebound_future_runner_stock_headless_hmr_boot_proof.py"
)
ACCEPTED_CONTROLLER_PATH = (
    REPO_ROOT / "orchestration_harness" / "native_post_hmr_pre_request_controller.py"
)
REBOUND_MODULE_PATH = (
    REPO_ROOT / "orchestration_harness" / "native_post_hmr_future_attempt_rebinding.py"
)
READINESS_SCHEMA = "ariadne.deepseek_native_harness_effective_tool_native_boot_event.v1"
EVIDENCE_SCHEMA = "ariadne.native_harness_rebound_stock_headless_hmr_boot_evidence.v1"
REPORT_TIMESTAMP = "2026-08-22T00:00:14.9384829+10:00"
FULL_OID = re.compile(r"^[0-9a-f]{40}$")


class ReboundNativeBootError(RuntimeError):
    """The rebound-runner native boot did not satisfy its closed contract."""


def _canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=15,
    )
    if completed.returncode != 0:
        raise ReboundNativeBootError("git_resolution_failed")
    return completed.stdout.strip()


def _ancestor(object_id: str) -> bool:
    return (
        FULL_OID.fullmatch(object_id) is not None
        and subprocess.run(
            ["git", "merge-base", "--is-ancestor", object_id, "HEAD"],
            cwd=REPO_ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )


def _write_exclusive(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = json.loads(path.read_bytes())
    schema = json.loads(CONTRACT_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(contract)
    plan_relative = PLAN_PATH.relative_to(REPO_ROOT).as_posix()
    if (
        contract["schema_version"]
        != "ariadne.native_harness_rebound_stock_headless_hmr_boot_contract.v1"
        or contract["operation_id"] != OPERATION_ID
        or contract["execution_attempt"]["attempt_id"] != EXECUTION_ATTEMPT_ID
        or _git("rev-parse", "--verify", f'{contract["planning_source"]}^{{commit}}')
        != contract["planning_source"]
        or _git("log", "-1", "--format=%H", "--", plan_relative)
        != contract["planning_source"]
    ):
        raise ReboundNativeBootError("contract_identity_or_planning_source_invalid")
    attempt = contract["execution_attempt"]
    if attempt != {
        "attempt_id": EXECUTION_ATTEMPT_ID,
        "native_process_count": 1,
        "automatic_retry": False,
        "manual_retry": False,
        "resume": False,
    }:
        raise ReboundNativeBootError("one_process_latch_invalid")
    expected_terminal = contract["expected_terminal"]
    if expected_terminal != {
        "coordinate": "post_hmr_pre_request_failure",
        "diagnostic_accepted": True,
        "broker_zero": True,
        "pre_request_supported": True,
        "stage": "preset_root_roster_admission",
        "cause_coordinate": "preset_root_roster_mismatch",
        "error_kind": "error",
    }:
        raise ReboundNativeBootError("expected_terminal_invalid")
    return contract


def source_payloads(
    contract: dict[str, Any],
) -> tuple[bytes, bytes, bytes, bytes, dict[str, Any]]:
    accepted_contract = accepted_rebinding.load_contract()
    runner, helper, bindings, _ = accepted_rebinding.source_payloads(accepted_contract)
    guard = build_guard_source()
    sentinel = sentinel_source()
    validate_guard_source(guard)
    diagnostic.validate_helper_source(helper)
    joined_controller.validate_future_runner_source(
        runner,
        accepted_payload=accepted_rebinding.accepted_materialisation._source_payloads(
            accepted_rebinding.accepted_materialisation.load_contract()
        )[0],
        expected_accepted_sha256=accepted_contract["accepted_materialisation"][
            "source_bindings"
        ]["future_runner_sha256"],
    )
    observed = {
        "future_runner_sha256": sha256_bytes(runner),
        "generated_helper_sha256": sha256_bytes(helper),
        "controller_module_sha256": sha256_file(ACCEPTED_CONTROLLER_PATH),
        "effective_tool_guard_sha256": sha256_bytes(guard),
        "readiness_sentinel_sha256": sha256_bytes(sentinel),
        "rebinding_module_sha256": sha256_file(REBOUND_MODULE_PATH),
    }
    if bindings != {
        key: observed[key]
        for key in (
            "future_runner_sha256",
            "generated_helper_sha256",
            "controller_module_sha256",
        )
    } or observed != contract["source_bindings"]:
        raise ReboundNativeBootError("source_binding_mismatch")
    return runner, helper, guard, sentinel, observed


def _yaml_path(path: Path) -> str:
    return json.dumps(str(path.resolve()))


def _patch_rows(payload: bytes) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = yaml.safe_load(payload)
    if not isinstance(rows, list):
        raise ReboundNativeBootError("patch_not_array")
    direct: list[dict[str, Any]] = []
    inserted: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ReboundNativeBootError("patch_row_invalid")
        if "insert" in row:
            if set(row) != {"insert"} or not isinstance(row["insert"], list):
                raise ReboundNativeBootError("patch_insert_invalid")
            inserted.extend(row["insert"])
        else:
            direct.append(row)
    return direct, inserted


def build_patch_pair(
    *,
    profile_dir: Path,
    readiness_path: Path,
    diagnostic_path: Path,
    collision_terminal_path: Path,
    shipped_mismatch: Path,
    user_mismatch: Path,
) -> tuple[bytes, bytes]:
    profile_patch = profile_dir / "cordis.patch.yml"
    home_patch = profile_dir.parents[1] / "cordis.patch.yml"
    common = f"""- id: headless-runner
  disabled: true
- id: code-runtime
  disabled: true
- id: session-telemetry-otel
  disabled: true
- insert:
    - id: provider-free-rebound-hmr-sentinel
      name: ../../../installation/proof/sentinel.mjs
      config:
        eventPath: {_yaml_path(readiness_path)}
        watchedPaths:
          - {_yaml_path(profile_patch)}
          - {_yaml_path(home_patch)}
"""
    changed = common + f"""    - id: agent-presets
      name: '@deepseek-ai/dsh-agent-presets'
      config:
        default: standard
    - id: provider-free-rebound-future-runner
      name: ../../../installation/proof/runner.mjs
      inject: [hmr, headlessStartup, agents, sessions, agentPresets]
      config:
        diagnosticPath: {_yaml_path(diagnostic_path)}
        terminalPath: {_yaml_path(collision_terminal_path)}
        shippedRoot: {_yaml_path(shipped_mismatch)}
        userRoot: {_yaml_path(user_mismatch)}
        task: provider-free inert control probe not dispatched
"""
    initial, changed_bytes = common.encode(), changed.encode()
    validate_patch_pair(
        initial,
        changed_bytes,
        diagnostic_path=diagnostic_path,
        collision_terminal_path=collision_terminal_path,
        shipped_mismatch=shipped_mismatch,
        user_mismatch=user_mismatch,
    )
    return initial, changed_bytes


def validate_patch_pair(
    initial: bytes,
    changed: bytes,
    *,
    diagnostic_path: Path,
    collision_terminal_path: Path,
    shipped_mismatch: Path,
    user_mismatch: Path,
) -> None:
    initial_direct, initial_inserted = _patch_rows(initial)
    changed_direct, changed_inserted = _patch_rows(changed)
    expected_direct = [
        {"id": "headless-runner", "disabled": True},
        {"id": "code-runtime", "disabled": True},
        {"id": "session-telemetry-otel", "disabled": True},
    ]
    if initial_direct != expected_direct or changed_direct != expected_direct:
        raise ReboundNativeBootError("disabled_patch_rows_invalid")
    if [row.get("id") for row in initial_inserted] != [
        "provider-free-rebound-hmr-sentinel"
    ]:
        raise ReboundNativeBootError("initial_patch_invalid")
    if [row.get("id") for row in changed_inserted] != [
        "provider-free-rebound-hmr-sentinel",
        "agent-presets",
        "provider-free-rebound-future-runner",
    ] or changed_inserted[:1] != initial_inserted:
        raise ReboundNativeBootError("changed_patch_roster_invalid")
    if changed_inserted[1] != {
        "id": "agent-presets",
        "name": "@deepseek-ai/dsh-agent-presets",
        "config": {"default": "standard"},
    }:
        raise ReboundNativeBootError("agent_presets_row_invalid")
    runner = changed_inserted[2]
    expected_config = {
        "diagnosticPath": str(diagnostic_path.resolve()),
        "terminalPath": str(collision_terminal_path.resolve()),
        "shippedRoot": str(shipped_mismatch.resolve()),
        "userRoot": str(user_mismatch.resolve()),
        "task": "provider-free inert control probe not dispatched",
    }
    if (
        runner.get("name") != "../../../installation/proof/runner.mjs"
        or runner.get("inject")
        != ["hmr", "headlessStartup", "agents", "sessions", "agentPresets"]
        or runner.get("config") != expected_config
    ):
        raise ReboundNativeBootError("runner_patch_row_invalid")
    if len({str(shipped_mismatch.resolve()), str(user_mismatch.resolve())}) != 2:
        raise ReboundNativeBootError("mismatch_coordinates_not_distinct")


def validate_predecessors(contract: dict[str, Any]) -> dict[str, Any]:
    accepted_sources = {
        "planning_source": contract["planning_source"],
        **contract["accepted_sources"],
    }
    if any(not _ancestor(value) for value in accepted_sources.values()):
        raise ReboundNativeBootError("accepted_source_missing_or_not_ancestor")
    paths = {
        "frozen_plan_sha256": PLAN_PATH,
        "threat_model_sha256": THREAT_PATH,
        "accepted_rebinding_contract_sha256": accepted_rebinding.CONTRACT_PATH,
        "accepted_rebinding_evidence_sha256": accepted_rebinding.EVIDENCE_PATH,
        "accepted_rebinding_controller_sha256": Path(accepted_rebinding.__file__).resolve(),
        "rebinding_module_sha256": REBOUND_MODULE_PATH,
        "accepted_controller_sha256": ACCEPTED_CONTROLLER_PATH,
        "native_boot_utility_sha256": Path(native_base.__file__).resolve(),
    }
    observed = {key: sha256_file(path) for key, path in paths.items()}
    if observed != contract["predecessor_bytes"]:
        raise ReboundNativeBootError("predecessor_digest_mismatch")
    implementation = {
        "execution_controller_sha256": sha256_file(Path(__file__).resolve()),
        "focused_test_sha256": sha256_file(FOCUSED_TEST_PATH),
        "contract_schema_sha256": sha256_file(CONTRACT_SCHEMA_PATH),
        "evidence_schema_sha256": sha256_file(EVIDENCE_SCHEMA_PATH),
    }
    if implementation != contract["implementation_bytes"]:
        raise ReboundNativeBootError("implementation_digest_mismatch")
    return {
        "accepted_sources": accepted_sources,
        "predecessor_sha256": observed,
        "implementation_sha256": implementation,
    }


def deterministic_check(cache_root: Path | None = None) -> dict[str, Any]:
    contract = load_contract()
    predecessor = validate_predecessors(contract)
    runner, helper, guard, sentinel, bindings = source_payloads(contract)
    resolved_cache = (cache_root or _default_cache_root()).resolve()
    _, cached = verify_cached_packages(contract, resolved_cache)
    deterministic_root = Path("C:/deterministic/rebound-runner-native-boot").resolve()
    profile_dir = deterministic_root / "home" / "profiles" / "headless"
    initial, changed = build_patch_pair(
        profile_dir=profile_dir,
        readiness_path=deterministic_root / "readiness.jsonl",
        diagnostic_path=deterministic_root / "bundle" / "control" / "post-hmr-diagnostic.json",
        collision_terminal_path=deterministic_root / "bundle" / "control" / "future-attempt-bundle.json",
        shipped_mismatch=deterministic_root / "mismatch-shipped",
        user_mismatch=deterministic_root / "mismatch-user",
    )
    return {
        "contract": contract,
        "predecessor": predecessor,
        "source_bindings": bindings,
        "source_bytes": {
            "runner": len(runner),
            "helper": len(helper),
            "guard": len(guard),
            "sentinel": len(sentinel),
        },
        "patch_sha256": {
            "initial": sha256_bytes(initial),
            "changed": sha256_bytes(changed),
        },
        "verified_cached_package_count": len(cached),
    }


def _safe_readiness(path: Path, contract: dict[str, Any]) -> tuple[list[dict[str, Any]], bool]:
    try:
        records = native_base.parse_readiness(path, contract, allow_incomplete=False)
        native_base.validate_readiness(records, contract)
        return records, True
    except (native_base.RecoveryBootError, OSError, ValueError, json.JSONDecodeError):
        return [], False


def _safe_sidecar(
    path: Path, *, bundle_root: Path, identity: dict[str, str]
) -> tuple[dict[str, Any] | None, bool]:
    try:
        value = diagnostic.read_diagnostic(
            path,
            disposable_root=bundle_root,
            operation_id=identity["operation_id"],
            attempt_id=identity["attempt_id"],
            candidate_source=identity["candidate_source"],
        )
        return value, True
    except (diagnostic.PostHmrDiagnosticError, OSError):
        return None, False


def _failure_coordinate(
    *,
    process_started: bool,
    readiness_valid: bool,
    readiness_events: list[str],
    mutated: bool,
    sidecar: dict[str, Any] | None,
    terminal: dict[str, Any] | None,
    network_attempt_count: int,
    network_ledger_valid: bool,
    bundle_unchanged: bool,
    target_absent: bool,
    process_absent: bool,
    root_absent: bool,
) -> str | None:
    if not process_started:
        return "PRELAUNCH_REJECTED"
    if not network_ledger_valid or network_attempt_count:
        return "NETWORK_BOUNDARY_REJECTED"
    if not readiness_valid or readiness_events != [
        "sentinel_activated",
        "stock_headless_hmr_ready",
    ]:
        return "READINESS_REJECTED"
    if not mutated:
        return "HMR_MUTATION_REJECTED"
    if sidecar is None:
        return "TYPED_SIDECAR_REJECTED"
    if (
        sidecar["stage"] != "preset_root_roster_admission"
        or sidecar["cause_coordinate"] != "preset_root_roster_mismatch"
        or sidecar["error_kind"] != "error"
    ):
        return "PRE_REQUEST_SUBCOORDINATE_REJECTED"
    if terminal is None or terminal["coordinate"] != "post_hmr_pre_request_failure":
        return "CONTROLLER_TERMINAL_REJECTED"
    if not bundle_unchanged:
        return "CANONICAL_BUNDLE_MUTATED"
    if not target_absent:
        return "TARGET_BOUNDARY_REJECTED"
    if not process_absent or not root_absent:
        return "CLEANUP_REJECTED"
    return None


def _render_report(evidence: dict[str, Any]) -> str:
    terminal = evidence["controller_terminal"] or {}
    diagnostic_value = evidence["diagnostic"] or {}
    return f"""# Rebound future-runner stock-headless HMR boot report

Date: 2026-08-22

Timestamp: {REPORT_TIMESTAMP} (Australia/Brisbane)

Result: **{evidence['result']}**

- Execution attempt: `{evidence['execution_attempt_id']}`
- Full execution source: `{evidence['candidate_source']}`
- Embedded attempt: `{evidence['bundle_identity']['attempt_id']}`
- Readiness: `{', '.join(evidence['readiness']['events'])}`
- HMR mutation count: `{evidence['launch']['hmr_mutation_count']}`
- Typed stage / cause: `{diagnostic_value.get('stage')}` / `{diagnostic_value.get('cause_coordinate')}`
- Controller coordinate: `{terminal.get('coordinate')}`
- Native process / retry: `{evidence['launch']['native_process_count']}` / `{evidence['launch']['retry_count']}`
- Broker / model / provider / network: `0 / 0 / 0 / {evidence['provider_boundary']['network_attempt_count']}`
- Target created or used: `false / false`
- Process absent / disposable root absent: `{str(evidence['cleanup']['process_absent']).lower()}` / `{str(evidence['cleanup']['disposable_root_absent']).lower()}`

This proves one pinned local rc.7 provider-free stock-headless HMR activation of
the exact accepted rebound runner to a typed pre-request subcoordinate. It is
not an occupied DeepSeek worker, model/provider request, coding-quality result,
product-runtime result or ordinary-practice admission.
"""


def _efficacy(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "ariadne.native_harness_rebound_stock_headless_hmr_boot_efficacy.v1",
        "operation_id": OPERATION_ID,
        "result": evidence["result"],
        "control_gain": "exact_rebound_runner_native_activation_is_machine_joined_to_typed_pre_request_and_broker_zero_evidence",
        "native_process_count": evidence["launch"]["native_process_count"],
        "retry_count": evidence["launch"]["retry_count"],
        "free_form_finite_control_fields": 0,
        "deepseek_worker_request_count": 0,
        "model_request_count": 0,
        "provider_request_count": 0,
        "next_gate": "one_bounded_provider_free_deepseek_worker_attempt_only_if_separately_frozen",
    }


def execute_boot(cache_root: Path | None = None) -> dict[str, Any]:
    if any(path.exists() for path in (EVIDENCE_PATH, REPORT_PATH, EFFICACY_PATH)):
        raise ReboundNativeBootError("canonical_attempt_output_already_exists")
    check = deterministic_check(cache_root)
    contract = check["contract"]
    candidate_source = _git("rev-parse", "HEAD")
    if FULL_OID.fullmatch(candidate_source) is None or not _ancestor(
        contract["planning_source"]
    ):
        raise ReboundNativeBootError("execution_candidate_source_invalid")
    tracked_diff = subprocess.run(
        ["git", "diff", "--quiet", "--"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if tracked_diff.returncode != 0:
        raise ReboundNativeBootError("tracked_worktree_must_be_clean_before_execution")
    identity = contract["bundle_identity"]
    bindings = {
        key: contract["source_bindings"][key]
        for key in (
            "future_runner_sha256",
            "generated_helper_sha256",
            "controller_module_sha256",
        )
    }
    runner, helper, guard, sentinel, _ = source_payloads(contract)
    network_guard = network_guard_source()
    resolved_cache = (cache_root or _default_cache_root()).resolve()
    cache_blob, cached_packages = verify_cached_packages(contract, resolved_cache)
    parent = DISPOSABLE_PARENT.resolve()
    if not parent.is_dir():
        raise ReboundNativeBootError("disposable_parent_missing")
    root = Path(tempfile.mkdtemp(prefix="dsh-rebound-hmr-boot-", dir=parent)).resolve()
    if root.parent != parent:
        raise ReboundNativeBootError("disposable_root_escape")

    process: subprocess.Popen[bytes] | None = None
    process_started = False
    process_absent = True
    started: float | None = None
    duration_ms: int | None = None
    launch_started_utc: str | None = None
    exit_code: int | None = None
    exit_mode: str | None = None
    removed_environment_names = 0
    hmr_mutation_count = 0
    readiness_records: list[dict[str, Any]] = []
    readiness_valid = False
    sidecar: dict[str, Any] | None = None
    sidecar_valid = False
    terminal: dict[str, Any] | None = None
    network_attempt_count = 0
    network_ledger_valid = True
    bundle_unchanged = False
    bundle_manifest_before = ""
    bundle_manifest_after = ""
    target_absent = False
    runner_copy_equal = False
    helper_copy_equal = False
    install_projection: dict[str, Any] = {}
    installed_source: dict[str, Any] = {}
    installed_versions: dict[str, str] = {}
    package_identity: dict[str, Any] = {}
    initial_patch = b""
    changed_patch = b""
    bundle_root: Path | None = None
    broker_path: Path | None = None
    sidecar_path: Path | None = None
    caught_after_launch = False

    try:
        bundle_parent = root / "bundle"
        bundle_parent.mkdir()
        materialised = rebinding.materialize_rebound_future_attempt(
            disposable_parent=bundle_parent,
            operation_id=identity["operation_id"],
            attempt_id=identity["attempt_id"],
            candidate_source=identity["candidate_source"],
            target_path=contract["target_binding"]["relative_path"],
            runner_payload=runner,
            helper_payload=helper,
            controller_payload=ACCEPTED_CONTROLLER_PATH.read_bytes(),
            expected_bindings=bindings,
        )
        bundle_root = materialised["root"]
        manifest_path = base_bundle._path(bundle_root, base_bundle.BUNDLE_RELATIVE_PATH)
        sidecar_path = base_bundle._path(bundle_root, base_bundle.SIDECAR_RELATIVE_PATH)
        broker_path = base_bundle._path(bundle_root, base_bundle.BROKER_RELATIVE_PATH)
        bundle_manifest_before = sha256_file(manifest_path)
        broker = joined_controller.build_broker_reading(
            operation_id=identity["operation_id"],
            attempt_id=identity["attempt_id"],
            candidate_source=identity["candidate_source"],
        )
        rebinding.write_broker_fixture(bundle_root, broker)
        target = bundle_root / Path(contract["target_binding"]["relative_path"])
        if target.exists() or target.is_symlink():
            raise ReboundNativeBootError("target_must_be_absent_prelaunch")

        home = root / "home"
        profile_dir = home / "profiles" / "headless"
        workspace = root / "workspace"
        proof_dir = root / "installation" / "proof"
        network_guard_path = root / "network-guard.mjs"
        network_path = root / "network.jsonl"
        readiness_path = root / "readiness.jsonl"
        tarball_path = root / "dsh-0.1.0-rc.7.tgz"
        workspace.mkdir()
        profile_dir.mkdir(parents=True)
        (home / ".agent-presets").mkdir()
        _write_exclusive(network_guard_path, network_guard)
        _write_exclusive(tarball_path, cache_blob.read_bytes())
        package_identity = verify_tarball(tarball_path, contract)
        environment, removed_environment_names = build_child_environment(
            home, network_guard_path, network_path
        )
        package_root, install_projection = _offline_install(root, tarball_path, environment)
        installed_source = _verify_installed_source(package_root, contract)
        installed_versions = validate_installed_packages(package_root, contract)

        profile_manifest = {
            "name": "dsh-profile-headless",
            "private": True,
            "dependencies": {},
            "dsh": {
                "profile": {
                    "bundles": ["@deepseek-ai/dsh-base", "@deepseek-ai/dsh-headless"]
                }
            },
        }
        _write_exclusive(
            profile_dir / "package.json",
            (json.dumps(profile_manifest, indent=2) + "\n").encode(),
        )
        _write_exclusive(
            profile_dir / "pnpm-workspace.yaml",
            b"packages:\n  - .\n\nnodeLinker: hoisted\nautoInstallPeers: false\n",
        )
        _write_exclusive(proof_dir / "runner.mjs", runner)
        _write_exclusive(proof_dir / "post-hmr-pre-request-diagnostic.mjs", helper)
        _write_exclusive(proof_dir / "effective-tool-guard.mjs", guard)
        _write_exclusive(proof_dir / "sentinel.mjs", sentinel)
        runner_copy_equal = sha256_file(proof_dir / "runner.mjs") == bindings[
            "future_runner_sha256"
        ]
        helper_copy_equal = sha256_file(
            proof_dir / "post-hmr-pre-request-diagnostic.mjs"
        ) == bindings["generated_helper_sha256"]
        if not runner_copy_equal or not helper_copy_equal:
            raise ReboundNativeBootError("execution_copy_digest_mismatch")
        initial_patch, changed_patch = build_patch_pair(
            profile_dir=profile_dir,
            readiness_path=readiness_path,
            diagnostic_path=sidecar_path,
            collision_terminal_path=manifest_path,
            shipped_mismatch=root / "mismatch-shipped",
            user_mismatch=root / "mismatch-user",
        )
        patch_path = profile_dir / "cordis.patch.yml"
        _write_exclusive(patch_path, initial_patch)

        node = shutil.which("node")
        if node is None:
            raise ReboundNativeBootError("node_not_found")
        command = [
            node,
            contract["launch"]["node_flag"],
            str(package_root / contract["package"]["bin"]),
            *contract["launch"]["profile_args"],
            "provider-free rebound runner stock-headless HMR boot proof",
        ]
        launch_started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        started = time.monotonic()
        process = subprocess.Popen(
            command,
            cwd=workspace,
            env=environment,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        process_started = True
        deadline = started + float(contract["launch"]["timeout_seconds"])
        while True:
            readiness_records = native_base.parse_readiness(
                readiness_path, contract, allow_incomplete=True
            )
            native_base.validate_readiness_prefix(readiness_records, contract)
            events = [record["event"] for record in readiness_records]
            if events == contract["readiness"]["events"] and hmr_mutation_count == 0:
                atomic_write(patch_path, changed_patch)
                hmr_mutation_count = 1
            if sidecar_path.exists():
                sidecar, sidecar_valid = _safe_sidecar(
                    sidecar_path, bundle_root=bundle_root, identity=identity
                )
                if sidecar_valid:
                    break
            if process.poll() is not None:
                exit_mode = "self_exited_before_typed_sidecar"
                break
            if time.monotonic() >= deadline:
                exit_mode = "controller_deadline_termination"
                break
            time.sleep(POLL_SECONDS)
        if process.poll() is None:
            _terminate_process(process)
            exit_mode = exit_mode or "controller_terminated_after_typed_sidecar"
        else:
            exit_mode = exit_mode or "self_exited_after_typed_sidecar"
        exit_code = process.returncode
    except (
        ReboundNativeBootError,
        ProofError,
        native_base.RecoveryBootError,
        subprocess.SubprocessError,
        OSError,
        ValueError,
        json.JSONDecodeError,
    ):
        caught_after_launch = process_started
    finally:
        if started is not None:
            duration_ms = round((time.monotonic() - started) * 1000)
        if process is not None:
            _terminate_process(process)
            exit_code = process.returncode
            process_absent = process.poll() is not None
        else:
            process_absent = True
        if bundle_root is not None:
            readiness_path = root / "readiness.jsonl"
            readiness_records, readiness_valid = _safe_readiness(readiness_path, contract)
            if sidecar_path is not None:
                sidecar, sidecar_valid = _safe_sidecar(
                    sidecar_path, bundle_root=bundle_root, identity=identity
                )
            network_path = root / "network.jsonl"
            try:
                network_attempt_count = len(_network_attempts(network_path))
            except (ProofError, OSError, ValueError, json.JSONDecodeError):
                network_ledger_valid = False
            manifest_path = base_bundle._path(bundle_root, base_bundle.BUNDLE_RELATIVE_PATH)
            try:
                bundle_manifest_after = sha256_file(manifest_path)
                bundle_unchanged = (
                    bool(bundle_manifest_before)
                    and bundle_manifest_after == bundle_manifest_before
                )
            except OSError:
                bundle_unchanged = False
            target = bundle_root / Path(contract["target_binding"]["relative_path"])
            target_absent = not target.exists() and not target.is_symlink()
            if broker_path is not None and bundle_unchanged:
                try:
                    terminal = rebinding.assemble_controller_terminal(
                        bundle_root,
                        operation_id=identity["operation_id"],
                        attempt_id=identity["attempt_id"],
                        candidate_source=identity["candidate_source"],
                        target_path=contract["target_binding"]["relative_path"],
                        expected_bindings=bindings,
                    )
                except (
                    rebinding.FutureAttemptRebindingError,
                    joined_controller.PostHmrControllerError,
                    diagnostic.PostHmrDiagnosticError,
                    OSError,
                ):
                    terminal = None
        if root.parent != parent:
            raise ReboundNativeBootError("cleanup_root_escape")
        shutil.rmtree(root)

    root_absent = not root.exists()
    if not process_started:
        raise ReboundNativeBootError("prelaunch_validation_failed")
    readiness_events = [record["event"] for record in readiness_records]
    failure = _failure_coordinate(
        process_started=process_started,
        readiness_valid=readiness_valid,
        readiness_events=readiness_events,
        mutated=hmr_mutation_count == 1,
        sidecar=sidecar if sidecar_valid else None,
        terminal=terminal,
        network_attempt_count=network_attempt_count,
        network_ledger_valid=network_ledger_valid,
        bundle_unchanged=bundle_unchanged,
        target_absent=target_absent,
        process_absent=process_absent,
        root_absent=root_absent,
    )
    expected_terminal = contract["expected_terminal"]
    if terminal is not None and any(
        terminal[key] != value for key, value in expected_terminal.items()
    ):
        failure = "CONTROLLER_TERMINAL_REJECTED"
    if caught_after_launch and failure is None:
        failure = "POSTLAUNCH_CONTROLLER_REJECTED"
    result = "pass" if failure is None else "fail"
    evidence = {
        "schema_version": EVIDENCE_SCHEMA,
        "operation_id": OPERATION_ID,
        "planning_source": contract["planning_source"],
        "candidate_source": candidate_source,
        "execution_attempt_id": EXECUTION_ATTEMPT_ID,
        "result": result,
        "failure_classification": failure,
        "bundle_identity": identity,
        "source_bindings": contract["source_bindings"],
        "target_binding": contract["target_binding"],
        "package": {
            "name": contract["package"]["name"],
            "version": contract["package"]["version"],
            "bin": contract["package"]["bin"],
            **package_identity,
            "offline_install": install_projection,
            "installed_source": installed_source,
            "installed_versions": installed_versions,
            "verified_cached_package_count": len(cached_packages),
        },
        "launch": {
            "started_at_utc": launch_started_utc,
            "duration_ms": duration_ms,
            "native_process_count": 1 if process_started else 0,
            "retry_count": 0,
            "resume_count": 0,
            "hmr_mutation_count": hmr_mutation_count,
            "exit_code": exit_code,
            "exit_mode": exit_mode,
            "stdout_retained": False,
            "stderr_retained": False,
            "raw_stream_read": False,
        },
        "composition": {
            "initial_patch_sha256": sha256_bytes(initial_patch),
            "changed_patch_sha256": sha256_bytes(changed_patch),
            "runner_copy_sha256": contract["source_bindings"]["future_runner_sha256"],
            "helper_copy_sha256": contract["source_bindings"]["generated_helper_sha256"],
            "runner_copy_equal": runner_copy_equal,
            "helper_copy_equal": helper_copy_equal,
            "guard_sha256": contract["source_bindings"]["effective_tool_guard_sha256"],
            "sentinel_sha256": contract["source_bindings"]["readiness_sentinel_sha256"],
            "bundle_manifest_before_sha256": bundle_manifest_before,
            "bundle_manifest_after_sha256": bundle_manifest_after,
            "bundle_manifest_unchanged": bundle_unchanged,
            "runner_fallback_terminal_absent": bundle_unchanged,
        },
        "readiness": {
            "events": readiness_events,
            "valid": readiness_valid,
            "exact_expected_order": readiness_events == contract["readiness"]["events"],
        },
        "diagnostic": sidecar if sidecar_valid else None,
        "broker_reading": {
            "schema_version": joined_controller.BROKER_SCHEMA_VERSION,
            **{counter: 0 for counter in joined_controller.BROKER_COUNTERS},
            "identity_bound": True,
            "canonical": True,
            "raw_broker_stream_retained": False,
        },
        "controller_terminal": terminal,
        "provider_boundary": {
            "credential_environment_names_removed_count": removed_environment_names,
            "network_attempt_count": network_attempt_count,
            "network_ledger_valid": network_ledger_valid,
            "agent_create_count": 0,
            "session_count": 0,
            "turn_count": 0,
            "broker_process_count": 0,
            "broker_request_count": 0,
            "worker_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "database_invocation_count": 0,
            "docker_invocation_count": 0,
        },
        "target": {
            "file_created": False,
            "used": False,
            "absent_after_process": target_absent,
        },
        "cleanup": {
            "process_absent": process_absent,
            "disposable_root_absent": root_absent,
            "raw_environment_retained": False,
            "raw_logs_retained": False,
            "npm_cache_retained_by_boot": False,
        },
    }
    evidence_schema = json.loads(EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(evidence_schema)
    jsonschema.Draft202012Validator(evidence_schema).validate(evidence)
    _write_exclusive(EVIDENCE_PATH, _canonical(evidence))
    _write_exclusive(REPORT_PATH, _render_report(evidence).encode())
    _write_exclusive(EFFICACY_PATH, _canonical(_efficacy(evidence)))
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--execute", action="store_true")
    parser.add_argument("--cache-root", type=Path)
    args = parser.parse_args()
    if args.check:
        projection = deterministic_check(args.cache_root)
        print(
            json.dumps(
                {
                    "status": "passed",
                    "execution_attempt_id": EXECUTION_ATTEMPT_ID,
                    "source_bindings": projection["source_bindings"],
                    "native_process_count": 0,
                },
                sort_keys=True,
            )
        )
        return 0
    evidence = execute_boot(args.cache_root)
    print(
        json.dumps(
            {
                "status": evidence["result"],
                "execution_attempt_id": EXECUTION_ATTEMPT_ID,
                "failure_classification": evidence["failure_classification"],
                "controller_coordinate": (evidence["controller_terminal"] or {}).get(
                    "coordinate"
                ),
                "cleanup": evidence["cleanup"],
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
