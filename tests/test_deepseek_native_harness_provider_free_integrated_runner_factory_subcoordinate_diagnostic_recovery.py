from __future__ import annotations

import json

import jsonschema
import pytest

from scripts import (
    deepseek_native_harness_provider_free_integrated_runner_factory_subcoordinate_diagnostic_recovery
    as subject,
)


def test_contract_and_schemas_are_closed_and_bound() -> None:
    contract = subject.load_contract()
    assert contract["operation_id"] == subject.OPERATION_ID
    assert contract["occupied_composition"] == {
        "runner_bytes": 14210,
        "runner_sha256": "017394e3f86a3efdf5eba0745c254a8b561615fb6ab923978b81bb5941e8e3f4",
        "guard_bytes": 4009,
        "guard_sha256": "6678ed31bdcd30a5018689b72ad509c182854bf5d63862f59b397acc8de40894",
        "runner_argument_count": 4,
        "guard_parameter_count": 3,
    }
    for path in (
        subject.CONTRACT_SCHEMA_PATH,
        subject.EVIDENCE_SCHEMA_PATH,
        subject.FAILURE_DIAGNOSIS_SCHEMA_PATH,
    ):
        schema = json.loads(path.read_bytes())
        jsonschema.Draft202012Validator.check_schema(schema)
        assert schema["additionalProperties"] is False


def test_source_diagnosis_reuses_the_existing_correction_lineage() -> None:
    diagnosis = subject.source_diagnosis(subject.load_contract())
    assert diagnosis == {
        "runner_sha256": "017394e3f86a3efdf5eba0745c254a8b561615fb6ab923978b81bb5941e8e3f4",
        "guard_sha256": "6678ed31bdcd30a5018689b72ad509c182854bf5d63862f59b397acc8de40894",
        "runner_call": subject.RUNNER_CALL,
        "guard_signature": subject.GUARD_SIGNATURE,
        "bound_preset_id_argument": "preset_service_object",
        "bound_selected_tools_argument": "emr4-bounded-worker",
        "predicted_coordinate": subject.EXPECTED_COORDINATE,
        "accepted_lineage_reused": True,
    }


def test_fixture_uses_installed_registry_and_exact_runner_without_agent_loop() -> None:
    package_root = (
        subject.DISPOSABLE_ROOT
        / "installation"
        / "node_modules"
        / "@deepseek-ai"
        / "dsh"
    )
    source = subject.fixture_source(
        package_root, subject.DISPOSABLE_ROOT / "installation" / "proof" / "integrated-runner.mjs"
    ).decode()
    assert "new AgentRegistry(ctx)" in source
    assert "await options.setup(agentCtx)" in source
    assert "AgentLoop" not in source
    assert "followup" not in source
    assert "providerRequest" not in source
    assert "broker" not in source.lower()
    assert source.count("async createAgent") == 1
    assert source.count("applyRunner(ctx") == 1


def test_consumed_fixture_path_builder_selected_the_unscoped_parent() -> None:
    source_package_root = (
        subject.package_projection.MATERIALIZATION_SOURCE_ROOT
        / "node_modules"
        / "@deepseek-ai"
        / "dsh"
    )
    selected = source_package_root.parents[1]
    corrected = source_package_root.parent
    assert selected.name == "node_modules"
    assert corrected.name == "@deepseek-ai"
    assert not (selected / "cordis" / "lib" / "index.js").exists()
    assert not (selected / "dsh-agent" / "lib" / "index.js").exists()
    assert (corrected / "cordis" / "lib" / "index.js").is_file()
    assert (corrected / "dsh-agent" / "lib" / "index.js").is_file()


def _fixture_value() -> dict:
    return {
        "schema_version": subject.FIXTURE_SCHEMA,
        "result": subject.PASS_RESULT,
        "structured_guard_coordinate": subject.EXPECTED_COORDINATE,
        "factory_create_agent_invocations": 1,
        "setup_invocations": 1,
        "setup_resolved": False,
        "runner_app_exit_code": 1,
        "runner_status": "failed",
        "runner_failure_stage": "factory",
        "runner_request_count": 0,
        "runner_tool_result_count": 0,
        "runner_turn_kind": None,
        "runner_conclusion_marked": False,
        "preset_root_reads": 4,
        "preset_mount_reads": 0,
        "agent_context_property_reads": 0,
        "live_agent_count": 0,
        "raw_error_retained": False,
        "cordis_disposed": True,
    }


def test_fixture_result_accepts_only_the_exact_closed_vector() -> None:
    assert subject.validate_fixture_result(_fixture_value()) == _fixture_value()
    for key, replacement in (
        ("structured_guard_coordinate", "UNCLASSIFIED"),
        ("preset_mount_reads", 1),
        ("runner_failure_stage", "roots"),
        ("runner_request_count", 1),
    ):
        hostile = _fixture_value()
        hostile[key] = replacement
        with pytest.raises(subject.FactoryDiagnosticError, match="fixture_result_rejected"):
            subject.validate_fixture_result(hostile)


def test_provider_free_check_starts_no_process(tmp_path, monkeypatch) -> None:
    for name in ("EVIDENCE_PATH", "CONSUMED_PATH", "PROCESS_ENVELOPE_PATH", "FAILURE_PATH"):
        monkeypatch.setattr(subject, name, tmp_path / name.lower())
    result = subject.provider_free_check()
    assert result["result"] == "provider_free_preflight_pass"
    assert result["node_process_count"] == 0
    assert result["native_harness_process_count"] == 0
    assert result["model_request_count"] == 0
    assert result["provider_request_count"] == 0
