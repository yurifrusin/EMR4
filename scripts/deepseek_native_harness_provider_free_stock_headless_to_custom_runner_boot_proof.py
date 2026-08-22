"""Prove stock rc.7 headless hands off to the corrected accepted guard graph."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import posixpath
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

from scripts import (  # noqa: E402
    deepseek_native_harness_provider_free_edit_coordinate_integrated_runner_stock_headless_boot_rehearsal
    as stock_boot,
)
from scripts import (  # noqa: E402
    deepseek_native_harness_provider_free_integrated_runner_accepted_guard_graph_materialization_recovery
    as materializer,
)


OPERATION_ID = (
    "deepseek-native-harness-provider-free-stock-headless-to-custom-runner-boot-proof"
)
ATTEMPT_ID = "stock-headless-custom-runner-boot-attempt-001"
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT_PATH = REPO_ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "native-boot-evidence.json"
REPORT_PATH = OPERATION_ROOT / "native-boot-report.md"
CONSUMED_PATH = OPERATION_ROOT / "native-attempt-consumed.json"
ADAPTER_PATH = OPERATION_ROOT / "accepted-guard-graph-boot-probe.mjs"
FOCUSED_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_provider_free_stock_headless_to_custom_runner_boot_proof.py"
)
DISPOSABLE_PARENT = Path("C:/Users/sarashera/EMR4-worktrees")
FULL_OID = re.compile(r"^[0-9a-f]{40}$")
SHA256_TEXT = re.compile(r"^sha256:[0-9a-f]{64}$")
READINESS_EVENTS = ["sentinel_activated", "stock_headless_hmr_ready"]
PASS_RESULT = "stock_headless_handed_off_to_accepted_guard_graph_runner"

RUNNER_FILENAME = materializer.RUNNER_FILENAME
GUARD_FILENAME = materializer.GUARD_FILENAME
BRIDGE_FILENAME = materializer.BRIDGE_FILENAME
SANITIZER_FILENAME = materializer.SANITIZER_FILENAME
ADAPTER_FILENAME = ADAPTER_PATH.name

EXPECTED_OBSERVATION = {
    "schema_version": "ariadne.native_harness_stock_headless_custom_runner_observation.v1",
    "result": PASS_RESULT,
    "structured_coordinate": materializer.SUCCESS_COORDINATE,
    "old_input_invalid_observed": False,
    "distinct_preset_root_count": 2,
    "factory_create_agent_invocations": 1,
    "setup_invocations": 1,
    "setup_resolved": True,
    "preset_root_reads": 4,
    "preset_mount_reads": 1,
    "preset_mount_calls": 1,
    "tool_view_calls": 1,
    "tool_restrict_calls": 1,
    "tool_schema_calls": 1,
    "hook_installations": 5,
    "scope_disposals": 1,
    "runner_app_exit_code": 1,
    "runner_status": "failed",
    "runner_failure_stage": "factory",
    "runner_request_count": 0,
    "runner_tool_result_count": 0,
    "runner_turn_kind": None,
    "runner_conclusion_marked": False,
    "live_agent_count": 0,
    "raw_error_retained": False,
    "cordis_disposed": True,
    "stock_app_exit_requested": True,
}


class StockHeadlessCustomRunnerBootError(RuntimeError):
    """The closed stock-headless/custom-runner contract rejected."""


sha256_bytes = stock_boot.sha256_bytes
sha256_file = stock_boot.sha256_file


def _canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _write_exclusive(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()


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
        raise StockHeadlessCustomRunnerBootError("git_resolution_failed")
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


def _binding(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {"path": path.relative_to(REPO_ROOT).as_posix(), "bytes": len(payload), "sha256": sha256_bytes(payload)}


def load_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_bytes())
    schema = json.loads(CONTRACT_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(contract)
    plan_relative = PLAN_PATH.relative_to(REPO_ROOT).as_posix()
    if (
        contract["operation_id"] != OPERATION_ID
        or contract["execution_attempt"]
        != {
            "attempt_id": ATTEMPT_ID,
            "native_process_count": 1,
            "automatic_retry": False,
            "manual_retry": False,
            "resume": False,
            "fallback": False,
        }
        or _git("rev-parse", "--verify", f'{contract["planning_source"]}^{{commit}}')
        != contract["planning_source"]
        or _git("log", "-1", "--format=%H", "--", plan_relative)
        != contract["planning_source"]
    ):
        raise StockHeadlessCustomRunnerBootError("contract_identity_rejected")
    if any(not _ancestor(value) for value in contract["accepted_sources"].values()):
        raise StockHeadlessCustomRunnerBootError("accepted_source_ancestry_rejected")
    for expected in contract["accepted_inputs"].values():
        path = REPO_ROOT / expected["path"]
        if _binding(path) != expected:
            raise StockHeadlessCustomRunnerBootError("accepted_input_binding_rejected")
    implementation_paths = {
        "controller": Path(__file__).resolve(),
        "focused_test": FOCUSED_TEST_PATH,
        "adapter": ADAPTER_PATH,
        "contract_schema": CONTRACT_SCHEMA_PATH,
        "evidence_schema": EVIDENCE_SCHEMA_PATH,
    }
    observed_implementation = {
        name: sha256_file(path) for name, path in implementation_paths.items()
    }
    if observed_implementation != contract["implementation_sha256"]:
        raise StockHeadlessCustomRunnerBootError("implementation_binding_rejected")
    if contract["expected_observation"] != EXPECTED_OBSERVATION:
        raise StockHeadlessCustomRunnerBootError("expected_observation_rejected")
    return contract


def validate_adapter_source(payload: bytes) -> dict[str, Any]:
    source = payload.decode("utf-8")
    required_once = [
        'from "./integrated-runner.mjs"',
        'export const inject = ["hmr", "headlessStartup"]',
        'structuredCoordinate = SUCCESS_COORDINATE',
        'throw new Error("CONTROLLED_POST_GUARD_SENTINEL")',
        'writeExclusive(config.observationPath, result)',
        "stockExit(0)",
    ]
    if any(source.count(fragment) != 1 for fragment in required_once):
        raise StockHeadlessCustomRunnerBootError("adapter_closed_shape_rejected")
    forbidden = [
        "fetch(",
        "http.request",
        "https.request",
        "child_process",
        "spawn(",
        "exec(",
        "provider request",
        "model request",
    ]
    if any(fragment in source for fragment in forbidden):
        raise StockHeadlessCustomRunnerBootError("adapter_forbidden_surface")
    return {"bytes": len(payload), "sha256": sha256_bytes(payload)}


def source_payloads(contract: dict[str, Any]) -> dict[str, bytes]:
    accepted = materializer.accepted_sources(materializer.load_contract())
    payloads = {
        "runner": accepted["runner"],
        "guard": accepted["guard"],
        "bridge": accepted["bridge"],
        "sanitizer": accepted["sanitizer"],
        "adapter": ADAPTER_PATH.read_bytes(),
        "readiness_sentinel": stock_boot.sentinel_source(),
        "network_guard": stock_boot.network_guard_source(),
    }
    validate_adapter_source(payloads["adapter"])
    observed = {
        name: {"bytes": len(payload), "sha256": sha256_bytes(payload)}
        for name, payload in payloads.items()
    }
    if observed != contract["source_bindings"]:
        raise StockHeadlessCustomRunnerBootError("source_binding_rejected")
    return payloads


def module_sources(contract: dict[str, Any]) -> dict[str, bytes]:
    payloads = source_payloads(contract)
    return {
        RUNNER_FILENAME: payloads["runner"],
        GUARD_FILENAME: payloads["guard"],
        BRIDGE_FILENAME: payloads["bridge"],
        SANITIZER_FILENAME: payloads["sanitizer"],
        ADAPTER_FILENAME: payloads["adapter"],
    }


def import_closure(contract: dict[str, Any], package_root: Path) -> dict[str, Any]:
    modules = module_sources(contract)
    package_scope = package_root.resolve(strict=True).parent.resolve(strict=True)
    if package_scope.name != "@deepseek-ai" or package_scope.parent.name != "node_modules":
        raise StockHeadlessCustomRunnerBootError("installed_package_scope_rejected")
    relative: set[tuple[str, str, str, str]] = set()
    bare: set[tuple[str, str, str]] = set()
    builtins: set[tuple[str, str, str]] = set()
    bare_targets: set[str] = set()
    for importer, payload in modules.items():
        for specifier, kind in materializer.import_parser._imports(payload):
            if "\\" in specifier or specifier.startswith(("/", "file:", "http:", "https:")):
                raise StockHeadlessCustomRunnerBootError("import_specifier_rejected")
            if specifier.startswith(("./", "../")):
                target = posixpath.normpath(
                    posixpath.join(posixpath.dirname(importer), specifier)
                )
                if target not in modules or target.startswith("../"):
                    raise StockHeadlessCustomRunnerBootError("relative_import_target_rejected")
                relative.add((importer, specifier, target, kind))
            elif specifier.startswith("node:"):
                builtins.add((importer, specifier, kind))
            elif specifier.startswith("@deepseek-ai/"):
                package = specifier.split("/", 1)[1]
                target = package_scope / package / "lib" / "index.js"
                try:
                    resolved = target.resolve(strict=True)
                except OSError as error:
                    raise StockHeadlessCustomRunnerBootError("bare_import_target_missing") from error
                if not resolved.is_file() or not resolved.is_relative_to(package_scope):
                    raise StockHeadlessCustomRunnerBootError("bare_import_target_rejected")
                bare.add((importer, specifier, kind))
                bare_targets.add(specifier)
            else:
                raise StockHeadlessCustomRunnerBootError("bare_import_specifier_rejected")
    expected = contract["expected_import_closure"]
    projection = {
        "module_count": len(modules),
        "relative_edge_count": len(relative),
        "bare_edge_count": len(bare),
        "builtin_edge_count": len(builtins),
        "bare_target_count": len(bare_targets),
        "all_targets_present": True,
    }
    if projection != expected:
        raise StockHeadlessCustomRunnerBootError("import_closure_rejected")
    return projection


def _yaml_path(path: Path) -> str:
    return json.dumps(str(path.resolve()))


def _patch_rows(payload: bytes) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = yaml.safe_load(payload)
    if not isinstance(rows, list):
        raise StockHeadlessCustomRunnerBootError("patch_not_array")
    direct: list[dict[str, Any]] = []
    inserted: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise StockHeadlessCustomRunnerBootError("patch_row_rejected")
        if "insert" in row:
            if set(row) != {"insert"} or not isinstance(row["insert"], list):
                raise StockHeadlessCustomRunnerBootError("patch_insert_rejected")
            inserted.extend(row["insert"])
        else:
            direct.append(row)
    return direct, inserted


def build_patch_pair(
    *,
    profile_dir: Path,
    readiness_path: Path,
    observation_path: Path,
    terminal_path: Path,
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
    - id: provider-free-accepted-guard-graph-hmr-sentinel
      name: ../../../installation/proof/sentinel.mjs
      config:
        eventPath: {_yaml_path(readiness_path)}
        watchedPaths:
          - {_yaml_path(profile_patch)}
          - {_yaml_path(home_patch)}
"""
    changed = common + f"""    - id: provider-free-accepted-guard-graph-boot-probe
      name: ../../../installation/proof/{ADAPTER_FILENAME}
      inject: [hmr, headlessStartup]
      config:
        observationPath: {_yaml_path(observation_path)}
        terminalPath: {_yaml_path(terminal_path)}
        watchedPaths:
          - {_yaml_path(profile_patch)}
          - {_yaml_path(home_patch)}
"""
    initial_bytes = common.encode()
    changed_bytes = changed.encode()
    validate_patch_pair(
        initial_bytes,
        changed_bytes,
        readiness_path=readiness_path,
        observation_path=observation_path,
        terminal_path=terminal_path,
    )
    return initial_bytes, changed_bytes


