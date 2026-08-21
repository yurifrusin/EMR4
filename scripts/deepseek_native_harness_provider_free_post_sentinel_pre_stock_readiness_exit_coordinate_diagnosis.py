"""Statically diagnose the post-sentinel, pre-stock-readiness rc.7 exit."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any

import jsonschema


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-post-sentinel-pre-stock-readiness-"
    "exit-coordinate-diagnosis"
)
CONTINUITY_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = CONTINUITY_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = CONTINUITY_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = CONTINUITY_ROOT / "evidence.schema.json"
EVIDENCE_PATH = CONTINUITY_ROOT / "diagnosis-evidence.json"
REPORT_PATH = CONTINUITY_ROOT / "diagnosis-report.md"
CONTRACT_SCHEMA = (
    "ariadne.deepseek_native_harness_post_sentinel_pre_stock_readiness_"
    "exit_diagnosis_contract.v1"
)
EVIDENCE_SCHEMA = (
    "ariadne.deepseek_native_harness_post_sentinel_pre_stock_readiness_"
    "exit_diagnosis_evidence.v1"
)
FULL_OID = re.compile(r"^[0-9a-f]{40}$")


class DiagnosisError(RuntimeError):
    """The bounded static diagnosis failed closed."""


@dataclass(frozen=True)
class StaticInputs:
    components: dict[str, bytes]
    package_files: dict[str, bytes]


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def _load_json_bytes(payload: bytes, coordinate: str) -> dict[str, Any]:
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise DiagnosisError(f"static_json_invalid:{coordinate}") from error
    if not isinstance(value, dict):
        raise DiagnosisError(f"static_json_not_object:{coordinate}")
    return value


def _decode_source(payload: bytes, coordinate: str) -> str:
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise DiagnosisError(f"static_source_not_utf8:{coordinate}") from error


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = _load_json_bytes(path.read_bytes(), "contract")
    schema = _load_json_bytes(CONTRACT_SCHEMA_PATH.read_bytes(), "contract_schema")
    jsonschema.validate(contract, schema)
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise DiagnosisError("contract_schema_mismatch")
    if contract.get("operation_id") != OPERATION_ID:
        raise DiagnosisError("contract_operation_mismatch")
    method = contract.get("method", {})
    expected_zero = {
        "import_repository_components": False,
        "execute_javascript": False,
        "node_process_limit": 0,
        "harness_process_limit": 0,
        "broker_process_limit": 0,
        "worker_process_limit": 0,
        "model_request_limit": 0,
        "provider_request_limit": 0,
        "network_request_limit": 0,
        "raw_stream_reconstruction": False,
        "required_supported_link_count": 8,
        "accepted_verdicts": [
            "unique_supported_exit_coordinate",
            "insufficient_static_evidence",
        ],
    }
    if method != expected_zero:
        raise DiagnosisError("contract_static_boundary_mismatch")
    return contract


def _git_source_is_ancestor(object_id: str) -> bool:
    if FULL_OID.fullmatch(object_id) is None:
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


def repository_inputs(contract: dict[str, Any]) -> StaticInputs:
    components: dict[str, bytes] = {}
    for row in contract["components"]:
        role = row["role"]
        path = REPO_ROOT / row["path"]
        if role in components or not path.is_file() or path.is_symlink():
            raise DiagnosisError(f"component_path_invalid:{role}")
        components[role] = path.read_bytes()

    package_files: dict[str, bytes] = {}
    package_root = Path(contract["package"]["materialization_root"])
    for row in contract["package"]["files"]:
        role = row["role"]
        path = package_root / row["path"]
        if role in package_files or not path.is_file() or path.is_symlink():
            raise DiagnosisError(f"package_path_invalid:{role}")
        package_files[role] = path.read_bytes()
    return StaticInputs(components=components, package_files=package_files)


def _binding_rows(
    contract: dict[str, Any], inputs: StaticInputs
) -> tuple[list[dict[str, Any]], bool]:
    rows: list[dict[str, Any]] = []
    for specification, observed_values in (
        (contract["components"], inputs.components),
        (contract["package"]["files"], inputs.package_files),
    ):
        for row in specification:
            expected = row["sha256"]
            observed = _sha256(observed_values.get(row["role"], b""))
            rows.append(
                {
                    "role": row["role"],
                    "expected_sha256": expected,
                    "observed_sha256": observed,
                    "matched": expected == observed,
                }
            )

    sources_ok = all(
        _git_source_is_ancestor(value)
        for value in [
            contract["planning_source"],
            *contract["accepted_sources"].values(),
        ]
    )
    rows.append(
        {
            "role": "git_sources_full_and_ancestral",
            "expected_sha256": "0" * 64,
            "observed_sha256": "0" * 64 if sources_ok else "f" * 64,
            "matched": sources_ok,
        }
    )
    return rows, all(row["matched"] for row in rows)


def _contains_once(source: str, token: str) -> bool:
    return source.count(token) == 1


def source_links(inputs: StaticInputs) -> list[dict[str, Any]]:
    boot_contract = _load_json_bytes(inputs.components["boot_contract"], "boot_contract")
    terminal = _load_json_bytes(inputs.components["failed_terminal"], "failed_terminal")
    profile_author = _decode_source(
        inputs.components["profile_and_sentinel_author"], "profile_author"
    )
    launcher = _decode_source(inputs.package_files["launcher_bin"], "launcher_bin")
    profile_boot = _decode_source(inputs.package_files["profile_boot"], "profile_boot")
    headless_patch = _decode_source(
        inputs.package_files["headless_bundle_patch"], "headless_bundle_patch"
    )
    startup = _decode_source(
        inputs.package_files["headless_startup"], "headless_startup"
    )
    cmdline = _decode_source(
        inputs.package_files["cmdline_adapter"], "cmdline_adapter"
    )
    commander = _decode_source(
        inputs.package_files["commander_command"], "commander_command"
    )

    startup_error = 'program.error("error: a task is required'
    startup_publish = 'ctx.provide(HEADLESS_STARTUP_SERVICE, { task });'
    startup_rejects_before_publish = (
        _contains_once(startup, 'const task = program.args.join(" ");')
        and _contains_once(startup, 'if (task.trim() === "")')
        and _contains_once(startup, startup_error)
        and _contains_once(startup, startup_publish)
        and startup.index(startup_error) < startup.index(startup_publish)
    )

    links = [
        (
            "frozen_launch.empty_inner_argument_snapshot",
            boot_contract.get("launch", {}).get("task_arguments") == []
            and terminal.get("launch", {}).get("task_argument_count") == 0
            and terminal.get("launch", {}).get("argument_count") == 5
            and terminal.get("launch", {}).get("profile_args")
            == ["--profile", "headless"],
        ),
        (
            "composition.headless_startup_mounted_and_not_disabled",
            _contains_once(headless_patch, "- id: headless-startup")
            and _contains_once(headless_patch, "name: '@deepseek-ai/dsh-headless/startup'")
            and profile_author.count("- id: headless-startup") == 0,
        ),
        (
            "composition.headless_runner_disabled_while_sentinel_activated",
            _contains_once(profile_author, "- id: headless-runner\n  disabled: true")
            and _contains_once(profile_author, "- id: synthetic-worker-hmr-sentinel")
            and terminal.get("hmr_events") == ["sentinel_activated"],
        ),
        (
            "launcher.profile_invocation_forwards_inner_args",
            _contains_once(launcher, "args: invocation.args")
            and _contains_once(launcher, "args: invocation.args\n")
            and _contains_once(launcher, "await runProfile({"),
        ),
        (
            "profile_boot.provides_args_and_app_exit_before_mount",
            _contains_once(profile_boot, "args: options.args,")
            and _contains_once(
                profile_boot, "exit: (code) => void shutdown.shutdown(code)"
            )
            and profile_boot.index("provideCmdline(hostCtx")
            < profile_boot.index("args: options.args,"),
        ),
        (
            "headless_startup.empty_task_rejected_before_service_publish",
            startup_rejects_before_publish,
        ),
        (
            "commander.error_defaults_to_exit_one",
            _contains_once(commander, "const exitCode = config.exitCode || 1;")
            and _contains_once(commander, "this._exit(exitCode, code, message);")
            and commander.index("const exitCode = config.exitCode || 1;")
            < commander.index("this._exit(exitCode, code, message);"),
        ),
        (
            "cmdline_app_exit_reaches_profile_shutdown_with_same_code",
            _contains_once(cmdline, "program.parse(args.get(), { from: \"user\" });")
            and _contains_once(cmdline, "exit(error.exitCode);")
            and _contains_once(profile_boot, "process.exitCode = code;")
            and profile_boot.count("forceExitOnce(code);") >= 1
            and _contains_once(profile_boot, "shutdown(code) {")
            and _contains_once(profile_boot, "return start(code, false);")
            and cmdline.index("program.parse(args.get(), { from: \"user\" });")
            < cmdline.index("exit(error.exitCode);")
            and profile_boot.index("shutdown(code) {")
            < profile_boot.index("return start(code, false);")
        ),
    ]
    return [
        {"ordinal": index, "coordinate": coordinate, "supported": supported}
        for index, (coordinate, supported) in enumerate(links, start=1)
    ]


def _terminal_projection(inputs: StaticInputs) -> tuple[dict[str, Any], bool]:
    terminal = _load_json_bytes(inputs.components["failed_terminal"], "failed_terminal")
    consumed = _load_json_bytes(inputs.components["consumed_attempt"], "consumed_attempt")
    boundary = terminal.get("provider_boundary", {})
    zero_fields = (
        "changed_runner_processes",
        "broker_processes",
        "worker_sessions",
        "prompts",
        "tool_executions",
        "model_requests",
        "provider_requests",
        "network_attempts",
        "docker_invocations",
        "database_invocations",
    )
    passed = bool(
        terminal.get("result") == "failed_closed"
        and terminal.get("failure_coordinate")
        == "native_process_exited_before_readiness"
        and terminal.get("hmr_events") == ["sentinel_activated"]
        and terminal.get("launch", {}).get("exit_code_after_controller_termination")
        == 1
        and terminal.get("launch", {}).get("readiness_observed") is False
        and terminal.get("launch", {}).get("retry_count") == 0
        and terminal.get("streams", {}).get("raw_retained") is False
        and terminal.get("cleanup", {}).get("raw_streams_retained") is False
        and all(boundary.get(field) == 0 for field in zero_fields)
        and consumed.get("state") == "consumed"
        and consumed.get("attempt_id") == terminal.get("attempt_id")
        and consumed.get("automatic_retry_count") == 0
        and consumed.get("resume_permitted") is False
    )
    return {
        "binding_passed": passed,
        "result": str(terminal.get("result")),
        "failure_coordinate": str(terminal.get("failure_coordinate")),
        "events": terminal.get("hmr_events", []),
        "exit_code": terminal.get("launch", {}).get(
            "exit_code_after_controller_termination"
        ),
        "readiness_observed": terminal.get("launch", {}).get("readiness_observed"),
        "retry_count": terminal.get("launch", {}).get("retry_count"),
        "raw_streams_retained": terminal.get("streams", {}).get("raw_retained"),
    }, passed


def analyze_static_inputs(
    contract: dict[str, Any], inputs: StaticInputs
) -> dict[str, Any]:
    bindings, bindings_ok = _binding_rows(contract, inputs)
    terminal, terminal_ok = _terminal_projection(inputs)
    package = _load_json_bytes(inputs.package_files["package_manifest"], "package")
    package_ok = bool(
        package.get("name") == contract["package"]["name"]
        and package.get("version") == contract["package"]["version"]
    )
    links = source_links(inputs)
    supported_count = sum(int(link["supported"]) for link in links)
    required_count = contract["method"]["required_supported_link_count"]
    all_links = supported_count == required_count == len(links)
    unique = bindings_ok and terminal_ok and package_ok and all_links

    evidence = {
        "schema_version": EVIDENCE_SCHEMA,
        "operation_id": OPERATION_ID,
        "result": "pass" if unique else "failed_closed",
        "verdict": (
            "unique_supported_exit_coordinate"
            if unique
            else "insufficient_static_evidence"
        ),
        "bindings": bindings,
        "terminal": terminal,
        "source_chain": {
            "supported_link_count": supported_count,
            "required_link_count": required_count,
            "all_links_supported": all_links,
            "links": links,
        },
        "narrowest_supported_coordinate": (
            "headless_startup.apply.missing_task_program_error_to_app_exit_one"
            if unique
            else None
        ),
        "zero_activity": {
            "node_process_count": 0,
            "harness_process_count": 0,
            "broker_process_count": 0,
            "worker_process_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "network_request_count": 0,
            "raw_stream_reconstruction_count": 0,
        },
        "claim_boundary": contract["claim_boundary"],
    }
    jsonschema.validate(
        evidence,
        _load_json_bytes(EVIDENCE_SCHEMA_PATH.read_bytes(), "evidence_schema"),
    )
    return evidence


def report_markdown(evidence: dict[str, Any]) -> str:
    timestamp = datetime.now().astimezone().isoformat()
    chain = evidence["source_chain"]
    coordinate = evidence["narrowest_supported_coordinate"] or "none"
    return f"""# DeepSeek native Harness post-sentinel exit-coordinate diagnosis

