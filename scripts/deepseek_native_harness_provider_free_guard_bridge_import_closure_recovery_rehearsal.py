"""Run one closed package-unloaded guard-bridge import-closure recovery."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import posixpath
import re
import subprocess
import sys
import tempfile
from typing import Any
from zoneinfo import ZoneInfo

import jsonschema

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orchestration_harness.git_object_resolution import resolve_commit_source
from orchestration_harness.git_refs_snapshot import build_git_refs_snapshot
from scripts import (
    deepseek_native_harness_provider_free_preset_mount_root_service_forwarding_package_unloaded_guard_bridge_module_graph_rehearsal as predecessor,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-guard-bridge-import-closure-"
    "recovery-rehearsal"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT_PATH = REPO_ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
PROCESS_ENVELOPE_SCHEMA_PATH = OPERATION_ROOT / "process-envelope.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
FAILURE_TERMINAL_SCHEMA_PATH = OPERATION_ROOT / "failure-terminal.schema.json"
PROCESS_ENVELOPE_PATH = OPERATION_ROOT / "attempt-001-process-envelope.json"
EVIDENCE_PATH = OPERATION_ROOT / "import-closure-recovery-evidence.json"
REPORT_PATH = OPERATION_ROOT / "import-closure-recovery-report.md"
FAILURE_TERMINAL_PATH = OPERATION_ROOT / "attempt-001-failure-terminal.json"
FOCUSED_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_provider_free_guard_bridge_import_closure_recovery_rehearsal.py"
)
PREDECESSOR_CONTROLLER_PATH = Path(predecessor.__file__).resolve()
PREDECESSOR_DIAGNOSIS_PATH = (
    predecessor.OPERATION_ROOT / "attempt-001-source-diagnosis.json"
)
PREDECESSOR_ENVELOPE_PATH = predecessor.PROCESS_ENVELOPE_PATH
PREDECESSOR_CLOSEOUT_PATH = (
    REPO_ROOT
    / "docs"
    / "deepseek-native-harness-provider-free-preset-mount-root-service-forwarding-package-unloaded-guard-bridge-module-graph-rehearsal-closeout.md"
)

GUARD_FILENAME = "effective-tool-guard.mjs"
BRIDGE_TARGET_FILENAME = "preset-mount-sanitizer-runner-bridge.mjs"
PREDECESSOR_BRIDGE_FILENAME = predecessor.BRIDGE_FILENAME
SANITIZER_FILENAME = predecessor.SANITIZER_FILENAME
FIXTURE_FILENAME = "package_unloaded_guard_bridge_import_closure_fixture.mjs"
SCOPE_STUB_MANIFEST = predecessor.SCOPE_STUB_MANIFEST
SCOPE_STUB_SOURCE = predecessor.SCOPE_STUB_SOURCE
PRESETS_STUB_MANIFEST = predecessor.PRESETS_STUB_MANIFEST
PRESETS_STUB_SOURCE = predecessor.PRESETS_STUB_SOURCE
MATERIALIZED_RELATIVE_PATHS = (
    GUARD_FILENAME,
    BRIDGE_TARGET_FILENAME,
    SANITIZER_FILENAME,
    FIXTURE_FILENAME,
    SCOPE_STUB_MANIFEST,
    SCOPE_STUB_SOURCE,
    PRESETS_STUB_MANIFEST,
    PRESETS_STUB_SOURCE,
)
EXPECTED_RELATIVE_EDGES = (
    (FIXTURE_FILENAME, f"./{GUARD_FILENAME}", GUARD_FILENAME),
    (
        GUARD_FILENAME,
        f"./{BRIDGE_TARGET_FILENAME}",
        BRIDGE_TARGET_FILENAME,
    ),
    (
        BRIDGE_TARGET_FILENAME,
        f"./{SANITIZER_FILENAME}",
        SANITIZER_FILENAME,
    ),
)
EXPECTED_BARE_EDGES = (
    (
        GUARD_FILENAME,
        "@deepseek-ai/dsh-scope",
        SCOPE_STUB_MANIFEST,
        SCOPE_STUB_SOURCE,
    ),
    (
        GUARD_FILENAME,
        "@deepseek-ai/dsh-agent-presets",
        PRESETS_STUB_MANIFEST,
        PRESETS_STUB_SOURCE,
    ),
)
PATCH_MARKER_COUNT = 103
EXPECTED_PROTECTED_COMMIT = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
PROTECTED_REFS = predecessor.PROTECTED_REFS
WINDOWS_ENVIRONMENT_KEYS = predecessor.WINDOWS_ENVIRONMENT_KEYS
FORBIDDEN_ENVIRONMENT_KEYS = predecessor.FORBIDDEN_ENVIRONMENT_KEYS
FULL_OID = re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])")
STATIC_FROM_SPECIFIER = re.compile(
    r"(?ms)^[ \t]*(?:import|export)\b(?:(?!;).)*?\bfrom\s*"
    r"(?P<quote>['\"])(?P<specifier>[^'\"]+)(?P=quote)\s*;"
)
STATIC_SIDE_EFFECT_SPECIFIER = re.compile(
    r"(?m)^[ \t]*import\s*(?P<quote>['\"])(?P<specifier>[^'\"]+)"
    r"(?P=quote)\s*;"
)
IMPORT_START = re.compile(r"(?m)^[ \t]*import\b")
DYNAMIC_OR_COMMONJS = re.compile(r"\b(?:import|require)\s*\(")

CONTRACT_VERSION = (
    "ariadne.native_harness_guard_bridge_import_closure_recovery_contract.v1"
)
PROCESS_ENVELOPE_VERSION = (
    "ariadne.native_harness_guard_bridge_import_closure_process_envelope.v1"
)
EVIDENCE_VERSION = (
    "ariadne.native_harness_guard_bridge_import_closure_recovery_evidence.v1"
)
FAILURE_TERMINAL_VERSION = (
    "ariadne.native_harness_guard_bridge_import_closure_failure_terminal.v1"
)
CLOSED_RESULTS = [
    "package_unloaded_guard_bridge_import_closure_recovery_pass",
    "import_closure_preflight_rejected",
    "import_closure_process_terminal",
    "import_closure_result_rejected",
]
ADMITTED_RESULT = CLOSED_RESULTS[0]
ZERO_COUNTERS = predecessor.ZERO_COUNTERS
OUTPUT_PATHS = (
    PROCESS_ENVELOPE_PATH,
    EVIDENCE_PATH,
    REPORT_PATH,
    FAILURE_TERMINAL_PATH,
)
ImportClosureError = predecessor.ModuleGraphError


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def source_entry(payload: bytes) -> dict[str, Any]:
    return {"bytes": len(payload), "sha256": sha256_bytes(payload)}


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ImportClosureError(f"json_unreadable:{path.name}") from error
    if not isinstance(value, dict):
        raise ImportClosureError(f"json_object_required:{path.name}")
    return value


def _validate(schema_path: Path, value: object, code: str) -> None:
    schema = _load_object(schema_path)
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(value)
    except (jsonschema.SchemaError, jsonschema.ValidationError) as error:
        raise ImportClosureError(code) from error


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
        raise ImportClosureError("git_resolution_failed")
    return completed.stdout.strip()


def documentation_bindings() -> dict[str, str]:
    return {
        "plan_sha256": sha256_bytes(PLAN_PATH.read_bytes()),
        "threat_model_sha256": sha256_bytes(THREAT_PATH.read_bytes()),
    }


def predecessor_bindings() -> dict[str, str]:
    paths = {
        "predecessor_controller_sha256": PREDECESSOR_CONTROLLER_PATH,
        "predecessor_process_envelope_sha256": PREDECESSOR_ENVELOPE_PATH,
        "predecessor_source_diagnosis_sha256": PREDECESSOR_DIAGNOSIS_PATH,
        "predecessor_closeout_sha256": PREDECESSOR_CLOSEOUT_PATH,
    }
    return {name: sha256_bytes(path.read_bytes()) for name, path in paths.items()}


def implementation_bindings() -> dict[str, str]:
    paths = {
        "controller_sha256": Path(__file__).resolve(),
        "focused_test_sha256": FOCUSED_TEST_PATH,
        "contract_schema_sha256": CONTRACT_SCHEMA_PATH,
        "process_envelope_schema_sha256": PROCESS_ENVELOPE_SCHEMA_PATH,
        "evidence_schema_sha256": EVIDENCE_SCHEMA_PATH,
        "failure_terminal_schema_sha256": FAILURE_TERMINAL_SCHEMA_PATH,
    }
    return {name: sha256_bytes(path.read_bytes()) for name, path in paths.items()}


def accepted_graph_sources() -> tuple[dict[str, bytes], dict[str, dict[str, Any]]]:
    sources, inventory = predecessor.accepted_graph_sources()
    expected = {
        "derived_guard": {
            "bytes": 4501,
            "sha256": "76029da0f9c030651fd10c0df16f4e75e86b2269d7560af7f94c74680f8598b9",
        },
        "derived_bridge": {
            "bytes": 1661,
            "sha256": "3a49b28174eeefd77d7efe0a00498901ac6636b637ed9dfe60aba46980df1d0b",
        },
        "accepted_sanitizer": {
            "bytes": 2439,
            "sha256": "12552925a600dc951afc30b9a738746499c7e2f4cefc9962bc05fb06780f158f",
        },
    }
    if inventory != expected:
        raise ImportClosureError("accepted_source_binding_rejected")
    return sources, inventory


def fixture_correction() -> tuple[bytes, dict[str, Any]]:
    predecessor_source = predecessor.fixture_source()
    try:
        decoded = predecessor_source.decode("utf-8", errors="strict")
    except UnicodeError as error:
        raise ImportClosureError("fixture_source_rejected") from error
    lines = decoded.splitlines(keepends=True)
    marker_lines = [index for index, line in enumerate(lines, 1) if line.startswith("+")]
    if len(marker_lines) != PATCH_MARKER_COUNT:
        raise ImportClosureError("fixture_patch_marker_reading_rejected")
    corrected = "".join(line[1:] if line.startswith("+") else line for line in lines)
    if (
        "\r" in corrected
        or any(line.startswith("+") for line in corrected.splitlines())
        or not corrected.endswith("\n")
    ):
        raise ImportClosureError("fixture_source_rejected")
    forbidden = (
        "process.env",
        "node:fs",
        "node:child_process",
        "node:http",
        "node:https",
        "fetch(",
        ".message",
        ".stack",
        ".cause",
    )
    if any(token in corrected for token in forbidden):
        raise ImportClosureError("fixture_source_forbidden_coordinate")
    payload = corrected.encode("utf-8")
    return payload, {
        "predecessor_fixture_source": source_entry(predecessor_source),
        "corrected_fixture_source": source_entry(payload),
        "leading_patch_marker_count_removed": len(marker_lines),
        "leading_patch_marker_absent_after_correction": True,
        "carriage_return_absent": True,
    }


def fixture_source() -> bytes:
    return fixture_correction()[0]


def package_stub_sources() -> dict[str, bytes]:
    return predecessor.package_stub_sources()


def executable_module_sources() -> dict[str, bytes]:
    accepted, _ = accepted_graph_sources()
    return {
        FIXTURE_FILENAME: fixture_source(),
        GUARD_FILENAME: accepted["derived_guard"],
        BRIDGE_TARGET_FILENAME: accepted["derived_bridge"],
        SANITIZER_FILENAME: accepted["accepted_sanitizer"],
    }


def _static_specifiers(payload: bytes) -> list[str]:
    try:
        source = payload.decode("utf-8", errors="strict")
    except UnicodeError as error:
        raise ImportClosureError("import_source_utf8_rejected") from error
    if "\r" in source or DYNAMIC_OR_COMMONJS.search(source):
        raise ImportClosureError("import_source_coordinate_rejected")
    matches = [*STATIC_FROM_SPECIFIER.finditer(source)]
    matches.extend(STATIC_SIDE_EFFECT_SPECIFIER.finditer(source))
    matches.sort(key=lambda item: item.start())
    if [match.start() for match in IMPORT_START.finditer(source)] != [
        match.start() for match in matches
    ]:
        raise ImportClosureError("static_import_parse_rejected")
    return [match.group("specifier") for match in matches]


def import_closure(
    modules: dict[str, bytes] | None = None,
    stubs: dict[str, bytes] | None = None,
) -> dict[str, Any]:
    module_map = executable_module_sources() if modules is None else modules
    stub_map = package_stub_sources() if stubs is None else stubs
    relative_edges: list[dict[str, Any]] = []
    bare_edges: list[dict[str, Any]] = []
    bare_targets = {
        specifier: (manifest, source)
        for _, specifier, manifest, source in EXPECTED_BARE_EDGES
    }
    for importer, payload in module_map.items():
        for specifier in _static_specifiers(payload):
            if "\\" in specifier or specifier.startswith(("/", "file:", "http:", "https:")):
                raise ImportClosureError("import_specifier_coordinate_rejected")
            if specifier.startswith(("./", "../")):
                target = posixpath.normpath(
                    posixpath.join(posixpath.dirname(importer), specifier)
                )
                if (
                    target in {"", ".", ".."}
                    or target.startswith("../")
                    or posixpath.isabs(target)
                    or target not in module_map
                ):
                    raise ImportClosureError("relative_import_target_rejected")
                relative_edges.append(
                    {
                        "importer": importer,
                        "specifier": specifier,
                        "resolved_target": target,
                        "target_source": source_entry(module_map[target]),
                    }
                )
                continue
            if specifier not in bare_targets:
                raise ImportClosureError("bare_import_specifier_rejected")
            manifest, source = bare_targets[specifier]
            if manifest not in stub_map or source not in stub_map:
                raise ImportClosureError("bare_import_target_rejected")
            bare_edges.append(
                {
                    "importer": importer,
                    "specifier": specifier,
                    "resolved_manifest": manifest,
                    "resolved_source": source,
                }
            )
    expected_relative = [
        {
            "importer": importer,
            "specifier": specifier,
            "resolved_target": target,
            "target_source": source_entry(module_map[target]),
        }
        for importer, specifier, target in EXPECTED_RELATIVE_EDGES
    ]
    expected_bare = [
        {
            "importer": importer,
            "specifier": specifier,
            "resolved_manifest": manifest,
            "resolved_source": source,
        }
        for importer, specifier, manifest, source in EXPECTED_BARE_EDGES
    ]
    if relative_edges != expected_relative or bare_edges != expected_bare:
        raise ImportClosureError("import_closure_edge_set_rejected")
    return {
        "relative_edges": relative_edges,
        "bare_edges": bare_edges,
        "relative_edge_count": len(relative_edges),
        "bare_edge_count": len(bare_edges),
        "all_resolved_targets_materialized": True,
    }


def materialized_sources() -> dict[str, bytes]:
    modules = executable_module_sources()
    result = {
        GUARD_FILENAME: modules[GUARD_FILENAME],
        BRIDGE_TARGET_FILENAME: modules[BRIDGE_TARGET_FILENAME],
        SANITIZER_FILENAME: modules[SANITIZER_FILENAME],
        FIXTURE_FILENAME: modules[FIXTURE_FILENAME],
        **package_stub_sources(),
    }
    if tuple(result) != MATERIALIZED_RELATIVE_PATHS:
        raise ImportClosureError("materialized_inventory_rejected")
    if PREDECESSOR_BRIDGE_FILENAME in result:
        raise ImportClosureError("predecessor_bridge_basename_rejected")
    if any(
        "runner" in path.lower()
        for path in result
        if path != BRIDGE_TARGET_FILENAME
    ):
        raise ImportClosureError("derived_runner_materialization_rejected")
    return result


def contract_value() -> dict[str, Any]:
    _, source_inventory = accepted_graph_sources()
    stubs = package_stub_sources()
    _, correction = fixture_correction()
    closure = import_closure()
    return {
        "schema_version": CONTRACT_VERSION,
        "operation_id": OPERATION_ID,
        "git_binding_policy": {
            "mode": "machine_resolved_only",
            "plan_path": PLAN_PATH.relative_to(REPO_ROOT).as_posix(),
            "controller_path": Path(__file__)
            .resolve()
            .relative_to(REPO_ROOT)
            .as_posix(),
            "caller_authored_object_id_count": 0,
        },
        "closed_results": CLOSED_RESULTS,
        "windows_environment_keys": list(WINDOWS_ENVIRONMENT_KEYS),
        "case_ids": ["success", "missing_service", "missing_mount"],
        "materialized_relative_paths": list(MATERIALIZED_RELATIVE_PATHS),
        "required_zero_counters": list(ZERO_COUNTERS),
        "documentation_bindings": documentation_bindings(),
        "predecessor_bindings": predecessor_bindings(),
        "implementation_bindings": implementation_bindings(),
        "accepted_source_inventory": source_inventory,
        "stub_source_inventory": {
            path: source_entry(payload) for path, payload in stubs.items()
        },
        "fixture_correction": correction,
        "import_closure": closure,
        "expected_result": predecessor.exact_fixture_outcome(),
        "claim_boundary": {
            "static_import_closure_proved": True,
            "package_unloaded_guard_bridge_graph_only": True,
            "predecessor_retry": False,
            "derived_runner_proved": False,
            "installed_package_loaded": False,
            "native_harness_proved": False,
            "worker_model_provider_executed": False,
            "retry_authorized": False,
            "product_authority": False,
        },
    }


def write_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    value = contract_value()
    _validate(CONTRACT_SCHEMA_PATH, value, "contract_schema_rejected")
    if FULL_OID.search(json.dumps(value, sort_keys=True)) is not None:
        raise ImportClosureError("caller_authored_git_object_id_rejected")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))
    return value


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = _load_object(path)
    _validate(CONTRACT_SCHEMA_PATH, contract, "contract_schema_rejected")
    if FULL_OID.search(json.dumps(contract, sort_keys=True)) is not None:
        raise ImportClosureError("caller_authored_git_object_id_rejected")
    if contract != contract_value():
        raise ImportClosureError("contract_rejected")
    return contract


def machine_git_bindings() -> dict[str, Any]:
    snapshot = build_git_refs_snapshot(
        repo_root=REPO_ROOT,
        expected_protected_commit=EXPECTED_PROTECTED_COMMIT,
        protected_refs=PROTECTED_REFS,
    )
    if (
        snapshot["status"] != "passed"
        or snapshot["tracked_worktree_clean"] is not True
        or snapshot["branch_origin_aligned"] is not True
        or snapshot["protected_refs_aligned"] is not True
    ):
        raise ImportClosureError("import_closure_preflight_rejected")
    plan_observed = _git(
        "log", "-1", "--format=%H", "--", PLAN_PATH.relative_to(REPO_ROOT).as_posix()
    )
    controller_observed = _git(
        "log",
        "-1",
        "--format=%H",
        "--",
        Path(__file__).resolve().relative_to(REPO_ROOT).as_posix(),
    )
    plan = resolve_commit_source(repo_root=REPO_ROOT, source_head=plan_observed)
    candidate = resolve_commit_source(
        repo_root=REPO_ROOT, source_head=controller_observed
    )
    if (
        plan["status"] != "passed"
        or candidate["status"] != "passed"
        or FULL_OID.fullmatch(plan["resolved_commit"]) is None
        or FULL_OID.fullmatch(candidate["resolved_commit"]) is None
    ):
        raise ImportClosureError("import_closure_preflight_rejected")
    _git("merge-base", "--is-ancestor", plan["resolved_commit"], candidate["resolved_commit"])
    return {
        "policy": "machine_resolved_only",
        "caller_authored_object_id_count": 0,
        "planning_source_commit": plan["resolved_commit"],
        "candidate_source_commit": candidate["resolved_commit"],
        "planning_source_is_ancestor_of_candidate": True,
        "branch": snapshot["branch"],
        "branch_origin_aligned": True,
        "protected_refs_aligned": True,
        "tracked_worktree_clean": True,
        "docs_branding_preserved": snapshot["preserved_untracked_paths"][
            "docs/branding"
        ],
    }


def minimum_windows_environment(
    source: dict[str, str] | os._Environ[str] | None = None,
) -> dict[str, str]:
    return predecessor.minimum_windows_environment(source)


def environment_projection() -> dict[str, Any]:
    return predecessor.environment_projection()


def resolved_node_executable() -> Path:
    return predecessor.resolved_node_executable()


def build_process_envelope(
    *,
    candidate_source: str,
    returncode: int,
    stdout: bytes,
    stderr: bytes,
    fixture_root_absent: bool,
) -> dict[str, Any]:
    envelope = {
        "schema_version": PROCESS_ENVELOPE_VERSION,
        "operation_id": OPERATION_ID,
        "attempt_id": "attempt-001",
        "candidate_source": candidate_source,
        "numeric_exit_code": returncode,
        "stdout_bytes": len(stdout),
        "stdout_sha256": sha256_bytes(stdout),
        "stderr_bytes": len(stderr),
        "stderr_sha256": sha256_bytes(stderr),
        "stream_content_retained": False,
        "raw_runtime_detail_retained": False,
        "executable_path_retained": False,
        "fixture_root_path_retained": False,
        "fixture_root_absent": fixture_root_absent,
        "environment": environment_projection(),
        "materialized_file_count": len(MATERIALIZED_RELATIVE_PATHS),
        "local_stub_package_count": 2,
        "installed_package_import_count": 0,
        "node_process_count": 1,
        "native_harness_process_count": 0,
        "worker_model_provider_process_count": 0,
        "further_process_authorized": False,
    }
    _validate(
        PROCESS_ENVELOPE_SCHEMA_PATH,
        envelope,
        "process_envelope_schema_rejected",
    )
    return envelope


def run_graph_once(
    *,
    node: Path,
    environment: dict[str, str],
    sources: dict[str, bytes],
    candidate_source: str,
    envelope_path: Path = PROCESS_ENVELOPE_PATH,
) -> tuple[subprocess.CompletedProcess[bytes], dict[str, Any]]:
    root_path: Path | None = None
    completed: subprocess.CompletedProcess[bytes]
    try:
        with tempfile.TemporaryDirectory(
            prefix="emr4-guard-bridge-import-closure-"
        ) as raw_root:
            root_path = Path(raw_root)
            for relative, payload in sources.items():
                destination = root_path / Path(relative)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(payload)
            observed = sorted(
                path.relative_to(root_path).as_posix()
                for path in root_path.rglob("*")
                if path.is_file()
            )
            if observed != sorted(MATERIALIZED_RELATIVE_PATHS):
                raise ImportClosureError("import_closure_preflight_rejected")
            fixture_path = (root_path / FIXTURE_FILENAME).resolve()
            try:
                completed = subprocess.run(
                    [str(node), str(fixture_path)],
                    cwd=root_path,
                    env=environment,
                    check=False,
                    capture_output=True,
                    text=False,
                    timeout=30,
                )
            except subprocess.TimeoutExpired as error:
                completed = subprocess.CompletedProcess(
                    args=[str(node), str(fixture_path)],
                    returncode=-1,
                    stdout=error.stdout or b"",
                    stderr=error.stderr or b"",
                )
    except ImportClosureError:
        raise
    except OSError as error:
        raise ImportClosureError("import_closure_process_terminal") from error
    root_absent = root_path is not None and not root_path.exists()
    envelope = build_process_envelope(
        candidate_source=candidate_source,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        fixture_root_absent=root_absent,
    )
    envelope_path.parent.mkdir(parents=True, exist_ok=True)
    envelope_path.write_bytes(canonical_bytes(envelope))
    return completed, envelope


def validate_fixture_result(
    *, completed: subprocess.CompletedProcess[bytes], contract: dict[str, Any]
) -> dict[str, Any]:
    try:
        return predecessor.validate_fixture_result(
            completed=completed,
            contract={"expected_result": contract["expected_result"]},
        )
    except ImportClosureError as error:
        code = str(error)
        if code == "module_graph_process_terminal":
            raise ImportClosureError("import_closure_process_terminal") from error
        raise ImportClosureError("import_closure_result_rejected") from error


def build_failure_terminal(
    *, candidate_source: str, result: str, code: str, envelope_sha256: str
) -> dict[str, Any]:
    terminal = {
        "schema_version": FAILURE_TERMINAL_VERSION,
        "operation_id": OPERATION_ID,
        "attempt_id": "attempt-001",
        "candidate_source": candidate_source,
        "result": result,
        "terminal": {
            "stage": "package_unloaded_import_closure_recovery",
            "code": code,
            "detail": None,
        },
        "process_envelope_sha256": envelope_sha256,
        "raw_runtime_detail_retained": False,
        "further_process_authorized": False,
    }
    _validate(
        FAILURE_TERMINAL_SCHEMA_PATH,
        terminal,
        "failure_terminal_schema_rejected",
    )
    return terminal


def build_evidence(
    *,
    contract: dict[str, Any],
    git_binding: dict[str, Any],
    outcome: dict[str, Any],
    process_envelope: dict[str, Any],
) -> dict[str, Any]:
    evidence = {
        "schema_version": EVIDENCE_VERSION,
        "operation_id": OPERATION_ID,
        "result": ADMITTED_RESULT,
        "git_binding": git_binding,
        "accepted_source_inventory": contract["accepted_source_inventory"],
        "stub_source_inventory": contract["stub_source_inventory"],
        "fixture_correction": contract["fixture_correction"],
        "import_closure": contract["import_closure"],
        "materialized_relative_paths": list(MATERIALIZED_RELATIVE_PATHS),
        "process_envelope_sha256": sha256_bytes(canonical_bytes(process_envelope)),
        "process_envelope_recorded_before_interpretation": True,
        "fixture_outcome": outcome,
        "environment": environment_projection(),
        "cleanup": {
            "fixture_root_absent": process_envelope["fixture_root_absent"],
            "fixture_root_path_retained": False,
            "materialized_javascript_retained": False,
            "materialized_package_manifests_retained": False,
        },
        "process_boundary": {
            "node_process_count": 1,
            "guard_module_execution_count": 1,
            "bridge_module_execution_count": 1,
            "sanitizer_module_execution_count": 1,
            "local_stub_package_count": 2,
            "materialized_file_count": len(MATERIALIZED_RELATIVE_PATHS),
            **{name: 0 for name in contract["required_zero_counters"]},
        },
        "claim_boundary": {
            "static_import_closure_proved": True,
            "package_unloaded_guard_bridge_graph_proved": True,
            "predecessor_retry": False,
            "derived_runner_proved": False,
            "installed_package_loaded": False,
            "native_harness_proved": False,
            "worker_model_provider_executed": False,
            "retry_authorized": False,
            "product_authority": False,
        },
    }
    _validate(EVIDENCE_SCHEMA_PATH, evidence, "evidence_schema_rejected")
    return evidence


def render_report(evidence: dict[str, Any], timestamp: str) -> str:
    candidate = evidence["git_binding"]["candidate_source_commit"]
    return f"""# Native Harness guard–bridge import-closure recovery report