def validate_patch_pair(
    initial: bytes,
    changed: bytes,
    *,
    readiness_path: Path,
    observation_path: Path,
    terminal_path: Path,
) -> None:
    initial_direct, initial_inserted = _patch_rows(initial)
    changed_direct, changed_inserted = _patch_rows(changed)
    expected_direct = [
        {"id": "headless-runner", "disabled": True},
        {"id": "code-runtime", "disabled": True},
        {"id": "session-telemetry-otel", "disabled": True},
    ]
    if initial_direct != expected_direct or changed_direct != expected_direct:
        raise StockHeadlessCustomRunnerBootError("disabled_rows_rejected")
    if [row.get("id") for row in initial_inserted] != [
        "provider-free-accepted-guard-graph-hmr-sentinel"
    ]:
        raise StockHeadlessCustomRunnerBootError("initial_patch_rejected")
    if [row.get("id") for row in changed_inserted] != [
        "provider-free-accepted-guard-graph-hmr-sentinel",
        "provider-free-accepted-guard-graph-boot-probe",
    ] or changed_inserted[:1] != initial_inserted:
        raise StockHeadlessCustomRunnerBootError("changed_patch_rejected")
    sentinel = initial_inserted[0]
    if sentinel.get("config", {}).get("eventPath") != str(readiness_path.resolve()):
        raise StockHeadlessCustomRunnerBootError("sentinel_path_rejected")
    runner = changed_inserted[1]
    if runner != {
        "id": "provider-free-accepted-guard-graph-boot-probe",
        "name": f"../../../installation/proof/{ADAPTER_FILENAME}",
        "inject": ["hmr", "headlessStartup"],
        "config": {
            "observationPath": str(observation_path.resolve()),
            "terminalPath": str(terminal_path.resolve()),
            "watchedPaths": sentinel["config"]["watchedPaths"],
        },
    }:
        raise StockHeadlessCustomRunnerBootError("runner_patch_row_rejected")


