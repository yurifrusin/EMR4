"""Bridge the accepted preset-composition sanitizer to one finite sidecar."""

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
    deepseek_native_harness_provider_free_post_hmr_agent_factory_closed_subcoordinate_diagnostic_rehearsal as base,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-preset-composition-safe-terminal-"
    "bridge-rehearsal"
)
EXECUTION_ATTEMPT_ID = "preset-composition-safe-terminal-attempt-001"
PRIVATE_SESSION_ID = "session-emr4-preset-composition-terminal-001"
PUBLICATION_STOP = base.PUBLICATION_STOP
PRESET_ID = base.PRESET_ID
EXPECTED_TOOLS = list(base.EXPECTED_TOOLS)
TARGET_PATH = base.TARGET_PATH
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT_PATH = REPO_ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
SIDECAR_SCHEMA_PATH = OPERATION_ROOT / "safe-terminal-sidecar.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "safe-terminal-bridge-evidence.json"
REPORT_PATH = OPERATION_ROOT / "safe-terminal-bridge-report.md"
EFFICACY_PATH = OPERATION_ROOT / "efficacy-reading.json"
ATTEMPT_CONSUMED_PATH = OPERATION_ROOT / "native-attempt-consumed.json"
FOCUSED_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_provider_free_preset_composition_safe_terminal_bridge_rehearsal.py"
)
PREDECESSOR_SCRIPT_PATH = Path(base.__file__).resolve()
PREDECESSOR_CONTRACT_PATH = base.CONTRACT_PATH
PREDECESSOR_EVIDENCE_PATH = base.EVIDENCE_PATH
PREDECESSOR_INTERPRETATION_PATH = base.OPERATION_ROOT / "diagnostic-interpretation.json"
PREDECESSOR_CLOSEOUT_PATH = (
    REPO_ROOT
    / "docs"
    / "deepseek-native-harness-provider-free-post-hmr-agent-factory-closed-subcoordinate-diagnostic-rehearsal-closeout.md"
)
PREDECESSOR_ACCEPTANCE_PATH = (
    REPO_ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "deepseek-native-harness-post-hmr-agent-factory-diagnostic-sol-acceptance.md"
)
GUARD_SCRIPT_PATH = (
    REPO_ROOT
    / "scripts"
    / "deepseek_native_harness_provider_free_effective_tool_composition_guard.py"
)
FULL_OID = re.compile(r"^[0-9a-f]{40}$")
SAFE_DETAIL = re.compile(r"^[a-z_]+(?:,[a-z_]+)*$")
MAX_SIDECAR_BYTES = 8_192
SIDECAR_SCHEMA = "ariadne.native_harness_preset_composition_safe_terminal_sidecar.v1"
EVIDENCE_SCHEMA = "ariadne.native_harness_preset_composition_safe_terminal_evidence.v1"
STAGES = list(base.STAGES)
ERROR_CLASSES = [*base.ERROR_CLASSES[:-1], "safe_terminal_invalid", "unclassified_error"]
TERMINALS = [
    "closed_subcoordinate_failure",
    "preset_composition_failure_attributed",
    "prepublication_veto_diagnosed",
    "runner_link_or_apply_absence",
]
SAFE_GUARD_COORDINATES = [
    "EFFECTIVE_TOOL_COMPOSITION_INPUT_INVALID",
    "EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED",
    "EFFECTIVE_TOOL_COMPOSITION_SCOPE_MISSING",
    "EFFECTIVE_TOOL_COMPOSITION_SCOPE_LOCAL_TOOL_PRESENT",
    "EFFECTIVE_TOOL_COMPOSITION_EXPECTED_TOOL_NOT_INHERITED",
    "EFFECTIVE_TOOL_COMPOSITION_RESTRICTION_FAILED",
    "EFFECTIVE_TOOL_COMPOSITION_SCHEMA_VIEW_INVALID",
    "EFFECTIVE_TOOL_COMPOSITION_EFFECTIVE_VIEW_MISMATCH",
    "EFFECTIVE_TOOL_COMPOSITION_UNCLASSIFIED",
]

_ACCEPTED_RUNNER_SOURCE = base.runner_source
_ACCEPTED_VALIDATE_RUNNER_SOURCE = base.validate_runner_source
_ACCEPTED_PRIVATE_SESSION_ID = base.PRIVATE_SESSION_ID


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


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
        raise base.ClosedSubcoordinateError("git_resolution_failed")
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


def _replace_once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise base.ClosedSubcoordinateError("accepted_runner_rewrite_anchor_invalid")
    return source.replace(old, new)


