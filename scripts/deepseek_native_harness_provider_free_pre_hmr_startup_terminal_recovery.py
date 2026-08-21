"""Build provider-disabled evidence for bounded native-Harness startup terminals."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import inspect
import json
from pathlib import Path
import sys
from typing import Any, Callable

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from orchestration_harness import native_startup_terminal as terminal  # noqa: E402
from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal
    as controller,
)  # noqa: E402


OPERATION_ID = (
    "deepseek-native-harness-provider-free-pre-hmr-startup-failure-"
    "classification-and-terminalization-recovery"
)
CONTINUITY_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = CONTINUITY_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = CONTINUITY_ROOT / "contract.schema.json"
TERMINAL_SCHEMA_PATH = CONTINUITY_ROOT / "pre-hmr-startup-terminal.schema.json"
EVIDENCE_SCHEMA_PATH = CONTINUITY_ROOT / "evidence.schema.json"
EVIDENCE_PATH = CONTINUITY_ROOT / "provider-free-recovery-evidence.json"
REPORT_PATH = CONTINUITY_ROOT / "provider-free-recovery-report.md"
EFFICACY_PATH = CONTINUITY_ROOT / "efficacy-reading.json"
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT_PATH = REPO_ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"
TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_pre_hmr_startup_terminal.py"
)
CONTROLLER_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal.py"
)
DATE = "2026-08-20"
TIMESTAMP = "2026-08-20T23:23:58.3235077+10:00"
EMPTY_DIGEST = hashlib.sha256(b"").hexdigest()
HISTORICAL_SOURCE_COMMIT = "12d8758fee2504435ca2b4ccf6225b9d7a86a6a1"
HISTORICAL_SOURCE_SHA256 = {
    "docs/deepseek-native-harness-provider-free-pre-hmr-startup-failure-"
    "classification-and-terminalization-recovery-plan.md": (
        "9274aa7b34bddcd78111f4120bb66896afbd987b92192225deaac4bae4bb249e"
    ),
    "docs/security/deepseek-native-harness-provider-free-pre-hmr-startup-"
    "failure-classification-and-terminalization-recovery-threat-model-delta.md": (
        "c149f4b63d3381138b02723b86a324c5fbcf9fa3b8e9b7686d1ef2778ded2e65"
    ),
    "orchestration_harness/native_startup_terminal.py": (
        "0a476ee7617fbc71d9cc3efb88ca08ac1cc6f01b433aa8d83d0603493cc05468"
    ),
    "scripts/deepseek_native_harness_provider_free_pre_hmr_startup_terminal_"
    "recovery.py": (
        "693645904b2779a54bc8d2afc3eb1395793fc184a1981e72a8cad20058d84e6b"
    ),
    "scripts/raisa_authored_synthetic_check_in_native_harness_bounded_worker_"
    "monitored_development_rehearsal.py": (
        "52d8ba01e7284e84de7308b3eb48aa5473cd3eb749f94850df17a4dad85da749"
    ),
    "tests/test_deepseek_native_harness_pre_hmr_startup_terminal.py": (
        "494cb4bef251481569239a4d878d0e55aec9cf9cfc78d963693ce6b99898cac8"
    ),
    "tests/test_raisa_authored_synthetic_check_in_native_harness_bounded_"
    "worker_monitored_development_rehearsal.py": (
        "b1b784f2cba677a52211f5ed6f759b27d43e931d7e9e54db72966a872adc61e8"
    ),
}


class RecoveryEvidenceError(RuntimeError):
    """A provider-disabled recovery evidence invariant failed closed."""


def pretty(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def historical_source_sha256() -> dict[str, str]:
    """Return the accepted source projection, not mutable descendant bytes."""

    return dict(HISTORICAL_SOURCE_SHA256)


def reading(payload: bytes) -> dict[str, Any]:
    return {
        "byte_count": len(payload),
        "sha256": sha256_bytes(payload),
        "classification_bytes": payload[: terminal.MAX_CLASSIFICATION_BYTES],
        "limit_exceeded": len(payload) > terminal.MAX_CLASSIFICATION_BYTES,
    }


def build_terminal(
    *,
    stdout: bytes = b"",
    stderr: bytes = b"opaque startup failure",
    started: bool = True,
    exit_code: int | None = 1,
    coordinate: str = "native_process_exited_nonzero",
    hmr_events: tuple[str, ...] = (),
) -> dict[str, Any]:
    return terminal.build_pre_hmr_terminal(
        operation_id=OPERATION_ID,
        attempt_id="synthetic-attempt-003",
        candidate_source="1" * 40,
        native_process_started=started,
        exit_code=exit_code,
        controller_coordinate=coordinate,
        hmr_events=hmr_events,
        stdout=reading(stdout),
        stderr=reading(stderr),
    )


def contract() -> dict[str, Any]:
    return {
        "schema_version": "ariadne.native_harness_pre_hmr_recovery_contract.v1",
        "operation_id": OPERATION_ID,
        "status": "frozen",
        "provider_posture": "provider_disabled_zero_process",
        "classification_byte_limit_per_stream": terminal.MAX_CLASSIFICATION_BYTES,
        "stages": sorted(terminal.STAGES),
        "causes": sorted(terminal.CAUSES),
        "controller_coordinates": sorted(terminal.CONTROLLER_COORDINATES),
        "signature_groups": {
            cause: [signature.decode("ascii") for signature in signatures]
            for cause, signatures in sorted(terminal.SIGNATURE_GROUPS.items())
        },
        "required_order": [
            "observe_failed_pre_hmr_lifecycle",
            "stop_exact_owned_process_tree",
            "incrementally_read_local_streams",
            "derive_and_validate_sanitized_terminal",
            "exclusive_write_and_readback_terminal",
            "remove_exact_disposable_root",
            "publish_outer_terminal_with_sanitized_digest",
        ],
        "immutable_attempts": ["attempt-001", "attempt-002"],
        "closed_surfaces": [
            "native_harness_process",
            "worker_or_broker_process",
            "deepseek_gemini_or_other_provider_request",
            "raw_stream_retention",
            "product_database_or_protected_data",
            "deployment_release_pages_or_protected_refs",
        ],
    }


def contract_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "operation_id",
            "status",
            "provider_posture",
            "classification_byte_limit_per_stream",
            "stages",
            "causes",
            "controller_coordinates",
            "signature_groups",
            "required_order",
            "immutable_attempts",
            "closed_surfaces",
        ],
        "properties": {
            "schema_version": {
                "const": "ariadne.native_harness_pre_hmr_recovery_contract.v1"
            },
            "operation_id": {"const": OPERATION_ID},
            "status": {"const": "frozen"},
            "provider_posture": {"const": "provider_disabled_zero_process"},
            "classification_byte_limit_per_stream": {
                "const": terminal.MAX_CLASSIFICATION_BYTES
            },
            "stages": {"const": sorted(terminal.STAGES)},
            "causes": {"const": sorted(terminal.CAUSES)},
            "controller_coordinates": {
                "const": sorted(terminal.CONTROLLER_COORDINATES)
            },
            "signature_groups": {"type": "object"},
            "required_order": {"type": "array", "minItems": 7, "maxItems": 7},
            "immutable_attempts": {"const": ["attempt-001", "attempt-002"]},
            "closed_surfaces": {"type": "array", "minItems": 6, "maxItems": 6},
        },
    }


def terminal_schema() -> dict[str, Any]:
    properties: dict[str, Any] = {
        "schema_version": {"const": terminal.SCHEMA_VERSION},
        "operation_id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9._-]{0,159}$"},
        "attempt_id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9._-]{0,159}$"},
        "candidate_source": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
        "stage": {"enum": sorted(terminal.STAGES)},
        "cause": {"enum": sorted(terminal.CAUSES)},
        "exit_code": {"type": ["integer", "null"]},
        "controller_coordinate": {"enum": sorted(terminal.CONTROLLER_COORDINATES)},
        "hmr_event_count": {"const": 0},
        "matched_signature_groups": {
            "type": "array",
            "uniqueItems": True,
            "items": {"enum": sorted(terminal.SIGNATURE_GROUPS)},
        },
        "classification_byte_limit_per_stream": {
            "const": terminal.MAX_CLASSIFICATION_BYTES
        },
        "raw_streams_retained": {"const": False},
    }
    stream = {
        "type": "object",
        "additionalProperties": False,
        "required": ["byte_count", "sha256"],
        "properties": {
            "byte_count": {"type": "integer", "minimum": 0},
            "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
        },
    }
    properties["stdout"] = stream
    properties["stderr"] = deepcopy(stream)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://emr4.dev/schemas/native-harness-pre-hmr-startup-terminal-v1.json",
        "type": "object",
        "additionalProperties": False,
        "required": list(properties),
        "properties": properties,
    }


def evidence_schema() -> dict[str, Any]:
    required = [
        "schema_version",
        "operation_id",
        "result",
        "provider_posture",
        "scenario_count",
        "mutation_count",
        "scenarios",
        "mutations_rejected",
        "controller_ordering",
        "immutable_artifact_count",
        "immutable_artifacts_match",
        "source_sha256",
        "schema_sha256",
        "boundary",
    ]
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": required,
        "properties": {
            "schema_version": {
                "const": "ariadne.native_harness_pre_hmr_recovery_evidence.v1"
            },
            "operation_id": {"const": OPERATION_ID},
            "result": {"const": "pass"},
            "provider_posture": {"const": "provider_disabled_zero_process"},
            "scenario_count": {"type": "integer", "minimum": 12},
            "mutation_count": {"type": "integer", "minimum": 10},
            "scenarios": {"type": "array", "minItems": 12},
            "mutations_rejected": {"type": "array", "minItems": 10},
            "controller_ordering": {"type": "object"},
            "immutable_artifact_count": {"type": "integer", "minimum": 17},
            "immutable_artifacts_match": {"const": True},
            "source_sha256": {"type": "object"},
            "schema_sha256": {"type": "object"},
            "boundary": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "subprocess_count",
                    "native_process_count",
                    "worker_process_count",
                    "provider_request_count",
                    "raw_stream_bytes_persisted",
                ],
                "properties": {
                    "subprocess_count": {"const": 0},
                    "native_process_count": {"const": 0},
                    "worker_process_count": {"const": 0},
                    "provider_request_count": {"const": 0},
                    "raw_stream_bytes_persisted": {"const": 0},
                },
            },
        },
    }


def scenario_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cause, signatures in sorted(terminal.SIGNATURE_GROUPS.items()):
        value = build_terminal(stderr=signatures[0].upper())
        rows.append(
            {
                "scenario_id": f"signature_{cause}",
                "stage": value["stage"],
                "cause": value["cause"],
                "matched_signature_groups": value["matched_signature_groups"],
            }
        )
    cases = [
        (
            "ambiguous",
            build_terminal(
                stdout=b"ERR_MODULE_NOT_FOUND",
                stderr=b"profile validation failed",
            ),
        ),
        ("unclassified", build_terminal()),
        (
            "process_creation",
            build_terminal(
                stderr=b"",
                started=False,
                exit_code=None,
                coordinate="native_process_creation_failed",
            ),
        ),
        (
            "controller_exception",
            build_terminal(
                exit_code=None,
                coordinate="unexpected_controller_failure",
            ),
        ),
        (
            "timeout",
            build_terminal(exit_code=None, coordinate="native_worker_timeout"),
        ),
        (
            "stream_limit",
            build_terminal(
                stderr=b"ERR_MODULE_NOT_FOUND"
                + b"x" * terminal.MAX_CLASSIFICATION_BYTES
            ),
        ),
    ]
    for scenario_id, value in cases:
        rows.append(
            {
                "scenario_id": scenario_id,
                "stage": value["stage"],
                "cause": value["cause"],
                "matched_signature_groups": value["matched_signature_groups"],
            }
        )
    return rows


def rejected_mutations() -> list[str]:
    builders: list[tuple[str, Callable[[], Any]]] = [
        ("hmr_event_present", lambda: build_terminal(hmr_events=("sentinel_activated",))),
        ("successful_exit", lambda: build_terminal(exit_code=0)),
        ("boolean_exit", lambda: build_terminal(exit_code=True)),
        ("unknown_coordinate", lambda: build_terminal(coordinate="unknown")),
        (
            "creation_stream_nonempty",
            lambda: build_terminal(
                started=False,
                exit_code=None,
                coordinate="native_process_creation_failed",
                stderr=b"not empty",
            ),
        ),
    ]
    rejected: list[str] = []
    for mutation_id, action in builders:
        try:
            action()
        except terminal.StartupTerminalError:
            rejected.append(mutation_id)
        else:
            raise RecoveryEvidenceError(f"mutation_admitted:{mutation_id}")

    valid = build_terminal(stderr=b"ERR_MODULE_NOT_FOUND")
    mutations: list[tuple[str, str, Any]] = [
        ("wrong_schema", "schema_version", "wrong"),
        ("wrong_cause", "cause", "operating_system_process_failure"),
        ("creation_coordinate", "controller_coordinate", "native_process_creation_failed"),
        ("hmr_count", "hmr_event_count", 1),
        ("raw_retained", "raw_streams_retained", True),
        ("wrong_limit", "classification_byte_limit_per_stream", 1),
    ]
    for mutation_id, field, replacement in mutations:
        value = deepcopy(valid)
        value[field] = replacement
        try:
            terminal.validate_pre_hmr_terminal(value)
        except terminal.StartupTerminalError:
            rejected.append(mutation_id)
        else:
            raise RecoveryEvidenceError(f"mutation_admitted:{mutation_id}")
    extra = deepcopy(valid)
    extra["raw_stderr"] = "forbidden"
    try:
        terminal.validate_pre_hmr_terminal(extra)
    except terminal.StartupTerminalError:
        rejected.append("extra_raw_field")
    else:
        raise RecoveryEvidenceError("mutation_admitted:extra_raw_field")
    return rejected


def controller_ordering() -> dict[str, bool]:
    source = inspect.getsource(controller.execute_native)
    read_index = source.index(
        "stream_readings[label] = startup_terminal.read_startup_stream("
    )
    write_index = source.index("startup_terminal.write_pre_hmr_terminal_exclusive(")
    cleanup_index = source.index("remove_exact_attempt_root(root, parent)")
    outer_index = source.index('"pre_hmr_startup_terminal_sha256"')
    publish_index = source.index("write_json_exclusive(TERMINAL_PATH, terminal)")
    return {
        "stale_sidecar_prelaunch_refusal": "PRE_HMR_TERMINAL_PATH.exists()" in source,
        "stream_read_before_terminal_write": read_index < write_index,
        "terminal_write_before_root_removal": write_index < cleanup_index,
        "root_removal_before_outer_terminal": cleanup_index < outer_index,
        "outer_digest_before_outer_publish": outer_index < publish_index,
    }


def immutable_artifact_count() -> int:
    root = controller.CONTINUITY_ROOT
    baseline = json.loads(
        (root / "attempt-002" / "attempt-001-immutability-baseline.json").read_text(
            encoding="utf-8"
        )
    )
    count = 0
    for name, expected in baseline["artifacts"].items():
        payload = (root / name).read_bytes()
        if len(payload) != expected["bytes"] or sha256_bytes(payload) != expected["sha256"]:
            raise RecoveryEvidenceError(f"attempt_001_drift:{name}")
        count += 1
    expected_two = {
        "occupied-attempt-consumed.json": "d9af398db0e9416f29df6316ac349a50a9c1516fbf54ccf6b0c40357340457a1",
        "occupied-terminal.json": "6f873651c94e81faa8af93bd3d191dd67c13982bfca081479cee6e390ff6cb00",
        "occupied-report.md": "eaaaf7d99e2a36f09516a8f69a4ea8559214d83807c73ccfa97044a1723a3a7c",
        "diagnosis.md": "d3cf50a3d5e94c744931143f2a796069ed5cba487859aacde877dcb3df3a3685",
        "efficacy-reading.json": "19f5f2db1a2a6deec435154ae1cf74b8af9af12b692431971800cebe2f85c7b6",
        "postterminal-command-validation-receipt.json": "fe44bc423fd37b07b019f9dee14c666553713795557a56364cff2839339c49d9",
    }
    for name, expected in expected_two.items():
        if file_sha256(root / "attempt-002" / name) != expected:
            raise RecoveryEvidenceError(f"attempt_002_drift:{name}")
        count += 1
    return count


def efficacy_reading() -> dict[str, Any]:
    return {
        "schema_version": "ariadne.native_harness_pre_hmr_recovery_efficacy.v1",
        "operation_id": OPERATION_ID,
        "result": "promising_bounded_traceability_improvement",
        "before": {
            "safe_stage_count": 1,
            "safe_cause_count": 1,
            "coordinate": "native_harness_terminal_failure",
            "raw_stream_bytes_persisted": 0,
        },
        "after": {
            "safe_stage_count": len(terminal.STAGES),
            "safe_cause_count": len(terminal.CAUSES),
            "ambiguous_and_unclassified_fail_closed": True,
            "raw_stream_bytes_persisted": 0,
        },
        "claim_boundary": (
            "Future pre-first-HMR failures gain a bounded sanitized coordinate; "
            "Harness reliability, attempt-002 cause and DeepSeek performance remain unproved."
        ),
    }


def evidence() -> dict[str, Any]:
    schemas = {
        "contract_schema": file_sha256(CONTRACT_SCHEMA_PATH),
        "terminal_schema": file_sha256(TERMINAL_SCHEMA_PATH),
        "evidence_schema": file_sha256(EVIDENCE_SCHEMA_PATH),
    }
    sources = historical_source_sha256()
    scenarios = scenario_matrix()
    mutations = rejected_mutations()
    ordering = controller_ordering()
    if not all(ordering.values()):
        raise RecoveryEvidenceError("controller_ordering_failed")
    count = immutable_artifact_count()
    return {
        "schema_version": "ariadne.native_harness_pre_hmr_recovery_evidence.v1",
        "operation_id": OPERATION_ID,
        "result": "pass",
        "provider_posture": "provider_disabled_zero_process",
        "scenario_count": len(scenarios),
        "mutation_count": len(mutations),
        "scenarios": scenarios,
        "mutations_rejected": mutations,
        "controller_ordering": ordering,
        "immutable_artifact_count": count,
        "immutable_artifacts_match": True,
        "source_sha256": sources,
        "schema_sha256": schemas,
        "boundary": {
            "subprocess_count": 0,
            "native_process_count": 0,
            "worker_process_count": 0,
            "provider_request_count": 0,
            "raw_stream_bytes_persisted": 0,
        },
    }


def report(value: dict[str, Any], efficacy: dict[str, Any]) -> str:
    return f"""# Provider-free pre-HMR startup terminal recovery report

