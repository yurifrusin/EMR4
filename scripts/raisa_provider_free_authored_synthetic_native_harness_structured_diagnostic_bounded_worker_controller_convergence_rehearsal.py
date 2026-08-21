"""Build provider-free evidence for bounded-worker diagnostic convergence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any

import jsonschema

from orchestration_harness import (
    bounded_worker_structured_diagnostic_controller as controller,
)
from orchestration_harness import native_pre_hmr_diagnostic as diagnostic


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "raisa-provider-free-authored-synthetic-native-harness-structured-diagnostic-"
    "bounded-worker-controller-convergence-rehearsal"
)
ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = ROOT / "contract.schema.json"
EVIDENCE_PATH = ROOT / "deterministic-evidence.json"
EVIDENCE_SCHEMA_PATH = ROOT / "deterministic-evidence.schema.json"
REPORT_PATH = ROOT / "deterministic-report.md"
ADAPTER_PATH = (
    REPO_ROOT
    / "orchestration_harness"
    / "bounded_worker_structured_diagnostic_controller.py"
)
BASE_CONTROLLER_PATH = (
    REPO_ROOT
    / "scripts"
    / "raisa_authored_synthetic_check_in_native_harness_bounded_worker_"
    "monitored_development_rehearsal.py"
)
DIAGNOSTIC_PATH = REPO_ROOT / "orchestration_harness" / "native_pre_hmr_diagnostic.py"
LEGACY_PATH = REPO_ROOT / "orchestration_harness" / "native_startup_terminal.py"
ATTEMPT_ID = "future-structured-bounded-worker-static-fixture-001"


class ConvergenceRehearsalError(ValueError):
    """The deterministic convergence evidence did not satisfy its contract."""


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    return _sha256(path.read_bytes())


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def load_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_bytes())
    schema = json.loads(CONTRACT_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(contract)
    if contract["operation_id"] != OPERATION_ID:
        raise ConvergenceRehearsalError("contract_operation_mismatch")
    return contract


def _stream(payload: bytes) -> dict[str, Any]:
    return {
        "byte_count": len(payload),
        "sha256": _sha256(payload),
        "classification_bytes": payload,
        "limit_exceeded": False,
    }


def _selection(
    *, root: Path, path: Path, source: str
) -> dict[str, Any]:
    return controller.select_pre_hmr_terminal(
        operation_id=OPERATION_ID,
        attempt_id=ATTEMPT_ID,
        candidate_source=source,
        native_process_started=True,
        exit_code=1,
        controller_coordinate="native_process_exited_nonzero",
        hmr_events=[],
        stdout=_stream(b""),
        stderr=_stream(b"secret-shaped raw stderr"),
        diagnostic_path=path,
        disposable_root=root,
    )


def deterministic_evidence() -> dict[str, Any]:
    contract = load_contract()
    components = contract["components"]
    observed_components = {
        "structured_diagnostic_sha256": _file_sha256(DIAGNOSTIC_PATH),
        "legacy_terminal_sha256": _file_sha256(LEGACY_PATH),
        "controller_baseline_sha256": _file_sha256(BASE_CONTROLLER_PATH),
    }
    if observed_components != components:
        raise ConvergenceRehearsalError("accepted_component_drift")
    immutable = []
    for row in contract["immutable_artifacts"]:
        path = REPO_ROOT / row["path"]
        observed = _file_sha256(path)
        if observed != row["sha256"]:
            raise ConvergenceRehearsalError("consumed_evidence_drift")
        immutable.append({"path": row["path"], "sha256": observed})

    source = contract["planning_source"]
    cleaned = False
    with tempfile.TemporaryDirectory(prefix="ariadne-controller-convergence-") as temp:
        temp_root = Path(temp).resolve()
        root = temp_root / "disposable"
        evidence_root = temp_root / "evidence"
        package_root = root / "package"
        (package_root / "lib").mkdir(parents=True)
        evidence_root.mkdir()
        (package_root / "lib" / "bin.js").write_bytes(b"throw new Error('fixture')\n")
        binding = controller.build_launch_binding(
            disposable_root=root,
            package_root=package_root,
            operation_id=OPERATION_ID,
            attempt_id=ATTEMPT_ID,
            candidate_source=source,
            target_path="C:/synthetic/synthetic_window_coalescer.py",
            node_executable="node",
        )
        structured = diagnostic.build_diagnostic_from_fixture(
            {"name": "Error", "message": "dynamic secret"},
            operation_id=OPERATION_ID,
            attempt_id=ATTEMPT_ID,
            candidate_source=source,
        )
        binding["diagnostic_path"].write_bytes(diagnostic.diagnostic_bytes(structured))
        valid = _selection(
            root=root, path=binding["diagnostic_path"], source=source
        )
        terminal_path = evidence_root / "pre-hmr-startup-terminal.json"
        terminal_sha256 = controller.write_selected_terminal_exclusive(
            path=terminal_path,
            terminal=valid["terminal"],
            evidence_root=evidence_root,
            disposable_root=root,
        )
        absent = _selection(root=root, path=root / "absent.json", source=source)
        malformed_path = root / "malformed.json"
        malformed_path.write_bytes(b"not-json")
        malformed = _selection(root=root, path=malformed_path, source=source)
        noncanonical_path = root / "noncanonical.json"
        noncanonical_path.write_text(json.dumps(structured, indent=2), encoding="utf-8")
        noncanonical = _selection(root=root, path=noncanonical_path, source=source)
        wrong = dict(structured)
        wrong["attempt_id"] = "wrong-attempt"
        wrong_path = root / "wrong-identity.json"
        wrong_path.write_bytes(diagnostic.diagnostic_bytes(wrong))
        wrong_identity = _selection(root=root, path=wrong_path, source=source)
        escaped_path = temp_root / "escaped.json"
        escaped_path.write_bytes(diagnostic.diagnostic_bytes(structured))
        escaped = _selection(root=root, path=escaped_path, source=source)
        launch_projection = {
            "argv_shape": [
                "node",
                "--expose-internals",
                "<exact-wrapper>",
                "--profile",
                "headless",
                "<accepted-authored-synthetic-task>",
            ],
            "wrapper_checks": binding["wrapper_projection"]["checks"],
            "wrapper_and_sidecar_inside_root": (
                binding["wrapper_path"].parent == root
                and binding["diagnostic_path"].parent == root
            ),
            "task_bound_to_accepted_controller": bool(binding["task_sha256"]),
        }
        selections = {
            "valid_exact_identity": {
                "schema": valid["terminal"]["schema_version"],
                "structured_accepted": valid["structured_accepted"],
                "reason": valid["failure_coordinate"],
            },
            "absent": {
                "schema": absent["terminal"]["schema_version"],
                "structured_accepted": absent["structured_accepted"],
                "reason": absent["failure_coordinate"],
            },
            "malformed": malformed["failure_coordinate"],
            "noncanonical": noncanonical["failure_coordinate"],
            "wrong_identity": wrong_identity["failure_coordinate"],
            "escaped": escaped["failure_coordinate"],
        }
        if terminal_sha256 != _file_sha256(terminal_path):
            raise ConvergenceRehearsalError("terminal_digest_mismatch")
    cleaned = not temp_root.exists()

    envelope = controller.validate_lifecycle_envelope(
        controller.lifecycle_envelope_source()
    )
    expected_selection = contract["selection"]
    if (
        selections["valid_exact_identity"] != expected_selection["valid_exact_identity"]
        or selections["absent"] != expected_selection["absent"]
        or any(
            selections[key] != "structured_diagnostic_invalid"
            for key in ("malformed", "noncanonical", "wrong_identity", "escaped")
        )
    ):
        raise ConvergenceRehearsalError("selection_matrix_mismatch")
    source_text = ADAPTER_PATH.read_text(encoding="utf-8")
    source_checks = {
        "base_controller_unchanged": observed_components[
            "controller_baseline_sha256"
        ]
        == components["controller_baseline_sha256"],
        "no_process_launcher": "subprocess.Popen" not in source_text,
        "no_provider_key": "DEEPSEEK_API_KEY" not in source_text,
        "accepted_wrapper_imported": "native_pre_hmr_diagnostic" in source_text,
        "accepted_base_controller_imported": (
            "raisa_authored_synthetic_check_in_native_harness_bounded_worker_"
            in source_text
        ),
    }
    if not all(source_checks.values()) or not cleaned:
        raise ConvergenceRehearsalError("source_or_cleanup_projection_failed")
    return {
        "schema_version": "ariadne.structured_diagnostic_bounded_worker_controller_convergence_evidence.v1",
        "operation_id": OPERATION_ID,
        "result": "pass",
        "claim": "provider_free_descendant_controller_adapter_converged",
        "components": observed_components,
        "immutable_artifact_count": len(immutable),
        "immutable_artifacts": immutable,
        "launch_projection": launch_projection,
        "selection_matrix": selections,
        "lifecycle_envelope": envelope,
        "source_checks": source_checks,
        "cleanup": {"disposable_fixture_root_absent": cleaned},
        "process_boundary": contract["process_boundary"],
        "occupied_attempt_authorized": False,
        "raw_historical_stream_read": False,
    }


def render_report(value: dict[str, Any]) -> str:
    return f"""# Provider-free bounded-worker controller convergence report

