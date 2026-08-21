"""Generate provider-free future-attempt identity and target rebinding evidence."""

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

from orchestration_harness import native_post_hmr_future_attempt_materialisation as base
from orchestration_harness import native_post_hmr_future_attempt_rebinding as rebinding
from orchestration_harness import native_post_hmr_pre_request_controller as controller
from orchestration_harness import native_post_hmr_pre_request_diagnostic as diagnostic
from scripts import (
    deepseek_native_harness_provider_free_future_runner_materialisation_and_controller_terminal_fixture_rehearsal as accepted_materialisation,
)


OPERATION_ID = (
    "deepseek-native-harness-provider-free-future-attempt-identity-and-target-"
    "rebinding-rehearsal"
)
ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = ROOT / "contract.schema.json"
BUNDLE_SCHEMA_PATH = ROOT / "rebound-future-attempt-bundle.schema.json"
TERMINAL_SCHEMA_PATH = ROOT / "rebound-controller-terminal.schema.json"
EVIDENCE_SCHEMA_PATH = ROOT / "rebinding-evidence.schema.json"
EVIDENCE_PATH = ROOT / "rebinding-evidence.json"
REPORT_PATH = ROOT / "rebinding-report.md"
EFFICACY_PATH = ROOT / "efficacy-reading.json"
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
CONTROLLER_PATH = (
    REPO_ROOT / "orchestration_harness" / "native_post_hmr_pre_request_controller.py"
)
REBINDER_PATH = REPO_ROOT / Path(rebinding.__file__).relative_to(REPO_ROOT)
REPORT_TIMESTAMP = "2026-08-21T22:49:59.5125472+10:00"


class RebindingRehearsalError(ValueError):
    """The provider-free rebinding evidence did not satisfy its contract."""


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
        raise RebindingRehearsalError("git_resolution_failed")
    return completed.stdout.strip()


def _load_schema(path: Path) -> dict[str, Any]:
    schema = json.loads(path.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    return schema


def load_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_bytes())
    schemas = [
        _load_schema(path)
        for path in (
            CONTRACT_SCHEMA_PATH,
            BUNDLE_SCHEMA_PATH,
            TERMINAL_SCHEMA_PATH,
            EVIDENCE_SCHEMA_PATH,
        )
    ]
    jsonschema.Draft202012Validator(schemas[0]).validate(contract)
    planning_source = contract["planning_source"]
    relative_plan = PLAN_PATH.relative_to(REPO_ROOT).as_posix()
    if (
        contract["operation_id"] != OPERATION_ID
        or _git("rev-parse", "--verify", f"{planning_source}^{{commit}}")
        != planning_source
        or _git("log", "-1", "--format=%H", "--", relative_plan) != planning_source
        or contract["fresh_identity"]["candidate_source"] != planning_source
    ):
        raise RebindingRehearsalError("planning_source_invalid")
    accepted_contract = accepted_materialisation.load_contract()
    accepted = contract["accepted_materialisation"]
    if (
        accepted["reviewed_source"] != "9b59c6dd7dac9a77030118e83bc81ebf74c3289c"
        or accepted["candidate_source"] != "55906f55dfd82474f095acaa9dc436013db77411"
        or accepted["fixture_identity"] != accepted_contract["fixture_identity"]
        or accepted["source_bindings"]
        != {
            key: accepted_contract["source_bindings"][key]
            for key in (
                "future_runner_sha256",
                "generated_helper_sha256",
                "controller_module_sha256",
            )
        }
    ):
        raise RebindingRehearsalError("accepted_materialisation_binding_invalid")
    fresh = contract["fresh_identity"]
    predecessor = accepted["fixture_identity"]
    if (
        fresh["operation_id"] != OPERATION_ID
        or fresh["attempt_id"] != "future-identity-target-rebinding-fixture-001"
        or any(fresh[key] == predecessor[key] for key in fresh)
    ):
        raise RebindingRehearsalError("fresh_identity_invalid")
    if contract["target_binding"] != rebinding.build_target_binding(
        rebinding.ADMITTED_TARGET_PATH
    ):
        raise RebindingRehearsalError("target_binding_invalid")
    if _sha256(REBINDER_PATH.read_bytes()) != contract["rebinder_module_sha256"]:
        raise RebindingRehearsalError("rebinder_module_binding_invalid")
    if any(value != 0 for value in contract["proof_boundary"].values()):
        raise RebindingRehearsalError("proof_boundary_invalid")
    return contract


