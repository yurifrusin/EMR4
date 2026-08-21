"""Generate provider-free future-attempt materialisation and terminal evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

import jsonschema


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from orchestration_harness import native_post_hmr_future_attempt_materialisation as materializer
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

OPERATION_ID = (
    "deepseek-native-harness-provider-free-future-runner-materialisation-and-"
    "controller-terminal-fixture-rehearsal"
)
ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = ROOT / "contract.schema.json"
BUNDLE_SCHEMA_PATH = ROOT / "future-attempt-bundle.schema.json"
TERMINAL_SCHEMA_PATH = ROOT / "controller-terminal.schema.json"
EVIDENCE_PATH = ROOT / "materialisation-evidence.json"
EVIDENCE_SCHEMA_PATH = ROOT / "materialisation-evidence.schema.json"
REPORT_PATH = ROOT / "materialisation-report.md"
EFFICACY_PATH = ROOT / "efficacy-reading.json"
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
CONTROLLER_PATH = (
    REPO_ROOT / "orchestration_harness" / "native_post_hmr_pre_request_controller.py"
)
DIAGNOSTIC_PATH = (
    REPO_ROOT / "orchestration_harness" / "native_post_hmr_pre_request_diagnostic.py"
)
MATERIALIZER_PATH = REPO_ROOT / Path(materializer.__file__).relative_to(REPO_ROOT)
REPORT_TIMESTAMP = "2026-08-21T21:54:38.7791038+10:00"


class MaterialisationRehearsalError(ValueError):
    """The provider-free materialisation evidence did not satisfy its contract."""


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
        raise MaterialisationRehearsalError("git_resolution_failed")
    return completed.stdout.strip()


def load_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_bytes())
    contract_schema = json.loads(CONTRACT_SCHEMA_PATH.read_bytes())
    bundle_schema = json.loads(BUNDLE_SCHEMA_PATH.read_bytes())
    terminal_schema = json.loads(TERMINAL_SCHEMA_PATH.read_bytes())
    evidence_schema = json.loads(EVIDENCE_SCHEMA_PATH.read_bytes())
    for schema in (contract_schema, bundle_schema, terminal_schema, evidence_schema):
        jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(contract_schema).validate(contract)
    source = contract["planning_source"]
    relative_plan = PLAN_PATH.relative_to(REPO_ROOT).as_posix()
    if (
        contract["operation_id"] != OPERATION_ID
        or _git("rev-parse", "--verify", f"{source}^{{commit}}") != source
        or _git("log", "-1", "--format=%H", "--", relative_plan) != source
    ):
        raise MaterialisationRehearsalError("planning_source_invalid")
    if contract["path_roster"] != list(materializer.PATH_ROSTER):
        raise MaterialisationRehearsalError("path_roster_source_mismatch")
    return contract


def _source_payloads(contract: dict[str, Any]) -> tuple[bytes, bytes, dict[str, str]]:
    bindings = contract["source_bindings"]
    accepted_payload = accepted_runner.runner_source(accepted_diagnosis.TARGET_PATH)
    future_payload = controller.derive_future_runner_source(
        accepted_payload,
        expected_accepted_sha256=bindings["accepted_runner_sha256"],
    )
    identity = contract["fixture_identity"]
    helper_payload = diagnostic.build_helper_source(
        operation_id=identity["operation_id"],
        attempt_id=identity["attempt_id"],
        candidate_source=identity["candidate_source"],
    )
    observed = {
        "accepted_runner_sha256": _sha256(accepted_payload),
        "accepted_diagnostic_module_sha256": _sha256(DIAGNOSTIC_PATH.read_bytes()),
        "controller_module_sha256": _sha256(CONTROLLER_PATH.read_bytes()),
        "future_runner_sha256": _sha256(future_payload),
        "generated_helper_sha256": _sha256(helper_payload),
        "materializer_module_sha256": _sha256(MATERIALIZER_PATH.read_bytes()),
    }
    if observed != bindings:
        raise MaterialisationRehearsalError("source_binding_mismatch")
    return future_payload, helper_payload, observed


def _sidecar(
    contract: dict[str, Any],
    *,
    stage: str = "loader_readiness_wait",
    cause: str = "operation_rejected",
    error_name: str = "Error",
) -> dict[str, Any]:
    identity = contract["fixture_identity"]
    return diagnostic.build_diagnostic_from_fixture(
        {"name": error_name, "constructor_name": error_name},
        operation_id=identity["operation_id"],
        attempt_id=identity["attempt_id"],
        candidate_source=identity["candidate_source"],
        stage=stage,
        cause_coordinate=cause,
    )


def _scenario(
    *,
    contract: dict[str, Any],
    runner_payload: bytes,
    helper_payload: bytes,
    sidecar: dict[str, Any] | bytes | None,
    counters: dict[str, int] | None = None,
) -> dict[str, Any]:
    identity = contract["fixture_identity"]
    bindings = contract["source_bindings"]
    terminal_schema = json.loads(TERMINAL_SCHEMA_PATH.read_bytes())
    bundle_schema = json.loads(BUNDLE_SCHEMA_PATH.read_bytes())
    temporary_root: Path | None = None
    with tempfile.TemporaryDirectory(prefix="ariadne-future-attempt-materialisation-") as temporary:
        temporary_root = Path(temporary).resolve()
        reading = materializer.materialize_future_attempt(
            disposable_parent=temporary_root,
            attempt_id=identity["attempt_id"],
            operation_id=identity["operation_id"],
            candidate_source=identity["candidate_source"],
            runner_payload=runner_payload,
            helper_payload=helper_payload,
            controller_payload=CONTROLLER_PATH.read_bytes(),
            expected_runner_sha256=bindings["future_runner_sha256"],
            expected_helper_sha256=bindings["generated_helper_sha256"],
            expected_controller_sha256=bindings["controller_module_sha256"],
        )
        root = reading["root"]
        jsonschema.Draft202012Validator(bundle_schema).validate(reading["manifest"])
        broker = controller.build_broker_reading(
            operation_id=identity["operation_id"],
            attempt_id=identity["attempt_id"],
            candidate_source=identity["candidate_source"],
            counters=counters,
        )
        materializer.write_broker_fixture(root, broker)
        if isinstance(sidecar, dict):
            materializer.write_sidecar_fixture(root, sidecar)
        elif isinstance(sidecar, bytes):
            path = root / Path(*materializer.SIDECAR_RELATIVE_PATH.split("/"))
            with path.open("xb") as stream:
                stream.write(sidecar)
        terminal = materializer.assemble_controller_terminal(
            root,
            operation_id=identity["operation_id"],
            attempt_id=identity["attempt_id"],
            candidate_source=identity["candidate_source"],
            expected_bindings={
                "future_runner_sha256": bindings["future_runner_sha256"],
                "generated_helper_sha256": bindings["generated_helper_sha256"],
                "controller_module_sha256": bindings["controller_module_sha256"],
            },
        )
        jsonschema.Draft202012Validator(terminal_schema).validate(terminal)
        result = {
            "coordinate": terminal["coordinate"],
            "diagnostic_accepted": terminal["diagnostic_accepted"],
            "broker_zero": terminal["broker_zero"],
            "pre_request_supported": terminal["pre_request_supported"],
            "occupied_launch_authorized": terminal["occupied_launch_authorized"],
            "raw_stream_read": terminal["raw_stream_read"],
            "raw_error_retained": terminal["raw_error_retained"],
            "initial_files": reading["files"],
            "runner_bytes": reading["runner_bytes"],
            "helper_bytes": reading["helper_bytes"],
        }
    result["cleanup_complete"] = temporary_root is not None and not temporary_root.exists()
    return result


def deterministic_evidence() -> dict[str, Any]:
    contract = load_contract()
    runner_payload, helper_payload, observed_bindings = _source_payloads(contract)
    valid_zero = _scenario(
        contract=contract,
        runner_payload=runner_payload,
        helper_payload=helper_payload,
        sidecar=_sidecar(contract),
    )
    stage_results = [
        _scenario(
            contract=contract,
            runner_payload=runner_payload,
            helper_payload=helper_payload,
            sidecar=_sidecar(contract, stage=stage),
        )["coordinate"]
        for stage in diagnostic.PRE_REQUEST_STAGES
    ]
    error_names = (
        "AggregateError",
        "Error",
        "InvalidPresetIdError",
        "PresetMountError",
        "TypeError",
        "UnknownErrorName",
        "UnknownPresetError",
    )
    error_results = [
        _scenario(
            contract=contract,
            runner_payload=runner_payload,
            helper_payload=helper_payload,
            sidecar=_sidecar(contract, error_name=error_name),
        )["coordinate"]
        for error_name in error_names
    ]
    special_results = [
        _scenario(
            contract=contract,
            runner_payload=runner_payload,
            helper_payload=helper_payload,
            sidecar=_sidecar(contract, stage=stage, cause=cause),
        )["coordinate"]
        for stage, cause in (
            ("required_service_lookup", "required_service_missing"),
            ("preset_root_roster_admission", "preset_root_roster_mismatch"),
        )
    ]
    nonzero_results = [
        _scenario(
            contract=contract,
            runner_payload=runner_payload,
            helper_payload=helper_payload,
            sidecar=_sidecar(contract),
            counters={counter: 1},
        )["coordinate"]
        for counter in controller.BROKER_COUNTERS
    ]
    absent = _scenario(
        contract=contract,
        runner_payload=runner_payload,
        helper_payload=helper_payload,
        sidecar=None,
    )
    invalid = _scenario(
        contract=contract,
        runner_payload=runner_payload,
        helper_payload=helper_payload,
        sidecar=b"not-json",
    )
    if any(
        value != "post_hmr_pre_request_failure"
        for value in (*stage_results, *error_results, *special_results)
    ):
        raise MaterialisationRehearsalError("pre_request_matrix_mismatch")
    if any(
        value != "post_hmr_request_boundary_unresolved"
        for value in nonzero_results
    ):
        raise MaterialisationRehearsalError("nonzero_matrix_mismatch")
    if (
        valid_zero["coordinate"] != "post_hmr_pre_request_failure"
        or absent["coordinate"] != "native_harness_terminal_failure"
        or invalid["coordinate"] != "native_harness_terminal_failure"
        or not all(
            result["cleanup_complete"]
            for result in (valid_zero, absent, invalid)
        )
    ):
        raise MaterialisationRehearsalError("terminal_or_cleanup_mismatch")
    evidence = {
        "schema_version": "ariadne.native_harness_future_attempt_materialisation_evidence.v1",
        "operation_id": OPERATION_ID,
        "result": "pass",
        "claim": "provider_free_exact_future_attempt_bundle_and_controller_terminal_assembly_representable",
        "source_bindings": observed_bindings,
        "materialisation": {
            "path_roster": list(materializer.PATH_ROSTER),
            "initial_files": valid_zero["initial_files"],
            "runner_bytes": valid_zero["runner_bytes"],
            "helper_bytes": valid_zero["helper_bytes"],
            "inherited_target_coordinate_present": accepted_diagnosis.TARGET_PATH.encode()
            in runner_payload,
            "inherited_target_classification": materializer.INHERITED_TARGET_CLASSIFICATION,
            "occupied_launch_authorized": False,
            "exclusive_write": True,
            "cleanup_complete": True,
        },
        "terminal_matrix": {
            "scenario_count": 24,
            "stage_count": len(stage_results),
            "error_kind_count": len(error_results),
            "special_cause_count": len(special_results),
            "nonzero_counter_count": len(nonzero_results),
            "valid_zero_coordinate": valid_zero["coordinate"],
            "nonzero_coordinate": nonzero_results[0],
            "absent_sidecar_coordinate": absent["coordinate"],
            "invalid_sidecar_coordinate": invalid["coordinate"],
            "pre_request_requires_both": True,
            "raw_stream_read": False,
            "raw_error_retained": False,
        },
        "proof_boundary": contract["proof_boundary"],
        "occupied_attempt_authorized": False,
        "raw_historical_stream_read": False,
    }
    schema = json.loads(EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator(schema).validate(evidence)
    return evidence


def render_report(evidence: dict[str, Any]) -> str:
    return f"""# Native Harness future-attempt materialisation report

