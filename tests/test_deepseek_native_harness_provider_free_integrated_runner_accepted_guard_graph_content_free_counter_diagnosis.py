from __future__ import annotations

import inspect
import json
from pathlib import Path

import jsonschema
import pytest

from scripts import (
    deepseek_native_harness_provider_free_integrated_runner_accepted_guard_graph_content_free_counter_diagnosis
    as subject,
)


def test_contract_and_schemas_are_closed_and_exact() -> None:
    contract = subject.load_contract()
    assert contract["operation_id"] == subject.OPERATION_ID
    assert contract["grammar"] == {
        "candidate_count": 496,
        "target_stdout_bytes": 756,
        "target_stdout_sha256": subject.TARGET_STDOUT_SHA256,
        "expected_byte_and_hash_match_count": 1,
        "uniqueness_scope": "frozen_source_derived_finite_grammar_only",
    }
    for path in (subject.CONTRACT_SCHEMA_PATH, subject.EVIDENCE_SCHEMA_PATH):
        schema = json.loads(path.read_bytes())
        jsonschema.Draft202012Validator.check_schema(schema)
        assert schema["additionalProperties"] is False


def test_source_derivation_binds_key_order_and_exact_read_sites() -> None:
    contract = subject.load_contract()
    assert subject.validate_source_derivation(contract) == {
        "fixture_result_key_count": 25,
        "runner_preset_root_reads": 4,
        "runner_hook_installations": 3,
        "model_selection_hook_installations": 2,
        "maximum_hook_installations": 5,
        "maximum_preset_root_reads": 4,
    }
    assert subject._result_keys_from_fixture(subject.predecessor.fixture_source()) == (
        subject.RESULT_KEYS
    )


def test_complete_finite_grammar_has_one_length_and_hash_match() -> None:
    contract = subject.load_contract()
    candidates = list(subject.enumerate_candidates())
    assert len(candidates) == subject.EXPECTED_CANDIDATE_COUNT == 496
    assert len({subject.serialize_candidate(value) for value in candidates}) == 496
    reading = subject.diagnose(contract)
    assert reading["candidate_count"] == 496
    assert reading["byte_length_match_count"] == 1
    assert reading["byte_and_hash_match_count"] == 1
    assert reading["unique_observation"] == contract["expected_unique_observation"]


def test_unique_observation_exactly_reconstructs_retained_clock_reading() -> None:
    candidate = next(iter(subject.enumerate_candidates()))
    payload = subject.serialize_candidate(candidate)
    assert len(payload) == subject.TARGET_STDOUT_BYTES == 756
    assert subject.sha256_bytes(payload) == subject.TARGET_STDOUT_SHA256
    assert candidate["structured_coordinate"] == subject.SUCCESS_COORDINATE
    assert candidate["preset_root_reads"] == 4
    assert candidate["hook_installations"] == 5
    assert candidate["runner_request_count"] == 0
    assert candidate["runner_tool_result_count"] == 0


def test_serialization_fails_closed_on_key_order_and_incidental_whitespace() -> None:
    candidate = next(iter(subject.enumerate_candidates()))
    reordered = {key: candidate[key] for key in reversed(candidate)}
    with pytest.raises(subject.ContentFreeCounterDiagnosisError, match="candidate_key_order_rejected"):
        subject.serialize_candidate(reordered)
    spaced = (json.dumps(candidate) + "\n").encode()
    assert len(spaced) != subject.TARGET_STDOUT_BYTES
    assert subject.sha256_bytes(spaced) != subject.TARGET_STDOUT_SHA256


def test_failure_grammar_is_conservative_bounded_and_free_form_absent() -> None:
    candidates = list(subject.enumerate_candidates())
    failures = [value for value in candidates if value["structured_coordinate"] is None]
    assert len(failures) == 495
    assert {value["runner_failure_stage"] for value in failures} == set(subject.FAILURE_STAGES)
    assert {value["preset_root_reads"] for value in failures} == set(range(5))
    assert {value["hook_installations"] for value in failures} == set(range(5))
    assert all(value["result"] == subject.REJECTED_RESULT for value in failures)
    assert all(value["old_input_invalid_observed"] is False for value in failures)


def test_controller_has_no_process_or_external_action_boundary() -> None:
    source = Path(subject.__file__).read_text(encoding="utf-8")
    execute_source = inspect.getsource(subject.execute)
    for forbidden in (
        "import subprocess",
        "subprocess.run",
        "Popen(",
        "shutil.which",
        "AgentRegistry(",
        "Harness(",
        "requests.",
        "httpx.",
    ):
        assert forbidden not in source
        assert forbidden not in execute_source
    result = subject.provider_free_check()
    assert result["result"] == "provider_free_counter_diagnosis_check_pass"
    assert result["node_process_count"] == 0
    assert result["native_harness_process_count"] == 0
    assert result["model_request_count"] == 0
    assert result["provider_request_count"] == 0


def test_persisted_evidence_is_exact_when_diagnosis_has_run() -> None:
    if not subject.EVIDENCE_PATH.exists():
        assert not subject.REPORT_PATH.exists()
        return
    evidence = json.loads(subject.EVIDENCE_PATH.read_bytes())
    schema = json.loads(subject.EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator(schema).validate(evidence)
    assert evidence["result"] == subject.RESULT
    assert evidence["grammar"]["byte_and_hash_match_count"] == 1
    assert evidence["unique_observation"]["preset_root_reads"] == 4
    assert evidence["unique_observation"]["hook_installations"] == 5
    assert evidence["predecessor_disposition"]["reclassified"] is False
    assert evidence["predecessor_disposition"]["retry_count"] == 0
    assert all(value == 0 for value in evidence["process_boundary"].values())


def test_plan_preserves_clockwork_and_product_boundaries() -> None:
    plan = (
        subject.REPO_ROOT
        / "docs"
        / "deepseek-native-harness-provider-free-integrated-runner-accepted-guard-graph-content-free-counter-diagnosis-plan.md"
    ).read_text(encoding="utf-8")
    threat = (
        subject.REPO_ROOT
        / "docs"
        / "security"
        / "deepseek-native-harness-provider-free-integrated-runner-accepted-guard-graph-content-free-counter-diagnosis-threat-model-delta.md"
    ).read_text(encoding="utf-8")
    for required in (
        "This is not general SHA-256 inversion",
        "The original materialization attempt remains",
        "No subprocess, native Harness, DeepSeek worker/turn",
        "2e34bdad732fdab32fbf778280b3d3c70d66d602",
        "docs/branding/",
    ):
        assert required in plan
    assert "The uniqueness claim is explicitly limited to the frozen" in threat
    assert "performs no executable" in threat