def read_observation(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError):
        return None
    return value if value == EXPECTED_OBSERVATION else None


def read_terminal(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError):
        return None
    expected_keys = {
        "schema_version",
        "status",
        "failure_stage",
        "session_id_sha256",
        "provider",
        "model",
        "reasoning_effort",
        "allowed_tool_names",
        "conclusion_marked",
        "target_path_sha256",
        "tool_lifecycle",
        "edit_argument_result",
        "request_count",
        "tool_names",
        "tool_result_count",
        "turn_kind",
    }
    if not isinstance(value, dict) or set(value) != expected_keys:
        return None
    fixed = {
        "schema_version": "ariadne.native_harness_tool_result_conclusion_runner_terminal.v1",
        "status": "failed",
        "failure_stage": "factory",
        "session_id_sha256": None,
        "provider": "deepseek-official",
        "model": "deepseek-v4-flash",
        "reasoning_effort": "high",
        "allowed_tool_names": ["edit", "glob", "read"],
        "conclusion_marked": False,
        "tool_lifecycle": {
            "input_result_kind": "unobserved",
            "post_execute_decision_kind": "unobserved",
            "conclusion_request_stage": "not_requested",
            "authoritative_final_result_kind": "unobserved",
            "coordinate": None,
        },
        "edit_argument_result": {"pre_dispatch_decision": "not_observed", "coordinate": None},
        "request_count": 0,
        "tool_names": [],
        "tool_result_count": 0,
        "turn_kind": None,
    }
    if any(value.get(key) != expected for key, expected in fixed.items()):
        return None
    if not isinstance(value["target_path_sha256"], str) or SHA256_TEXT.fullmatch(value["target_path_sha256"]) is None:
        return None
    return value