def runner_source() -> bytes:
    source = _ACCEPTED_RUNNER_SOURCE().decode("utf-8")
    source = _replace_once(
        source,
        'export const name = "provider-free-agent-factory-closed-subcoordinate-runner";',
        'export const name = "provider-free-preset-composition-safe-terminal-runner";',
    )
    source = _replace_once(
        source,
        'const PRIVATE_ID = "session-emr4-agent-factory-diagnostic-001";',
        f'const PRIVATE_ID = "{PRIVATE_SESSION_ID}";',
    )
    source = _replace_once(
        source,
        'const PUBLICATION_STOP = "EMR4_AGENT_PUBLICATION_STOP";',
        'const PUBLICATION_STOP = "EMR4_AGENT_PUBLICATION_STOP";\n'
        'const ATTRIBUTED_STOP = "EMR4_PRESET_COMPOSITION_ATTRIBUTED_STOP";\n'
        "const SAFE_GUARD_COORDINATES = new Set([\n  "
        + ",\n  ".join(json.dumps(value) for value in SAFE_GUARD_COORDINATES)
        + "\n]);\nconst SAFE_GUARD_DETAIL = /^[a-z_]+(?:,[a-z_]+)*$/;",
    )
    source = _replace_once(
        source,
        '  CWD_NOT_ABSOLUTE: "cwd_not_absolute",',
        '  CWD_NOT_ABSOLUTE: "cwd_not_absolute",\n'
        '  SAFE_TERMINAL_INVALID: "safe_terminal_invalid",',
    )
    source = _replace_once(
        source,
        "    vetoRejected: false,",
        "    vetoRejected: false,\n"
        "    safeGuardCoordinate: null,\n"
        "    safeGuardDetail: null,",
    )
    source = _replace_once(
        source,
        "      raw_error_retained: false,",
        "      raw_error_retained: false,\n"
        "      safe_guard_coordinate: observed.safeGuardCoordinate,\n"
        "      safe_guard_detail: observed.safeGuardDetail,",
    )
    source = _replace_once(
        source,
        '      schema_version: "ariadne.native_harness_agent_factory_diagnostic_sidecar.v1",',
        f'      schema_version: "{SIDECAR_SCHEMA}",',
    )
    source = _replace_once(
        source,
        "    const assertEffectiveToolComposition = guardModule.assertEffectiveToolComposition;",
        "    const assertEffectiveToolComposition = guardModule.assertEffectiveToolComposition;\n"
        "    const sanitizeEffectiveToolTerminal = guardModule.sanitizeEffectiveToolTerminal;",
    )
    source = _replace_once(
        source,
        '    if (typeof installModelSelection !== "function" || typeof SessionId !== "function" || typeof assertEffectiveToolComposition !== "function") throw new Error("REQUIRED_SERVICE_MISSING");',
        '    if (typeof installModelSelection !== "function" || typeof SessionId !== "function" || typeof assertEffectiveToolComposition !== "function" || typeof sanitizeEffectiveToolTerminal !== "function") throw new Error("REQUIRED_SERVICE_MISSING");',
    )
    source = _replace_once(
        source,
        "          const composition = await assertEffectiveToolComposition(agentCtx, PRESET_ID, TOOLS);",
        "          let composition;\n"
        "          try {\n"
        "            composition = await assertEffectiveToolComposition(agentCtx, PRESET_ID, TOOLS);\n"
        "          } catch (error) {\n"
        "            const safe = sanitizeEffectiveToolTerminal(error);\n"
        "            if (!safe || safe.stage !== \"pre_provider_tool_composition\" || !SAFE_GUARD_COORDINATES.has(safe.code) || !(safe.detail === null || (typeof safe.detail === \"string\" && SAFE_GUARD_DETAIL.test(safe.detail)))) throw new Error(\"SAFE_TERMINAL_INVALID\");\n"
        "            const names = safe.detail === null ? [] : safe.detail.split(\",\");\n"
        "            if (new Set(names).size !== names.length || JSON.stringify(names) !== JSON.stringify([...names].sort())) throw new Error(\"SAFE_TERMINAL_INVALID\");\n"
        "            observed.safeGuardCoordinate = safe.code;\n"
        "            observed.safeGuardDetail = safe.detail;\n"
        "            emit(\"preset_composition_failure_attributed\", null);\n"
        "            throw new Error(ATTRIBUTED_STOP);\n"
        "          }",
    )
    source = _replace_once(
        source,
        "    } catch (error) {\n      if (!(error instanceof Error) || error.message !== PUBLICATION_STOP || !observed.vetoExact) throw error;",
        "    } catch (error) {\n"
        "      if (error instanceof Error && error.message === ATTRIBUTED_STOP && terminalWritten) { ctx.get(\"appExit\")(3); return; }\n"
        "      if (!(error instanceof Error) || error.message !== PUBLICATION_STOP || !observed.vetoExact) throw error;",
    )
    source = _replace_once(
        source,
        "  run().catch((error) => {\n    try { emit(\"closed_subcoordinate_failure\", classify(error, lastStage)); }",
        "  run().catch((error) => {\n"
        "    if (terminalWritten) { ctx.get(\"appExit\")(2); return; }\n"
        "    try { emit(\"closed_subcoordinate_failure\", classify(error, lastStage)); }",
    )
    return source.encode("utf-8")


