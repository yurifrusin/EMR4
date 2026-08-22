"""Prove the accepted integrated runner loads through one provider-free rc.7 HMR boot."""

from __future__ import annotations

import argparse
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

from scripts import (  # noqa: E402
    deepseek_native_harness_provider_free_rebound_future_runner_stock_headless_hmr_boot_proof as accepted_boot,
)
from scripts.deepseek_native_harness_provider_free_effective_tool_composition_guard import (  # noqa: E402
    _default_cache_root,
    build_guard_source,
    validate_guard_source,
)
from scripts.deepseek_native_harness_provider_free_effective_tool_composition_native_boot_proof import (  # noqa: E402
    sentinel_source,
    validate_installed_packages,
    verify_cached_packages,
)
from scripts.deepseek_native_harness_provider_free_hmr_boot_proof import (  # noqa: E402
    DISPOSABLE_PARENT,
    POLL_SECONDS,
    ProofError,
    _network_attempts,
    _terminate_process,
    _verify_installed_source,
    atomic_write,
    build_child_environment,
    network_guard_source,
    sha256_bytes,
    sha256_file,
)


OPERATION_ID = (
    "deepseek-native-harness-provider-free-edit-coordinate-integrated-runner-"
    "stock-headless-boot-rehearsal"
)
ATTEMPT_ID = "integrated-runner-stock-headless-boot-attempt-001"
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT_PATH = REPO_ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "native-boot-evidence.json"
REPORT_PATH = OPERATION_ROOT / "native-boot-report.md"
EFFICACY_PATH = OPERATION_ROOT / "efficacy-reading.json"
ADAPTER_PATH = OPERATION_ROOT / "integrated-runner-boot-probe.mjs"
INTEGRATED_RUNNER_PATH = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-edit-coordinate-future-runner-integration-rehearsal"
    / "integrated-future-runner.mjs"
)
FOCUSED_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_provider_free_edit_coordinate_integrated_runner_stock_headless_boot_rehearsal.py"
)
PLAN_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_provider_free_edit_coordinate_integrated_runner_stock_headless_boot_rehearsal_plan.py"
)
FULL_OID = re.compile(r"^[0-9a-f]{40}$")
READINESS_EVENTS = ["sentinel_activated", "stock_headless_hmr_ready"]
EXPECTED_EXPORTS = [
    "apply",
    "classifyEditArgumentResult",
    "classifyToolLifecycle",
    "preflightEditArguments",
]
EXPECTED_COORDINATE = "integrated_runner_post_hmr_pre_request_hold"