def deterministic_check(cache_root: Path | None = None) -> dict[str, Any]:
    contract = load_contract()
    payloads = source_payloads(contract)
    seed = stock_boot.accepted_boot._verify_package_seed(contract)
    source_root = stock_boot.accepted_boot.PACKAGE_SEED_ROOT.resolve(strict=True)
    package_root = source_root / "node_modules" / "@deepseek-ai" / "dsh"
    closure = import_closure(contract, package_root)
    root = Path("C:/deterministic/stock-headless-custom-runner-boot")
    profile_dir = root / "home" / "profiles" / "headless"
    initial, changed = build_patch_pair(
        profile_dir=profile_dir,
        readiness_path=root / "readiness.jsonl",
        observation_path=root / "observation.json",
        terminal_path=root / "runner-terminal.json",
    )
    terminal_result = "provider_free_preflight_pass"
    cached_package_count: int
    terminal_paths = (EVIDENCE_PATH, REPORT_PATH, CONSUMED_PATH)
    if any(path.exists() for path in terminal_paths):
        if not all(path.is_file() for path in terminal_paths):
            raise StockHeadlessCustomRunnerBootError("canonical_attempt_output_incomplete")
        evidence = json.loads(EVIDENCE_PATH.read_bytes())
        evidence_schema = json.loads(EVIDENCE_SCHEMA_PATH.read_bytes())
        jsonschema.Draft202012Validator(evidence_schema).validate(evidence)
        consumed = json.loads(CONSUMED_PATH.read_bytes())
        if (
            evidence.get("operation_id") != OPERATION_ID
            or evidence.get("execution_attempt_id") != ATTEMPT_ID
            or evidence.get("result") != "pass"
            or evidence.get("coordinate") != PASS_RESULT
            or evidence.get("observation") != EXPECTED_OBSERVATION
            or evidence.get("launch", {}).get("native_process_count") != 1
            or evidence.get("launch", {}).get("retry_count") != 0
            or evidence.get("cleanup", {}).get("process_absent") is not True
            or evidence.get("cleanup", {}).get("disposable_root_absent") is not True
            or evidence.get("package", {}).get("verified_cached_package_count") != 4
            or consumed
            != {
                "schema_version": "ariadne.native_harness_stock_headless_custom_runner_attempt.v1",
                "operation_id": OPERATION_ID,
                "attempt_id": ATTEMPT_ID,
                "status": "consumed_before_native_launch",
                "retry_count": 0,
                "resume_count": 0,
                "fallback_count": 0,
            }
            or f"- Result: `pass`" not in REPORT_PATH.read_text(encoding="utf-8")
        ):
            raise StockHeadlessCustomRunnerBootError("canonical_attempt_readback_rejected")
        terminal_result = "provider_free_success_readback_pass"
        cached_package_count = evidence["package"]["verified_cached_package_count"]
    else:
        resolved_cache = (cache_root or stock_boot._default_cache_root()).resolve()
        _, cached = stock_boot.verify_cached_packages(contract, resolved_cache)
        cached_package_count = len(cached)
    if any(DISPOSABLE_PARENT.glob("dsh-accepted-guard-boot-*")):
        raise StockHeadlessCustomRunnerBootError("disposable_root_not_absent")
    return {
        "result": terminal_result,
        "contract": contract,
        "source_sha256": {name: sha256_bytes(value) for name, value in payloads.items()},
        "import_closure": closure,
        "verified_cached_package_count": cached_package_count,
        "package_seed": seed,
        "patch_sha256": {"initial": sha256_bytes(initial), "changed": sha256_bytes(changed)},
    }


