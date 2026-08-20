"""Prove the provider-disabled native-Harness structured startup diagnostic seam."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

from orchestration_harness import native_pre_hmr_diagnostic as diagnostic
from orchestration_harness import native_startup_terminal as startup_terminal


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-unclassified-pre-hmr-structured-"
    "diagnostic-seam-recovery"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "provider-free-structured-diagnostic-seam-evidence.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
REPORT_PATH = OPERATION_ROOT / "provider-free-structured-diagnostic-seam-report.md"
ATTEMPT_TERMINAL_PATH = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "raisa-authored-synthetic-check-in-native-harness-bounded-worker-"
    "monitored-development-rehearsal"
    / "attempt-003"
    / "pre-hmr-startup-terminal.json"
)
CONTROLLER_PATH = (
    REPO_ROOT
    / "scripts"
    / "raisa_authored_synthetic_check_in_native_harness_bounded_worker_"
    "monitored_development_rehearsal.py"
)
CONTRACT_SCHEMA_VERSION = (
    "ariadne.native_harness_pre_hmr_structured_diagnostic_recovery_contract.v1"
)
EVIDENCE_SCHEMA_VERSION = (
    "ariadne.native_harness_pre_hmr_structured_diagnostic_recovery_evidence.v1"
)


class RecoveryError(RuntimeError):
    """The source-static recovery failed closed."""


def canonical_pretty(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def contract_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "operation_id",
            "planning_source",
            "attempt_003",
            "installed_source",
            "diagnostic",
            "proof_boundary",
        ],
        "properties": {
            "schema_version": {"const": CONTRACT_SCHEMA_VERSION},
            "operation_id": {"const": OPERATION_ID},
            "planning_source": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
            "attempt_003": {"type": "object"},
            "installed_source": {"type": "object"},
            "diagnostic": {"type": "object"},
            "proof_boundary": {"type": "object"},
        },
    }


def evidence_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "operation_id",
            "planning_source",
            "result",
            "immutable_attempt_003",
            "installed_source",
            "structured_seam",
            "hostile_fixtures",
            "proof_boundary",
            "conclusion",
        ],
        "properties": {
            "schema_version": {"const": EVIDENCE_SCHEMA_VERSION},
            "operation_id": {"const": OPERATION_ID},
            "planning_source": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
            "result": {"const": "pass"},
            "immutable_attempt_003": {"type": "object"},
            "installed_source": {"type": "object"},
            "structured_seam": {"type": "object"},
            "hostile_fixtures": {"type": "array", "minItems": 8},
            "proof_boundary": {"type": "object"},
            "conclusion": {"type": "string"},
        },
    }


def load_contract() -> dict[str, Any]:
    value = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(contract_schema()).validate(value)
    if value["proof_boundary"] != {
        "python_process_count": 1,
        "node_process_count": 0,
        "native_harness_process_count": 0,
        "broker_process_count": 0,
        "worker_process_count": 0,
        "model_request_count": 0,
        "provider_request_count": 0,
        "raw_attempt_stream_read_count": 0,
    }:
        raise RecoveryError("proof_boundary_mismatch")
    vocabulary = value["diagnostic"]
    expected = {
        "schema_version": diagnostic.SCHEMA_VERSION,
        "phase": diagnostic.PHASE,
        "maximum_cause_nodes": diagnostic.MAX_CAUSE_NODES,
        "maximum_sidecar_bytes": diagnostic.MAX_SIDECAR_BYTES,
        "error_kinds": sorted(diagnostic.ERROR_KINDS),
        "code_coordinates": sorted(diagnostic.CODE_COORDINATES),
        "config_stages": sorted(diagnostic.CONFIG_STAGES),
        "message_coordinates": sorted(diagnostic.MESSAGE_COORDINATES),
        "aggregate_shapes": sorted(diagnostic.AGGREGATE_SHAPES),
    }
    if vocabulary != expected:
        raise RecoveryError("diagnostic_vocabulary_mismatch")
    return value


def inspect_immutable_attempt(contract: dict[str, Any]) -> dict[str, Any]:
    expected = contract["attempt_003"]
    if sha256_file(ATTEMPT_TERMINAL_PATH) != expected["pre_hmr_terminal_sha256"]:
        raise RecoveryError("attempt_003_terminal_drift")
    value = json.loads(ATTEMPT_TERMINAL_PATH.read_text(encoding="utf-8"))
    startup_terminal.validate_pre_hmr_terminal(value)
    if startup_terminal.terminal_bytes(value) != ATTEMPT_TERMINAL_PATH.read_bytes():
        raise RecoveryError("attempt_003_terminal_bytes_not_canonical")
    projection = {
        "candidate_source": value["candidate_source"],
        "cause": value["cause"],
        "stderr_bytes": value["stderr"]["byte_count"],
        "stderr_sha256": value["stderr"]["sha256"],
        "schema_version": value["schema_version"],
        "unchanged": True,
        "reclassified": False,
        "raw_stream_read_count": 0,
    }
    if projection != {
        "candidate_source": expected["candidate_source"],
        "cause": "unclassified_nonzero_exit",
        "stderr_bytes": expected["stderr_bytes"],
        "stderr_sha256": expected["stderr_sha256"],
        "schema_version": startup_terminal.SCHEMA_VERSION,
        "unchanged": True,
        "reclassified": False,
        "raw_stream_read_count": 0,
    }:
        raise RecoveryError("attempt_003_projection_mismatch")
    return projection


def inspect_installed_source(contract: dict[str, Any]) -> dict[str, Any]:
    specification = contract["installed_source"]
    root = Path(specification["root"]).resolve(strict=True)
    if root.as_posix() != specification["root"]:
        raise RecoveryError("installed_source_root_mismatch")
    observed: dict[str, str] = {}
    sources: dict[str, str] = {}
    for relative, expected_digest in specification["files"].items():
        path = (root / relative).resolve(strict=True)
        try:
            path.relative_to(root)
        except ValueError as error:
            raise RecoveryError("installed_source_path_escape") from error
        observed[relative] = sha256_file(path)
        if observed[relative] != expected_digest:
            raise RecoveryError("installed_source_digest_mismatch:" + relative)
        sources[relative] = path.read_text(encoding="utf-8")
    manifest = json.loads((root / "dsh" / "package.json").read_text(encoding="utf-8"))
    if manifest.get("name") != specification["package"] or manifest.get(
        "version"
    ) != specification["version"]:
        raise RecoveryError("installed_package_identity_mismatch")
    launcher = sources["dsh/lib/bin.js"]
    dispatch = launcher[launcher.index("switch (invocation.mode)") :]
    shim = sources["dsh/lib/profile-boot-BnJoK_kl.js"]
    profile = sources["dsh/lib/profile-boot-DG5t9aNs.js"]
    app_boot = sources["dsh-app-boot/lib/index.js"]
    loader = sources["cordis-plugin-loader/lib/index.js"]
    cordis = sources["cordis/lib/index.js"]
    checks = {
        "launcher_awaits_profile_import": (
            'await import("./profile-boot-BnJoK_kl.js")' in dispatch
            and "await runProfile({" in dispatch
            and dispatch.index('await import("./profile-boot-BnJoK_kl.js")')
            < dispatch.index("await runProfile({")
        ),
        "launcher_dispatch_has_no_outer_catch": "catch (" not in dispatch,
        "shim_reexports_actual_profile": (
            shim.strip()
            == 'import { o as runProfile } from "./profile-boot-DG5t9aNs.js";\nexport { runProfile };'
        ),
        "fail_loud_precedes_boot_and_hmr": (
            profile.index("installFailLoud(NAME")
            < profile.index("const ctx = await boot(")
            < profile.index("await watchUserPatches(")
        ),
        "boot_stage_coordinates_present": all(
            literal in app_boot
            for literal in (
                'let stage = "host preparation failed"',
                'stage = "plugin tree failed to load"',
                "while (deepest instanceof Error && deepest.cause",
                "throw new Error(`",
                "{ cause }",
            )
        ),
        "config_file_error_structure_present": all(
            literal in app_boot
            for literal in ("var ConfigFileError = class", "stage;", "this.stage = stage")
        ),
        "activation_coordinates_present": all(
            literal in app_boot
            for literal in (
                "function assertEntriesLoaded",
                "function assertEntriesActivated",
                "plugin(s) failed to load",
                "did not activate",
            )
        ),
        "aggregate_error_structure_present": "AggregateError" in loader,
        "cordis_typed_errors_present": all(
            literal in cordis
            for literal in (
                'name = "ValidationError"',
                "var CordisError = class CordisError extends Error",
                'INACTIVE_EFFECT: "cannot create effect on inactive context"',
            )
        ),
    }
    if not all(checks.values()):
        raise RecoveryError("installed_source_shape_mismatch")
    return {
        "package": specification["package"],
        "version": specification["version"],
        "file_sha256": observed,
        "checks": checks,
    }


class HostileGetter:
    @property
    def name(self) -> str:
        raise RuntimeError("secret-shaped getter value")

    @property
    def cause(self) -> object:
        raise RuntimeError("secret-shaped cause value")


def hostile_fixture_matrix(contract: dict[str, Any]) -> list[dict[str, Any]]:
    identity = {
        "operation_id": OPERATION_ID,
        "attempt_id": "future-source-static-fixture-001",
        "candidate_source": contract["planning_source"],
    }
    secret = "sk-secret-C:/patient/private/plugin-name"
    cycle: dict[str, Any] = {"constructor_name": "Error", "message": secret}
    cycle["cause"] = cycle
    chain: dict[str, Any] = {"constructor_name": "Error"}
    for _ in range(diagnostic.MAX_CAUSE_NODES + 2):
        chain = {"constructor_name": "Error", "cause": chain}
    cases: list[tuple[str, object]] = [
        (
            "source_backed_nested_chain",
            {
                "constructor_name": "Error",
                "message": "dsh: plugin tree failed to load: dynamic secret",
                "cause": {
                    "constructor_name": "ConfigFileError",
                    "stage": "parse",
                    "message": secret,
                    "cause": {
                        "constructor_name": "TypeError",
                        "code": "ERR_MODULE_NOT_FOUND",
                    },
                },
            },
        ),
        ("unknown_secret_message", {"name": "CustomSecretError", "message": secret}),
        ("unrecognized_code", {"name": "Error", "code": secret}),
        ("aggregate_zero", {"name": "AggregateError", "errors": []}),
        ("aggregate_one", {"name": "AggregateError", "errors": [secret]}),
        ("aggregate_multiple", {"name": "AggregateError", "errors": [secret, secret]}),
        ("aggregate_unreadable", {"name": "AggregateError", "errors": secret}),
        ("cycle", cycle),
        ("over_depth", chain),
        ("hostile_getter", HostileGetter()),
        ("non_error_throw", secret),
    ]
    rows = []
    for name, fixture in cases:
        value = diagnostic.build_diagnostic_from_fixture(fixture, **identity)
        payload = diagnostic.diagnostic_bytes(value)
        if secret.encode() in payload or b"patient" in payload or b"private" in payload:
            raise RecoveryError("hostile_fixture_leaked_dynamic_value:" + name)
        rows.append(
            {
                "scenario": name,
                "cause_node_count": len(value["cause_chain"]),
                "top_error_kind": value["cause_chain"][0]["error_kind"],
                "top_message_coordinate": value["cause_chain"][0][
                    "message_coordinate"
                ],
                "cycle_detected": value["cause_chain_cycle_detected"],
                "truncated": value["cause_chain_truncated"],
                "safe": True,
            }
        )
    return rows


def prove_structured_seam(contract: dict[str, Any]) -> dict[str, Any]:
    source_root = Path(contract["installed_source"]["root"]).resolve(strict=True)
    package_root = source_root / "dsh"
    deterministic_root = Path("C:/deterministic/native-pre-hmr-diagnostic").resolve()
    wrapper_path = deterministic_root / "entrypoint-wrapper.mjs"
    diagnostic_path = deterministic_root / "diagnostic.json"
    wrapper = diagnostic.build_entrypoint_wrapper_source(
        package_root=package_root,
        wrapper_path=wrapper_path,
        diagnostic_path=diagnostic_path,
        disposable_root=deterministic_root,
        operation_id=OPERATION_ID,
        attempt_id="future-source-static-fixture-001",
        candidate_source=contract["planning_source"],
    )
    wrapper_projection = diagnostic.validate_entrypoint_wrapper_source(wrapper)
    command = diagnostic.build_launch_command(
        node_executable="node",
        wrapper_path=wrapper_path,
        profile="headless",
        task="future authored-synthetic task",
    )
    if command[1:] != [
        "--expose-internals",
        str(wrapper_path),
        "--profile",
        "headless",
        "future authored-synthetic task",
    ]:
        raise RecoveryError("future_launch_command_shape_mismatch")
    controller = CONTROLLER_PATH.read_text(encoding="utf-8")
    insertion_checks = {
        "accepted_controller_direct_entrypoint_precedes_process": controller.index(
            'str(package_root / "lib" / "bin.js")'
        )
        < controller.index("harness = subprocess.Popen("),
        "accepted_v1_terminal_precedes_root_cleanup": controller.index(
            "startup_terminal.write_pre_hmr_terminal_exclusive("
        )
        < controller.index("cleanup_passed = remove_exact_attempt_root("),
        "accepted_controller_has_zero_automatic_retry": (
            '"automatic_retry_count": 0' in controller
        ),
    }
    if not all(insertion_checks.values()):
        raise RecoveryError("accepted_controller_insertion_point_invalid")
    controller_envelope = diagnostic.future_controller_binding_envelope_source()
    controller_envelope_projection = (
        diagnostic.validate_future_controller_binding_envelope(controller_envelope)
    )
    identity = {
        "operation_id": OPERATION_ID,
        "attempt_id": "future-source-static-fixture-001",
        "candidate_source": contract["planning_source"],
    }
    structured = diagnostic.build_diagnostic_from_fixture(
        {
            "name": "Error",
            "message": "dsh: plugin tree failed to load: secret plugin",
            "cause": {"name": "TypeError", "code": "ERR_MODULE_NOT_FOUND"},
        },
        **identity,
    )
    empty = {
        "byte_count": 0,
        "sha256": hashlib.sha256(b"").hexdigest(),
        "classification_bytes": b"",
        "limit_exceeded": False,
    }
    stderr_payload = b"dynamic secret-shaped stderr is never retained"
    stderr = {
        "byte_count": len(stderr_payload),
        "sha256": hashlib.sha256(stderr_payload).hexdigest(),
        "classification_bytes": stderr_payload,
        "limit_exceeded": False,
    }
    terminal_v2 = diagnostic.build_structured_pre_hmr_terminal(
        **identity,
        native_process_started=True,
        exit_code=1,
        controller_coordinate="native_process_exited_nonzero",
        hmr_events=[],
        stdout=empty,
        stderr=stderr,
        structured_diagnostic=structured,
    )
    terminal_payload = diagnostic.structured_terminal_bytes(terminal_v2)
    if stderr_payload in terminal_payload or b"secret plugin" in terminal_payload:
        raise RecoveryError("v2_terminal_leaked_dynamic_value")
    return {
        "wrapper": wrapper_projection,
        "future_launch_argv_shape": [
            "node",
            "--expose-internals",
            "<generated-wrapper>",
            "--profile",
            "headless",
            "<task>",
        ],
        "accepted_controller_insertion_checks": insertion_checks,
        "future_controller_envelope": controller_envelope_projection,
        "v1_fallback_schema": startup_terminal.SCHEMA_VERSION,
        "v2_structured_schema": diagnostic.TERMINAL_SCHEMA_VERSION,
        "v2_cause": terminal_v2["cause"],
        "v2_terminal_sha256": sha256_bytes(terminal_payload),
        "original_rejection_rethrown": True,
        "diagnostic_write_changes_exit_semantics": False,
    }


def deterministic_evidence() -> dict[str, Any]:
    contract = load_contract()
    value = {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "operation_id": OPERATION_ID,
        "planning_source": contract["planning_source"],
        "result": "pass",
        "immutable_attempt_003": inspect_immutable_attempt(contract),
        "installed_source": inspect_installed_source(contract),
        "structured_seam": prove_structured_seam(contract),
        "hostile_fixtures": hostile_fixture_matrix(contract),
        "proof_boundary": contract["proof_boundary"],
        "conclusion": (
            "A future rejected dsh entrypoint import can be reduced before stderr "
            "serialization to a closed non-secret typed cause chain and then "
            "rethrow the identical rejection. Attempt 003 remains unclassified "
            "and no Harness/provider readiness claim is made."
        ),
    }
    jsonschema.Draft202012Validator(evidence_schema()).validate(value)
    return value


def render_report(value: dict[str, Any]) -> str:
    seam = value["structured_seam"]
    return f"""# Provider-free unclassified pre-HMR structured diagnostic seam report