def source_payloads(
    contract: dict[str, Any],
) -> tuple[bytes, bytes, dict[str, str], dict[str, Any]]:
    accepted_contract = accepted_materialisation.load_contract()
    accepted_runner, accepted_helper, _ = accepted_materialisation._source_payloads(
        accepted_contract
    )
    accepted = contract["accepted_materialisation"]
    rebound_runner, transformation = rebinding.rebind_future_runner_source(
        accepted_runner,
        expected_accepted_sha256=accepted["source_bindings"]["future_runner_sha256"],
        consumed_target_path=accepted["consumed_target_path"],
        target_path=contract["target_binding"]["relative_path"],
    )
    fresh = contract["fresh_identity"]
    rebound_helper = diagnostic.build_helper_source(
        operation_id=fresh["operation_id"],
        attempt_id=fresh["attempt_id"],
        candidate_source=fresh["candidate_source"],
    )
    observed = {
        "future_runner_sha256": _sha256(rebound_runner),
        "generated_helper_sha256": _sha256(rebound_helper),
        "controller_module_sha256": _sha256(CONTROLLER_PATH.read_bytes()),
    }
    if observed != contract["rebound_source_bindings"]:
        raise RebindingRehearsalError("rebound_source_binding_mismatch")
    predecessor = accepted["fixture_identity"]
    if accepted["consumed_target_path"].encode() in rebound_runner or any(
        value.encode() in rebound_helper for value in predecessor.values()
    ):
        raise RebindingRehearsalError("consumed_coordinate_retained")
    if accepted_helper == rebound_helper:
        raise RebindingRehearsalError("helper_identity_not_rebound")
    if len(set(observed.values())) != len(observed):
        raise RebindingRehearsalError("semantic_hash_distinctness_failed")
    return rebound_runner, rebound_helper, observed, transformation


def _sidecar(
    contract: dict[str, Any],
    *,
    stage: str = "loader_readiness_wait",
    cause: str = "operation_rejected",
    error_name: str = "Error",
) -> dict[str, Any]:
    identity = contract["fresh_identity"]
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
    identity = contract["fresh_identity"]
    target_path = contract["target_binding"]["relative_path"]
    bindings = contract["rebound_source_bindings"]
    temporary_root: Path | None = None
    with tempfile.TemporaryDirectory(
        prefix="ariadne-future-attempt-rebinding-"
    ) as temporary:
        temporary_root = Path(temporary).resolve()
        reading = rebinding.materialize_rebound_future_attempt(
            disposable_parent=temporary_root,
            operation_id=identity["operation_id"],
            attempt_id=identity["attempt_id"],
            candidate_source=identity["candidate_source"],
            target_path=target_path,
            runner_payload=runner_payload,
            helper_payload=helper_payload,
            controller_payload=CONTROLLER_PATH.read_bytes(),
            expected_bindings=bindings,
        )
        root = reading["root"]
        jsonschema.Draft202012Validator(_load_schema(BUNDLE_SCHEMA_PATH)).validate(
            reading["manifest"]
        )
        broker = controller.build_broker_reading(
            operation_id=identity["operation_id"],
            attempt_id=identity["attempt_id"],
            candidate_source=identity["candidate_source"],
            counters=counters,
        )
        rebinding.write_broker_fixture(root, broker)
        if isinstance(sidecar, dict):
            rebinding.write_sidecar_fixture(root, sidecar)
        elif isinstance(sidecar, bytes):
            path = base._path(root, base.SIDECAR_RELATIVE_PATH)
            base._write_exclusive(path, sidecar)
        target_created = (root / Path(target_path)).exists()
        terminal = rebinding.assemble_controller_terminal(
            root,
            operation_id=identity["operation_id"],
            attempt_id=identity["attempt_id"],
            candidate_source=identity["candidate_source"],
            target_path=target_path,
            expected_bindings=bindings,
        )
        jsonschema.Draft202012Validator(_load_schema(TERMINAL_SCHEMA_PATH)).validate(
            terminal
        )
        result = {
            "coordinate": terminal["coordinate"],
            "initial_files": reading["files"],
            "runner_bytes": reading["runner_bytes"],
            "helper_bytes": reading["helper_bytes"],
            "target_file_created": target_created,
            "bindings_converged": (
                terminal["source_bindings"] == reading["manifest"]["source_bindings"]
                and terminal["target_binding"] == reading["manifest"]["target_binding"]
            ),
        }
    if temporary_root is None or temporary_root.exists():
        raise RebindingRehearsalError("temporary_cleanup_failed")
    return {**result, "cleanup_complete": True}