def _failure_coordinate(
    *,
    process_started: bool,
    readiness_events: list[str],
    hmr_mutation_count: int,
    observation: dict[str, Any] | None,
    terminal: dict[str, Any] | None,
    exit_code: int | None,
    network_attempt_count: int,
    network_ledger_valid: bool,
    source_copies_equal: bool,
    canonical_sources_unchanged: bool,
    seed_unchanged: bool,
    process_absent: bool,
    root_absent: bool,
) -> str | None:
    checks = [
        (process_started, "NATIVE_PROCESS_NOT_STARTED"),
        (readiness_events == READINESS_EVENTS, "READINESS_REJECTED"),
        (hmr_mutation_count == 1, "HMR_MUTATION_REJECTED"),
        (observation == EXPECTED_OBSERVATION, "TYPED_OBSERVATION_REJECTED"),
        (terminal is not None, "RUNNER_TERMINAL_REJECTED"),
        (exit_code == 0, "STOCK_EXIT_REJECTED"),
        (network_ledger_valid and network_attempt_count == 0, "NETWORK_BOUNDARY_REJECTED"),
        (source_copies_equal, "EXECUTION_COPY_REJECTED"),
        (canonical_sources_unchanged, "CANONICAL_SOURCE_MUTATION_REJECTED"),
        (seed_unchanged, "PACKAGE_SEED_MUTATION_REJECTED"),
        (process_absent, "PROCESS_CLEANUP_REJECTED"),
        (root_absent, "ROOT_CLEANUP_REJECTED"),
    ]
    for passed, coordinate in checks:
        if not passed:
            return coordinate
    return None


