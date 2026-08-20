"""Execute the structured diagnostic wrapper against authored local Node fixtures."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any
from zoneinfo import ZoneInfo

import jsonschema

from orchestration_harness import native_pre_hmr_diagnostic as diagnostic


ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-structured-diagnostic-wrapper-"
    "node-fixture-rehearsal"
)
OPERATION_ROOT = ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "provider-free-node-fixture-evidence.json"
REPORT_PATH = OPERATION_ROOT / "provider-free-node-fixture-report.md"
ATTEMPTS_ROOT = OPERATION_ROOT / "attempts"
TEMP_PARENT_NAME = "emr4-native-diagnostic-node-fixture"
EVIDENCE_VERSION = (
    "ariadne.native_harness_structured_diagnostic_node_fixture_evidence.v1"
)
OBSERVER_VERSION = "ariadne.native_harness_node_fixture_observer.v1"
ATTEMPT_ID_PATTERN = re.compile(r"^node-fixture-attempt-[0-9]{3}$")
FULL_OID = re.compile(r"^[0-9a-f]{40}$")
SCENARIOS = (
    "nested_known",
    "unknown_secret_shaped",
    "aggregate_multiple",
    "preexisting_sidecar",
)
SECRET_SENTINEL = "AUTHORED_SECRET_SENTINEL_9J4Z_DO_NOT_RETAIN"
PREEXISTING_BYTES = b"AUTHORED_PREEXISTING_SIDECAR_SENTINEL\n"
MAX_STREAM_BYTES = 32_768


class NodeFixtureRehearsalError(RuntimeError):
    """The authored Node fixture rehearsal failed closed."""


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _write_exclusive(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def load_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    schema = json.loads(CONTRACT_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(contract, schema)
    if tuple(contract["scenario_order"]) != SCENARIOS:
        raise NodeFixtureRehearsalError("scenario_order_invalid")
    if contract["process_boundary"] != {
        "python_controller_processes": 1,
        "node_processes": 4,
        "native_harness_processes": 0,
        "broker_processes": 0,
        "worker_processes": 0,
        "model_requests": 0,
        "provider_requests": 0,
        "serial": True,
    }:
        raise NodeFixtureRehearsalError("process_boundary_invalid")
    return contract


def fixture_source(scenario: str) -> bytes:
    if scenario == "nested_known":
        body = '''const inner = new Error("plugin tree failed to load: authored fixture");
inner.code = "ERR_MODULE_NOT_FOUND";
const error = new TypeError("host preparation failed: authored fixture", { cause: inner });
globalThis.__EMR4_AUTHORED_FIXTURE_ERROR__ = error;
throw error;
'''
    elif scenario == "unknown_secret_shaped":
        body = f'''const error = {{name: "NovelFixtureError", message: {json.dumps(SECRET_SENTINEL + " C:/invented/private/path")}}};
globalThis.__EMR4_AUTHORED_FIXTURE_ERROR__ = error;
throw error;
'''
    elif scenario == "aggregate_multiple":
        body = '''const error = new AggregateError([new Error("one"), new Error("two")], "authored aggregate");
globalThis.__EMR4_AUTHORED_FIXTURE_ERROR__ = error;
throw error;
'''
    elif scenario == "preexisting_sidecar":
        body = '''const error = new Error("authored write-failure fixture");
globalThis.__EMR4_AUTHORED_FIXTURE_ERROR__ = error;
throw error;
'''
    else:
        raise NodeFixtureRehearsalError("scenario_invalid")
    return body.encode()


def observer_source(*, scenario: str, wrapper_path: Path, result_path: Path) -> bytes:
    source = f'''import {{ closeSync, fsyncSync, openSync, writeFileSync }} from "node:fs";

const WRAPPER_URL = {json.dumps(wrapper_path.as_uri())};
const RESULT_PATH = {json.dumps(str(result_path))};
const SCENARIO = {json.dumps(scenario)};

let caught = false;
let identical = false;
try {{
  await import(WRAPPER_URL);
}} catch (error) {{
  caught = true;
  identical = error === globalThis.__EMR4_AUTHORED_FIXTURE_ERROR__;
}}

const value = {{
  caught_rejection: caught,
  exit_coordinate: caught && identical ? "caught_identical" : "observer_rejected",
  identical_rejection: identical,
  node_version: process.versions.node,
  scenario: SCENARIO,
  schema_version: {json.dumps(OBSERVER_VERSION)},
}};
let descriptor;
try {{
  descriptor = openSync(RESULT_PATH, "wx", 0o600);
  writeFileSync(descriptor, JSON.stringify(value) + "\\n", "utf8");
  fsyncSync(descriptor);
}} finally {{
  if (descriptor !== undefined) {{ try {{ closeSync(descriptor); }} catch {{}} }}
}}
if (!caught || !identical) process.exitCode = 41;
'''
    return source.encode()


def validate_authored_sources(
    *, fixture: bytes, wrapper: bytes, observer: bytes, contract: dict[str, Any]
) -> dict[str, str]:
    combined = fixture + b"\n" + wrapper + b"\n" + observer
    for token in contract["forbidden_source_tokens"]:
        if token.encode() in combined:
            raise NodeFixtureRehearsalError("forbidden_source_token")
    wrapper_projection = diagnostic.validate_entrypoint_wrapper_source(wrapper)
    observer_text = observer.decode("utf-8")
    if (
        observer_text.count("await import(WRAPPER_URL)") != 1
        or observer_text.count("error === globalThis.__EMR4_AUTHORED_FIXTURE_ERROR__")
        != 1
        or observer_text.count('openSync(RESULT_PATH, "wx"') != 1
        or ".message" in observer_text
        or ".stack" in observer_text
    ):
        raise NodeFixtureRehearsalError("observer_source_invalid")
    return {
        "fixture_sha256": _sha256(fixture),
        "wrapper_sha256": wrapper_projection["sha256"],
        "observer_sha256": _sha256(observer),
    }


def validate_observer(value: object, scenario: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {
        "caught_rejection",
        "exit_coordinate",
        "identical_rejection",
        "node_version",
        "scenario",
        "schema_version",
    }:
        raise NodeFixtureRehearsalError("observer_keys_invalid")
    if (
        value["schema_version"] != OBSERVER_VERSION
        or value["scenario"] != scenario
        or value["caught_rejection"] is not True
        or value["identical_rejection"] is not True
        or value["exit_coordinate"] != "caught_identical"
        or not isinstance(value["node_version"], str)
        or re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", value["node_version"]) is None
    ):
        raise NodeFixtureRehearsalError("observer_relationship_invalid")
    return value


def _safe_remove_scenario(path: Path, operation_parent: Path) -> None:
    if path.is_symlink() or path.parent.resolve() != operation_parent.resolve():
        raise NodeFixtureRehearsalError("cleanup_target_invalid")
    if path.exists():
        shutil.rmtree(path)
    if path.exists():
        raise NodeFixtureRehearsalError("scenario_cleanup_failed")


def _safe_remove_operation(path: Path, temp_root: Path) -> None:
    if path.is_symlink() or path.parent.resolve() != temp_root.resolve():
        raise NodeFixtureRehearsalError("operation_cleanup_target_invalid")
    if path.exists():
        shutil.rmtree(path)
    if path.exists():
        raise NodeFixtureRehearsalError("operation_cleanup_failed")


def _scenario_projection(
    *,
    scenario: str,
    root: Path,
    candidate_source: str,
    attempt_id: str,
    node_executable: str,
    run: Callable[..., subprocess.CompletedProcess[bytes]],
    contract: dict[str, Any],
) -> dict[str, Any]:
    package_root = root / "fixture-package"
    entrypoint = package_root / "lib" / "bin.js"
    wrapper_path = root / "entrypoint-wrapper.mjs"
    observer_path = root / "identity-observer.mjs"
    diagnostic_path = root / "diagnostic.json"
    observer_result_path = root / "observer-result.json"
    entrypoint.parent.mkdir(parents=True)

    fixture = fixture_source(scenario)
    _write_exclusive(entrypoint, fixture)
    wrapper = diagnostic.build_entrypoint_wrapper_source(
        package_root=package_root.resolve(),
        wrapper_path=wrapper_path.resolve(),
        diagnostic_path=diagnostic_path.resolve(),
        disposable_root=root.resolve(),
        operation_id=OPERATION_ID,
        attempt_id=attempt_id,
        candidate_source=candidate_source,
    )
    _write_exclusive(wrapper_path, wrapper)
    observer = observer_source(
        scenario=scenario,
        wrapper_path=wrapper_path.resolve(),
        result_path=observer_result_path.resolve(),
    )
    _write_exclusive(observer_path, observer)
    source_hashes = validate_authored_sources(
        fixture=fixture, wrapper=wrapper, observer=observer, contract=contract
    )

    preexisting_before: str | None = None
    if scenario == contract["sidecar_write_failure_scenario"]:
        _write_exclusive(diagnostic_path, PREEXISTING_BYTES)
        preexisting_before = _sha256(PREEXISTING_BYTES)

    completed = run(
        [node_executable, str(observer_path)],
        cwd=root,
        capture_output=True,
        timeout=20,
        check=False,
    )
    stdout = completed.stdout if isinstance(completed.stdout, bytes) else b""
    stderr = completed.stderr if isinstance(completed.stderr, bytes) else b""
    if len(stdout) > MAX_STREAM_BYTES or len(stderr) > MAX_STREAM_BYTES:
        raise NodeFixtureRehearsalError("process_stream_size_exceeded")
    observer_value = validate_observer(
        json.loads(observer_result_path.read_text(encoding="utf-8")), scenario
    )
    if completed.returncode != 0:
        raise NodeFixtureRehearsalError("observer_process_nonzero")

    diagnostic_accepted = False
    diagnostic_error: str | None = None
    top_error_kind: str | None = None
    top_message_coordinate: str | None = None
    top_aggregate_shape: str | None = None
    cause_nodes = 0
    preexisting_unchanged: bool | None = None
    try:
        if scenario == contract["sidecar_write_failure_scenario"]:
            preexisting_unchanged = (
                _sha256(diagnostic_path.read_bytes()) == preexisting_before
            )
            if not preexisting_unchanged:
                raise NodeFixtureRehearsalError("preexisting_sidecar_changed")
        else:
            value = diagnostic.read_structured_diagnostic(
                diagnostic_path,
                disposable_root=root,
                operation_id=OPERATION_ID,
                attempt_id=attempt_id,
                candidate_source=candidate_source,
            )
            diagnostic_accepted = True
            cause_nodes = len(value["cause_chain"])
            top = value["cause_chain"][0]
            top_error_kind = top["error_kind"]
            top_message_coordinate = top["message_coordinate"]
            top_aggregate_shape = top["aggregate_shape"]
    except (diagnostic.StructuredDiagnosticError, OSError, ValueError) as error:
        diagnostic_error = str(error)

    return {
        "scenario": scenario,
        "process_exit_code": completed.returncode,
        "stdout_bytes": len(stdout),
        "stderr_bytes": len(stderr),
        "caught_rejection": observer_value["caught_rejection"],
        "identical_rejection": observer_value["identical_rejection"],
        "node_version": observer_value["node_version"],
        "diagnostic_accepted": diagnostic_accepted,
        "diagnostic_error": diagnostic_error,
        "top_error_kind": top_error_kind,
        "top_message_coordinate": top_message_coordinate,
        "top_aggregate_shape": top_aggregate_shape,
        "cause_node_count": cause_nodes,
        "preexisting_sidecar_unchanged": preexisting_unchanged,
        **source_hashes,
    }


def validate_scenario_outcomes(rows: list[dict[str, Any]]) -> list[str]:
    reasons: list[str] = []
    expected = {
        "nested_known": ("type_error", "host_preparation_failed", "none"),
        "unknown_secret_shaped": ("unknown", "none", "none"),
        "aggregate_multiple": ("aggregate_error", "none", "multiple"),
    }
    if [row["scenario"] for row in rows] != list(SCENARIOS):
        reasons.append("scenario_order_invalid")
    for row in rows:
        if row["process_exit_code"] != 0 or not row["identical_rejection"]:
            reasons.append(f"{row['scenario']}:identity_rethrow_failed")
        if row["scenario"] in expected:
            if not row["diagnostic_accepted"]:
                reasons.append(
                    f"{row['scenario']}:diagnostic_rejected:{row['diagnostic_error']}"
                )
            elif (
                row["top_error_kind"],
                row["top_message_coordinate"],
                row["top_aggregate_shape"],
            ) != expected[row["scenario"]]:
                reasons.append(f"{row['scenario']}:diagnostic_coordinate_mismatch")
        elif (
            row["diagnostic_accepted"]
            or row["preexisting_sidecar_unchanged"] is not True
        ):
            reasons.append("preexisting_sidecar_fail_closed_invalid")
    return reasons


def execute_attempt(
    *,
    candidate_source: str,
    attempt_id: str,
    node_executable: str | None = None,
    run: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> dict[str, Any]:
    if FULL_OID.fullmatch(candidate_source) is None:
        raise NodeFixtureRehearsalError("candidate_source_invalid")
    if ATTEMPT_ID_PATTERN.fullmatch(attempt_id) is None:
        raise NodeFixtureRehearsalError("attempt_id_invalid")
    contract = load_contract()
    executable = node_executable or shutil.which("node")
    if not executable:
        raise NodeFixtureRehearsalError("node_executable_unavailable")
    executable_path = Path(executable).resolve(strict=True)

    temp_root = Path(os.environ.get("TEMP", os.environ.get("TMP", ""))).resolve()
    if not temp_root.is_dir():
        raise NodeFixtureRehearsalError("temp_root_invalid")
    operation_parent = temp_root / TEMP_PARENT_NAME
    if operation_parent.exists() or operation_parent.is_symlink():
        raise NodeFixtureRehearsalError("operation_parent_preexists")
    operation_parent.mkdir()

    rows: list[dict[str, Any]] = []
    cleanup_rows: list[dict[str, Any]] = []
    try:
        for scenario in SCENARIOS:
            scenario_root = operation_parent / scenario
            scenario_root.mkdir()
            try:
                row = _scenario_projection(
                    scenario=scenario,
                    root=scenario_root,
                    candidate_source=candidate_source,
                    attempt_id=attempt_id,
                    node_executable=str(executable_path),
                    run=run,
                    contract=contract,
                )
                rows.append(row)
            except Exception as error:  # retained only as a fixed validation coordinate
                rows.append(
                    {
                        "scenario": scenario,
                        "process_exit_code": None,
                        "stdout_bytes": 0,
                        "stderr_bytes": 0,
                        "caught_rejection": False,
                        "identical_rejection": False,
                        "node_version": None,
                        "diagnostic_accepted": False,
                        "diagnostic_error": type(error).__name__ + ":" + str(error),
                        "top_error_kind": None,
                        "top_message_coordinate": None,
                        "top_aggregate_shape": None,
                        "cause_node_count": 0,
                        "preexisting_sidecar_unchanged": None,
                        "fixture_sha256": None,
                        "wrapper_sha256": None,
                        "observer_sha256": None,
                    }
                )
            finally:
                _safe_remove_scenario(scenario_root, operation_parent)
                cleanup_rows.append({"scenario": scenario, "root_absent": True})
    finally:
        _safe_remove_operation(operation_parent, temp_root)

    reasons = validate_scenario_outcomes(rows)
    evidence = {
        "schema_version": EVIDENCE_VERSION,
        "operation_id": OPERATION_ID,
        "candidate_source": candidate_source,
        "result": "pass" if not reasons else "revision_required",
        "node": {
            "executable_name": executable_path.name,
            "executable_sha256": _sha256(executable_path.read_bytes()),
            "versions": sorted(
                {row["node_version"] for row in rows if row["node_version"]}
            ),
        },
        "scenarios": rows,
        "proof_boundary": contract["process_boundary"],
        "retention": {
            "raw_stdout_retained": False,
            "raw_stderr_retained": False,
            "raw_error_message_retained": False,
            "raw_stack_retained": False,
            "raw_paths_retained": False,
            "secret_sentinel_retained": False,
            "failure_reasons": reasons,
        },
        "cleanup": {
            "scenarios": cleanup_rows,
            "operation_parent_absent": not operation_parent.exists(),
        },
    }
    if SECRET_SENTINEL.encode() in _canonical_bytes(evidence):
        raise NodeFixtureRehearsalError("secret_sentinel_retained")
    jsonschema.validate(
        evidence, json.loads(EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8"))
    )
    return evidence


def report_text(evidence: dict[str, Any], *, attempt_id: str) -> str:
    now = datetime.now(ZoneInfo("Australia/Brisbane"))
    accepted = sum(row["diagnostic_accepted"] for row in evidence["scenarios"])
    identity = sum(row["identical_rejection"] for row in evidence["scenarios"])
    return f"""# Structured diagnostic wrapper Node fixture rehearsal report

