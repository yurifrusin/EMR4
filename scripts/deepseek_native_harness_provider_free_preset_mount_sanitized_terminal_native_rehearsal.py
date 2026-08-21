"""Run one exact-source native preset-mount sanitized-terminal rehearsal."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Iterator
from zoneinfo import ZoneInfo

import jsonschema

from scripts import (
    deepseek_native_harness_provider_free_preset_composition_safe_terminal_bridge_rehearsal as native_base,
)
from scripts import (
    deepseek_native_harness_provider_free_preset_mount_sanitizer_runner_bridge_rehearsal as runner_bridge,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-preset-mount-sanitized-terminal-"
    "native-rehearsal"
)
EXECUTION_ATTEMPT_ID = "preset-mount-sanitized-terminal-native-attempt-001"
PRIVATE_SESSION_ID = "session-emr4-preset-mount-sanitized-terminal-001"
PUBLICATION_STOP = native_base.PUBLICATION_STOP
PRESET_ID = native_base.PRESET_ID
EXPECTED_TOOLS = list(native_base.EXPECTED_TOOLS)
TARGET_PATH = native_base.TARGET_PATH
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT_PATH = REPO_ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
SIDECAR_SCHEMA_PATH = OPERATION_ROOT / "sanitized-terminal-sidecar.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
PROCESS_ENVELOPE_SCHEMA_PATH = OPERATION_ROOT / "process-envelope.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "sanitized-terminal-native-evidence.json"
REPORT_PATH = OPERATION_ROOT / "sanitized-terminal-native-report.md"
EFFICACY_PATH = OPERATION_ROOT / "efficacy-reading.json"
ATTEMPT_CONSUMED_PATH = OPERATION_ROOT / "native-attempt-consumed.json"
PROCESS_ENVELOPE_PATH = OPERATION_ROOT / "attempt-001-process-envelope.json"
FOCUSED_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_provider_free_preset_mount_sanitized_terminal_native_rehearsal.py"
)
ACCEPTED_NATIVE_CONTROLLER_PATH = Path(native_base.__file__).resolve()
ACCEPTED_NATIVE_CONTRACT_PATH = native_base.CONTRACT_PATH
ACCEPTED_NATIVE_EVIDENCE_PATH = native_base.EVIDENCE_PATH
ACCEPTED_BRIDGE_CONTROLLER_PATH = Path(runner_bridge.__file__).resolve()
ACCEPTED_BRIDGE_CONTRACT_PATH = runner_bridge.CONTRACT_PATH
ACCEPTED_BRIDGE_EVIDENCE_PATH = runner_bridge.EVIDENCE_PATH
BRIDGE_PATH = runner_bridge.BRIDGE_PATH
SANITIZER_PATH = runner_bridge.SANITIZER_PATH
BRIDGE_MATERIALIZED_NAME = "preset-mount-sanitizer-runner-bridge.mjs"
SANITIZER_MATERIALIZED_NAME = (
    "deepseek_native_harness_provider_free_preset_mount_safe_subcoordinate_"
    "sanitizer.mjs"
)
FULL_OID = re.compile(r"^[0-9a-f]{40}$")
SAFE_DETAIL = native_base.SAFE_DETAIL
MAX_SIDECAR_BYTES = native_base.MAX_SIDECAR_BYTES
SIDECAR_SCHEMA = (
    "ariadne.native_harness_preset_composition_safe_terminal_sidecar.v1"
)
INTENDED_SIDECAR_SCHEMA = (
    "ariadne.native_harness_preset_mount_sanitized_terminal_sidecar.v1"
)
EVIDENCE_SCHEMA = "ariadne.native_harness_preset_mount_sanitized_terminal_evidence.v1"
PROCESS_ENVELOPE_SCHEMA = (
    "ariadne.native_harness_preset_mount_sanitized_terminal_process_envelope.v1"
)
STAGES = list(native_base.STAGES)
ERROR_CLASSES = list(native_base.ERROR_CLASSES)
TERMINALS = [
    "closed_subcoordinate_failure",
    "preset_mount_failure_attributed",
    "preset_composition_failure_attributed",
    "prepublication_veto_diagnosed",
    "runner_link_or_apply_absence",
]
SAFE_GUARD_COORDINATES = list(native_base.SAFE_GUARD_COORDINATES)
PRESET_MOUNT_CODES = list(runner_bridge.EXPECTED_CODES)
OUTPUT_PATHS = (
    EVIDENCE_PATH,
    REPORT_PATH,
    EFFICACY_PATH,
    ATTEMPT_CONSUMED_PATH,
    PROCESS_ENVELOPE_PATH,
)

_MATERIALIZATION_COUNT = 0


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _write_exclusive(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(payload)


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
        raise native_base.base.ClosedSubcoordinateError("git_resolution_failed")
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


def runner_source() -> bytes:
    return runner_bridge.build_runner_source()


def guard_source() -> bytes:
    return runner_bridge.build_guard_source()


def validate_runner_source(payload: bytes) -> dict[str, Any]:
    contract = runner_bridge.load_contract()
    derivation = runner_bridge.validate_source_derivation(contract)
    expected = runner_source()
    if payload != expected:
        raise native_base.base.ClosedSubcoordinateError("derived_runner_mismatch")
    source = payload.decode("utf-8")
    checks = {
        "accepted_runner_hash_exact": sha256_bytes(payload)
        == contract["source_sha256"]["derived_runner_sha256"],
        "preset_mount_terminal_once": source.count(
            'emit("preset_mount_failure_attributed", null)'
        )
        == 1,
        "preset_mount_branch_precedes_broader_guard": source.index(
            "error instanceof PresetMountSanitizedTerminalError"
        )
        < source.index("sanitizeEffectiveToolTerminal(error)"),
        "bridge_derivation_checks_all_pass": all(
            derivation["bridge_checks"].values()
        ),
        "emitted_sidecar_schema_token_exact": source.count(SIDECAR_SCHEMA) == 1,
        "unemitted_successor_schema_token_absent": INTENDED_SIDECAR_SCHEMA
        not in source,
    }
    if not all(checks.values()):
        raise native_base.base.ClosedSubcoordinateError(
            "sanitized_terminal_runner_shape_invalid"
        )
    return {
        **derivation["accepted_runner_projection"],
        "sha256": sha256_bytes(payload),
        "bytes": len(payload),
        "sanitized_terminal_checks": checks,
    }


def source_payloads(
    contract: dict[str, Any],
) -> tuple[bytes, bytes, bytes, bytes, dict[str, str]]:
    post = native_base.base
    base_contract = post.predecessor.load_contract()
    _, helper, _old_guard, sentinel, _ = post.predecessor.source_payloads(
        base_contract
    )
    runner = runner_source()
    guard = guard_source()
    validate_runner_source(runner)
    observed = {
        "diagnostic_runner_sha256": sha256_bytes(runner),
        "generated_helper_sha256": sha256_bytes(helper),
        "controller_module_sha256": sha256_file(post.ACCEPTED_CONTROLLER_PATH),
        "effective_tool_guard_sha256": sha256_bytes(guard),
        "readiness_sentinel_sha256": sha256_bytes(sentinel),
        "accepted_runner_generator_sha256": sha256_file(
            runner_bridge.ACCEPTED_RUNNER_GENERATOR_PATH
        ),
        "accepted_guard_generator_sha256": sha256_file(
            runner_bridge.ACCEPTED_GUARD_GENERATOR_PATH
        ),
        "runner_bridge_generator_sha256": sha256_file(
            ACCEPTED_BRIDGE_CONTROLLER_PATH
        ),
        "preset_mount_bridge_sha256": sha256_file(BRIDGE_PATH),
        "preset_mount_sanitizer_sha256": sha256_file(SANITIZER_PATH),
    }
    if observed != contract["source_bindings"]:
        raise native_base.base.ClosedSubcoordinateError("source_binding_mismatch")
    return runner, helper, guard, sentinel, observed


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = json.loads(path.read_bytes())
    schema = json.loads(CONTRACT_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(contract)
    plan_relative = PLAN_PATH.relative_to(REPO_ROOT).as_posix()
    if (
        contract["schema_version"]
        != "ariadne.native_harness_preset_mount_sanitized_terminal_contract.v1"
        or contract["operation_id"] != OPERATION_ID
        or contract["planning_source"]
        != _git("rev-parse", "--verify", f"{contract['planning_source']}^{{commit}}")
        or contract["planning_source"]
        != _git("log", "-1", "--format=%H", "--", plan_relative)
    ):
        raise native_base.base.ClosedSubcoordinateError(
            "contract_identity_or_planning_source_invalid"
        )
    if contract["execution_attempt"] != {
        "attempt_id": EXECUTION_ATTEMPT_ID,
        "native_process_count": 1,
        "automatic_retry": False,
        "manual_retry": False,
        "resume": False,
    }:
        raise native_base.base.ClosedSubcoordinateError("one_process_latch_invalid")
    if contract["closed_vocabulary"] != {
        "stages": STAGES,
        "error_classes": ERROR_CLASSES,
        "terminals": TERMINALS,
        "safe_guard_coordinates": SAFE_GUARD_COORDINATES,
        "preset_mount_codes": PRESET_MOUNT_CODES,
    }:
        raise native_base.base.ClosedSubcoordinateError("closed_vocabulary_invalid")
    if contract["preset_mount_bridge"] != {
        "stage": "preset_mount",
        "detail": None,
        "only_proving_result": "preset_mount_failure_attributed",
        "bridge_materialized_name": BRIDGE_MATERIALIZED_NAME,
        "sanitizer_materialized_name": SANITIZER_MATERIALIZED_NAME,
    }:
        raise native_base.base.ClosedSubcoordinateError(
            "preset_mount_bridge_contract_invalid"
        )
    if contract["process_envelope"] != {
        "path": PROCESS_ENVELOPE_PATH.relative_to(REPO_ROOT).as_posix(),
        "persist_before_semantic_admission": True,
        "stream_content_retained": False,
        "numeric_exit_code_observed": False,
    }:
        raise native_base.base.ClosedSubcoordinateError(
            "process_envelope_contract_invalid"
        )
    if contract["factory_boundary"] != {
        "private_session_id": PRIVATE_SESSION_ID,
        "publication_stop": PUBLICATION_STOP,
        "agents_create_invocations_max": 1,
        "published_agents": 0,
        "published_sessions": 0,
    }:
        raise native_base.base.ClosedSubcoordinateError("factory_boundary_invalid")
    if contract["selection"] != {
        "provider": "deepseek-official",
        "model": "deepseek-v4-flash",
        "reasoning_effort": "high",
        "max_tokens": 4096,
    }:
        raise native_base.base.ClosedSubcoordinateError("selection_invalid")
    if contract["required_zero_counters"] != [
        "turn_count",
        "request_count",
        "broker_process_count",
        "broker_request_count",
        "occupied_worker_count",
        "model_request_count",
        "provider_request_count",
        "network_attempt_count",
        "database_invocation_count",
        "docker_invocation_count",
        "target_creation_count",
        "target_use_count",
        "published_agents",
        "published_sessions",
    ]:
        raise native_base.base.ClosedSubcoordinateError(
            "required_zero_counters_invalid"
        )
    if contract["claim_boundary"] != {
        "only_preset_mount_failure_attributed_proves_new_bridge": True,
        "worker_launch_authorized": False,
        "model_provider_request_authorized": False,
        "retry_authorized": False,
        "target_or_product_authority": False,
    }:
        raise native_base.base.ClosedSubcoordinateError("claim_boundary_invalid")
    return contract


def validate_predecessors(contract: dict[str, Any]) -> dict[str, Any]:
    if not _ancestor(contract["planning_source"]):
        raise native_base.base.ClosedSubcoordinateError(
            "planning_source_not_ancestor"
        )
    post = native_base.base
    base_contract = post.predecessor.load_contract()
    predecessor_paths = {
        "frozen_plan_sha256": PLAN_PATH,
        "threat_model_sha256": THREAT_PATH,
        "accepted_native_controller_sha256": ACCEPTED_NATIVE_CONTROLLER_PATH,
        "accepted_native_contract_sha256": ACCEPTED_NATIVE_CONTRACT_PATH,
        "accepted_native_evidence_sha256": ACCEPTED_NATIVE_EVIDENCE_PATH,
        "accepted_runner_bridge_controller_sha256": ACCEPTED_BRIDGE_CONTROLLER_PATH,
        "accepted_runner_bridge_contract_sha256": ACCEPTED_BRIDGE_CONTRACT_PATH,
        "accepted_runner_bridge_evidence_sha256": ACCEPTED_BRIDGE_EVIDENCE_PATH,
        "accepted_bridge_module_sha256": BRIDGE_PATH,
        "accepted_sanitizer_module_sha256": SANITIZER_PATH,
    }
    observed = {
        key: sha256_file(path) for key, path in predecessor_paths.items()
    }
    if observed != contract["predecessor_bytes"]:
        raise native_base.base.ClosedSubcoordinateError(
            "predecessor_digest_mismatch"
        )
    if sha256_file(post.predecessor.CONTRACT_PATH) != contract["base_contract_sha256"]:
        raise native_base.base.ClosedSubcoordinateError(
            "base_contract_binding_mismatch"
        )
    implementation = {
        "execution_controller_sha256": sha256_file(Path(__file__).resolve()),
        "focused_test_sha256": sha256_file(FOCUSED_TEST_PATH),
        "contract_schema_sha256": sha256_file(CONTRACT_SCHEMA_PATH),
        "sidecar_schema_sha256": sha256_file(SIDECAR_SCHEMA_PATH),
        "evidence_schema_sha256": sha256_file(EVIDENCE_SCHEMA_PATH),
        "process_envelope_schema_sha256": sha256_file(
            PROCESS_ENVELOPE_SCHEMA_PATH
        ),
    }
    if implementation != contract["implementation_bytes"]:
        raise native_base.base.ClosedSubcoordinateError(
            "implementation_digest_mismatch"
        )
    accepted_bridge = json.loads(ACCEPTED_BRIDGE_EVIDENCE_PATH.read_bytes())
    accepted_native = json.loads(ACCEPTED_NATIVE_EVIDENCE_PATH.read_bytes())
    if (
        accepted_bridge.get("result") != "pass"
        or accepted_bridge.get("claim_boundary", {}).get(
            "runner_bridge_deterministically_admitted"
        )
        is not True
        or accepted_bridge.get("claim_boundary", {}).get("runner_executed")
        is not False
        or accepted_native.get("result") != "pass"
        or accepted_native.get("provider_boundary", {}).get(
            "provider_request_count"
        )
        != 0
    ):
        raise native_base.base.ClosedSubcoordinateError(
            "accepted_predecessor_semantics_invalid"
        )
    source_payloads(contract)
    return {
        "base_contract": base_contract,
        "predecessor_sha256": observed,
        "implementation_sha256": implementation,
    }


def _persist_process_envelope(
    *, candidate_source: str, sidecar_payload: bytes | None
) -> dict[str, Any]:
    envelope = {
        "schema_version": PROCESS_ENVELOPE_SCHEMA,
        "operation_id": OPERATION_ID,
        "execution_attempt_id": EXECUTION_ATTEMPT_ID,
        "candidate_source": candidate_source,
        "sidecar_file_seen": sidecar_payload is not None,
        "sidecar_bytes": len(sidecar_payload) if sidecar_payload is not None else 0,
        "sidecar_sha256": (
            sha256_bytes(sidecar_payload) if sidecar_payload is not None else None
        ),
        "numeric_exit_code_observed": False,
        "numeric_exit_code": None,
        "stdout_retained": False,
        "stderr_retained": False,
        "raw_stream_read": False,
        "stream_content_retained": False,
        "sidecar_semantics_interpreted": False,
        "raw_runtime_detail_retained": False,
        "native_process_count": 1,
        "retry_count": 0,
        "resume_count": 0,
        "further_process_authorized": False,
    }
    schema = json.loads(PROCESS_ENVELOPE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(envelope)
    payload = _canonical(envelope)
    if PROCESS_ENVELOPE_PATH.exists():
        if PROCESS_ENVELOPE_PATH.read_bytes() != payload:
            raise native_base.base.ClosedSubcoordinateError(
                "process_envelope_changed_after_persistence"
            )
    else:
        _write_exclusive(PROCESS_ENVELOPE_PATH, payload)
    return envelope


def read_sidecar(
    path: Path,
    *,
    disposable_root: Path,
    contract: dict[str, Any],
    candidate_source: str,
) -> dict[str, Any]:
    if not path.is_absolute() or not disposable_root.is_absolute():
        raise native_base.base.ClosedSubcoordinateError(
            "sidecar_paths_must_be_absolute"
        )
    if disposable_root.is_symlink() or not disposable_root.is_dir() or path.is_symlink():
        raise native_base.base.ClosedSubcoordinateError("sidecar_path_invalid")
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(disposable_root.resolve())
    except (OSError, ValueError) as error:
        raise native_base.base.ClosedSubcoordinateError(
            "sidecar_path_outside_disposable_root"
        ) from error
    if not resolved.is_file() or resolved.stat().st_size > MAX_SIDECAR_BYTES:
        raise native_base.base.ClosedSubcoordinateError("sidecar_file_invalid")
    payload = resolved.read_bytes()
    try:
        value = json.loads(payload)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise native_base.base.ClosedSubcoordinateError(
            "sidecar_json_invalid"
        ) from error

    # The content-free envelope is durable before schema or terminal semantics
    # are admitted. Only byte count and digest cross this boundary.
    _persist_process_envelope(
        candidate_source=candidate_source,
        sidecar_payload=payload,
    )

    schema = json.loads(SIDECAR_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(value)
    fixed = {
        "schema_version": SIDECAR_SCHEMA,
        "operation_id": OPERATION_ID,
        "execution_attempt_id": EXECUTION_ATTEMPT_ID,
        "candidate_source": candidate_source,
        "runner_sha256": contract["source_bindings"]["diagnostic_runner_sha256"],
        "effective_tool_guard_sha256": contract["source_bindings"][
            "effective_tool_guard_sha256"
        ],
        "preset_sha256": contract["preset"]["sha256"],
        "fixed_identity_sha256": sha256_bytes(PRIVATE_SESSION_ID.encode()),
        "target_path_sha256": sha256_bytes(TARGET_PATH.encode()),
        "raw_error_retained": False,
        "target_created": False,
        "target_used": False,
        "turn_count": 0,
        "request_count": 0,
        "broker_process_count": 0,
        "broker_request_count": 0,
        "occupied_worker_count": 0,
        "model_request_count": 0,
        "provider_request_count": 0,
        "database_invocation_count": 0,
        "docker_invocation_count": 0,
    }
    if any(value[key] != expected for key, expected in fixed.items()):
        raise native_base.base.ClosedSubcoordinateError(
            "sidecar_fixed_binding_mismatch"
        )
    stage_index = STAGES.index(value["last_admitted_stage"])
    expected_invocations = (
        1 if stage_index >= STAGES.index("agent_factory_invoked") else 0
    )
    expected_private = (
        1 if stage_index >= STAGES.index("private_identity_admitted") else 0
    )
    if value["agent_create_invocation_count"] != expected_invocations:
        raise native_base.base.ClosedSubcoordinateError(
            "sidecar_factory_count_stage_mismatch"
        )
    if (
        value["private_agent_preparation_count"] != expected_private
        or value["private_session_preparation_count"] != expected_private
    ):
        raise native_base.base.ClosedSubcoordinateError(
            "sidecar_private_count_stage_mismatch"
        )

    result = value["result"]
    preset_terminal = value["preset_mount_terminal"]
    if result == "prepublication_veto_diagnosed":
        valid = (
            value["last_admitted_stage"] == "postrollback_registries_empty"
            and value["error_class"] is None
            and value["safe_guard_coordinate"] is None
            and value["safe_guard_detail"] is None
            and preset_terminal is None
            and value["preset_mounted"]
            and value["model_selection_installed"]
            and value["veto_exact"]
            and value["veto_rejected"]
        )
    elif result == "preset_mount_failure_attributed":
        valid = (
            value["last_admitted_stage"] == "private_identity_admitted"
            and value["error_class"] is None
            and value["safe_guard_coordinate"] is None
            and value["safe_guard_detail"] is None
            and isinstance(preset_terminal, dict)
            and list(preset_terminal) == ["stage", "code", "detail"]
            and preset_terminal["stage"] == "preset_mount"
            and preset_terminal["code"] in PRESET_MOUNT_CODES
            and preset_terminal["detail"] is None
            and not value["preset_mounted"]
            and not value["model_selection_installed"]
            and not value["veto_exact"]
            and not value["veto_rejected"]
        )
    elif result == "preset_composition_failure_attributed":
        detail = value["safe_guard_detail"]
        names = [] if detail is None else detail.split(",")
        valid = (
            value["last_admitted_stage"] == "private_identity_admitted"
            and value["error_class"] is None
            and value["safe_guard_coordinate"] in SAFE_GUARD_COORDINATES
            and (detail is None or SAFE_DETAIL.fullmatch(detail) is not None)
            and names == sorted(set(names))
            and preset_terminal is None
            and not value["preset_mounted"]
            and not value["model_selection_installed"]
            and not value["veto_exact"]
            and not value["veto_rejected"]
        )
    elif result == "closed_subcoordinate_failure":
        valid = (
            value["error_class"] is not None
            and value["safe_guard_coordinate"] is None
            and value["safe_guard_detail"] is None
            and preset_terminal is None
        )
    else:
        valid = False
    if not valid:
        raise native_base.base.ClosedSubcoordinateError(
            "sidecar_terminal_semantics_invalid"
        )
    return value


def build_controller_terminal(sidecar: dict[str, Any] | None) -> dict[str, Any]:
    if sidecar is None:
        if PROCESS_ENVELOPE_PATH.exists():
            envelope = json.loads(PROCESS_ENVELOPE_PATH.read_bytes())
            schema = json.loads(PROCESS_ENVELOPE_SCHEMA_PATH.read_bytes())
            jsonschema.Draft202012Validator(schema).validate(envelope)
            if (
                envelope["sidecar_file_seen"] is not True
                or envelope["sidecar_semantics_interpreted"] is not False
                or envelope["stream_content_retained"] is not False
            ):
                raise native_base.base.ClosedSubcoordinateError(
                    "existing_rejected_sidecar_envelope_invalid"
                )
        else:
            _persist_process_envelope(
                candidate_source=_git("rev-parse", "HEAD"),
                sidecar_payload=None,
            )
        return {
            "result": "runner_link_or_apply_absence",
            "last_admitted_stage": None,
            "error_class": None,
            "safe_guard_coordinate": None,
            "safe_guard_detail": None,
            "preset_mount_terminal": None,
            "factory_boundary": None,
            "raw_runtime_detail_retained": False,
        }
    return {
        "result": sidecar["result"],
        "last_admitted_stage": sidecar["last_admitted_stage"],
        "error_class": sidecar["error_class"],
        "safe_guard_coordinate": sidecar["safe_guard_coordinate"],
        "safe_guard_detail": sidecar["safe_guard_detail"],
        "preset_mount_terminal": sidecar["preset_mount_terminal"],
        "factory_boundary": {
            key: sidecar[key]
            for key in (
                "agent_create_invocation_count",
                "private_agent_preparation_count",
                "private_session_preparation_count",
                "live_agent_count",
                "live_session_count",
                "session_created_event_count",
                "agent_created_event_count",
                "agent_session_start_event_count",
            )
        },
        "raw_runtime_detail_retained": False,
    }


def _controller_failure(**kwargs: Any) -> str | None:
    terminal = kwargs["terminal"]
    if not kwargs["process_started"]:
        return "PRELAUNCH_REJECTED"
    if not kwargs["readiness_valid"] or kwargs["readiness_events"] != [
        "sentinel_activated",
        "stock_headless_hmr_ready",
    ]:
        return "READINESS_REJECTED"
    if kwargs["hmr_mutation_count"] != 1:
        return "HMR_MUTATION_REJECTED"
    if kwargs["sidecar_file_seen"] and not kwargs["sidecar_valid"]:
        return "TYPED_SIDECAR_REJECTED"
    if terminal is None:
        return "CONTROLLER_TERMINAL_REJECTED"
    expected_exit = {
        "prepublication_veto_diagnosed": 0,
        "preset_mount_failure_attributed": 3,
        "preset_composition_failure_attributed": 3,
        "closed_subcoordinate_failure": 2,
        "runner_link_or_apply_absence": 2,
    }[terminal["result"]]
    if kwargs["exit_code"] != expected_exit:
        return "PROCESS_EXIT_REJECTED"
    factory = terminal["factory_boundary"]
    if factory is not None and any(
        factory[key] != 0
        for key in (
            "live_agent_count",
            "live_session_count",
            "session_created_event_count",
            "agent_created_event_count",
            "agent_session_start_event_count",
        )
    ):
        return "PUBLICATION_BOUNDARY_REJECTED"
    if not kwargs["broker_zero"]:
        return "BROKER_BOUNDARY_REJECTED"
    if not kwargs["network_ledger_valid"] or kwargs["network_attempt_count"]:
        return "NETWORK_BOUNDARY_REJECTED"
    if not kwargs["bundle_unchanged"]:
        return "CANONICAL_BUNDLE_MUTATED"
    if not kwargs["target_absent"]:
        return "TARGET_BOUNDARY_REJECTED"
    if not kwargs["process_absent"] or not kwargs["root_absent"]:
        return "CLEANUP_REJECTED"
    if not PROCESS_ENVELOPE_PATH.is_file():
        return "PROCESS_ENVELOPE_MISSING"
    return None


def _report_timestamp() -> str:
    return datetime.now(ZoneInfo("Australia/Brisbane")).isoformat()


def _render_report(evidence: dict[str, Any]) -> str:
    terminal = evidence["controller_terminal"] or {}
    preset_terminal = terminal.get("preset_mount_terminal")
    envelope_sha = (
        sha256_file(PROCESS_ENVELOPE_PATH)
        if PROCESS_ENVELOPE_PATH.is_file()
        else "missing"
    )
    return f"""# Native Harness preset-mount sanitized-terminal report

