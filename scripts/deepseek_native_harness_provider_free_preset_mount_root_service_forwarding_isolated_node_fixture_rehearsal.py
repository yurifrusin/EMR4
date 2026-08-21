"""Run one isolated Node fixture for the accepted root-service bridge."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
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
    deepseek_native_harness_provider_free_preset_mount_root_service_forwarding_process_free_correction_rehearsal
    as predecessor,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-preset-mount-root-service-forwarding-"
    "isolated-node-fixture-rehearsal"
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
EVIDENCE_PATH = OPERATION_ROOT / "isolated-node-fixture-evidence.json"
REPORT_PATH = OPERATION_ROOT / "isolated-node-fixture-report.md"
FAILURE_TERMINAL_PATH = OPERATION_ROOT / "attempt-001-failure-terminal.json"
FOCUSED_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_provider_free_preset_mount_root_service_forwarding_isolated_node_fixture_rehearsal.py"
)
PREDECESSOR_EVIDENCE_PATH = predecessor.EVIDENCE_PATH
PREDECESSOR_CONTROLLER_PATH = Path(predecessor.__file__).resolve()
BRIDGE_FILENAME = predecessor.predecessor.BRIDGE_PATH.name
SANITIZER_FILENAME = predecessor.predecessor.SANITIZER_PATH.name
FIXTURE_FILENAME = "root_service_forwarding_fixture.mjs"
EXPECTED_PROTECTED_COMMIT = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
PROTECTED_REFS = (
    "refs/heads/master",
    "refs/remotes/origin/master",
    "refs/heads/handoff/current",
    "refs/remotes/origin/handoff/current",
)
WINDOWS_ENVIRONMENT_KEYS = ("SystemRoot", "WINDIR", "ComSpec", "TEMP", "TMP")
FORBIDDEN_ENVIRONMENT_KEYS = frozenset({"PATH", "NODE_OPTIONS"})
FULL_OID = re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])")
CONTRACT_VERSION = (
    "ariadne.native_harness_root_service_forwarding_isolated_node_fixture_contract.v1"
)
PROCESS_ENVELOPE_VERSION = (
    "ariadne.native_harness_root_service_forwarding_isolated_node_process_envelope.v1"
)
FIXTURE_RESULT_VERSION = (
    "ariadne.native_harness_root_service_forwarding_isolated_fixture_result.v1"
)
EVIDENCE_VERSION = (
    "ariadne.native_harness_root_service_forwarding_isolated_node_fixture_evidence.v1"
)
FAILURE_TERMINAL_VERSION = (
    "ariadne.native_harness_root_service_forwarding_isolated_node_failure_terminal.v1"
)
CLOSED_RESULTS = [
    "isolated_node_fixture_pass",
    "fixture_preflight_rejected",
    "fixture_process_terminal",
    "fixture_result_rejected",
]
ADMITTED_RESULT = "isolated_node_fixture_pass"
OUTPUT_PATHS = (
    PROCESS_ENVELOPE_PATH,
    EVIDENCE_PATH,
    REPORT_PATH,
    FAILURE_TERMINAL_PATH,
)


class IsolatedNodeFixtureError(RuntimeError):
    """A closed fixture coordinate failed without raw runtime detail."""


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
        raise IsolatedNodeFixtureError(f"json_unreadable:{path.name}") from error
    if not isinstance(value, dict):
        raise IsolatedNodeFixtureError(f"json_object_required:{path.name}")
    return value


def _validate(schema_path: Path, value: object, code: str) -> None:
    schema = _load_object(schema_path)
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(value)
    except (jsonschema.SchemaError, jsonschema.ValidationError) as error:
        raise IsolatedNodeFixtureError(code) from error


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
        raise IsolatedNodeFixtureError("git_resolution_failed")
    return completed.stdout.strip()


def documentation_bindings() -> dict[str, str]:
    return {
        "plan_sha256": sha256_bytes(PLAN_PATH.read_bytes()),
        "threat_model_sha256": sha256_bytes(THREAT_PATH.read_bytes()),
    }


def predecessor_bindings() -> dict[str, str]:
    return {
        "accepted_correction_evidence_sha256": sha256_bytes(
            PREDECESSOR_EVIDENCE_PATH.read_bytes()
        ),
        "accepted_correction_controller_sha256": sha256_bytes(
            PREDECESSOR_CONTROLLER_PATH.read_bytes()
        ),
    }


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


def accepted_fixture_sources() -> tuple[dict[str, bytes], dict[str, dict[str, Any]]]:
    evidence = _load_object(PREDECESSOR_EVIDENCE_PATH)
    if (
        evidence.get("result") != "root_service_forwarding_correction_admitted"
        or evidence.get("failed_source_coordinates") != []
    ):
        raise IsolatedNodeFixtureError("accepted_correction_evidence_rejected")
    accepted, _ = predecessor.accepted_source_inventory()
    bridge = predecessor.derive_bridge_source(
        accepted["accepted_preset_mount_bridge"]
    )
    sanitizer = accepted["accepted_preset_mount_sanitizer"]
    sources = {
        "derived_bridge": bridge,
        "accepted_sanitizer": sanitizer,
    }
    inventory = {name: source_entry(payload) for name, payload in sources.items()}
    if (
        inventory["derived_bridge"]
        != evidence.get("derived_source_inventory", {}).get("derived_bridge")
        or inventory["accepted_sanitizer"]
        != evidence.get("accepted_source_inventory", {}).get(
            "accepted_preset_mount_sanitizer"
        )
    ):
        raise IsolatedNodeFixtureError("accepted_source_binding_rejected")
    return sources, inventory


def exact_fixture_outcome() -> dict[str, Any]:
    terminal = {
        "stage": "preset_mount",
        "code": "PRESET_MOUNT_UNCLASSIFIED",
        "detail": None,
    }
    return {
        "schema_version": FIXTURE_RESULT_VERSION,
        "result": "pass",
        "cases": [
            {
                "case_id": "success",
                "passed": True,
                "terminal": None,
                "mount_call_count": 1,
                "receiver_bound": True,
                "context_forwarded": True,
                "preset_id_forwarded": True,
            },
            {
                "case_id": "missing_service",
                "passed": False,
                "terminal": dict(terminal),
            },
            {
                "case_id": "missing_mount",
                "passed": False,
                "terminal": dict(terminal),
            },
        ],
    }


def fixture_source() -> bytes:
    source = f"""import {{ mountWithSanitizedTerminal }} from "./{BRIDGE_FILENAME}";

