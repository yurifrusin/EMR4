from __future__ import annotations

import inspect
import json
from pathlib import Path

import jsonschema
import pytest

from scripts import (
    deepseek_native_harness_provider_free_integrated_runner_factory_fixture_import_path_recovery
    as subject,
)


def test_contract_and_every_schema_are_closed_and_bound() -> None:
    contract = subject.load_contract()
    assert contract["operation_id"] == subject.OPERATION_ID
    assert contract["source_equivalence"] == {
        "predecessor_projection": "package_root.parents[1]",
        "recovery_projection": "package_root.parent",
        "other_source_difference_count": 0,
    }
    assert contract["expected_import_binding"]["targets_required_before_process"] == 2
    for path in (
        subject.CONTRACT_SCHEMA_PATH,
        subject.EVIDENCE_SCHEMA_PATH,
        subject.FAILURE_SCHEMA_PATH,
    ):
        schema = json.loads(path.read_bytes())
        jsonschema.Draft202012Validator.check_schema(schema)
        assert schema["additionalProperties"] is False


def test_fixture_is_byte_equivalent_after_exactly_one_projection_normalization() -> None:
    assert subject.fixture_source_equivalent() is True
    predecessor_source = inspect.getsource(subject.predecessor.fixture_source)
    recovery_source = inspect.getsource(subject.fixture_source)
    assert predecessor_source.count("package_root.parents[1]") == 1
    assert recovery_source.count("package_root.parent") == 1
    assert "package_root.parents[1]" not in recovery_source


def _materialized_package_root(root: Path) -> Path:
    package_root = root / "node_modules" / "@deepseek-ai" / "dsh"
    package_root.mkdir(parents=True)
    for package in ("cordis", "dsh-agent"):
        target = package_root.parent / package / "lib" / "index.js"
        target.parent.mkdir(parents=True)
        target.write_text("export {};\n", encoding="utf-8")
    return package_root


def test_import_binding_requires_both_files_under_exact_scoped_parent(tmp_path: Path) -> None:
    package_root = _materialized_package_root(tmp_path)
    binding = subject.resolve_import_binding(package_root)
    assert {key: value for key, value in binding.items() if not key.endswith("_uri")} == {
        "package_scope": "node_modules/@deepseek-ai",
        "package_root_projection": "package_root.parent",
        "cordis_target_present": True,
        "agent_target_present": True,
    }
    source = subject.fixture_source(package_root, tmp_path / "runner.mjs")
    subject._validate_emitted_imports(source, binding)
    text = source.decode()
    assert binding["cordis_uri"] in text
    assert binding["agent_uri"] in text
    assert "/node_modules/cordis/lib/index.js" not in text
    assert "/node_modules/dsh-agent/lib/index.js" not in text


def test_missing_import_rejects_before_any_process_boundary(tmp_path: Path) -> None:
    package_root = _materialized_package_root(tmp_path)
    (package_root.parent / "dsh-agent" / "lib" / "index.js").unlink()
    with pytest.raises(subject.FactoryImportPathRecoveryError, match="import_target_missing"):
        subject.resolve_import_binding(package_root)


def test_provider_free_check_starts_no_node_process() -> None:
    check_source = inspect.getsource(subject.provider_free_check)
    assert "subprocess.run" not in check_source
    assert "shutil.which" not in check_source
    result = subject.provider_free_check()
    assert result["result"] == "provider_free_preflight_pass"
    assert result["source_equivalent_except_projection"] is True
    assert result["import_binding"] == {
        "package_scope": "node_modules/@deepseek-ai",
        "package_root_projection": "package_root.parent",
        "cordis_target_present": True,
        "agent_target_present": True,
    }
    assert result["node_process_count"] == 0
    assert result["native_harness_process_count"] == 0
    assert result["model_request_count"] == 0
    assert result["provider_request_count"] == 0


def test_controller_has_one_process_boundary_and_distinct_attempt_identity() -> None:
    source = Path(subject.__file__).read_text(encoding="utf-8")
    execute_source = inspect.getsource(subject.execute)
    assert source.count("subprocess.run(") == 1
    assert execute_source.count("subprocess.run(") == 1
    assert subject.ATTEMPT_ID == "factory-fixture-import-path-recovery-001"
    assert "AgentLoop(" not in execute_source
    assert "Harness(" not in execute_source
    assert "provider_request_count\": 0" in execute_source
    assert "retry_count\": 0" in execute_source
    assert "raw_error_retained\": False" in execute_source


def test_persisted_attempt_passes_exact_schema_and_cleanup_readback() -> None:
    evidence = json.loads(subject.EVIDENCE_PATH.read_bytes())
    schema = json.loads(subject.EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator(schema).validate(evidence)
    assert evidence["result"] == subject.PASS_RESULT
    assert evidence["fixture"]["structured_guard_coordinate"] == subject.EXPECTED_COORDINATE
    assert evidence["fixture"]["factory_create_agent_invocations"] == 1
    assert evidence["fixture"]["setup_invocations"] == 1
    assert evidence["fixture"]["preset_mount_reads"] == 0
    assert evidence["process_boundary"]["attempt_id"] == subject.ATTEMPT_ID
    assert evidence["process_boundary"]["node_process_count"] == 1
    assert evidence["process_boundary"]["model_request_count"] == 0
    assert evidence["process_boundary"]["provider_request_count"] == 0
    assert evidence["process_boundary"]["retry_count"] == 0
    assert evidence["cleanup"]["disposable_root_absent"] is True
    assert not subject.DISPOSABLE_ROOT.exists()
    assert not subject.FAILURE_PATH.exists()
    consumed = json.loads(subject.CONSUMED_PATH.read_bytes())
    envelope = json.loads(subject.PROCESS_ENVELOPE_PATH.read_bytes())
    assert consumed["attempt_id"] == subject.ATTEMPT_ID
    assert envelope["attempt_id"] == subject.ATTEMPT_ID
    assert envelope["exit_code"] == 0
    assert envelope["stdout_bytes"] == 641
    assert envelope["stderr_bytes"] == 0
    assert envelope["raw_stream_retained"] is False


def test_plan_preserves_exact_process_and_product_boundaries() -> None:
    plan = (
        subject.REPO_ROOT
        / "docs"
        / "deepseek-native-harness-provider-free-integrated-runner-factory-fixture-import-path-recovery-plan.md"
    ).read_text(encoding="utf-8")
    threat = (
        subject.REPO_ROOT
        / "docs"
        / "security"
        / "deepseek-native-harness-provider-free-integrated-runner-factory-fixture-import-path-recovery-threat-model-delta.md"
    ).read_text(encoding="utf-8")
    for required in (
        "package_root.parents[1]",
        "package_root.parent",
        "one separately identified provider-free Node process",
        "There is no retry, resume, fallback, second fixture",
        "No native Harness process",
        "No native Harness process, DeepSeek worker, broker, model/provider request",
        "2e34bdad732fdab32fbf778280b3d3c70d66d602",
        "docs/branding/",
    ):
        assert required in plan
    assert "Both derived imports must resolve strictly as regular files" in threat
    assert "One process is permitted" in threat