class IntegratedRunnerBootError(RuntimeError):
    """The integrated-runner native boot failed its closed contract."""


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
        raise IntegratedRunnerBootError("git_resolution_failed")
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


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = json.loads(path.read_bytes())
    schema = json.loads(CONTRACT_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(contract)
    plan_relative = PLAN_PATH.relative_to(REPO_ROOT).as_posix()
    if (
        contract["operation_id"] != OPERATION_ID
        or contract["execution_attempt"]["attempt_id"] != ATTEMPT_ID
        or _git("rev-parse", "--verify", f'{contract["planning_source"]}^{{commit}}')
        != contract["planning_source"]
        or _git("log", "-1", "--format=%H", "--", plan_relative)
        != contract["planning_source"]
    ):
        raise IntegratedRunnerBootError("contract_identity_or_planning_source_invalid")
    if contract["execution_attempt"] != {
        "attempt_id": ATTEMPT_ID,
        "native_process_count": 1,
        "automatic_retry": False,
        "manual_retry": False,
        "resume": False,
    }:
        raise IntegratedRunnerBootError("one_process_latch_invalid")
    if contract["expected_result"] != {
        "coordinate": EXPECTED_COORDINATE,
        "control_load_coordinate": "integrated_edit_controls_loaded",
        "runner_status": "failed",
        "runner_failure_stage": "roots",
        "request_count": 0,
    }:
        raise IntegratedRunnerBootError("expected_result_invalid")
    return contract


def validate_adapter_source(payload: bytes) -> dict[str, Any]:
    source = payload.decode("utf-8")
    required_once = [
        'from "./integrated-future-runner.mjs"',
        'openSync(path, "wx")',
        'coordinate: "integrated_edit_controls_loaded"',
        "return integratedRunner.apply(ctx, config)",
    ]
    if any(source.count(fragment) != 1 for fragment in required_once):
        raise IntegratedRunnerBootError("adapter_closed_delegate_shape_invalid")
    forbidden = [
        "agents.create",
        "sessions.create",
        "fetch(",
        "http.request",
        "https.request",
        "retry",
        "fallback",
    ]
    if any(fragment in source for fragment in forbidden):
        raise IntegratedRunnerBootError("adapter_forbidden_authority_surface")
    if source.count("writeControlLoad(config.controlLoadPath)") != 1:
        raise IntegratedRunnerBootError("adapter_control_load_count_invalid")
    return {"sha256": sha256_bytes(payload), "bytes": len(payload)}


def source_payloads(contract: dict[str, Any]) -> dict[str, bytes]:
    payloads = {
        "integrated_runner": INTEGRATED_RUNNER_PATH.read_bytes(),
        "adapter": ADAPTER_PATH.read_bytes(),
        "effective_tool_guard": build_guard_source(),
        "readiness_sentinel": sentinel_source(),
        "network_guard": network_guard_source(),
    }
    validate_adapter_source(payloads["adapter"])
    validate_guard_source(payloads["effective_tool_guard"])
    observed = {key: sha256_bytes(value) for key, value in payloads.items()}
    observed["integrated_runner_bytes"] = len(payloads["integrated_runner"])
    if observed != contract["source_bindings"]:
        raise IntegratedRunnerBootError("source_binding_mismatch")
    return payloads


def validate_predecessors(contract: dict[str, Any]) -> dict[str, Any]:
    sources = {"planning_source": contract["planning_source"], **contract["accepted_sources"]}
    if any(not _ancestor(value) for value in sources.values()):
        raise IntegratedRunnerBootError("accepted_source_missing_or_not_ancestor")
    paths = {
        "plan_sha256": PLAN_PATH,
        "threat_model_sha256": THREAT_PATH,
        "accepted_stock_boot_controller_sha256": Path(accepted_boot.__file__).resolve(),
        "accepted_stock_boot_contract_sha256": accepted_boot.CONTRACT_PATH,
        "accepted_stock_boot_evidence_sha256": accepted_boot.EVIDENCE_PATH,
    }
    predecessor = {key: sha256_file(path) for key, path in paths.items()}
    if predecessor != contract["predecessor_bytes"]:
        raise IntegratedRunnerBootError("predecessor_digest_mismatch")
    implementation_paths = {
        "controller_sha256": Path(__file__).resolve(),
        "focused_test_sha256": FOCUSED_TEST_PATH,
        "plan_test_sha256": PLAN_TEST_PATH,
        "adapter_sha256": ADAPTER_PATH,
        "contract_schema_sha256": CONTRACT_SCHEMA_PATH,
        "evidence_schema_sha256": EVIDENCE_SCHEMA_PATH,
    }
    implementation = {key: sha256_file(path) for key, path in implementation_paths.items()}
    if implementation != contract["implementation_bytes"]:
        raise IntegratedRunnerBootError("implementation_digest_mismatch")
    return {
        "accepted_sources": sources,
        "predecessor_sha256": predecessor,
        "implementation_sha256": implementation,
    }


def _yaml_path(path: Path) -> str:
    return json.dumps(str(path.resolve()))


def _patch_rows(payload: bytes) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = yaml.safe_load(payload)
    if not isinstance(rows, list):
        raise IntegratedRunnerBootError("patch_not_array")
    direct: list[dict[str, Any]] = []
    inserted: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise IntegratedRunnerBootError("patch_row_invalid")
        if "insert" in row:
            if set(row) != {"insert"} or not isinstance(row["insert"], list):
                raise IntegratedRunnerBootError("patch_insert_invalid")
            inserted.extend(row["insert"])
        else:
            direct.append(row)
    return direct, inserted


def build_patch_pair(
    *,
    profile_dir: Path,
    readiness_path: Path,
    control_load_path: Path,
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
    - id: provider-free-integrated-runner-hmr-sentinel
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
        includeUserRoot: false
    - id: provider-free-integrated-runner-boot-probe
      name: ../../../installation/proof/integrated-runner-boot-probe.mjs
      inject: [hmr, headlessStartup, agents, sessions, agentPresets]
      config:
        controlLoadPath: {_yaml_path(control_load_path)}
        terminalPath: {_yaml_path(terminal_path)}
        task: provider-free inert edit-control boot probe not dispatched
"""
    initial_bytes = common.encode()
    changed_bytes = changed.encode()
    validate_patch_pair(
        initial_bytes,
        changed_bytes,
        control_load_path=control_load_path,
        terminal_path=terminal_path,
    )
    return initial_bytes, changed_bytes


def validate_patch_pair(
    initial: bytes,
    changed: bytes,
    *,
    control_load_path: Path,
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
        raise IntegratedRunnerBootError("disabled_patch_rows_invalid")
    if [row.get("id") for row in initial_inserted] != [
        "provider-free-integrated-runner-hmr-sentinel"
    ]:
        raise IntegratedRunnerBootError("initial_patch_invalid")
    if [row.get("id") for row in changed_inserted] != [
        "provider-free-integrated-runner-hmr-sentinel",
        "agent-presets",
        "provider-free-integrated-runner-boot-probe",
    ] or changed_inserted[:1] != initial_inserted:
        raise IntegratedRunnerBootError("changed_patch_roster_invalid")
    if changed_inserted[1] != {
        "id": "agent-presets",
        "name": "@deepseek-ai/dsh-agent-presets",
        "config": {"default": "standard", "includeUserRoot": False},
    }:
        raise IntegratedRunnerBootError("deliberate_single_root_config_invalid")
    runner = changed_inserted[2]
    if runner != {
        "id": "provider-free-integrated-runner-boot-probe",
        "name": "../../../installation/proof/integrated-runner-boot-probe.mjs",
        "inject": ["hmr", "headlessStartup", "agents", "sessions", "agentPresets"],
        "config": {
            "controlLoadPath": str(control_load_path.resolve()),
            "terminalPath": str(terminal_path.resolve()),
            "task": "provider-free inert edit-control boot probe not dispatched",
        },
    }:
        raise IntegratedRunnerBootError("integrated_runner_patch_row_invalid")


def _read_json_exact(path: Path, expected_keys: set[str]) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(value, dict) or set(value) != expected_keys:
        return None
    return value


def read_control_load(path: Path) -> dict[str, Any] | None:
    value = _read_json_exact(
        path,
        {
            "schema_version",
            "coordinate",
            "exports",
            "apply_loaded",
            "preflight_edit_arguments_loaded",
            "classify_edit_argument_result_loaded",
        },
    )
    expected = {
        "schema_version": "ariadne.native_harness_integrated_edit_controls_loaded.v1",
        "coordinate": "integrated_edit_controls_loaded",
        "exports": EXPECTED_EXPORTS,
        "apply_loaded": True,
        "preflight_edit_arguments_loaded": True,
        "classify_edit_argument_result_loaded": True,
    }
    return value if value == expected else None


def read_runner_terminal(path: Path) -> dict[str, Any] | None:
    value = _read_json_exact(
        path,
        {
            "schema_version",
            "status",
            "failure_stage",
            "session_id_sha256",
            "provider",
            "model",
            "reasoning_effort",
            "allowed_tool_names",
            "target_path_sha256",
            "tool_lifecycle",
            "edit_argument_result",
            "request_count",
            "tool_names",
            "tool_result_count",
            "turn_kind",
        },
    )
    if value is None:
        return None
    if (
        value["schema_version"]
        != "ariadne.native_harness_tool_result_conclusion_runner_terminal.v1"
        or value["status"] != "failed"
        or value["failure_stage"] != "roots"
        or value["session_id_sha256"] is not None
        or value["provider"] != "deepseek-official"
        or value["model"] != "deepseek-v4-flash"
        or value["reasoning_effort"] != "high"
        or value["allowed_tool_names"] != ["edit", "glob", "read"]
        or not isinstance(value["target_path_sha256"], str)
        or value["request_count"] != 0
        or value["tool_names"] != []
        or value["tool_result_count"] != 0
        or value["turn_kind"] is not None
        or value["tool_lifecycle"]
        != {
            "input_result_kind": "unobserved",
            "post_execute_decision_kind": "unobserved",
            "conclusion_request_stage": "not_requested",
            "authoritative_final_result_kind": "unobserved",
            "coordinate": None,
        }
        or value["edit_argument_result"]
        != {"pre_dispatch_decision": "not_observed", "coordinate": None}
    ):
        return None
    return value


def parse_readiness(path: Path, *, allow_incomplete: bool) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_bytes().splitlines(keepends=True)
    records: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        if not line.endswith(b"\n"):
            if allow_incomplete and index == len(lines) - 1:
                break
            raise IntegratedRunnerBootError("readiness_partial_line")
        record = json.loads(line)
        if record != {
            "schema_version": "ariadne.deepseek_native_harness_effective_tool_native_boot_event.v1",
            "sequence": len(records) + 1,
            "event": READINESS_EVENTS[len(records)],
        }:
            raise IntegratedRunnerBootError("readiness_record_invalid")
        records.append(record)
        if len(records) > len(READINESS_EVENTS):
            raise IntegratedRunnerBootError("readiness_surplus")
    return records


def _failure_coordinate(
    *,
    process_started: bool,
    readiness_events: list[str],
    hmr_mutation_count: int,
    control_load: dict[str, Any] | None,
    terminal: dict[str, Any] | None,
    network_attempt_count: int,
    network_ledger_valid: bool,
    source_copies_equal: bool,
    process_absent: bool,
    root_absent: bool,
    seed_unchanged: bool,
    canonical_runner_unchanged: bool,
) -> str | None:
    if not process_started:
        return "PRELAUNCH_REJECTED"
    if not network_ledger_valid or network_attempt_count != 0:
        return "NETWORK_BOUNDARY_REJECTED"
    if readiness_events != READINESS_EVENTS:
        return "READINESS_REJECTED"
    if hmr_mutation_count != 1:
        return "HMR_MUTATION_REJECTED"
    if control_load is None:
        return "INTEGRATED_CONTROL_LOAD_REJECTED"
    if terminal is None:
        return "ROOTS_STAGE_TERMINAL_REJECTED"
    if not source_copies_equal:
        return "EXECUTION_COPY_REJECTED"
    if not seed_unchanged or not canonical_runner_unchanged:
        return "ACCEPTED_SOURCE_MUTATION_REJECTED"
    if not process_absent or not root_absent:
        return "CLEANUP_REJECTED"
    return None


def deterministic_check(cache_root: Path | None = None) -> dict[str, Any]:
    contract = load_contract()
    predecessor = validate_predecessors(contract)
    payloads = source_payloads(contract)
    resolved_cache = (cache_root or _default_cache_root()).resolve()
    _, cached = verify_cached_packages(contract, resolved_cache)
    seed = accepted_boot._verify_package_seed(contract)
    root = Path("C:/deterministic/integrated-runner-stock-headless-boot")
    profile_dir = root / "home" / "profiles" / "headless"
    initial, changed = build_patch_pair(
        profile_dir=profile_dir,
        readiness_path=root / "readiness.jsonl",
        control_load_path=root / "integrated-edit-controls-loaded.json",
        terminal_path=root / "runner-terminal.json",
    )
    return {
        "contract": contract,
        "predecessor": predecessor,
        "source_sha256": {key: sha256_bytes(value) for key, value in payloads.items()},
        "patch_sha256": {"initial": sha256_bytes(initial), "changed": sha256_bytes(changed)},
        "verified_cached_package_count": len(cached),
        "package_seed": seed,
    }


def _render_report(evidence: dict[str, Any]) -> str:
    return f"""# Integrated runner stock-headless boot report

- Result: `{evidence['result']}`
- Coordinate: `{evidence['coordinate']}`
- Candidate: `{evidence['candidate_source']}`
- Native process count: `{evidence['launch']['native_process_count']}`
- HMR mutation count: `{evidence['launch']['hmr_mutation_count']}`
- Readiness: `{', '.join(evidence['readiness']['events'])}`
- Control load: `{evidence['control_load']['coordinate']}`
- Runner terminal: `{evidence['runner_terminal']['status']}` at `{evidence['runner_terminal']['failure_stage']}`
- Model/provider requests: `{evidence['provider_boundary']['model_request_count']}` / `{evidence['provider_boundary']['provider_request_count']}`
- Network attempts: `{evidence['provider_boundary']['network_attempt_count']}`
- Cleanup: process absent `{str(evidence['cleanup']['process_absent']).lower()}`, root absent `{str(evidence['cleanup']['disposable_root_absent']).lower()}`

The exact accepted integrated runner and its typed edit controls loaded through
one real rc.7 stock-headless HMR mutation. The deliberately single-root preset
roster stopped the runner at its closed `roots` stage before agent creation or
any worker, model, provider, broker, session, turn, tool or network request.
"""


def _efficacy(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "ariadne.parallelism_efficacy_reading.v1",
        "operation_id": OPERATION_ID,
        "result": evidence["result"],
        "deepseek": {
            "disposition": "declined",
            "rationale": "Proof stops before worker, model and provider request.",
            "owned_work_package": None,
        },
        "gemini": {
            "disposition": "declined_after_deterministic_evidence",
            "rationale": "Typed native lifecycle evidence left no material loading ambiguity.",
            "owned_work_package": None,
        },
        "native_subagents": {
            "disposition": "declined",
            "rationale": "Developer policy prohibits delegation and process custody is serial.",
            "owned_work_package": None,
        },
        "serial_owner": "gpt-sol",
        "coordinate": evidence["coordinate"],
    }


def execute_boot(cache_root: Path | None = None) -> dict[str, Any]:
    if any(path.exists() for path in (EVIDENCE_PATH, REPORT_PATH, EFFICACY_PATH)):
        raise IntegratedRunnerBootError("canonical_attempt_output_already_exists")
    check = deterministic_check(cache_root)
    contract = check["contract"]
    candidate_source = _git("rev-parse", "HEAD")
    if FULL_OID.fullmatch(candidate_source) is None or not _ancestor(contract["planning_source"]):
        raise IntegratedRunnerBootError("execution_candidate_source_invalid")
    if subprocess.run(
        ["git", "diff", "--quiet", "--"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode != 0:
        raise IntegratedRunnerBootError("tracked_worktree_must_be_clean_before_execution")

    payloads = source_payloads(contract)
    canonical_runner_before = sha256_file(INTEGRATED_RUNNER_PATH)
    resolved_cache = (cache_root or _default_cache_root()).resolve()
    _, cached_packages = verify_cached_packages(contract, resolved_cache)
    parent = DISPOSABLE_PARENT.resolve()
    if not parent.is_dir():
        raise IntegratedRunnerBootError("disposable_parent_missing")
    root = Path(tempfile.mkdtemp(prefix="dsh-integrated-runner-boot-", dir=parent)).resolve()
    if root.parent != parent:
        raise IntegratedRunnerBootError("disposable_root_escape")

    process: subprocess.Popen[bytes] | None = None
    process_started = False
    process_absent = True
    started: float | None = None
    launch_started_utc: str | None = None
    duration_ms: int | None = None
    exit_code: int | None = None
    exit_mode: str | None = None
    hmr_mutation_count = 0
    removed_environment_names = 0
    readiness_records: list[dict[str, Any]] = []
    control_load: dict[str, Any] | None = None
    terminal: dict[str, Any] | None = None
    network_attempt_count = 0
    network_ledger_valid = True
    installed_source: dict[str, Any] = {}
    installed_versions: dict[str, str] = {}
    install_projection: dict[str, Any] = {}
    source_copy_sha256: dict[str, str] = {}
    source_copies_equal = False
    initial_patch = b""
    changed_patch = b""
    caught_after_launch = False

    try:
        home = root / "home"
        profile_dir = home / "profiles" / "headless"
        workspace = root / "workspace"
        proof_dir = root / "installation" / "proof"
        network_guard_path = root / "network-guard.mjs"
        network_path = root / "network.jsonl"
        readiness_path = root / "readiness.jsonl"
        control_load_path = root / "integrated-edit-controls-loaded.json"
        terminal_path = root / "runner-terminal.json"
        workspace.mkdir()
        profile_dir.mkdir(parents=True)
        _write_exclusive(network_guard_path, payloads["network_guard"])
        environment, removed_environment_names = build_child_environment(
            home, network_guard_path, network_path
        )
        package_root, install_projection = accepted_boot._materialize_package_seed(
            root, contract
        )
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
        for name, source_key in (
            ("integrated-future-runner.mjs", "integrated_runner"),
            ("integrated-runner-boot-probe.mjs", "adapter"),
            ("effective-tool-guard.mjs", "effective_tool_guard"),
            ("sentinel.mjs", "readiness_sentinel"),
        ):
            _write_exclusive(proof_dir / name, payloads[source_key])
            source_copy_sha256[source_key] = sha256_file(proof_dir / name)
        source_copies_equal = all(
            source_copy_sha256[key] == contract["source_bindings"][key]
            for key in source_copy_sha256
        )
        if not source_copies_equal:
            raise IntegratedRunnerBootError("execution_copy_digest_mismatch")

        initial_patch, changed_patch = build_patch_pair(
            profile_dir=profile_dir,
            readiness_path=readiness_path,
            control_load_path=control_load_path,
            terminal_path=terminal_path,
        )
        patch_path = profile_dir / "cordis.patch.yml"
        _write_exclusive(patch_path, initial_patch)
        node = shutil.which("node")
        if node is None:
            raise IntegratedRunnerBootError("node_not_found")
        command = [
            node,
            contract["launch"]["node_flag"],
            str(package_root / contract["package"]["bin"]),
            *contract["launch"]["profile_args"],
            "provider-free integrated runner stock-headless boot proof",
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
            readiness_records = parse_readiness(readiness_path, allow_incomplete=True)
            events = [record["event"] for record in readiness_records]
            if events == READINESS_EVENTS and hmr_mutation_count == 0:
                atomic_write(patch_path, changed_patch)
                hmr_mutation_count = 1
            control_load = read_control_load(control_load_path)
            terminal = read_runner_terminal(terminal_path)
            if control_load is not None and terminal is not None:
                break
            if process.poll() is not None:
                exit_mode = "self_exited_after_or_before_typed_terminal"
                break
            if time.monotonic() >= deadline:
                exit_mode = "controller_deadline_termination"
                break
            time.sleep(POLL_SECONDS)
        if process.poll() is None:
            _terminate_process(process)
            exit_mode = exit_mode or "controller_terminated_after_typed_terminal"
        else:
            exit_mode = exit_mode or "self_exited_after_typed_terminal"
        exit_code = process.returncode
    except (
        IntegratedRunnerBootError,
        accepted_boot.ReboundNativeBootError,
        ProofError,
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
        try:
            readiness_records = parse_readiness(root / "readiness.jsonl", allow_incomplete=False)
        except (IntegratedRunnerBootError, OSError, json.JSONDecodeError):
            readiness_records = []
        control_load = read_control_load(root / "integrated-edit-controls-loaded.json")
        terminal = read_runner_terminal(root / "runner-terminal.json")
        try:
            network_attempt_count = len(_network_attempts(root / "network.jsonl"))
        except (ProofError, OSError, ValueError, json.JSONDecodeError):
            network_ledger_valid = False
        if root.parent != parent:
            raise IntegratedRunnerBootError("cleanup_root_escape")
        shutil.rmtree(root)

    root_absent = not root.exists()
    if not process_started:
        raise IntegratedRunnerBootError("prelaunch_validation_failed")
    seed_after = accepted_boot._verify_package_seed(contract)
    seed_unchanged = seed_after == check["package_seed"]
    canonical_runner_after = sha256_file(INTEGRATED_RUNNER_PATH)
    canonical_runner_unchanged = (
        canonical_runner_before
        == canonical_runner_after
        == contract["source_bindings"]["integrated_runner"]
    )
    readiness_events = [record["event"] for record in readiness_records]
    failure = _failure_coordinate(
        process_started=process_started,
        readiness_events=readiness_events,
        hmr_mutation_count=hmr_mutation_count,
        control_load=control_load,
        terminal=terminal,
        network_attempt_count=network_attempt_count,
        network_ledger_valid=network_ledger_valid,
        source_copies_equal=source_copies_equal,
        process_absent=process_absent,
        root_absent=root_absent,
        seed_unchanged=seed_unchanged,
        canonical_runner_unchanged=canonical_runner_unchanged,
    )
    if caught_after_launch and failure is None:
        failure = "POSTLAUNCH_CONTROLLER_REJECTED"
    result = "pass" if failure is None else "fail"
    evidence = {
        "schema_version": "ariadne.native_harness_integrated_runner_stock_headless_boot_evidence.v1",
        "operation_id": OPERATION_ID,
        "planning_source": contract["planning_source"],
        "candidate_source": candidate_source,
        "execution_attempt_id": ATTEMPT_ID,
        "result": result,
        "coordinate": EXPECTED_COORDINATE if result == "pass" else None,
        "failure_classification": failure,
        "source_bindings": contract["source_bindings"],
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
            "native_process_count": 1,
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
            "canonical_runner_unchanged": canonical_runner_unchanged,
            "single_root_mismatch_deliberate": True,
        },
        "readiness": {
            "events": readiness_events,
            "exact_expected_order": readiness_events == READINESS_EVENTS,
        },
        "control_load": control_load,
        "runner_terminal": terminal,
        "provider_boundary": {
            "credential_environment_names_removed_count": removed_environment_names,
            "network_attempt_count": network_attempt_count,
            "network_ledger_valid": network_ledger_valid,
            "agent_create_count": 0,
            "session_count": 0,
            "turn_count": 0,
            "tool_call_count": 0,
            "tool_result_count": 0,
            "broker_process_count": 0,
            "broker_request_count": 0,
            "worker_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
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
                    "attempt_id": ATTEMPT_ID,
                    "source_sha256": projection["source_sha256"],
                    "package_seed": projection["package_seed"],
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
