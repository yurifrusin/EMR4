"""Generate provider-free evidence for future-runner sidecar integration."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any

import jsonschema

from orchestration_harness import native_post_hmr_pre_request_controller as controller
from orchestration_harness import native_post_hmr_pre_request_diagnostic as diagnostic
from scripts import (
    deepseek_native_harness_provider_free_custom_runner_pre_request_failure_coordinate_diagnosis
    as accepted_diagnosis,
)
from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal
    as accepted_runner,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-post-hmr-pre-request-diagnostic-"
    "sidecar-integration-rehearsal"
)
ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = ROOT / "contract.schema.json"
BROKER_SCHEMA_PATH = ROOT / "broker-request-reading.schema.json"
EVIDENCE_PATH = ROOT / "integration-evidence.json"
EVIDENCE_SCHEMA_PATH = ROOT / "integration-evidence.schema.json"
REPORT_PATH = ROOT / "integration-report.md"
EFFICACY_PATH = ROOT / "efficacy-reading.json"
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
CONTROLLER_PATH = (
    REPO_ROOT / "orchestration_harness" / "native_post_hmr_pre_request_controller.py"
)
DIAGNOSTIC_PATH = (
    REPO_ROOT / "orchestration_harness" / "native_post_hmr_pre_request_diagnostic.py"
)


class IntegrationRehearsalError(ValueError):
    """The provider-free integration evidence did not satisfy its contract."""


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


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
        raise IntegrationRehearsalError("git_resolution_failed")
    return completed.stdout.strip()


def load_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_bytes())
    schema = json.loads(CONTRACT_SCHEMA_PATH.read_bytes())
    broker_schema = json.loads(BROKER_SCHEMA_PATH.read_bytes())
    evidence_schema = json.loads(EVIDENCE_SCHEMA_PATH.read_bytes())
    for value in (schema, broker_schema, evidence_schema):
        jsonschema.Draft202012Validator.check_schema(value)
    jsonschema.Draft202012Validator(schema).validate(contract)
    source = contract["planning_source"]
    relative_plan = PLAN_PATH.relative_to(REPO_ROOT).as_posix()
    if (
        contract["operation_id"] != OPERATION_ID
        or _git("rev-parse", "--verify", f"{source}^{{commit}}") != source
        or _git("log", "-1", "--format=%H", "--", relative_plan) != source
    ):
        raise IntegrationRehearsalError("planning_source_invalid")
    return contract


def _write_fixture(path: Path, value: object, serializer: Any) -> None:
    path.write_bytes(serializer(value))


def _diagnostic(
    *,
    contract: dict[str, Any],
    stage: str = "loader_readiness_wait",
    cause: str = "operation_rejected",
    error_name: str = "Error",
) -> dict[str, Any]:
    identity = contract["fixture_identity"]
    return diagnostic.build_diagnostic_from_fixture(
        {"name": error_name, "constructor_name": error_name},
        operation_id=OPERATION_ID,
        attempt_id=identity["attempt_id"],
        candidate_source=identity["candidate_source"],
        stage=stage,
        cause_coordinate=cause,
    )


def _selection(
    *, contract: dict[str, Any], root: Path, sidecar: Path, broker: Path
) -> dict[str, Any]:
    identity = contract["fixture_identity"]
    return controller.select_post_hmr_failure(
        diagnostic_path=sidecar,
        broker_reading_path=broker,
        disposable_root=root,
        operation_id=OPERATION_ID,
        attempt_id=identity["attempt_id"],
        candidate_source=identity["candidate_source"],
    )


def deterministic_evidence() -> dict[str, Any]:
    contract = load_contract()
    bindings = contract["source_bindings"]
    accepted_payload = accepted_runner.runner_source(accepted_diagnosis.TARGET_PATH)
    future_payload = controller.derive_future_runner_source(
        accepted_payload,
        expected_accepted_sha256=bindings["accepted_runner_sha256"],
    )
    future = controller.validate_future_runner_source(
        future_payload,
        accepted_payload=accepted_payload,
        expected_accepted_sha256=bindings["accepted_runner_sha256"],
    )
    identity = contract["fixture_identity"]
    helper_payload = diagnostic.build_helper_source(
        operation_id=OPERATION_ID,
        attempt_id=identity["attempt_id"],
        candidate_source=identity["candidate_source"],
    )
    helper = diagnostic.validate_helper_source(helper_payload)
    observed_bindings = {
        "accepted_runner_sha256": _sha256(accepted_payload),
        "accepted_diagnostic_module_sha256": _sha256(DIAGNOSTIC_PATH.read_bytes()),
        "controller_module_sha256": _sha256(CONTROLLER_PATH.read_bytes()),
    }
    if (
        observed_bindings
        != {
            key: bindings[key]
            for key in (
                "accepted_runner_sha256",
                "accepted_diagnostic_module_sha256",
                "controller_module_sha256",
            )
        }
        or future["sha256"] != bindings["future_runner_sha256"]
        or helper["sha256"] != bindings["generated_helper_sha256"]
    ):
        raise IntegrationRehearsalError("source_binding_mismatch")

    cleaned = False
    with tempfile.TemporaryDirectory(prefix="ariadne-post-hmr-sidecar-") as temporary:
        temp_root = Path(temporary).resolve()
        root = temp_root / "disposable"
        root.mkdir()
        sidecar = root / "post-hmr-diagnostic.json"
        broker = root / "broker-reading.json"
        zero = controller.build_broker_reading(
            operation_id=OPERATION_ID,
            attempt_id=identity["attempt_id"],
            candidate_source=identity["candidate_source"],
        )
        _write_fixture(broker, zero, controller.broker_reading_bytes)

        stage_results = []
        for stage in diagnostic.PRE_REQUEST_STAGES:
            _write_fixture(sidecar, _diagnostic(contract=contract, stage=stage), diagnostic.diagnostic_bytes)
            selected = _selection(contract=contract, root=root, sidecar=sidecar, broker=broker)
            stage_results.append(selected["coordinate"])

        error_names = (
            "AggregateError",
            "Error",
            "InvalidPresetIdError",
            "PresetMountError",
            "TypeError",
            "UnknownErrorName",
            "UnknownPresetError",
        )
        error_results = []
        for error_name in error_names:
            _write_fixture(
                sidecar,
                _diagnostic(contract=contract, error_name=error_name),
                diagnostic.diagnostic_bytes,
            )
            error_results.append(
                _selection(contract=contract, root=root, sidecar=sidecar, broker=broker)[
                    "coordinate"
                ]
            )

        special = (
            ("required_service_lookup", "required_service_missing"),
            ("preset_root_roster_admission", "preset_root_roster_mismatch"),
        )
        special_results = []
        for stage, cause in special:
            _write_fixture(
                sidecar,
                _diagnostic(contract=contract, stage=stage, cause=cause),
                diagnostic.diagnostic_bytes,
            )
            special_results.append(
                _selection(contract=contract, root=root, sidecar=sidecar, broker=broker)[
                    "coordinate"
                ]
            )

        valid_zero = _selection(
            contract=contract, root=root, sidecar=sidecar, broker=broker
        )
        nonzero_results = []
        for counter in controller.BROKER_COUNTERS:
            reading = controller.build_broker_reading(
                operation_id=OPERATION_ID,
                attempt_id=identity["attempt_id"],
                candidate_source=identity["candidate_source"],
                counters={counter: 1},
            )
            _write_fixture(broker, reading, controller.broker_reading_bytes)
            nonzero_results.append(
                _selection(contract=contract, root=root, sidecar=sidecar, broker=broker)[
                    "coordinate"
                ]
            )
        _write_fixture(broker, zero, controller.broker_reading_bytes)
        sidecar.write_bytes(b"not-json")
        invalid_sidecar = _selection(
            contract=contract, root=root, sidecar=sidecar, broker=broker
        )
        if not all(
            coordinate == "post_hmr_pre_request_failure"
            for coordinate in (*stage_results, *error_results, *special_results)
        ):
            raise IntegrationRehearsalError("valid_join_matrix_mismatch")
        if any(
            coordinate != "post_hmr_request_boundary_unresolved"
            for coordinate in nonzero_results
        ):
            raise IntegrationRehearsalError("nonzero_join_matrix_mismatch")
        if (
            valid_zero["coordinate"] != "post_hmr_pre_request_failure"
            or invalid_sidecar["coordinate"] != "native_harness_terminal_failure"
        ):
            raise IntegrationRehearsalError("selection_coordinate_mismatch")
    cleaned = not temp_root.exists()
    evidence = {
        "schema_version": "ariadne.native_harness_post_hmr_sidecar_integration_evidence.v1",
        "operation_id": OPERATION_ID,
        "result": "pass",
        "claim": "provider_free_future_runner_sidecar_and_broker_zero_join_representable",
        "source_bindings": observed_bindings,
        "future_runner": future,
        "diagnostic_helper": helper,
        "join_matrix": {
            "stage_count": len(stage_results),
            "error_kind_count": len(error_results),
            "special_cause_count": len(special_results),
            "nonzero_counter_count": len(nonzero_results),
            "valid_zero_coordinate": valid_zero["coordinate"],
            "invalid_sidecar_coordinate": invalid_sidecar["coordinate"],
            "nonzero_coordinate": nonzero_results[0],
            "pre_request_requires_both": True,
        },
        "cleanup": {"disposable_fixture_root_absent": cleaned},
        "proof_boundary": contract["proof_boundary"],
        "occupied_attempt_authorized": False,
        "raw_historical_stream_read": False,
    }
    jsonschema.Draft202012Validator(json.loads(EVIDENCE_SCHEMA_PATH.read_bytes())).validate(
        evidence
    )
    return evidence


def render_report(evidence: dict[str, Any]) -> str:
    return f"""# Native Harness post-HMR sidecar integration report