Date: {now.date().isoformat()}

Timestamp: {now.isoformat()} (Australia/Brisbane)

- Attempt: `{attempt_id}`
- Result: `{evidence['result']}`
- Candidate source: `{evidence['candidate_source']}`
- Node processes: `4`
- Identical rejections: `{identity}/4`
- Accepted safe diagnostics: `{accepted}/3`
- Pre-existing sidecar unchanged: `{str(evidence['scenarios'][3]['preexisting_sidecar_unchanged']).lower()}`
- Harness / broker / worker / model / provider activity: `0 / 0 / 0 / 0 / 0`
- Raw process streams retained: `false`
- Operation root absent: `{str(evidence['cleanup']['operation_parent_absent']).lower()}`
- Failure coordinates: `{len(evidence['retention']['failure_reasons'])}`

Only authored local fixture modules were imported. No result in this report is
evidence of DSH boot, native Harness readiness, DeepSeek execution or provider
reliability.
"""


def write_attempt(evidence: dict[str, Any], *, attempt_id: str, promote: bool) -> None:
    attempt_root = ATTEMPTS_ROOT / attempt_id
    _write_exclusive(attempt_root / "execution-evidence.json", _canonical_bytes(evidence))
    _write_exclusive(
        attempt_root / "execution-report.md",
        report_text(evidence, attempt_id=attempt_id).encode(),
    )
    if promote:
        if evidence["result"] != "pass":
            raise NodeFixtureRehearsalError("cannot_promote_failed_attempt")
        _write_exclusive(EVIDENCE_PATH, _canonical_bytes(evidence))
        _write_exclusive(REPORT_PATH, report_text(evidence, attempt_id=attempt_id).encode())


def deterministic_check() -> dict[str, Any]:
    contract = load_contract()
    fake_root = Path("C:/deterministic/authored-node-fixture").resolve()
    fixture = fixture_source("nested_known")
    observer = observer_source(
        scenario="nested_known",
        wrapper_path=fake_root / "entrypoint-wrapper.mjs",
        result_path=fake_root / "observer-result.json",
    )
    if SECRET_SENTINEL.encode() not in fixture_source("unknown_secret_shaped"):
        raise NodeFixtureRehearsalError("secret_fixture_missing")
    if set(contract["accepted_sidecar_scenarios"]) != set(SCENARIOS[:3]):
        raise NodeFixtureRehearsalError("accepted_sidecar_scenarios_invalid")
    if "@deepseek-ai".encode() in fixture + observer:
        raise NodeFixtureRehearsalError("dsh_token_in_authored_source")
    return {
        "result": "pass",
        "scenario_count": len(SCENARIOS),
        "fixture_sha256": _sha256(fixture),
        "observer_sha256": _sha256(observer),
        "node_process_count": 0,
        "native_harness_process_count": 0,
        "provider_request_count": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--execute", action="store_true")
    parser.add_argument("--candidate-source")
    parser.add_argument("--attempt-id")
    parser.add_argument("--promote-pass", action="store_true")
    args = parser.parse_args()
    if args.check:
        print(json.dumps(deterministic_check(), sort_keys=True, indent=2))
        return 0
    if not args.candidate_source or not args.attempt_id:
        parser.error("--execute requires --candidate-source and --attempt-id")
    evidence = execute_attempt(
        candidate_source=args.candidate_source,
        attempt_id=args.attempt_id,
    )
    write_attempt(evidence, attempt_id=args.attempt_id, promote=args.promote_pass)
    print(json.dumps(evidence, sort_keys=True, indent=2))
    return 0 if evidence["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