Date: 2026-08-22

Timestamp: {timestamp} (Australia/Brisbane)

Result: **{evidence['result']}**

Candidate source: `{candidate}`

Before process execution, the controller removed the exact 103 embedded fixture
patch markers, derived the exact three relative ESM edges, resolved all three
targets in the eight-file disposable inventory and admitted only the two exact
local package stubs. The accepted bridge bytes were materialized at the
guard-owned target.

Exactly one distinct isolated Node process then passed the frozen success,
missing-service and missing-mount matrix. The content-free envelope was written
after cleanup and before stream interpretation. No predecessor retry, runner,
installed-package import, native Harness, DeepSeek worker, model, provider,
network, database, Docker, target, retry or resume activity occurred.
"""


def _ensure_fresh_outputs() -> None:
    if any(path.exists() for path in OUTPUT_PATHS):
        raise ImportClosureError("import_closure_preflight_rejected")


def execute() -> dict[str, Any]:
    contract = load_contract()
    _ensure_fresh_outputs()
    if import_closure() != contract["import_closure"]:
        raise ImportClosureError("import_closure_preflight_rejected")
    sources = materialized_sources()
    git_binding = machine_git_bindings()
    node = resolved_node_executable()
    environment = minimum_windows_environment()
    completed, envelope = run_graph_once(
        node=node,
        environment=environment,
        sources=sources,
        candidate_source=git_binding["candidate_source_commit"],
    )
    envelope_sha256 = sha256_bytes(canonical_bytes(envelope))
    try:
        outcome = validate_fixture_result(completed=completed, contract=contract)
        if envelope["fixture_root_absent"] is not True:
            raise ImportClosureError("import_closure_process_terminal")
    except ImportClosureError as error:
        result = (
            "import_closure_process_terminal"
            if str(error) == "import_closure_process_terminal"
            else "import_closure_result_rejected"
        )
        terminal = build_failure_terminal(
            candidate_source=git_binding["candidate_source_commit"],
            result=result,
            code=str(error),
            envelope_sha256=envelope_sha256,
        )
        FAILURE_TERMINAL_PATH.write_bytes(canonical_bytes(terminal))
        raise
    evidence = build_evidence(
        contract=contract,
        git_binding=git_binding,
        outcome=outcome,
        process_envelope=envelope,
    )
    timestamp = datetime.now(ZoneInfo("Australia/Brisbane")).isoformat()
    EVIDENCE_PATH.write_bytes(canonical_bytes(evidence))
    REPORT_PATH.write_text(render_report(evidence, timestamp), encoding="utf-8")
    return evidence


def check() -> dict[str, Any]:
    contract = load_contract()
    closure = import_closure()
    if closure != contract["import_closure"]:
        raise ImportClosureError("committed_import_closure_rejected")
    git_binding = machine_git_bindings()
    envelope = _load_object(PROCESS_ENVELOPE_PATH)
    _validate(
        PROCESS_ENVELOPE_SCHEMA_PATH,
        envelope,
        "process_envelope_schema_rejected",
    )
    evidence = _load_object(EVIDENCE_PATH)
    _validate(EVIDENCE_SCHEMA_PATH, evidence, "evidence_schema_rejected")
    if FAILURE_TERMINAL_PATH.exists():
        raise ImportClosureError("failure_terminal_present")
    if (
        envelope["candidate_source"] != git_binding["candidate_source_commit"]
        or envelope["numeric_exit_code"] != 0
        or envelope["stderr_bytes"] != 0
        or envelope["node_process_count"] != 1
        or envelope["fixture_root_absent"] is not True
        or evidence["git_binding"] != git_binding
        or evidence["import_closure"] != closure
        or evidence["fixture_outcome"] != contract["expected_result"]
        or evidence["process_envelope_sha256"]
        != sha256_bytes(canonical_bytes(envelope))
    ):
        raise ImportClosureError("committed_evidence_rejected")
    report = REPORT_PATH.read_text(encoding="utf-8")
    if (
        f"Candidate source: `{git_binding['candidate_source_commit']}`" not in report
        or f"Result: **{ADMITTED_RESULT}**" not in report
    ):
        raise ImportClosureError("committed_report_rejected")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write-contract", action="store_true")
    mode.add_argument("--execute", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.write_contract:
            contract = write_contract()
            print(
                json.dumps(
                    {
                        "operation_id": OPERATION_ID,
                        "result": "contract_written",
                        "relative_edge_count": contract["import_closure"][
                            "relative_edge_count"
                        ],
                        "materialized_file_count": len(
                            contract["materialized_relative_paths"]
                        ),
                    },
                    sort_keys=True,
                )
            )
            return 0
        evidence = execute() if args.execute else check()
    except ImportClosureError as error:
        raise SystemExit(str(error)) from None
    print(
        json.dumps(
            {
                "operation_id": OPERATION_ID,
                "result": evidence["result"],
                "candidate_source": evidence["git_binding"][
                    "candidate_source_commit"
                ],
                "relative_edge_count": evidence["import_closure"][
                    "relative_edge_count"
                ],
                "node_process_count": evidence["process_boundary"][
                    "node_process_count"
                ],
                "native_harness_process_count": evidence["process_boundary"][
                    "native_harness_process_count"
                ],
                "fixture_root_absent": evidence["cleanup"]["fixture_root_absent"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