- Result: `{value["result"]}`
- Installed Harness: `@deepseek-ai/dsh 0.1.0-rc.7`
- Installed source files bound: `{len(value["installed_source"]["file_sha256"])}`
- Hostile fixtures passed: `{len(value["hostile_fixtures"])}`
- Wrapper SHA-256: `{seam["wrapper"]["sha256"]}`
- Historical fallback: `{seam["v1_fallback_schema"]}`
- Structured terminal: `{seam["v2_structured_schema"]}`
- Node / Harness / broker / worker / model / provider activity: `0 / 0 / 0 / 0 / 0 / 0`
- Raw attempt-stream reads: `0`

The accepted seam catches only a future rejected import of the pinned native
Harness entrypoint. It projects a bounded typed cause chain, writes once, and
rethrows the identical value. The controller validates and embeds that safe
projection before destroying the disposable root. Absent or invalid structured
evidence falls back to the accepted v1 terminal.

Attempt 003 is unchanged and remains `unclassified_nonzero_exit`. This result
does not run DeepSeek, make the native Harness operationally ready or authorise
another occupied attempt.
"""


def build_artifacts() -> dict[str, Any]:
    for path in (CONTRACT_SCHEMA_PATH, EVIDENCE_SCHEMA_PATH, EVIDENCE_PATH, REPORT_PATH):
        if path.exists():
            raise RecoveryError("canonical_output_already_exists:" + path.name)
    value = deterministic_evidence()
    CONTRACT_SCHEMA_PATH.write_bytes(canonical_pretty(contract_schema()))
    EVIDENCE_SCHEMA_PATH.write_bytes(canonical_pretty(evidence_schema()))
    EVIDENCE_PATH.write_bytes(canonical_pretty(value))
    REPORT_PATH.write_text(render_report(value), encoding="utf-8", newline="\n")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--build", action="store_true")
    args = parser.parse_args()
    try:
        value = deterministic_evidence() if args.check else build_artifacts()
    except (
        RecoveryError,
        diagnostic.StructuredDiagnosticError,
        startup_terminal.StartupTerminalError,
        jsonschema.ValidationError,
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
    ) as error:
        print(json.dumps({"result": "fail", "error": str(error)}))
        return 1
    print(
        json.dumps(
            {
                "result": value["result"],
                "source_file_count": len(value["installed_source"]["file_sha256"]),
                "hostile_fixture_count": len(value["hostile_fixtures"]),
                "native_harness_process_count": value["proof_boundary"][
                    "native_harness_process_count"
                ],
                "provider_request_count": value["proof_boundary"][
                    "provider_request_count"
                ],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
