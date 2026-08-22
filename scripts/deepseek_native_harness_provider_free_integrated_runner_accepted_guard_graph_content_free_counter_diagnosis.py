"""Reconstruct one consumed fixture observation without starting a process."""

from __future__ import annotations

import argparse
from collections.abc import Iterator
from datetime import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any
from zoneinfo import ZoneInfo

import jsonschema


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import (  # noqa: E402
    deepseek_native_harness_provider_free_integrated_runner_accepted_guard_graph_materialization_recovery
    as predecessor,
)


OPERATION_ID = (
    "deepseek-native-harness-provider-free-integrated-runner-accepted-guard-"
    "graph-content-free-counter-diagnosis"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "diagnosis-evidence.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
REPORT_PATH = OPERATION_ROOT / "diagnosis-report.md"
CONTRACT_SCHEMA = "ariadne.native_harness_content_free_counter_contract.v1"
EVIDENCE_SCHEMA = "ariadne.native_harness_content_free_counter_evidence.v1"
RESULT = "unique_content_free_counter_observation_reconstructed"
FIXTURE_SCHEMA = predecessor.FIXTURE_SCHEMA
PASS_RESULT = predecessor.PASS_RESULT
SUCCESS_COORDINATE = predecessor.SUCCESS_COORDINATE
REJECTED_RESULT = "fixture_result_rejected"
TARGET_STDOUT_BYTES = 756
TARGET_STDOUT_SHA256 = (
    "6e75c083f6b42d5c828d53c7f16a11ae09897023bf0a8139abde615c674225ff"
)
EXPECTED_FIXTURE_SOURCE = {
    "bytes": 5165,
    "sha256": "81359ea4357b9f6b18d896f8681651582665ab7855e6bc5bb749937ca228fdc3",
}
EXPECTED_AGENT_SOURCE = {
    "bytes": 31560,
    "sha256": "e7e40c5ca66d9827a5084c5c0c68983f9685842bb9b6d604803d4cb4642bb263",
}
RESULT_KEYS = (
    "schema_version",
    "result",
    "structured_coordinate",
    "old_input_invalid_observed",
    "factory_create_agent_invocations",
    "setup_invocations",
    "setup_resolved",
    "preset_root_reads",
    "preset_mount_reads",
    "preset_mount_calls",
    "tool_view_calls",
    "tool_restrict_calls",
    "tool_schema_calls",
    "hook_installations",
    "scope_disposals",
    "runner_app_exit_code",
    "runner_status",
    "runner_failure_stage",
    "runner_request_count",
    "runner_tool_result_count",
    "runner_turn_kind",
    "runner_conclusion_marked",
    "live_agent_count",
    "raw_error_retained",
    "cordis_disposed",
)
FAILURE_STAGES = (
    "loader",
    "packages",
    "services",
    "roots",
    "factory",
    "published",
    "turn",
    "flush",
    "terminal",
)
EXPECTED_CANDIDATE_COUNT = 496


class ContentFreeCounterDiagnosisError(RuntimeError):
    """The closed content-free diagnosis rejected."""


sha256_bytes = predecessor.sha256_bytes
canonical_bytes = predecessor.canonical_bytes


def _binding(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {"bytes": len(payload), "sha256": sha256_bytes(payload)}


def write_exclusive(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(canonical_bytes(value))


def load_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_bytes())
    schema = json.loads(CONTRACT_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(contract)
    if contract["schema_version"] != CONTRACT_SCHEMA or contract["operation_id"] != OPERATION_ID:
        raise ContentFreeCounterDiagnosisError("contract_identity_rejected")
    for expected in contract["accepted_inputs"].values():
        if _binding(REPO_ROOT / expected["path"]) != {
            "bytes": expected["bytes"],
            "sha256": expected["sha256"],
        }:
            raise ContentFreeCounterDiagnosisError("accepted_input_binding_rejected")
    if contract["git_binding_policy"] != {
        "mode": "machine_resolved_only",
        "caller_authored_object_id_count": 0,
    }:
        raise ContentFreeCounterDiagnosisError("git_binding_policy_rejected")
    if contract["grammar"]["candidate_count"] != EXPECTED_CANDIDATE_COUNT:
        raise ContentFreeCounterDiagnosisError("grammar_contract_rejected")
    validate_source_derivation(contract)
    return contract


def installed_agent_source_path() -> Path:
    source_root = (
        predecessor.predecessor.predecessor.package_projection.MATERIALIZATION_SOURCE_ROOT.resolve(
            strict=True
        )
    )
    path = source_root / "node_modules" / "@deepseek-ai" / "dsh-agent" / "lib" / "index.js"
    resolved = path.resolve(strict=True)
    if not resolved.is_file() or not resolved.is_relative_to(source_root):
        raise ContentFreeCounterDiagnosisError("installed_agent_source_rejected")
    return resolved


def _result_keys_from_fixture(source: bytes) -> tuple[str, ...]:
    text = source.decode("utf-8")
    match = re.search(r"const result = \{\n(?P<body>[\s\S]+?)\n\};\nprocess\.stdout", text)
    if match is None:
        raise ContentFreeCounterDiagnosisError("fixture_result_object_rejected")
    return tuple(re.findall(r"^  ([a-z_]+):", match.group("body"), flags=re.MULTILINE))


def _install_model_selection_source(agent_source: bytes) -> str:
    text = agent_source.decode("utf-8")
    match = re.search(
        r"function installModelSelection\(agentCtx, selection\) \{[\s\S]+?\n\}\n//#endregion",
        text,
    )
    if match is None:
        raise ContentFreeCounterDiagnosisError("model_selection_source_rejected")
    return match.group(0)


def validate_source_derivation(contract: dict[str, Any]) -> dict[str, Any]:
    predecessor_contract = predecessor.load_contract()
    fixture = predecessor.fixture_source()
    if {"bytes": len(fixture), "sha256": sha256_bytes(fixture)} != EXPECTED_FIXTURE_SOURCE:
        raise ContentFreeCounterDiagnosisError("fixture_source_binding_rejected")
    if _result_keys_from_fixture(fixture) != RESULT_KEYS:
        raise ContentFreeCounterDiagnosisError("fixture_key_order_rejected")
    sources = predecessor.accepted_sources(predecessor_contract)
    runner = sources["runner"].decode("utf-8")
    agent_source_path = installed_agent_source_path()
    agent_source = agent_source_path.read_bytes()
    if {"bytes": len(agent_source), "sha256": sha256_bytes(agent_source)} != EXPECTED_AGENT_SOURCE:
        raise ContentFreeCounterDiagnosisError("installed_agent_source_binding_rejected")
    model_selection = _install_model_selection_source(agent_source)
    observed = {
        "fixture_result_key_count": len(RESULT_KEYS),
        "runner_preset_root_reads": runner.count("presets.roots"),
        "runner_hook_installations": runner.count("agentCtx.on("),
        "model_selection_hook_installations": model_selection.count("agentCtx.on("),
        "maximum_hook_installations": runner.count("agentCtx.on(")
        + model_selection.count("agentCtx.on("),
        "maximum_preset_root_reads": runner.count("presets.roots"),
    }
    if observed != contract["source_derivation"]:
        raise ContentFreeCounterDiagnosisError("source_derivation_rejected")
    return observed


def serialize_candidate(candidate: dict[str, Any]) -> bytes:
    if tuple(candidate) != RESULT_KEYS:
        raise ContentFreeCounterDiagnosisError("candidate_key_order_rejected")
    try:
        text = json.dumps(
            candidate,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as error:
        raise ContentFreeCounterDiagnosisError("candidate_serialization_rejected") from error
    return (text + "\n").encode("utf-8")


def _candidate(
    *,
    coordinate: str | None,
    create_count: int,
    setup_count: int,
    setup_resolved: bool,
    root_reads: int,
    mount_reads: int,
    mount_calls: int,
    view_calls: int,
    restrict_calls: int,
    schema_calls: int,
    hook_installations: int,
    scope_disposals: int,
    failure_stage: str,
) -> dict[str, Any]:
    return {
        "schema_version": FIXTURE_SCHEMA,
        "result": PASS_RESULT if coordinate == SUCCESS_COORDINATE else REJECTED_RESULT,
        "structured_coordinate": coordinate,
        "old_input_invalid_observed": False,
        "factory_create_agent_invocations": create_count,
        "setup_invocations": setup_count,
        "setup_resolved": setup_resolved,
        "preset_root_reads": root_reads,
        "preset_mount_reads": mount_reads,
        "preset_mount_calls": mount_calls,
        "tool_view_calls": view_calls,
        "tool_restrict_calls": restrict_calls,
        "tool_schema_calls": schema_calls,
        "hook_installations": hook_installations,
        "scope_disposals": scope_disposals,
        "runner_app_exit_code": 1,
        "runner_status": "failed",
        "runner_failure_stage": failure_stage,
        "runner_request_count": 0,
        "runner_tool_result_count": 0,
        "runner_turn_kind": None,
        "runner_conclusion_marked": False,
        "live_agent_count": 0,
        "raw_error_retained": False,
        "cordis_disposed": True,
    }


def enumerate_candidates() -> Iterator[dict[str, Any]]:
    yield _candidate(
        coordinate=SUCCESS_COORDINATE,
        create_count=1,
        setup_count=1,
        setup_resolved=True,
        root_reads=4,
        mount_reads=1,
        mount_calls=1,
        view_calls=1,
        restrict_calls=1,
        schema_calls=1,
        hook_installations=5,
        scope_disposals=1,
        failure_stage="factory",
    )
    for root_reads in range(5):
        for failure_stage in FAILURE_STAGES:
            yield _candidate(
                coordinate=None,
                create_count=0,
                setup_count=0,
                setup_resolved=False,
                root_reads=root_reads,
                mount_reads=0,
                mount_calls=0,
                view_calls=0,
                restrict_calls=0,
                schema_calls=0,
                hook_installations=0,
                scope_disposals=0,
                failure_stage=failure_stage,
            )
    chains = (
        (0, 0, 0, 0, 0),
        (1, 0, 0, 0, 0),
        (1, 1, 0, 0, 0),
        (1, 1, 1, 0, 0),
        (1, 1, 1, 1, 0),
        (1, 1, 1, 1, 1),
    )
    for root_reads in range(5):
        for failure_stage in FAILURE_STAGES:
            for mount_reads, mount_calls, view_calls, restrict_calls, schema_calls in chains:
                hook_values = range(5) if schema_calls == 1 else (0,)
                for hook_installations in hook_values:
                    yield _candidate(
                        coordinate=None,
                        create_count=1,
                        setup_count=1,
                        setup_resolved=False,
                        root_reads=root_reads,
                        mount_reads=mount_reads,
                        mount_calls=mount_calls,
                        view_calls=view_calls,
                        restrict_calls=restrict_calls,
                        schema_calls=schema_calls,
                        hook_installations=hook_installations,
                        scope_disposals=1,
                        failure_stage=failure_stage,
                    )


def diagnose(contract: dict[str, Any]) -> dict[str, Any]:
    candidates = list(enumerate_candidates())
    if len(candidates) != EXPECTED_CANDIDATE_COUNT:
        raise ContentFreeCounterDiagnosisError("candidate_count_rejected")
    length_matches: list[dict[str, Any]] = []
    hash_matches: list[dict[str, Any]] = []
    for candidate in candidates:
        payload = serialize_candidate(candidate)
        if len(payload) == TARGET_STDOUT_BYTES:
            length_matches.append(candidate)
            if sha256_bytes(payload) == TARGET_STDOUT_SHA256:
                hash_matches.append(candidate)
    if len(hash_matches) != 1:
        raise ContentFreeCounterDiagnosisError("unique_hash_match_rejected")
    unique = hash_matches[0]
    direct = serialize_candidate(unique)
    expected = next(iter(enumerate_candidates()))
    if unique != expected or len(direct) != TARGET_STDOUT_BYTES or sha256_bytes(direct) != TARGET_STDOUT_SHA256:
        raise ContentFreeCounterDiagnosisError("unique_observation_rejected")
    return {
        "candidate_count": len(candidates),
        "byte_length_match_count": len(length_matches),
        "byte_and_hash_match_count": len(hash_matches),
        "unique_observation": unique,
    }


def provider_free_check() -> dict[str, Any]:
    contract = load_contract()
    reading = diagnose(contract)
    if EVIDENCE_PATH.exists():
        schema = json.loads(EVIDENCE_SCHEMA_PATH.read_bytes())
        jsonschema.Draft202012Validator(schema).validate(json.loads(EVIDENCE_PATH.read_bytes()))
    return {
        "result": "provider_free_counter_diagnosis_check_pass",
        "candidate_count": reading["candidate_count"],
        "byte_length_match_count": reading["byte_length_match_count"],
        "byte_and_hash_match_count": reading["byte_and_hash_match_count"],
        "node_process_count": 0,
        "native_harness_process_count": 0,
        "model_request_count": 0,
        "provider_request_count": 0,
    }


def execute() -> dict[str, Any]:
    if EVIDENCE_PATH.exists() or REPORT_PATH.exists():
        raise ContentFreeCounterDiagnosisError("diagnosis_evidence_already_exists")
    contract = load_contract()
    reading = diagnose(contract)
    envelope = json.loads(predecessor.PROCESS_ENVELOPE_PATH.read_bytes())
    now = datetime.now(ZoneInfo("Australia/Brisbane"))
    evidence = {
        "schema_version": EVIDENCE_SCHEMA,
        "operation_id": OPERATION_ID,
        "timestamp": now.isoformat(),
        "result": RESULT,
        "contract_sha256": sha256_bytes(CONTRACT_PATH.read_bytes()),
        "source_derivation": validate_source_derivation(contract),
        "grammar": {
            "candidate_count": reading["candidate_count"],
            "byte_length_match_count": reading["byte_length_match_count"],
            "byte_and_hash_match_count": reading["byte_and_hash_match_count"],
            "target_stdout_bytes": envelope["stdout_bytes"],
            "target_stdout_sha256": envelope["stdout_sha256"],
            "uniqueness_scope": "frozen_source_derived_finite_grammar_only",
        },
        "unique_observation": reading["unique_observation"],
        "process_boundary": {
            "diagnosis_subprocess_count": 0,
            "node_process_count": 0,
            "native_harness_process_count": 0,
            "broker_process_count": 0,
            "worker_process_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "network_attempt_count": 0,
            "database_attempt_count": 0,
            "docker_attempt_count": 0,
            "product_target_attempt_count": 0,
        },
        "predecessor_disposition": {
            "attempt_id": predecessor.ATTEMPT_ID,
            "terminal_remains": "fixture_result_rejected",
            "reclassified": False,
            "retry_count": 0,
            "raw_stream_recovered": False,
        },
        "next_decision": {
            "decision": "admit_corrected_counter_contract_for_provider_free_boot_proof",
            "deepseek_turn_authorized": False,
            "provider_request_authorized": False,
        },
        "claim_boundary": {
            "unique_typed_observation_reconstructed": True,
            "old_input_invalid_coordinate_absent": True,
            "accepted_guard_crossing_diagnosed": True,
            "materialization_attempt_accepted": False,
            "native_harness_proved": False,
            "deepseek_turn_proved": False,
            "provider_reached": False,
            "product_authority": False,
        },
    }
    schema = json.loads(EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(evidence)
    write_exclusive(EVIDENCE_PATH, evidence)
    REPORT_PATH.write_text(
        "# Accepted guard-graph content-free counter diagnosis report\n\n"
        f"Date: {now.date().isoformat()}\n\n"
        f"Timestamp: {now.isoformat()} (Australia/Brisbane)\n\n"
        f"Result: `{RESULT}`\n\n"
        f"Exactly one of {reading['candidate_count']} frozen source-derived candidates "
        "matched both the retained 756-byte length and SHA-256. It records four "
        "preset-root reads, five hook installations and the passed composition "
        "coordinate before the controlled factory sentinel.\n\n"
        "The consumed predecessor remains rejected and was not retried, rewritten "
        "or reclassified. No process, Harness, worker, model, provider, network, "
        "database, Docker or product target was started.\n",
        encoding="utf-8",
        newline="\n",
    )
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.check == args.execute:
        raise ContentFreeCounterDiagnosisError("exactly_one_mode_required")
    result = provider_free_check() if args.check else execute()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