Date: 2026-08-21

Result: **{value['result']}**

- Claim: `{value['claim']}`
- Valid exact-identity selection: `{value['selection_matrix']['valid_exact_identity']['schema']}`
- Missing-sidecar fallback / reason: `{value['selection_matrix']['absent']['schema']}` / `{value['selection_matrix']['absent']['reason']}`
- Invalid fixture coordinates: `structured_diagnostic_invalid`
- Consumed immutable artifacts: `{value['immutable_artifact_count']}`
- Disposable fixture root absent: `{str(value['cleanup']['disposable_fixture_root_absent']).lower()}`
- Harness / broker / worker / model / provider activity: `0 / 0 / 0 / 0 / 0`

This proves provider-free controller composition only. A separately authorised
fresh occupied attempt is still required to exercise the adapter against the
native runtime.
"""


def build_artifacts() -> dict[str, Any]:
    value = deterministic_evidence()
    schema = json.loads(EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(value)
    EVIDENCE_PATH.write_bytes(_canonical(value))
    REPORT_PATH.write_text(render_report(value), encoding="utf-8", newline="\n")
    if json.loads(EVIDENCE_PATH.read_bytes()) != deterministic_evidence():
        raise ConvergenceRehearsalError("evidence_readback_mismatch")
    return value


def validate_artifacts() -> dict[str, Any]:
    value = deterministic_evidence()
    schema = json.loads(EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator(schema).validate(value)
    if json.loads(EVIDENCE_PATH.read_bytes()) != value:
        raise ConvergenceRehearsalError("evidence_not_current")
    if REPORT_PATH.read_text(encoding="utf-8") != render_report(value):
        raise ConvergenceRehearsalError("report_not_current")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--build", action="store_true")
    action.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        value = build_artifacts() if args.build else validate_artifacts()
    except (ConvergenceRehearsalError, OSError, jsonschema.ValidationError) as error:
        print(json.dumps({"result": "failed_closed", "error": str(error)}))
        return 1
    print(json.dumps({"result": value["result"], "operation_id": OPERATION_ID}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