def deterministic_evidence() -> dict[str, Any]:
    contract = load_contract()
    runner_payload, helper_payload, bindings, transformation = source_payloads(contract)
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
            sidecar=_sidecar(contract, error_name=name),
        )["coordinate"]
        for name in error_names
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
        coordinate != "post_hmr_pre_request_failure"
        for coordinate in (*stage_results, *error_results, *special_results)
    ):
        raise RebindingRehearsalError("pre_request_matrix_mismatch")
    if any(
        coordinate != "post_hmr_request_boundary_unresolved"
        for coordinate in nonzero_results
    ):
        raise RebindingRehearsalError("nonzero_matrix_mismatch")
    if (
        valid_zero["coordinate"] != "post_hmr_pre_request_failure"
        or absent["coordinate"] != "native_harness_terminal_failure"
        or invalid["coordinate"] != "native_harness_terminal_failure"
        or not all(
            value
            for value in (
                valid_zero["cleanup_complete"],
                absent["cleanup_complete"],
                invalid["cleanup_complete"],
                valid_zero["bindings_converged"],
            )
        )
        or valid_zero["target_file_created"]
    ):
        raise RebindingRehearsalError("terminal_binding_or_cleanup_mismatch")
    evidence = {
        "schema_version": "ariadne.native_harness_future_attempt_rebinding_evidence.v1",
        "operation_id": OPERATION_ID,
        "result": "pass",
        "claim": "provider_free_fresh_future_attempt_identity_and_inert_target_rebinding_representable",
        "fresh_identity": contract["fresh_identity"],
        "target_binding": contract["target_binding"],
        "source_bindings": bindings,
        "transformation": {
            "accepted_future_runner_sha256": transformation[
                "accepted_future_runner_sha256"
            ],
            "rebound_future_runner_sha256": transformation[
                "rebound_future_runner_sha256"
            ],
            "consumed_target_absent": transformation["consumed_target_absent"],
            "predecessor_helper_identity_absent": True,
            "target_literal_count": transformation["target_literal_count"],
            "reverse_binding_exact": transformation["reverse_binding_exact"],
            "independent_hash_fields": True,
        },
        "materialisation": {
            "path_roster": list(base.PATH_ROSTER),
            "initial_files": valid_zero["initial_files"],
            "runner_bytes": valid_zero["runner_bytes"],
            "helper_bytes": valid_zero["helper_bytes"],
            "bundle_terminal_bindings_converged": valid_zero["bindings_converged"],
            "target_file_created": False,
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
    jsonschema.Draft202012Validator(_load_schema(EVIDENCE_SCHEMA_PATH)).validate(
        evidence
    )
    return evidence


def render_report(evidence: dict[str, Any]) -> str:
    return f"""# Native Harness future-attempt identity and target rebinding report

Date: 2026-08-21

Timestamp: {REPORT_TIMESTAMP} (Australia/Brisbane)

Result: **{evidence["result"]}**

- Claim: `{evidence["claim"]}`
- Fresh attempt: `{evidence["fresh_identity"]["attempt_id"]}`
- Full candidate: `{evidence["fresh_identity"]["candidate_source"]}`
- Inert target: `{evidence["target_binding"]["relative_path"]}`
- Rebound runner: `{evidence["source_bindings"]["future_runner_sha256"]}`
- Rebound helper: `{evidence["source_bindings"]["generated_helper_sha256"]}`
- Consumed target absent; reverse runner binding exact
- Bundle and terminal identity, target and hashes converge
- Target-file creation and Node/Harness/broker/worker/model/provider counts: zero

This is provider-free identity and inert-target transformation evidence. It
does not prove JavaScript parsing, native loading, HMR boot, DeepSeek behavior
or occupied Harness readiness.
"""


def efficacy(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "ariadne.native_harness_future_attempt_rebinding_efficacy.v1",
        "operation_id": OPERATION_ID,
        "result": "pass",
        "control_gain": "fresh_identity_and_inert_target_are_machine_bound_before_worker_execution",
        "free_form_finite_control_fields": 0,
        "occupied_harness_evidence": False,
        "deepseek_performance_evidence": False,
        "next_gate": "provider_free_stock_headless_to_custom_runner_boot_proof_if_separately_frozen",
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
            raise RebindingRehearsalError("generated_artifact_drift")
        print(json.dumps({"result": "pass", "operation_id": OPERATION_ID}))
        return 0
    except (
        RebindingRehearsalError,
        rebinding.FutureAttemptRebindingError,
        base.FutureAttemptMaterialisationError,
        controller.PostHmrControllerError,
        diagnostic.PostHmrDiagnosticError,
        jsonschema.ValidationError,
        jsonschema.SchemaError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
    ) as error:
        print(json.dumps({"result": "fail", "reason": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