class PresetMountError extends Error {{
  constructor(reason) {{
    super("PRESET_MOUNT_FAILURE");
    this.reason = reason;
  }}
}}

const agentCtx = Object.freeze({{ fixture: "authored-synthetic" }});
const presetId = "emr4-authored-synthetic-preset";
const call = {{
  count: 0,
  receiverBound: false,
  contextForwarded: false,
  presetIdForwarded: false,
}};
const presetService = {{
  async mount(observedContext, observedPresetId) {{
    call.count += 1;
    call.receiverBound = this === presetService;
    call.contextForwarded = observedContext === agentCtx;
    call.presetIdForwarded = observedPresetId === presetId;
  }},
}};

const success = await mountWithSanitizedTerminal({{
  presetService,
  agentCtx,
  presetId,
  PresetMountError,
}});
const missingService = await mountWithSanitizedTerminal({{
  presetService: null,
  agentCtx,
  presetId,
  PresetMountError,
}});
const missingMount = await mountWithSanitizedTerminal({{
  presetService: Object.freeze({{}}),
  agentCtx,
  presetId,
  PresetMountError,
}});

const output = {{
  schema_version: "{FIXTURE_RESULT_VERSION}",
  result: "pass",
  cases: [
    {{
      case_id: "success",
      passed: success.passed,
      terminal: success.terminal,
      mount_call_count: call.count,
      receiver_bound: call.receiverBound,
      context_forwarded: call.contextForwarded,
      preset_id_forwarded: call.presetIdForwarded,
    }},
    {{
      case_id: "missing_service",
      passed: missingService.passed,
      terminal: missingService.terminal,
    }},
    {{
      case_id: "missing_mount",
      passed: missingMount.passed,
      terminal: missingMount.terminal,
    }},
  ],
}};
process.stdout.write(JSON.stringify(output) + "\\n");
"""
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
    if any(token in source for token in forbidden):
        raise IsolatedNodeFixtureError("fixture_source_forbidden_coordinate")
    return source.encode("utf-8")


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = _load_object(path)
    _validate(CONTRACT_SCHEMA_PATH, contract, "contract_schema_rejected")
    serialized = json.dumps(contract, sort_keys=True)
    if FULL_OID.search(serialized) is not None:
        raise IsolatedNodeFixtureError("caller_authored_git_object_id_rejected")
    expected_identity = {
        "schema_version": CONTRACT_VERSION,
        "operation_id": OPERATION_ID,
        "git_binding_policy": {
            "mode": "machine_resolved_only",
            "plan_path": PLAN_PATH.relative_to(REPO_ROOT).as_posix(),
            "controller_path": Path(__file__).resolve()
            .relative_to(REPO_ROOT)
            .as_posix(),
            "caller_authored_object_id_count": 0,
        },
        "closed_results": CLOSED_RESULTS,
        "windows_environment_keys": list(WINDOWS_ENVIRONMENT_KEYS),
        "case_ids": ["success", "missing_service", "missing_mount"],
        "required_zero_counters": [
            "native_harness_process_count",
            "runner_process_count",
            "guard_process_count",
            "installed_package_import_count",
            "worker_process_count",
            "model_request_count",
            "provider_request_count",
            "network_attempt_count",
            "database_attempt_count",
            "docker_attempt_count",
            "target_creation_count",
            "target_use_count",
            "retry_count",
            "resume_count",
        ],
    }
    for key, expected in expected_identity.items():
        if contract.get(key) != expected:
            raise IsolatedNodeFixtureError(f"contract_{key}_rejected")
    if contract["documentation_bindings"] != documentation_bindings():
        raise IsolatedNodeFixtureError("documentation_binding_rejected")
    if contract["predecessor_bindings"] != predecessor_bindings():
        raise IsolatedNodeFixtureError("predecessor_binding_rejected")
    if contract["implementation_bindings"] != implementation_bindings():
        raise IsolatedNodeFixtureError("implementation_binding_rejected")
    _, inventory = accepted_fixture_sources()
    if contract["accepted_source_inventory"] != inventory:
        raise IsolatedNodeFixtureError("accepted_source_inventory_rejected")
    if contract["fixture_source_inventory"] != source_entry(fixture_source()):
        raise IsolatedNodeFixtureError("fixture_source_inventory_rejected")
    if contract["expected_result"] != exact_fixture_outcome():
        raise IsolatedNodeFixtureError("expected_result_rejected")
    if contract["claim_boundary"] != {
        "isolated_bridge_behavior_only": True,
        "runner_guard_graph_proved": False,
        "native_harness_proved": False,
        "worker_model_provider_executed": False,
        "retry_authorized": False,
        "product_authority": False,
    }:
        raise IsolatedNodeFixtureError("claim_boundary_rejected")
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
        raise IsolatedNodeFixtureError("fixture_preflight_rejected")
    plan_observed = _git(
        "log",
        "-1",
        "--format=%H",
        "--",
        PLAN_PATH.relative_to(REPO_ROOT).as_posix(),
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
        raise IsolatedNodeFixtureError("fixture_preflight_rejected")
    _git(
        "merge-base",
        "--is-ancestor",
        plan["resolved_commit"],
        candidate["resolved_commit"],
    )
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
    environment = os.environ if source is None else source
    if any(not environment.get(key) for key in WINDOWS_ENVIRONMENT_KEYS):
        raise IsolatedNodeFixtureError("fixture_preflight_rejected")
    result = {key: environment[key] for key in WINDOWS_ENVIRONMENT_KEYS}
    if (
        tuple(result) != WINDOWS_ENVIRONMENT_KEYS
        or set(result) & FORBIDDEN_ENVIRONMENT_KEYS
        or len(result) != len(WINDOWS_ENVIRONMENT_KEYS)
    ):
        raise IsolatedNodeFixtureError("fixture_preflight_rejected")
    return result


def environment_projection() -> dict[str, Any]:
    return {
        "keys": list(WINDOWS_ENVIRONMENT_KEYS),
        "key_count": len(WINDOWS_ENVIRONMENT_KEYS),
        "values_retained": False,
        "path_present": False,
        "node_options_present": False,
    }


def resolved_node_executable() -> Path:
    raw = shutil.which("node")
    if not raw:
        raise IsolatedNodeFixtureError("fixture_preflight_rejected")
    node = Path(raw).resolve()
    if not node.is_absolute() or not node.is_file():
        raise IsolatedNodeFixtureError("fixture_preflight_rejected")
    return node


def build_process_envelope(
    *,
    candidate_source: str,
    returncode: int,
    stdout: str,
    stderr: str,
    fixture_root_absent: bool,
) -> dict[str, Any]:
    stdout_bytes = stdout.encode("utf-8")
    stderr_bytes = stderr.encode("utf-8")
    envelope = {
        "schema_version": PROCESS_ENVELOPE_VERSION,
        "operation_id": OPERATION_ID,
        "attempt_id": "attempt-001",
        "candidate_source": candidate_source,
        "numeric_exit_code": returncode,
        "stdout_bytes": len(stdout_bytes),
        "stdout_sha256": sha256_bytes(stdout_bytes),
        "stderr_bytes": len(stderr_bytes),
        "stderr_sha256": sha256_bytes(stderr_bytes),
        "stream_content_retained": False,
        "raw_runtime_detail_retained": False,
        "executable_path_retained": False,
        "fixture_root_path_retained": False,
        "fixture_root_absent": fixture_root_absent,
        "environment": environment_projection(),
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


def run_fixture_once(
    *,
    node: Path,
    environment: dict[str, str],
    sources: dict[str, bytes],
    fixture: bytes,
    candidate_source: str,
    envelope_path: Path = PROCESS_ENVELOPE_PATH,
) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    root_path: Path | None = None
    try:
        with tempfile.TemporaryDirectory(
            prefix="emr4-root-service-forwarding-fixture-"
        ) as raw_root:
            root_path = Path(raw_root)
            (root_path / BRIDGE_FILENAME).write_bytes(sources["derived_bridge"])
            (root_path / SANITIZER_FILENAME).write_bytes(
                sources["accepted_sanitizer"]
            )
            fixture_path = root_path / FIXTURE_FILENAME
            fixture_path.write_bytes(fixture)
            if sorted(path.name for path in root_path.iterdir()) != sorted(
                [BRIDGE_FILENAME, SANITIZER_FILENAME, FIXTURE_FILENAME]
            ):
                raise IsolatedNodeFixtureError("fixture_preflight_rejected")
            completed = subprocess.run(
                [str(node), str(fixture_path)],
                cwd=root_path,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="strict",
                timeout=30,
            )
    except IsolatedNodeFixtureError:
        raise
    except (OSError, subprocess.SubprocessError, UnicodeError) as error:
        raise IsolatedNodeFixtureError("fixture_process_terminal") from error
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


def _require_keys(value: dict[str, Any], keys: list[str], code: str) -> None:
    if list(value) != keys:
        raise IsolatedNodeFixtureError(code)


def validate_fixture_result(
    *,
    completed: subprocess.CompletedProcess[str],
    contract: dict[str, Any],
) -> dict[str, Any]:
    if (
        completed.returncode != 0
        or completed.stderr != ""
        or not completed.stdout.endswith("\n")
        or completed.stdout.count("\n") != 1
        or "\r" in completed.stdout
    ):
        raise IsolatedNodeFixtureError("fixture_process_terminal")
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise IsolatedNodeFixtureError("fixture_result_rejected") from error
    if not isinstance(value, dict):
        raise IsolatedNodeFixtureError("fixture_result_rejected")
    _require_keys(value, ["schema_version", "result", "cases"], "fixture_result_rejected")
    cases = value.get("cases")
    if not isinstance(cases, list) or len(cases) != 3:
        raise IsolatedNodeFixtureError("fixture_result_rejected")
    _require_keys(
        cases[0],
        [
            "case_id",
            "passed",
            "terminal",
            "mount_call_count",
            "receiver_bound",
            "context_forwarded",
            "preset_id_forwarded",
        ],
        "fixture_result_rejected",
    )
    for row in cases[1:]:
        if not isinstance(row, dict):
            raise IsolatedNodeFixtureError("fixture_result_rejected")
        _require_keys(
            row,
            ["case_id", "passed", "terminal"],
            "fixture_result_rejected",
        )
        terminal = row.get("terminal")
        if not isinstance(terminal, dict):
            raise IsolatedNodeFixtureError("fixture_result_rejected")
        _require_keys(
            terminal,
            ["stage", "code", "detail"],
            "fixture_result_rejected",
        )
    if value != contract["expected_result"]:
        raise IsolatedNodeFixtureError("fixture_result_rejected")
    return value


def build_failure_terminal(
    *, candidate_source: str, result: str, code: str, envelope_sha256: str
) -> dict[str, Any]:
    terminal = {
        "schema_version": FAILURE_TERMINAL_VERSION,
        "operation_id": OPERATION_ID,
        "attempt_id": "attempt-001",
        "candidate_source": candidate_source,
        "result": result,
        "terminal": {"stage": "isolated_node_fixture", "code": code, "detail": None},
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
    source_inventory: dict[str, dict[str, Any]],
    fixture_inventory: dict[str, Any],
    outcome: dict[str, Any],
    process_envelope: dict[str, Any],
) -> dict[str, Any]:
    evidence = {
        "schema_version": EVIDENCE_VERSION,
        "operation_id": OPERATION_ID,
        "result": ADMITTED_RESULT,
        "git_binding": git_binding,
        "accepted_source_inventory": source_inventory,
        "fixture_source_inventory": fixture_inventory,
        "process_envelope_sha256": sha256_bytes(canonical_bytes(process_envelope)),
        "process_envelope_recorded_before_interpretation": True,
        "fixture_outcome": outcome,
        "environment": environment_projection(),
        "cleanup": {
            "fixture_root_absent": process_envelope["fixture_root_absent"],
            "fixture_root_path_retained": False,
            "materialized_javascript_retained": False,
        },
        "process_boundary": {
            "node_process_count": 1,
            **{name: 0 for name in contract["required_zero_counters"]},
        },
        "claim_boundary": {
            "isolated_bridge_behavior_proved": True,
            "runner_guard_graph_proved": False,
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
    return f"""# Native Harness root-service-forwarding isolated Node-fixture report

