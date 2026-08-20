from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from orchestration_harness import native_pre_hmr_diagnostic as diagnostic
from scripts import (
    deepseek_native_harness_provider_free_structured_diagnostic_wrapper_node_fixture_rehearsal
    as rehearsal,
)


CANDIDATE = "0" * 40
ATTEMPT = "node-fixture-attempt-999"


def test_deterministic_check_is_provider_and_process_free() -> None:
    assert rehearsal.deterministic_check()["result"] == "pass"
    assert rehearsal.deterministic_check()["node_process_count"] == 0
    assert rehearsal.load_contract()["scenario_order"] == list(rehearsal.SCENARIOS)


def test_fixture_sources_are_authored_and_cover_closed_coordinates() -> None:
    nested = rehearsal.fixture_source("nested_known")
    unknown = rehearsal.fixture_source("unknown_secret_shaped")
    aggregate = rehearsal.fixture_source("aggregate_multiple")
    assert b"ERR_MODULE_NOT_FOUND" in nested
    assert rehearsal.SECRET_SENTINEL.encode() in unknown
    assert b"AggregateError" in aggregate
    for payload in (nested, unknown, aggregate):
        assert b"@deepseek-ai" not in payload
        assert b"node_modules" not in payload


def test_observer_retains_only_identity_and_fixed_coordinates() -> None:
    root = Path("C:/deterministic/authored-node-fixture")
    source = rehearsal.observer_source(
        scenario="nested_known",
        wrapper_path=root / "entrypoint-wrapper.mjs",
        result_path=root / "observer-result.json",
    ).decode()
    assert source.count("await import(WRAPPER_URL)") == 1
    assert source.count("error === globalThis.__EMR4_AUTHORED_FIXTURE_ERROR__") == 1
    assert source.count('openSync(RESULT_PATH, "wx"') == 1
    assert ".message" not in source
    assert ".stack" not in source


def test_canonical_wrapper_mode_sorts_recursive_json_without_changing_default(
    tmp_path: Path,
) -> None:
    package_root = tmp_path / "fixture-package"
    entrypoint = package_root / "lib" / "bin.js"
    entrypoint.parent.mkdir(parents=True)
    entrypoint.write_bytes(rehearsal.fixture_source("nested_known"))
    default = diagnostic.build_entrypoint_wrapper_source(
        package_root=package_root.resolve(),
        wrapper_path=(tmp_path / "default-wrapper.mjs").resolve(),
        diagnostic_path=(tmp_path / "default-diagnostic.json").resolve(),
        disposable_root=tmp_path.resolve(),
        operation_id=rehearsal.OPERATION_ID,
        attempt_id=ATTEMPT,
        candidate_source=CANDIDATE,
    )
    canonical = diagnostic.build_entrypoint_wrapper_source(
        package_root=package_root.resolve(),
        wrapper_path=(tmp_path / "canonical-wrapper.mjs").resolve(),
        diagnostic_path=(tmp_path / "canonical-diagnostic.json").resolve(),
        disposable_root=tmp_path.resolve(),
        operation_id=rehearsal.OPERATION_ID,
        attempt_id=ATTEMPT,
        candidate_source=CANDIDATE,
        canonical_json=True,
    )
    assert b"function canonicalize(value)" not in default
    projection = diagnostic.validate_entrypoint_wrapper_source(
        canonical, require_canonical_json=True
    )
    assert projection["checks"]["canonical_json_serializer"] is True


def test_observer_validation_rejects_nonidentical_and_extra_fields() -> None:
    value = {
        "caught_rejection": True,
        "exit_coordinate": "caught_identical",
        "identical_rejection": True,
        "node_version": "22.1.0",
        "scenario": "nested_known",
        "schema_version": rehearsal.OBSERVER_VERSION,
    }
    assert rehearsal.validate_observer(value, "nested_known") == value
    value["identical_rejection"] = False
    with pytest.raises(rehearsal.NodeFixtureRehearsalError, match="relationship"):
        rehearsal.validate_observer(value, "nested_known")
    value["identical_rejection"] = True
    value["raw_message"] = "forbidden"
    with pytest.raises(rehearsal.NodeFixtureRehearsalError, match="keys"):
        rehearsal.validate_observer(value, "nested_known")


def test_scenario_outcomes_require_three_diagnostics_and_write_failure_identity() -> None:
    rows = []
    for scenario in rehearsal.SCENARIOS:
        accepted = scenario != "preexisting_sidecar"
        expected = {
            "nested_known": ("type_error", "host_preparation_failed", "none"),
            "unknown_secret_shaped": ("unknown", "none", "none"),
            "aggregate_multiple": ("aggregate_error", "none", "multiple"),
            "preexisting_sidecar": (None, None, None),
        }[scenario]
        rows.append(
            {
                "scenario": scenario,
                "process_exit_code": 0,
                "identical_rejection": True,
                "diagnostic_accepted": accepted,
                "diagnostic_error": None,
                "top_error_kind": expected[0],
                "top_message_coordinate": expected[1],
                "top_aggregate_shape": expected[2],
                "preexisting_sidecar_unchanged": True if not accepted else None,
            }
        )
    assert rehearsal.validate_scenario_outcomes(rows) == []
    rows[0]["identical_rejection"] = False
    assert "nested_known:identity_rethrow_failed" in rehearsal.validate_scenario_outcomes(
        rows
    )


def test_execute_rejects_invalid_identity_before_node_process() -> None:
    def forbidden(*args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        raise AssertionError("Node process forbidden")

    with pytest.raises(rehearsal.NodeFixtureRehearsalError, match="candidate_source"):
        rehearsal.execute_attempt(
            candidate_source="short",
            attempt_id=ATTEMPT,
            node_executable="node",
            run=forbidden,
        )


def test_accepted_component_still_requires_canonical_sidecar_bytes(tmp_path: Path) -> None:
    value = diagnostic.build_diagnostic_from_fixture(
        {"name": "Error", "message": "host preparation failed"},
        operation_id=rehearsal.OPERATION_ID,
        attempt_id=ATTEMPT,
        candidate_source=CANDIDATE,
    )
    path = tmp_path / "diagnostic.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(
        diagnostic.StructuredDiagnosticError, match="canonical_bytes_required"
    ):
        diagnostic.read_structured_diagnostic(
            path,
            disposable_root=tmp_path.resolve(),
            operation_id=rehearsal.OPERATION_ID,
            attempt_id=ATTEMPT,
            candidate_source=CANDIDATE,
        )
