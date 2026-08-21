from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from scripts import (
    deepseek_native_harness_provider_free_preset_mount_safe_subcoordinate_sanitizer_rehearsal as subject,
)


def test_contract_and_evidence_schemas_are_closed() -> None:
    contract = subject.load_contract()
    contract_schema = json.loads(subject.CONTRACT_SCHEMA_PATH.read_text(encoding="utf-8"))
    evidence_schema = json.loads(subject.EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(contract_schema).validate(contract)
    assert contract_schema["additionalProperties"] is False
    assert evidence_schema["additionalProperties"] is False
    assert contract["closed_codes"][-1] == "PRESET_MOUNT_UNCLASSIFIED"
    assert len(contract["expected_result_codes"]) == 15


def test_exact_accepted_upstream_source_and_nine_anchors_pass() -> None:
    contract = subject.load_contract()
    binding = subject.verify_upstream_source(contract)
    assert binding == {**contract["upstream_source"], "passed": True}
    assert contract["seed_relative_path"] == (
        "emr4-native-harness/dsh-0.1.0-rc.7-package-seed/"
        "node_modules/@deepseek-ai"
    )
    assert len(contract["upstream_source_anchors"]) == 9


def test_repository_bindings_and_static_effect_boundary_pass() -> None:
    contract = subject.load_contract()
    bindings = subject.verify_repository_bindings(contract)
    assert len(bindings) == 2
    assert all(binding["passed"] for binding in bindings)
    sanitizer = subject._safe_repo_path(contract["repository_files"][0]["path"])
    fixture = subject._safe_repo_path(contract["repository_files"][1]["path"])
    assert sanitizer.suffix == ".mjs"
    assert fixture.suffix == ".mjs"


def test_expected_stdout_is_exact_closed_three_field_json() -> None:
    contract = subject.load_contract()
    stdout = subject.expected_stdout(contract)
    results = subject.validate_fixture_result(
        stdout=stdout,
        stderr="",
        returncode=0,
        contract=contract,
    )
    assert len(results) == 15
    assert all(list(row) == ["stage", "code", "detail"] for row in results)
    assert all(row["stage"] == "preset_mount" for row in results)
    assert all(row["detail"] is None for row in results)
    assert subject.FORBIDDEN_FIXTURE_DETAIL not in stdout


@pytest.mark.parametrize(
    ("stdout_mutation", "stderr", "returncode", "expected"),
    [
        (lambda value: value, "safe-stderr", 0, "node_fixture_stderr_nonempty"),
        (lambda value: value, "", 2, "node_fixture_exit_nonzero"),
        (
            lambda value: value.replace(
                '"detail":null',
                f'"detail":"{subject.FORBIDDEN_FIXTURE_DETAIL}"',
                1,
            ),
            "",
            0,
            "node_fixture_detail_leak",
        ),
    ],
)
def test_fixture_admission_rejects_any_nonexact_result(
    stdout_mutation, stderr: str, returncode: int, expected: str
) -> None:
    contract = subject.load_contract()
    with pytest.raises(subject.SanitizerRehearsalError, match=f"^{expected}$"):
        subject.validate_fixture_result(
            stdout=stdout_mutation(subject.expected_stdout(contract)),
            stderr=stderr,
            returncode=returncode,
            contract=contract,
        )


def test_safe_closed_vector_mismatch_remains_observable_without_detail() -> None:
    contract = subject.load_contract()
    value = subject.expected_results(contract)
    value[0] = {
        "stage": "preset_mount",
        "code": "PRESET_MOUNT_UNCLASSIFIED",
        "detail": None,
    }
    stdout = json.dumps(value, separators=(",", ":")) + "\n"
    with pytest.raises(subject.SafeVectorMismatch) as raised:
        subject.validate_fixture_result(
            stdout=stdout,
            stderr="",
            returncode=0,
            contract=contract,
        )
    assert raised.value.first_mismatch_index == 0
    assert raised.value.observed_codes == [row["code"] for row in value]


def test_byte_only_mismatch_uses_safe_nonindex_sentinel() -> None:
    contract = subject.load_contract()
    with pytest.raises(subject.SafeVectorMismatch) as raised:
        subject.validate_fixture_result(
            stdout=subject.expected_stdout(contract) + " ",
            stderr="",
            returncode=0,
            contract=contract,
        )
    assert raised.value.first_mismatch_index == -1


def test_synthetic_evidence_has_one_node_process_and_zero_runtime_effects() -> None:
    contract = subject.load_contract()
    upstream = subject.verify_upstream_source(contract)
    repository = subject.verify_repository_bindings(contract)
    evidence = subject.build_evidence(
        contract=contract,
        candidate_source="a" * 40,
        upstream_binding=upstream,
        repository_bindings=repository,
        results=subject.expected_results(contract),
    )
    assert evidence["fixture"]["node_process_count"] == 1
    assert evidence["fixture"]["cumulative_node_process_count"] == 2
    assert evidence["fixture"]["native_harness_import_count"] == 0
    assert set(evidence["zero_counters"].values()) == {0}
    assert evidence["claim_boundary"] == {
        "safe_reduction_only": True,
        "raw_runtime_detail_retained": False,
        "runner_integrated": False,
        "repair_selected": False,
        "retry_authorized": False,
        "worker_launch_authorized": False,
        "occupied_model_launch_authorized": False,
    }


def test_rehearsal_source_has_one_node_launch_and_check_is_nonexecuting() -> None:
    source = Path(subject.__file__).read_text(encoding="utf-8")
    fixture = subject._safe_repo_path(
        subject.load_contract()["repository_files"][1]["path"]
    ).read_text(encoding="utf-8")
    run_body = source.split("def run_fixture_once", 1)[1].split("def _git", 1)[0]
    check_body = source.split("def check()", 1)[1].split("def parse_args", 1)[0]
    assert run_body.count("subprocess.run(") == 1
    assert "run_fixture_once(" not in check_body
    assert "expectedCodes" not in fixture
    assert "process.exitCode" not in fixture
    assert "write_safe_vector_rejection(" in source
    assert "--execute" in source
    assert "--check" in source


def test_plan_and_threat_preserve_no_harness_no_detail_boundary() -> None:
    plan = subject.PLAN_PATH.read_text(encoding="utf-8")
    threat = subject.THREAT_PATH.read_text(encoding="utf-8")
    normalized_plan = " ".join(plan.split())
    assert "without starting the DeepSeek Harness" in normalized_plan
    assert "No native Harness process" in normalized_plan
    assert "null detail" in normalized_plan
    assert "Path-bearing exception text escapes" in threat
    assert "Runner integration and any native attempt remain separately closed" in threat