def _report(evidence: dict[str, Any]) -> str:
    return f"""# Stock-headless to corrected custom runner boot report

- Result: `{evidence['result']}`
- Failure coordinate: `{evidence['failure_classification']}`
- Native process count: `{evidence['launch']['native_process_count']}`
- HMR mutation count: `{evidence['launch']['hmr_mutation_count']}`
- Readiness: `{', '.join(evidence['readiness']['events'])}`
- Distinct roots / root reads / hook installations: `{evidence['observation']['distinct_preset_root_count']}` / `{evidence['observation']['preset_root_reads']}` / `{evidence['observation']['hook_installations']}`
- Structured coordinate: `{evidence['observation']['structured_coordinate']}`
- Runner terminal: `{evidence['terminal']['status']}` / `{evidence['terminal']['failure_stage']}`
- Stock exit: `{evidence['launch']['exit_code']}`
- Model/provider/network requests: `{evidence['provider_boundary']['model_request_count']}` / `{evidence['provider_boundary']['provider_request_count']}` / `{evidence['provider_boundary']['network_attempt_count']}`
- Cleanup: process absent `{str(evidence['cleanup']['process_absent']).lower()}`, root absent `{str(evidence['cleanup']['disposable_root_absent']).lower()}`

This provider-free proof admits only the pinned stock-headless handoff to the
exact corrected integrated runner and accepted guard graph before any target,
DeepSeek turn, model or provider request.
"""