Date: 2026-08-22

Timestamp: {_report_timestamp()} (Australia/Brisbane)

Result: **{evidence['result']}**

- Execution attempt: `{evidence['execution_attempt_id']}`
- Full execution source: `{evidence['candidate_source']}`
- Native terminal: `{terminal.get('result')}`
- Preset-mount terminal: `{json.dumps(preset_terminal, sort_keys=True)}`
- Broader safe coordinate: `{terminal.get('safe_guard_coordinate')}`
- Last admitted stage: `{terminal.get('last_admitted_stage')}`
- Native process / retry: `{evidence['launch']['native_process_count']} / 0`
- Turn / broker / model / provider / network: `0 / 0 / 0 / 0 / {evidence['provider_boundary']['network_attempt_count']}`
- Content-free presemantic envelope SHA-256: `{envelope_sha}`
- Target created or used: `false / false`
- Process and disposable root absent: `{str(evidence['cleanup']['process_absent']).lower()} / {str(evidence['cleanup']['disposable_root_absent']).lower()}`

Only `preset_mount_failure_attributed` proves that the new exact bridge executed
inside the native rc.7 path. Every other finite terminal remains bounded
provider-free diagnostic evidence. No worker turn, model/provider request,
target use, product/data action or production authority is claimed.
"""


def _efficacy(evidence: dict[str, Any]) -> dict[str, Any]:
    terminal = evidence["controller_terminal"] or {}
    result = terminal.get("result")
    return {
        "schema_version": (
            "ariadne.native_harness_preset_mount_sanitized_terminal_efficacy.v1"
        ),
        "operation_id": OPERATION_ID,
        "execution_attempt_id": EXECUTION_ATTEMPT_ID,
        "candidate_source": evidence["candidate_source"],
        "result": evidence["result"],
        "native_terminal": result,
        "preset_mount_terminal": terminal.get("preset_mount_terminal"),
        "safe_guard_coordinate": terminal.get("safe_guard_coordinate"),
        "process_envelope_sha256": (
            sha256_file(PROCESS_ENVELOPE_PATH)
            if PROCESS_ENVELOPE_PATH.is_file()
            else None
        ),
        "new_bridge_runtime_path_proved": result
        == "preset_mount_failure_attributed",
        "worker_launch_authorized": False,
        "occupied_model_launch_authorized": False,
        "provider_request_authorized": False,
        "retry_authorized": False,
    }


@contextmanager
def _bound_native() -> Iterator[None]:
    global _MATERIALIZATION_COUNT
    post = native_base.base
    package_controller = post.predecessor.predecessor
    post_bindings: dict[str, Any] = {
        "OPERATION_ID": OPERATION_ID,
        "EXECUTION_ATTEMPT_ID": EXECUTION_ATTEMPT_ID,
        "PRIVATE_SESSION_ID": PRIVATE_SESSION_ID,
        "OPERATION_ROOT": OPERATION_ROOT,
        "PLAN_PATH": PLAN_PATH,
        "THREAT_PATH": THREAT_PATH,
        "CONTRACT_PATH": CONTRACT_PATH,
        "CONTRACT_SCHEMA_PATH": CONTRACT_SCHEMA_PATH,
        "SIDECAR_SCHEMA_PATH": SIDECAR_SCHEMA_PATH,
        "EVIDENCE_SCHEMA_PATH": EVIDENCE_SCHEMA_PATH,
        "EVIDENCE_PATH": EVIDENCE_PATH,
        "REPORT_PATH": REPORT_PATH,
        "EFFICACY_PATH": EFFICACY_PATH,
        "ATTEMPT_CONSUMED_PATH": ATTEMPT_CONSUMED_PATH,
        "FOCUSED_TEST_PATH": FOCUSED_TEST_PATH,
        "SIDECAR_SCHEMA": SIDECAR_SCHEMA,
        "EVIDENCE_SCHEMA": EVIDENCE_SCHEMA,
        "STAGES": STAGES,
        "ERROR_CLASSES": ERROR_CLASSES,
        "TERMINALS": TERMINALS,
        "runner_source": runner_source,
        "validate_runner_source": validate_runner_source,
        "load_contract": load_contract,
        "validate_predecessors": validate_predecessors,
        "read_sidecar": read_sidecar,
        "build_controller_terminal": build_controller_terminal,
        "_controller_failure": _controller_failure,
        "_render_report": _render_report,
        "_efficacy": _efficacy,
        "source_payloads": source_payloads,
    }
    original_post = {name: getattr(post, name) for name in post_bindings}
    original_write = package_controller._write_exclusive
    _MATERIALIZATION_COUNT = 0

    def exact_write(path: Path, payload: bytes) -> None:
        global _MATERIALIZATION_COUNT
        original_write(path, payload)
        if path.name != "effective-tool-guard.mjs":
            return
        if payload != guard_source():
            raise native_base.base.ClosedSubcoordinateError(
                "materialized_guard_payload_mismatch"
            )
        proof_dir = path.parent
        original_write(
            proof_dir / BRIDGE_MATERIALIZED_NAME,
            BRIDGE_PATH.read_bytes(),
        )
        original_write(
            proof_dir / SANITIZER_MATERIALIZED_NAME,
            SANITIZER_PATH.read_bytes(),
        )
        _MATERIALIZATION_COUNT += 1

    try:
        for name, value in post_bindings.items():
            setattr(post, name, value)
        package_controller._write_exclusive = exact_write
        yield
    finally:
        package_controller._write_exclusive = original_write
        for name, value in original_post.items():
            setattr(post, name, value)


def _validate_persisted_outputs() -> dict[str, Any]:
    evidence = json.loads(EVIDENCE_PATH.read_bytes())
    envelope = json.loads(PROCESS_ENVELOPE_PATH.read_bytes())
    evidence_schema = json.loads(EVIDENCE_SCHEMA_PATH.read_bytes())
    envelope_schema = json.loads(PROCESS_ENVELOPE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator(evidence_schema).validate(evidence)
    jsonschema.Draft202012Validator(envelope_schema).validate(envelope)
    if (
        evidence["source_bindings"] != load_contract()["source_bindings"]
        or evidence["launch"]["native_process_count"] != 1
        or evidence["launch"]["retry_count"] != 0
        or any(
            evidence["provider_boundary"][key] != 0
            for key in (
                "turn_count",
                "request_count",
                "broker_process_count",
                "broker_request_count",
                "occupied_worker_count",
                "model_request_count",
                "provider_request_count",
                "database_invocation_count",
                "docker_invocation_count",
                "network_attempt_count",
            )
        )
        or not evidence["cleanup"]["process_absent"]
        or not evidence["cleanup"]["disposable_root_absent"]
        or not evidence["target"]["absent_after_process"]
        or envelope["sidecar_semantics_interpreted"] is not False
        or envelope["stream_content_retained"] is not False
        or envelope["further_process_authorized"] is not False
    ):
        raise native_base.base.ClosedSubcoordinateError(
            "persisted_native_evidence_rejected"
        )
    return evidence


def deterministic_check(cache_root: Path | None = None) -> dict[str, Any]:
    existing = [path.exists() for path in OUTPUT_PATHS]
    if any(existing) and not all(existing):
        raise native_base.base.ClosedSubcoordinateError(
            "partial_native_output_state"
        )
    with _bound_native():
        result = native_base.base.deterministic_check(cache_root)
    result["artifact_state"] = "fresh"
    result["native_process_count"] = 0
    result["source_bindings"] = source_payloads(load_contract())[-1]
    if all(existing):
        evidence = _validate_persisted_outputs()
        result.update(
            {
                "artifact_state": "consumed",
                "native_process_count": evidence["launch"][
                    "native_process_count"
                ],
                "result": evidence["result"],
                "native_terminal": evidence["controller_terminal"]["result"],
                "new_bridge_runtime_path_proved": evidence[
                    "controller_terminal"
                ]["result"]
                == "preset_mount_failure_attributed",
            }
        )
    return result


def execute_rehearsal(cache_root: Path | None = None) -> dict[str, Any]:
    if any(path.exists() for path in OUTPUT_PATHS):
        raise native_base.base.ClosedSubcoordinateError(
            "native_output_already_exists"
        )
    with _bound_native():
        evidence = native_base.base.execute_rehearsal(cache_root)
        if _MATERIALIZATION_COUNT != 1:
            raise native_base.base.ClosedSubcoordinateError(
                "exact_import_materialization_count_rejected"
            )
    _validate_persisted_outputs()
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--execute", action="store_true")
    parser.add_argument("--cache-root", type=Path)
    args = parser.parse_args()
    try:
        result = (
            execute_rehearsal(args.cache_root)
            if args.execute
            else deterministic_check(args.cache_root)
        )
    except (
        native_base.base.ClosedSubcoordinateError,
        jsonschema.ValidationError,
        jsonschema.SchemaError,
        OSError,
        ValueError,
        json.JSONDecodeError,
        subprocess.SubprocessError,
    ) as error:
        print(json.dumps({"status": "failed", "error": type(error).__name__}))
        return 1
    terminal = result.get("controller_terminal") or {}
    print(
        json.dumps(
            {
                "status": "passed",
                "operation_id": OPERATION_ID,
                "artifact_state": result.get("artifact_state", "consumed"),
                "native_process_count": result.get("native_process_count", 1),
                "result": result.get("result", "deterministic_check_passed"),
                "native_terminal": result.get(
                    "native_terminal", terminal.get("result")
                ),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
