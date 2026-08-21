from __future__ import annotations

from pathlib import Path

import pytest

from scripts import (
    deepseek_native_harness_provider_free_preset_mount_safe_subcoordinate_sanitizer_rehearsal
    as base,
)
from scripts import (
    deepseek_native_harness_provider_free_preset_mount_sanitizer_windows_minimum_environment_recovery
    as subject,
)


CANDIDATE = "a" * 40


def test_contract_and_predecessor_bindings_pass() -> None:
    contract = subject.load_contract()
    subject.verify_predecessor_bindings(contract)
    assert contract["child_environment_keys"] == list(subject.WINDOWS_ENVIRONMENT_KEYS)
    assert contract["forbidden_environment_keys"] == ["PATH", "NODE_OPTIONS"]
    assert contract["prior_consumed_node_process_count"] == 3
    assert base.verify_upstream_source(contract)["passed"] is True
    assert all(row["passed"] for row in base.verify_repository_bindings(contract))


def test_sanitizer_and_wrapper_hashes_are_unchanged() -> None:
    contract = subject.load_contract()
    for row in contract["repository_files"]:
        payload = (subject.REPO_ROOT / row["path"]).read_bytes()
        assert len(payload) == row["bytes"]
        assert base.sha256_bytes(payload) == row["sha256"]
    assert contract["repository_files"][0]["sha256"] == (
        "12552925a600dc951afc30b9a738746499c7e2f4cefc9962bc05fb06780f158f"
    )
    assert contract["repository_files"][1]["sha256"] == (
        "601bb41f21916fc836603e54cb5caecec6987e75347609ff1881eef758940788"
    )


def test_minimum_environment_returns_exact_five_keys_only() -> None:
    source = {
        "SystemRoot": "synthetic-system-root",
        "WINDIR": "synthetic-windir",
        "ComSpec": "synthetic-comspec",
        "TEMP": "synthetic-temp",
        "TMP": "synthetic-tmp",
        "PATH": "forbidden-path",
        "NODE_OPTIONS": "forbidden-options",
        "CREDENTIAL": "forbidden-credential",
    }
    result = subject.minimum_windows_environment(source)
    assert tuple(result) == subject.WINDOWS_ENVIRONMENT_KEYS
    assert list(result.values()) == [source[key] for key in subject.WINDOWS_ENVIRONMENT_KEYS]
    assert set(result).isdisjoint({"PATH", "NODE_OPTIONS", "CREDENTIAL"})


def test_missing_environment_key_fails_without_naming_value() -> None:
    source = {key: "synthetic" for key in subject.WINDOWS_ENVIRONMENT_KEYS}
    del source["TEMP"]
    with pytest.raises(
        subject.MinimumEnvironmentRecoveryError,
        match="^minimum_environment_key_missing$",
    ):
        subject.minimum_windows_environment(source)


def test_environment_projection_contains_names_not_values() -> None:
    projection = subject.environment_projection()
    assert projection == {
        "keys": ["SystemRoot", "WINDIR", "ComSpec", "TEMP", "TMP"],
        "key_count": 5,
        "values_retained": False,
        "unlisted_key_count": 0,
        "path_present": False,
        "node_options_present": False,
    }


def test_process_envelope_is_content_free_and_schema_valid() -> None:
    envelope = subject.build_process_envelope(
        candidate_source=CANDIDATE,
        returncode=134,
        stdout="",
        stderr="SYNTHETIC_PATH_DETAIL_NOT_RETAINED",
    )
    serialized = base.canonical_bytes(envelope)
    assert b"SYNTHETIC_PATH_DETAIL_NOT_RETAINED" not in serialized
    assert envelope["numeric_exit_code"] == 134
    assert envelope["stdout_bytes"] == 0
    assert envelope["stderr_bytes"] == len(
        "SYNTHETIC_PATH_DETAIL_NOT_RETAINED".encode("utf-8")
    )
    assert envelope["stream_content_retained"] is False
    assert envelope["further_process_authorized"] is False


def test_exact_fifteen_result_vector_is_admitted_without_node() -> None:
    contract = subject.load_contract()
    stdout = base.expected_stdout(contract)
    results = base.validate_fixture_result(
        stdout=stdout,
        stderr="",
        returncode=0,
        contract=contract,
    )
    assert len(results) == 15
    assert [row["code"] for row in results] == contract["expected_result_codes"]
    assert all(row["detail"] is None for row in results)


def test_success_evidence_schema_keeps_abort_cause_unproved() -> None:
    contract = subject.load_contract()
    upstream = {**contract["upstream_source"], "passed": True}
    repository = [{**row, "passed": True} for row in contract["repository_files"]]
    results = base.expected_results(contract)
    envelope = subject.build_process_envelope(
        candidate_source=CANDIDATE,
        returncode=0,
        stdout=base.expected_stdout(contract),
        stderr="",
    )
    evidence = subject.build_evidence(
        contract=contract,
        candidate_source=CANDIDATE,
        upstream_binding=upstream,
        repository_bindings=repository,
        results=results,
        process_envelope=envelope,
    )
    assert evidence["claim_boundary"]["sanitizer_admitted"] is True
    assert evidence["claim_boundary"]["exact_previous_abort_cause_proven"] is False
    assert evidence["claim_boundary"]["runner_integrated"] is False
    assert evidence["zero_counters"]["native_harness_process_count"] == 0


def test_controller_uses_exact_projected_environment_and_one_shot_outputs() -> None:
    source = Path(subject.__file__).read_text(encoding="utf-8")
    assert "env=child_environment" in source
    assert "env={}," not in source
    assert "_ensure_fresh_output_paths()" in source
    assert '"successor_output_already_exists"' in source
    assert source.count("subprocess.run(") == 1
    assert "PATH" in source and "NODE_OPTIONS" in source


def test_plan_and_threat_freeze_single_process_and_no_harness() -> None:
    plan = " ".join(subject.PLAN_PATH.read_text(encoding="utf-8").split())
    threat = " ".join(subject.THREAT_PATH.read_text(encoding="utf-8").split())
    assert "one local Node process in this successor" in plan
    assert "Any other result stops without another process" in plan
    assert "No DSH/native Harness import or process" in plan
    assert "Exactly one successor process; any non-pass stops" in threat
    assert "Persist only exit, byte counts and SHA-256" in threat


def test_all_runtime_outputs_are_successor_scoped() -> None:
    assert set(subject.OUTPUT_PATHS) == {
        subject.EVIDENCE_PATH,
        subject.REPORT_PATH,
        subject.PROCESS_ENVELOPE_PATH,
        subject.SAFE_VECTOR_REJECTION_PATH,
        subject.WRAPPER_TERMINAL_PATH,
    }
    assert all(path.parent == subject.OPERATION_ROOT for path in subject.OUTPUT_PATHS)