Date: 2026-08-21

Timestamp: {REPORT_TIMESTAMP} (Australia/Brisbane)

Result: **{evidence['result']}**

- Claim: `{evidence['claim']}`
- Exact future runner: `{evidence['source_bindings']['future_runner_sha256']}`
- Exact helper: `{evidence['source_bindings']['generated_helper_sha256']}`
- Closed materialised roster: {len(evidence['materialisation']['path_roster'])} paths
- Exact sidecar plus broker zero -> `post_hmr_pre_request_failure`
- Non-zero broker -> `post_hmr_request_boundary_unresolved`
- Invalid/absent sidecar -> `native_harness_terminal_failure`
- Inherited consumed target classified; occupied launch remains false
- Node/Harness/broker/worker/model/provider/network/database/Docker counts: zero

This is provider-free materialisation and terminal-assembly evidence. It does
not prove JavaScript parsing, native loading, a safe new target coordinate,
DeepSeek behavior or Harness readiness.
"""


def efficacy(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "ariadne.native_harness_future_attempt_materialisation_efficacy.v1",
        "operation_id": OPERATION_ID,
        "result": "pass",
        "control_gain": "exact_future_attempt_bundle_and_two_evidence_terminal_assembly_materialised",
        "occupied_harness_evidence": False,
        "deepseek_performance_evidence": False,
        "next_gate": "provider_free_future_target_coordinate_rebinding_or_occupied_readiness_decision_if_separately_planned",
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
        elif any(
            not path.is_file() or path.read_bytes() != payload
            for path, payload in outputs.items()
        ):
            raise MaterialisationRehearsalError("generated_artifact_drift")
        print(json.dumps({"result": "pass", "operation_id": OPERATION_ID}))
        return 0
    except (
        MaterialisationRehearsalError,
        materializer.FutureAttemptMaterialisationError,
        controller.PostHmrControllerError,
        diagnostic.PostHmrDiagnosticError,
        OSError,
    ) as error:
        print(json.dumps({"result": "failed_closed", "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