Date: 2026-08-22

Timestamp: {timestamp} (Australia/Brisbane)

Result: **{evidence['result']}**

Candidate source: `{candidate}`

Exactly one isolated authored-synthetic Node process evaluated the exact
accepted derived bridge and sanitizer. The success case invoked the service
once with the correct receiver, context and preset ID. Missing service and
missing mount each reduced to `PRESET_MOUNT_UNCLASSIFIED` with null detail.

The content-free process envelope was persisted before stream interpretation.
The five-key child environment retained no values, and the disposable fixture
root plus all materialized JavaScript were absent before admission.

No runner, guard, installed package, native Harness, DeepSeek worker, model,
provider, network, database, Docker, target, retry or resume activity occurred.
This proves isolated bridge behavior only.
"""


def _ensure_fresh_outputs() -> None:
    if any(path.exists() for path in OUTPUT_PATHS):
        raise IsolatedNodeFixtureError("fixture_preflight_rejected")


def execute() -> dict[str, Any]:
    contract = load_contract()
    _ensure_fresh_outputs()
    sources, source_inventory = accepted_fixture_sources()
    fixture = fixture_source()
    fixture_inventory = source_entry(fixture)
    git_binding = machine_git_bindings()
    node = resolved_node_executable()
    environment = minimum_windows_environment()
    completed, envelope = run_fixture_once(
        node=node,
        environment=environment,
        sources=sources,
        fixture=fixture,
        candidate_source=git_binding["candidate_source_commit"],
    )
    envelope_sha256 = sha256_bytes(canonical_bytes(envelope))
    try:
        outcome = validate_fixture_result(completed=completed, contract=contract)
        if envelope["fixture_root_absent"] is not True:
            raise IsolatedNodeFixtureError("fixture_process_terminal")
    except IsolatedNodeFixtureError as error:
        result = (
            "fixture_process_terminal"
            if str(error) == "fixture_process_terminal"
            else "fixture_result_rejected"
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
        source_inventory=source_inventory,
        fixture_inventory=fixture_inventory,
        outcome=outcome,
        process_envelope=envelope,
    )
    timestamp = datetime.now(ZoneInfo("Australia/Brisbane")).isoformat()
    EVIDENCE_PATH.write_bytes(canonical_bytes(evidence))
    REPORT_PATH.write_text(render_report(evidence, timestamp), encoding="utf-8")
    return evidence


def check() -> dict[str, Any]:
    contract = load_contract()
    sources, source_inventory = accepted_fixture_sources()
    if source_inventory != contract["accepted_source_inventory"]:
        raise IsolatedNodeFixtureError("accepted_source_inventory_rejected")
    fixture_inventory = source_entry(fixture_source())
    if fixture_inventory != contract["fixture_source_inventory"]:
        raise IsolatedNodeFixtureError("fixture_source_inventory_rejected")
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
        raise IsolatedNodeFixtureError("failure_terminal_present")
    if (
        envelope["candidate_source"] != git_binding["candidate_source_commit"]
        or envelope["numeric_exit_code"] != 0
        or envelope["stderr_bytes"] != 0
        or envelope["node_process_count"] != 1
        or envelope["fixture_root_absent"] is not True
        or evidence["git_binding"] != git_binding
        or evidence["accepted_source_inventory"] != source_inventory
        or evidence["fixture_source_inventory"] != fixture_inventory
        or evidence["fixture_outcome"] != contract["expected_result"]
        or evidence["process_envelope_sha256"]
        != sha256_bytes(canonical_bytes(envelope))
    ):
        raise IsolatedNodeFixtureError("committed_evidence_rejected")
    report = REPORT_PATH.read_text(encoding="utf-8")
    if (
        f"Candidate source: `{git_binding['candidate_source_commit']}`" not in report
        or "Result: **isolated_node_fixture_pass**" not in report
    ):
        raise IsolatedNodeFixtureError("committed_report_rejected")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--execute", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        evidence = execute() if args.execute else check()
    except IsolatedNodeFixtureError as error:
        raise SystemExit(str(error)) from None
    print(
        json.dumps(
            {
                "operation_id": OPERATION_ID,
                "result": evidence["result"],
                "candidate_source": evidence["git_binding"][
                    "candidate_source_commit"
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