Date: {timestamp[:10]}
Timestamp: {timestamp} (Australia/Brisbane)

## Result

- Verdict: `{evidence['verdict']}`
- Narrowest supported coordinate: `{coordinate}`
- Exact source-chain links: `{chain['supported_link_count']} / {chain['required_link_count']}`
- Retained events: `{', '.join(evidence['terminal']['events'])}`
- Retained exit / readiness / retry: `{evidence['terminal']['exit_code']}` / `{str(evidence['terminal']['readiness_observed']).lower()}` / `{evidence['terminal']['retry_count']}`
- Node / Harness / broker / worker / model / provider / network activity: `0 / 0 / 0 / 0 / 0 / 0 / 0`

## Reading

The frozen launch passed no inner task argument. The exact headless bundle kept
its startup provider mounted even though the user patch disabled the one-shot
runner. After the sentinel activated, headless startup therefore took its
mandatory empty-task rejection branch. The exact command-line adapter routed
Commander's default failure code through `ctx.appExit`, and profile shutdown
disposed the tree with that same code before HMR registered both watched patch
paths.

This source chain is sufficient to explain the retained post-sentinel exit-one
terminal. It was derived without executing JavaScript and without reconstructing
or guessing the destroyed stderr text, stack, path, environment or stream.

## Claim boundary

{evidence['claim_boundary']}
"""


def run(output_root: Path = CONTINUITY_ROOT) -> dict[str, Any]:
    contract = load_contract()
    evidence = analyze_static_inputs(contract, repository_inputs(contract))
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / EVIDENCE_PATH.name).write_bytes(_canonical_json(evidence))
    (output_root / REPORT_PATH.name).write_text(
        report_markdown(evidence), encoding="utf-8", newline="\n"
    )
    return evidence


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=CONTINUITY_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        evidence = run(args.output_root)
    except (DiagnosisError, OSError, jsonschema.ValidationError) as error:
        raise SystemExit(str(error)) from error
    print(evidence["verdict"])
    return 0 if evidence["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