Date: 2026-08-21

Result: **{evidence['result']}**

- Claim: `{evidence['claim']}`
- Complete future runner: `{evidence['future_runner']['sha256']}`
- Generated helper: `{evidence['diagnostic_helper']['sha256']}`
- Closed join: exact sidecar plus broker-zero -> `post_hmr_pre_request_failure`
- Non-zero broker -> `post_hmr_request_boundary_unresolved`
- Invalid/absent sidecar -> `native_harness_terminal_failure`
- Node/Harness/broker/worker/model/provider/network/database/Docker counts: zero

This is provider-free representability evidence. It does not prove native
loading, a real sidecar, a real broker reading, DeepSeek behavior or Harness
readiness.
"""


def efficacy(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "ariadne.native_harness_post_hmr_sidecar_integration_efficacy.v1",
        "operation_id": OPERATION_ID,
        "result": "pass",
        "control_gain": "complete_future_runner_and_two_evidence_pre_request_join_represented",
        "occupied_harness_evidence": False,
        "deepseek_performance_evidence": False,
        "next_gate": "provider_free_future_runner_materialisation_and_controller_terminal_fixture_if_separately_planned",
    }


def _expected_outputs() -> dict[Path, bytes]:
    evidence = deterministic_evidence()
    return {
        EVIDENCE_PATH: _canonical(evidence),
        REPORT_PATH: render_report(evidence).encode(),
        EFFICACY_PATH: _canonical(efficacy(evidence)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        outputs = _expected_outputs()
        if args.write:
            for path, payload in outputs.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
        elif any(not path.is_file() or path.read_bytes() != payload for path, payload in outputs.items()):
            raise IntegrationRehearsalError("generated_artifact_drift")
        print(json.dumps({"result": "pass", "operation_id": OPERATION_ID}))
        return 0
    except (IntegrationRehearsalError, controller.PostHmrControllerError, OSError) as error:
        print(json.dumps({"result": "failed_closed", "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