Date: {DATE}

Timestamp: {TIMESTAMP} (Australia/Brisbane)

Result: `{value['result']}`

- Closed stages / causes: `{len(terminal.STAGES)}` / `{len(terminal.CAUSES)}`
- Deterministic scenarios / rejected hostile mutations: `{value['scenario_count']}` / `{value['mutation_count']}`
- Immutable attempt artifacts checked: `{value['immutable_artifact_count']}`
- Native processes / worker processes / provider requests: `0` / `0` / `0`
- Raw startup bytes persisted: `0`
- Controller ordering checks: `{sum(value['controller_ordering'].values())}/{len(value['controller_ordering'])}`

The outer controller now hashes and classifies bounded local startup streams,
writes and validates one safe terminal outside the disposable root, then removes
the root and publishes only the sidecar digest in its ordinary terminal.

Efficacy: `{efficacy['result']}`. This improves future pre-first-HMR attribution
without retaining raw output. It does not identify attempt 002's deleted stderr,
prove Harness reliability, measure DeepSeek, or authorize another occupied run.
"""


def validate_artifacts() -> dict[str, Any]:
    contract_value = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    evidence_value = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    terminal_value = build_terminal(stderr=b"ERR_MODULE_NOT_FOUND")
    jsonschema.Draft202012Validator(
        json.loads(CONTRACT_SCHEMA_PATH.read_text(encoding="utf-8"))
    ).validate(contract_value)
    jsonschema.Draft202012Validator(
        json.loads(TERMINAL_SCHEMA_PATH.read_text(encoding="utf-8"))
    ).validate(terminal_value)
    jsonschema.Draft202012Validator(
        json.loads(EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8"))
    ).validate(evidence_value)
    current = evidence()
    if current != evidence_value:
        raise RecoveryEvidenceError("evidence_not_current")
    return current


def build_artifacts() -> dict[str, Any]:
    CONTINUITY_ROOT.mkdir(parents=True, exist_ok=True)
    CONTRACT_SCHEMA_PATH.write_bytes(pretty(contract_schema()))
    TERMINAL_SCHEMA_PATH.write_bytes(pretty(terminal_schema()))
    EVIDENCE_SCHEMA_PATH.write_bytes(pretty(evidence_schema()))
    contract_value = contract()
    jsonschema.Draft202012Validator(contract_schema()).validate(contract_value)
    CONTRACT_PATH.write_bytes(pretty(contract_value))
    efficacy = efficacy_reading()
    EFFICACY_PATH.write_bytes(pretty(efficacy))
    value = evidence()
    jsonschema.Draft202012Validator(evidence_schema()).validate(value)
    EVIDENCE_PATH.write_bytes(pretty(value))
    REPORT_PATH.write_text(report(value, efficacy), encoding="utf-8", newline="\n")
    return validate_artifacts()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--build", action="store_true")
    action.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        value = build_artifacts() if args.build else validate_artifacts()
        print(
            json.dumps(
                {
                    "result": value["result"],
                    "scenario_count": value["scenario_count"],
                    "mutation_count": value["mutation_count"],
                    "subprocess_count": value["boundary"]["subprocess_count"],
                    "provider_request_count": value["boundary"]["provider_request_count"],
                },
                sort_keys=True,
            )
        )
        return 0
    except (RecoveryEvidenceError, terminal.StartupTerminalError, OSError) as error:
        print(json.dumps({"result": "failed_closed", "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