def execute_boot(cache_root: Path | None = None) -> dict[str, Any]:
    check = deterministic_check(cache_root)
    contract = check["contract"]
    candidate_source = _git("rev-parse", "HEAD")
    if FULL_OID.fullmatch(candidate_source) is None or not _ancestor(contract["planning_source"]):
        raise StockHeadlessCustomRunnerBootError("execution_candidate_source_rejected")
    if subprocess.run(
        ["git", "diff", "--quiet", "--"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode != 0:
        raise StockHeadlessCustomRunnerBootError("tracked_worktree_must_be_clean_before_execution")

    payloads = source_payloads(contract)
    canonical_before = {name: sha256_bytes(value) for name, value in payloads.items()}
    resolved_cache = (cache_root or stock_boot._default_cache_root()).resolve()
    _, cached_packages = stock_boot.verify_cached_packages(contract, resolved_cache)
    seed_before = stock_boot.accepted_boot._verify_package_seed(contract)
    parent = DISPOSABLE_PARENT.resolve(strict=True)
    root = Path(tempfile.mkdtemp(prefix="dsh-accepted-guard-boot-", dir=parent)).resolve()
    if root.parent != parent:
        raise StockHeadlessCustomRunnerBootError("disposable_root_escape")

    process: subprocess.Popen[bytes] | None = None
    process_started = False
    process_absent = True
    started: float | None = None
    duration_ms: int | None = None
    launch_started_utc: str | None = None
    exit_code: int | None = None
    exit_mode: str | None = None
    hmr_mutation_count = 0
    removed_environment_names = 0
    readiness_records: list[dict[str, Any]] = []
    observation: dict[str, Any] | None = None
    terminal: dict[str, Any] | None = None
    network_attempt_count = 0
    network_ledger_valid = True
    source_copy_sha256: dict[str, str] = {}
    source_copies_equal = False
    initial_patch = b""
    changed_patch = b""
    installed_source: dict[str, Any] = {}
    installed_versions: dict[str, str] = {}
    install_projection: dict[str, Any] = {}
    caught_after_launch = False

    try:
        home = root / "home"
        profile_dir = home / "profiles" / "headless"
        workspace = root / "workspace"
        proof_dir = root / "installation" / "proof"
        network_guard_path = root / "network-guard.mjs"
        network_path = root / "network.jsonl"
        readiness_path = root / "readiness.jsonl"
        observation_path = root / "observation.json"
        terminal_path = root / "runner-terminal.json"
        workspace.mkdir()
        profile_dir.mkdir(parents=True)
        _write_exclusive(network_guard_path, payloads["network_guard"])
        environment, removed_environment_names = stock_boot.build_child_environment(
            home, network_guard_path, network_path
        )
        package_root, install_projection = stock_boot.accepted_boot._materialize_package_seed(
            root, contract
        )
        installed_source = stock_boot._verify_installed_source(package_root, contract)
        installed_versions = stock_boot.validate_installed_packages(package_root, contract)
        if import_closure(contract, package_root) != contract["expected_import_closure"]:
            raise StockHeadlessCustomRunnerBootError("installed_import_closure_rejected")
        profile_manifest = {
            "name": "dsh-profile-headless",
            "private": True,
            "dependencies": {},
            "dsh": {"profile": {"bundles": ["@deepseek-ai/dsh-base", "@deepseek-ai/dsh-headless"]}},
        }
        _write_exclusive(profile_dir / "package.json", (json.dumps(profile_manifest, indent=2) + "\n").encode())
        _write_exclusive(
            profile_dir / "pnpm-workspace.yaml",
            b"packages:\n  - .\n\nnodeLinker: hoisted\nautoInstallPeers: false\n",
        )
        execution_names = {
            "runner": RUNNER_FILENAME,
            "guard": GUARD_FILENAME,
            "bridge": BRIDGE_FILENAME,
            "sanitizer": SANITIZER_FILENAME,
            "adapter": ADAPTER_FILENAME,
            "readiness_sentinel": "sentinel.mjs",
        }
        for source_name, filename in execution_names.items():
            _write_exclusive(proof_dir / filename, payloads[source_name])
            source_copy_sha256[source_name] = sha256_file(proof_dir / filename)
        source_copies_equal = all(
            source_copy_sha256[name] == contract["source_bindings"][name]["sha256"]
            for name in source_copy_sha256
        )
        if not source_copies_equal:
            raise StockHeadlessCustomRunnerBootError("execution_copy_binding_rejected")
        initial_patch, changed_patch = build_patch_pair(
            profile_dir=profile_dir,
            readiness_path=readiness_path,
            observation_path=observation_path,
            terminal_path=terminal_path,
        )
        patch_path = profile_dir / "cordis.patch.yml"
        _write_exclusive(patch_path, initial_patch)
        node = shutil.which("node")
        if node is None:
            raise StockHeadlessCustomRunnerBootError("node_unavailable")
        command = [
            node,
            contract["launch"]["node_flag"],
            str(package_root / contract["package"]["bin"]),
            *contract["launch"]["profile_args"],
            "provider-free accepted guard graph stock-headless boot proof",
        ]
        _write_exclusive(
            CONSUMED_PATH,
            _canonical(
                {
                    "schema_version": "ariadne.native_harness_stock_headless_custom_runner_attempt.v1",
                    "operation_id": OPERATION_ID,
                    "attempt_id": ATTEMPT_ID,
                    "status": "consumed_before_native_launch",
                    "retry_count": 0,
                    "resume_count": 0,
                    "fallback_count": 0,
                }
            ),
        )
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
            readiness_records = stock_boot.parse_readiness(readiness_path, allow_incomplete=True)
            readiness_events = [record["event"] for record in readiness_records]
            if readiness_events == READINESS_EVENTS and hmr_mutation_count == 0:
                stock_boot.atomic_write(patch_path, changed_patch)
                hmr_mutation_count = 1
            observation = read_observation(observation_path)
            terminal = read_terminal(terminal_path)
            if process.poll() is not None:
                exit_mode = "self_exited_after_or_before_typed_terminal"
                break
            if time.monotonic() >= deadline:
                exit_mode = "controller_deadline_termination"
                break
            time.sleep(stock_boot.POLL_SECONDS)
        if process.poll() is None:
            stock_boot._terminate_process(process)
        exit_code = process.returncode
    except (
        StockHeadlessCustomRunnerBootError,
        stock_boot.IntegratedRunnerBootError,
        stock_boot.accepted_boot.ReboundNativeBootError,
        stock_boot.ProofError,
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
            stock_boot._terminate_process(process)
            exit_code = process.returncode
            process_absent = process.poll() is not None
        try:
            readiness_records = stock_boot.parse_readiness(
                root / "readiness.jsonl", allow_incomplete=False
            )
        except (stock_boot.IntegratedRunnerBootError, OSError, json.JSONDecodeError):
            readiness_records = []
        observation = read_observation(root / "observation.json")
        terminal = read_terminal(root / "runner-terminal.json")
        try:
            network_attempt_count = len(stock_boot._network_attempts(root / "network.jsonl"))
        except (stock_boot.ProofError, OSError, ValueError, json.JSONDecodeError):
            network_ledger_valid = False
        if root.parent != parent:
            raise StockHeadlessCustomRunnerBootError("cleanup_root_escape")
        shutil.rmtree(root)

    root_absent = not root.exists()
    seed_after = stock_boot.accepted_boot._verify_package_seed(contract)
    seed_unchanged = seed_after == seed_before
    canonical_after_payloads = source_payloads(contract)
    canonical_after = {
        name: sha256_bytes(value) for name, value in canonical_after_payloads.items()
    }
    canonical_sources_unchanged = canonical_after == canonical_before
    readiness_events = [record["event"] for record in readiness_records]
    failure = _failure_coordinate(
        process_started=process_started,
        readiness_events=readiness_events,
        hmr_mutation_count=hmr_mutation_count,
        observation=observation,
        terminal=terminal,
        exit_code=exit_code,
        network_attempt_count=network_attempt_count,
        network_ledger_valid=network_ledger_valid,
        source_copies_equal=source_copies_equal,
        canonical_sources_unchanged=canonical_sources_unchanged,
        seed_unchanged=seed_unchanged,
        process_absent=process_absent,
        root_absent=root_absent,
    )
    if caught_after_launch and failure is None:
        failure = "POSTLAUNCH_CONTROLLER_REJECTED"
    result = "pass" if failure is None else "fail"
    safe_observation = observation or {
        key: (False if isinstance(value, bool) else 0 if isinstance(value, int) else None)
        for key, value in EXPECTED_OBSERVATION.items()
    }
    safe_terminal = (
        {
            "status": terminal["status"],
            "failure_stage": terminal["failure_stage"],
            "request_count": terminal["request_count"],
            "tool_result_count": terminal["tool_result_count"],
            "turn_kind": terminal["turn_kind"],
            "conclusion_marked": terminal["conclusion_marked"],
            "target_path_sha256": terminal["target_path_sha256"],
        }
        if terminal is not None
        else {
            "status": None,
            "failure_stage": None,
            "request_count": None,
            "tool_result_count": None,
            "turn_kind": None,
            "conclusion_marked": None,
            "target_path_sha256": None,
        }
    )
    evidence = {
        "schema_version": "ariadne.native_harness_stock_headless_custom_runner_boot_evidence.v1",
        "operation_id": OPERATION_ID,
        "planning_source": contract["planning_source"],
        "candidate_source": candidate_source,
        "execution_attempt_id": ATTEMPT_ID,
        "result": result,
        "coordinate": PASS_RESULT if result == "pass" else None,
        "failure_classification": failure,
        "source_bindings": contract["source_bindings"],
        "import_closure": check["import_closure"],
        "package": {
            "name": contract["package"]["name"],
            "version": contract["package"]["version"],
            "bin": contract["package"]["bin"],
            "installed_source": installed_source,
            "installed_versions": installed_versions,
            "offline_materialisation": install_projection,
            "verified_cached_package_count": len(cached_packages),
            "seed_unchanged": seed_unchanged,
        },
        "launch": {
            "started_at_utc": launch_started_utc,
            "duration_ms": duration_ms,
            "native_process_count": 1 if process_started else 0,
            "retry_count": 0,
            "resume_count": 0,
            "fallback_count": 0,
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
            "execution_copy_sha256": source_copy_sha256,
            "execution_copies_equal": source_copies_equal,
            "canonical_sources_unchanged": canonical_sources_unchanged,
        },
        "readiness": {
            "events": readiness_events,
            "exact_expected_order": readiness_events == READINESS_EVENTS,
        },
        "observation": safe_observation,
        "terminal": safe_terminal,
        "provider_boundary": {
            "credential_environment_names_removed_count": removed_environment_names,
            "target_attempt_count": 0,
            "agent_publication_count": 0,
            "session_count": 0,
            "turn_count": 0,
            "tool_call_count": 0,
            "tool_result_count": 0,
            "broker_process_count": 0,
            "broker_request_count": 0,
            "worker_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "network_attempt_count": network_attempt_count,
            "network_ledger_valid": network_ledger_valid,
            "database_invocation_count": 0,
            "docker_invocation_count": 0,
        },
        "cleanup": {
            "process_absent": process_absent,
            "disposable_root_absent": root_absent,
            "raw_environment_retained": False,
            "raw_logs_retained": False,
            "package_seed_unchanged": seed_unchanged,
        },
    }
    schema = json.loads(EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(evidence)
    _write_exclusive(EVIDENCE_PATH, _canonical(evidence))
    _write_exclusive(REPORT_PATH, _report(evidence).encode())
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
                    "status": projection["result"],
                    "attempt_id": ATTEMPT_ID,
                    "source_sha256": projection["source_sha256"],
                    "import_closure": projection["import_closure"],
                },
                sort_keys=True,
            )
        )
        return 0
    evidence = execute_boot(args.cache_root)
    print(json.dumps({"result": evidence["result"], "coordinate": evidence["coordinate"]}))
    return 0 if evidence["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