def validate_runner_source(payload: bytes) -> dict[str, Any]:
    projection = _ACCEPTED_VALIDATE_RUNNER_SOURCE(payload)
    source = payload.decode("utf-8")
    checks = {
        "sanitizer_imported_once": source.count(
            "guardModule.sanitizeEffectiveToolTerminal"
        )
        == 1,
        "sanitizer_called_once": source.count("sanitizeEffectiveToolTerminal(error)")
        == 1,
        "safe_coordinate_set_exact": all(
            source.count(json.dumps(code)) == 1 for code in SAFE_GUARD_COORDINATES
        ),
        "attributed_terminal_once": source.count(
            'emit("preset_composition_failure_attributed", null)'
        )
        == 1,
        "safe_fields_only": source.count("safe_guard_coordinate") == 1
        and source.count("safe_guard_detail") == 1,
        "no_raw_guard_projection": all(
            token not in source
            for token in (
                "error.stack",
                "error.cause",
                "String(error)",
                "error.path",
                "error.prompt",
                "error.response",
            )
        ),
        "distinct_identity": PRIVATE_SESSION_ID in source
        and _ACCEPTED_PRIVATE_SESSION_ID not in source,
    }
    if not all(checks.values()):
        failed = sorted(name for name, passed in checks.items() if not passed)
        raise base.ClosedSubcoordinateError(
            "safe_terminal_runner_shape_invalid:" + ",".join(failed)
        )
    return {**projection, "safe_terminal_checks": checks}


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = json.loads(path.read_bytes())
    schema = json.loads(CONTRACT_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(contract)
    plan_relative = PLAN_PATH.relative_to(REPO_ROOT).as_posix()
    if (
        contract["schema_version"]
        != "ariadne.native_harness_preset_composition_safe_terminal_contract.v1"
        or contract["operation_id"] != OPERATION_ID
        or contract["planning_source"]
        != _git("rev-parse", "--verify", f"{contract['planning_source']}^{{commit}}")
        or contract["planning_source"]
        != _git("log", "-1", "--format=%H", "--", plan_relative)
    ):
        raise base.ClosedSubcoordinateError(
            "contract_identity_or_planning_source_invalid"
        )
    if contract["execution_attempt"] != {
        "attempt_id": EXECUTION_ATTEMPT_ID,
        "native_process_count": 1,
        "automatic_retry": False,
        "manual_retry": False,
        "resume": False,
    }:
        raise base.ClosedSubcoordinateError("one_process_latch_invalid")
    if contract["closed_vocabulary"] != {
        "stages": STAGES,
        "error_classes": ERROR_CLASSES,
        "terminals": TERMINALS,
        "safe_guard_coordinates": SAFE_GUARD_COORDINATES,
    }:
        raise base.ClosedSubcoordinateError("closed_vocabulary_invalid")
    if contract["safe_terminal_bridge"] != {
        "sanitizer": "sanitizeEffectiveToolTerminal",
        "stage": "pre_provider_tool_composition",
        "detail": "null_or_sorted_comma_separated_safe_tool_names",
    }:
        raise base.ClosedSubcoordinateError("safe_terminal_bridge_invalid")
    if contract["factory_boundary"] != {
        "private_session_id": PRIVATE_SESSION_ID,
        "publication_stop": PUBLICATION_STOP,
        "agents_create_invocations_max": 1,
        "published_agents": 0,
        "published_sessions": 0,
    }:
        raise base.ClosedSubcoordinateError("factory_boundary_invalid")
    if contract["selection"] != {
        "provider": "deepseek-official",
        "model": "deepseek-v4-flash",
        "reasoning_effort": "high",
        "max_tokens": 4096,
    }:
        raise base.ClosedSubcoordinateError("selection_invalid")
    return contract


def validate_predecessors(contract: dict[str, Any]) -> dict[str, Any]:
    if not _ancestor(contract["planning_source"]):
        raise base.ClosedSubcoordinateError("planning_source_not_ancestor")
    base_contract = base.predecessor.load_contract()
    predecessor_paths = {
        "frozen_plan_sha256": PLAN_PATH,
        "threat_model_sha256": THREAT_PATH,
        "accepted_diagnostic_script_sha256": PREDECESSOR_SCRIPT_PATH,
        "accepted_diagnostic_contract_sha256": PREDECESSOR_CONTRACT_PATH,
        "accepted_diagnostic_evidence_sha256": PREDECESSOR_EVIDENCE_PATH,
        "accepted_interpretation_sha256": PREDECESSOR_INTERPRETATION_PATH,
        "accepted_closeout_sha256": PREDECESSOR_CLOSEOUT_PATH,
        "accepted_acceptance_sha256": PREDECESSOR_ACCEPTANCE_PATH,
        "accepted_guard_script_sha256": GUARD_SCRIPT_PATH,
    }
    observed = {key: sha256_file(path) for key, path in predecessor_paths.items()}
    if observed != contract["predecessor_bytes"]:
        raise base.ClosedSubcoordinateError("predecessor_digest_mismatch")
    if sha256_file(base.predecessor.CONTRACT_PATH) != contract["base_contract_sha256"]:
        raise base.ClosedSubcoordinateError("base_contract_binding_mismatch")
    implementation = {
        "execution_controller_sha256": sha256_file(Path(__file__).resolve()),
        "focused_test_sha256": sha256_file(FOCUSED_TEST_PATH),
        "contract_schema_sha256": sha256_file(CONTRACT_SCHEMA_PATH),
        "sidecar_schema_sha256": sha256_file(SIDECAR_SCHEMA_PATH),
        "evidence_schema_sha256": sha256_file(EVIDENCE_SCHEMA_PATH),
    }
    if implementation != contract["implementation_bytes"]:
        raise base.ClosedSubcoordinateError("implementation_digest_mismatch")
    return {
        "base_contract": base_contract,
        "predecessor_sha256": observed,
        "implementation_sha256": implementation,
    }


def read_sidecar(
    path: Path,
    *,
    disposable_root: Path,
    contract: dict[str, Any],
    candidate_source: str,
) -> dict[str, Any]:
    if not path.is_absolute() or not disposable_root.is_absolute():
        raise base.ClosedSubcoordinateError("sidecar_paths_must_be_absolute")
    if disposable_root.is_symlink() or not disposable_root.is_dir() or path.is_symlink():
        raise base.ClosedSubcoordinateError("sidecar_path_invalid")
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(disposable_root.resolve())
    except (OSError, ValueError) as error:
        raise base.ClosedSubcoordinateError(
            "sidecar_path_outside_disposable_root"
        ) from error
    if not resolved.is_file() or resolved.stat().st_size > MAX_SIDECAR_BYTES:
        raise base.ClosedSubcoordinateError("sidecar_file_invalid")
    try:
        value = json.loads(resolved.read_bytes())
    except (UnicodeError, json.JSONDecodeError) as error:
        raise base.ClosedSubcoordinateError("sidecar_json_invalid") from error
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
        raise base.ClosedSubcoordinateError("sidecar_fixed_binding_mismatch")
    stage_index = STAGES.index(value["last_admitted_stage"])
    expected_invocations = 1 if stage_index >= STAGES.index("agent_factory_invoked") else 0
    expected_private = 1 if stage_index >= STAGES.index("private_identity_admitted") else 0
    if value["agent_create_invocation_count"] != expected_invocations:
        raise base.ClosedSubcoordinateError("sidecar_factory_count_stage_mismatch")
    if (
        value["private_agent_preparation_count"] != expected_private
        or value["private_session_preparation_count"] != expected_private
    ):
        raise base.ClosedSubcoordinateError("sidecar_private_count_stage_mismatch")
    result = value["result"]
    if result == "prepublication_veto_diagnosed":
        valid = (
            value["last_admitted_stage"] == "postrollback_registries_empty"
            and value["error_class"] is None
            and value["safe_guard_coordinate"] is None
            and value["safe_guard_detail"] is None
            and value["preset_mounted"]
            and value["model_selection_installed"]
            and value["veto_exact"]
            and value["veto_rejected"]
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
        )
    else:
        valid = False
    if not valid:
        raise base.ClosedSubcoordinateError("sidecar_terminal_semantics_invalid")
    return value


def build_controller_terminal(sidecar: dict[str, Any] | None) -> dict[str, Any]:
    if sidecar is None:
        return {
            "result": "runner_link_or_apply_absence",
            "last_admitted_stage": None,
            "error_class": None,
            "safe_guard_coordinate": None,
            "safe_guard_detail": None,
            "factory_boundary": None,
            "raw_runtime_detail_retained": False,
        }
    return {
        "result": sidecar["result"],
        "last_admitted_stage": sidecar["last_admitted_stage"],
        "error_class": sidecar["error_class"],
        "safe_guard_coordinate": sidecar["safe_guard_coordinate"],
        "safe_guard_detail": sidecar["safe_guard_detail"],
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
    return None


def _report_timestamp(evidence: dict[str, Any]) -> str:
    started = datetime.fromisoformat(
        evidence["launch"]["started_at_utc"].replace("Z", "+00:00")
    )
    return started.astimezone(ZoneInfo("Australia/Brisbane")).isoformat()


def _render_report(evidence: dict[str, Any]) -> str:
    terminal = evidence["controller_terminal"] or {}
    factory = terminal.get("factory_boundary")
    factory_text = "unknown" if factory is None else json.dumps(factory, sort_keys=True)
    return f"""# Native preset-composition safe-terminal bridge report

Date: 2026-08-22

Timestamp: {_report_timestamp(evidence)} (Australia/Brisbane)

Result: **{evidence['result']}**

- Execution attempt: `{evidence['execution_attempt_id']}`
- Full execution source: `{evidence['candidate_source']}`
- Diagnostic terminal: `{terminal.get('result')}`
- Last admitted stage: `{terminal.get('last_admitted_stage')}`
- Error class: `{terminal.get('error_class')}`
- Safe guard coordinate: `{terminal.get('safe_guard_coordinate')}`
- Safe guard detail: `{terminal.get('safe_guard_detail')}`
- Factory boundary: `{factory_text}`
- Native process / retry: `{evidence['launch']['native_process_count']} / 0`
- Broker / model / provider / network: `0 / 0 / 0 / {evidence['provider_boundary']['network_attempt_count']}`
- Target created or used: `false / false`
- Process and disposable root absent: `{str(evidence['cleanup']['process_absent']).lower()} / {str(evidence['cleanup']['disposable_root_absent']).lower()}`

This is finite provider-free diagnostic evidence. A safe coordinate attributes
only preset composition; it is not a worker-readiness or occupied-model result.
No raw error, turn, request, target, product/data action or production authority
is retained or claimed.
"""


def _efficacy(evidence: dict[str, Any]) -> dict[str, Any]:
    terminal = evidence["controller_terminal"] or {}
    return {
        "schema_version": "ariadne.native_harness_preset_composition_safe_terminal_efficacy.v1",
        "operation_id": OPERATION_ID,
        "execution_attempt_id": EXECUTION_ATTEMPT_ID,
        "candidate_source": evidence["candidate_source"],
        "result": evidence["result"],
        "diagnostic_terminal": terminal.get("result"),
        "last_admitted_stage": terminal.get("last_admitted_stage"),
        "error_class": terminal.get("error_class"),
        "safe_guard_coordinate": terminal.get("safe_guard_coordinate"),
        "safe_guard_detail": terminal.get("safe_guard_detail"),
        "factory_boundary_observed": terminal.get("factory_boundary") is not None,
        "control_gain": (
            "finite_guard_coordinate_or_prepublication_veto_or_exact_link_apply_absence"
            if evidence["result"] == "pass"
            else "none"
        ),
        "worker_launch_authorized": False,
        "occupied_model_launch_authorized": False,
    }


@contextmanager
def _bound_base() -> Iterator[None]:
    bindings: dict[str, Any] = {
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
    }
    original = {name: getattr(base, name) for name in bindings}
    try:
        for name, value in bindings.items():
            setattr(base, name, value)
        yield
    finally:
        for name, value in original.items():
            setattr(base, name, value)


def deterministic_check(cache_root: Path | None = None) -> dict[str, Any]:
    with _bound_base():
        return base.deterministic_check(cache_root)


def execute_rehearsal(cache_root: Path | None = None) -> dict[str, Any]:
    with _bound_base():
        return base.execute_rehearsal(cache_root)


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
        base.ClosedSubcoordinateError,
        jsonschema.ValidationError,
        jsonschema.SchemaError,
        OSError,
        ValueError,
        json.JSONDecodeError,
        subprocess.SubprocessError,
    ) as error:
        print(json.dumps({"status": "failed", "error": type(error).__name__}))
        return 1
    print(
        json.dumps(
            {
                "status": "passed",
                "operation_id": OPERATION_ID,
                "native_process_count": result.get("native_process_count", 1),
                "result": result.get("result", "deterministic_check_passed"),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
