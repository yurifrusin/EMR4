from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import pytest

from scripts import (
    raisa_provider_free_check_in_server_post_readiness_lifecycle_conformance_repair as repair,
)
from scripts import (
    raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal as base,
)


ROOT = Path(__file__).resolve().parents[1]


def _contract() -> dict[str, object]:
    return repair.validate_contract(repair._load_json(repair.CONTRACT_PATH))


def test_contract_and_git_sources_are_full_closed_and_resolved() -> None:
    contract = _contract()
    assert contract["plan_source"] == repair.PLAN_SOURCE
    assert all(
        repair.HEX40.fullmatch(row["commit"])
        for row in contract["git_sources"]
    )
    assert all(value is False for value in contract["closed_boundaries"].values())
    resolved = repair.resolve_git_bindings(contract)
    assert set(resolved) == {
        "baseline",
        "frozen_plan",
        "attempt_005_execution",
        "attempt_005_closeout",
        "complete_composition_clockwork",
        "complete_composition_candidate",
    }
    assert all(row["status"] == "passed" for row in resolved.values())
    hostile = copy.deepcopy(contract)
    hostile["git_sources"][0]["commit"] = repair.PLAN_SOURCE[:7]
    with pytest.raises(repair.LifecycleRepairError, match="contract_schema_invalid"):
        repair.validate_contract(hostile)


def test_immutable_attempt_and_baseline_blob_bindings_remain_exact() -> None:
    observed = repair.verify_immutable_bindings(_contract())
    assert len(observed) == 6
    assert observed[
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-005/rehearsal-failure-evidence.json"
    ] == "a9e6331471dadc06ddc1fc7f5f6e9510a231fa7cd3a0fc748495f8c9794bb887"
    assert observed[
        f"{repair.BASELINE_SOURCE}:scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal.py"
    ] == "62a18d9ce2a29eb417f491c8ce341416f03183375f042f8c41bcb1f4674df77c"


def test_native_installation_is_exact_rc7_and_method_shape_bound() -> None:
    projection = repair.verify_native_installation(_contract())
    assert projection["installation_id"] == repair.NATIVE_INSTALLATION_ID
    assert set(projection["versions"].values()) == {"0.1.0-rc.7"}
    assert len(projection["method_checks"]) == 10
    assert all(projection["method_checks"].values())


def test_dependency_closure_comes_from_both_manifests_and_rejects_omission() -> None:
    contract = _contract()
    reading = repair.derive_test_dependencies(contract)
    assert list(reading) == ["PF_CHECK_IN_LIFECYCLE_REPAIR"]
    assert set(contract["dependency_manifest"]["commands"][0]["test_paths"]) <= set(
        reading["PF_CHECK_IN_LIFECYCLE_REPAIR"]
    )
    hostile = copy.deepcopy(contract)
    hostile["dependency_manifest"]["commands"][0]["required_paths"].remove(
        "tests/test_raisa_provider_free_check_in_server_post_readiness_lifecycle_conformance_repair.py"
    )
    with pytest.raises(
        repair.LifecycleRepairError, match="dependency_selected_test_omitted"
    ):
        repair.derive_test_dependencies(hostile)


def test_checkpoint_renderer_and_artifact_roles_fail_closed() -> None:
    contract = _contract()
    rendered = repair.render_checkpoint(
        contract, "deterministic_ready", {"test_count": "3"}
    )
    assert rendered == "Deterministic lifecycle gate passed for 3 selected test files."
    hostile = copy.deepcopy(contract)
    hostile["checkpoint_templates"]["deterministic_ready"] = "x" * 161
    with pytest.raises(repair.LifecycleRepairError, match="checkpoint_render_not_bounded"):
        repair.render_checkpoint(hostile, "deterministic_ready", {"test_count": "3"})
    hostile = copy.deepcopy(contract)
    hostile["artifact_roles"]["repair_report"] = "invented-report.md"
    with pytest.raises(repair.LifecycleRepairError, match="artifact_role_noncanonical"):
        repair.artifact_paths(hostile)


def test_changed_path_reading_excludes_byte_identical_placeholders() -> None:
    baseline = {
        "changed.py": "a" * 64,
        "new.py": None,
        "same.py": "b" * 64,
    }
    terminal = {
        "changed.py": "c" * 64,
        "new.py": "d" * 64,
        "same.py": "b" * 64,
    }
    assert repair.derive_changed_paths(baseline, terminal) == ["changed.py", "new.py"]
    hostile = dict(terminal)
    hostile.pop("same.py")
    with pytest.raises(
        repair.LifecycleRepairError, match="changed_path_map_coverage_mismatch"
    ):
        repair.derive_changed_paths(baseline, hostile)


def test_server_projection_schema_is_exact_and_denies_raw_fields() -> None:
    schema = repair._load_json(repair.DIAGNOSTIC_SCHEMA_PATH)
    projection = repair.example_server_projection()
    assert list(Draft202012Validator(schema).iter_errors(projection)) == []
    assert set(projection) == {
        "projection_valid",
        "status",
        "running",
        "exit_code",
        "oom_killed",
        "state_error_empty",
        "restart_count",
        "attachment_process",
        "attachment_stdin",
    }
    for field in ("raw_error", "container_id", "stdout", "credential"):
        hostile = {**projection, field: "sensitive"}
        assert list(Draft202012Validator(schema).iter_errors(hostile))


def test_failure_evidence_separates_server_and_native_coordinate_families() -> None:
    projection = repair.example_server_projection()
    server = base.RehearsalFailure(
        "environment",
        "server_not_running_after_readiness",
        server_post_readiness=projection,
    )
    evidence = base._failure_evidence(server, [], {"status": "cleanup_verified"})
    assert evidence["server_post_readiness"] == projection
    other = base._failure_evidence(
        base.RehearsalFailure("native_harness", repair.INSTRUMENTATION_UNAVAILABLE),
        [],
        {"status": "not_applicable"},
    )
    assert other["server_post_readiness"] is None
    assert repair.INSTRUMENTATION_UNAVAILABLE not in json.dumps(projection)


def test_generated_runner_uses_full_create_setup_without_turn_or_provider() -> None:
    source = repair.runner_source().decode("utf-8")
    reading = repair.validate_runner_source(source.encode("utf-8"))
    assert reading["single_agents_create"] is True
    assert reading["single_preset_mount"] is True
    assert source.index("AGENTS_CREATE_ENTERED") < source.index("await agents.create(")
    assert source.index("AGENT_SETUP_ENTERED") < source.index("await presets.mount(")
    assert "PRESET_SUBSTAGE_INSTRUMENTATION_UNAVAILABLE" in source
    assert ".followup(" not in source
    assert "createUserMessage" not in source
    assert "provider-disabled" in source
    assert "DEEPSEEK_API_KEY" not in source


def test_profile_is_provider_disabled_and_has_no_execution_surface() -> None:
    payload = repair.profile_patch(Path("C:/deterministic/check-in-lifecycle"))
    reading = repair.validate_profile_patch(payload)
    assert reading["row_count"] >= 25
    text = payload.decode("utf-8")
    assert "- id: llm-deepseek\n  disabled: true" in text
    assert "- id: tool-bash\n  disabled: true" in text
    assert "- id: tool-web\n  disabled: true" in text
    assert "http://" not in text and "https://" not in text
    assert "attempt-006" not in text


def test_complete_deterministic_gate_has_zero_native_execution() -> None:
    reading = repair.deterministic_check()
    assert reading["checkpoint"].endswith("3 selected test files.")
    assert reading["runner"]["provider_disabled"] is True
    assert reading["profile"]["row_count"] >= 25
    assert set(reading["changed_paths"]["changed_paths"]) >= {
        "scripts/raisa_provider_free_check_in_server_post_readiness_lifecycle_conformance_repair.py",
        "scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal.py",
        "tests/test_raisa_provider_free_check_in_server_post_readiness_lifecycle_conformance_repair.py",
    }
    assert not repair.PROBE_TERMINAL_PATH.exists() or repair.PROBE_CONSUMED_PATH.exists()


def test_retained_native_terminal_is_schema_valid_when_present() -> None:
    if not repair.PROBE_TERMINAL_PATH.exists():
        return
    terminal = repair._load_json(repair.PROBE_TERMINAL_PATH)
    repair._validate_schema(
        terminal, repair.EVIDENCE_SCHEMA_PATH, "native_terminal_schema_invalid"
    )
    assert terminal["counts"]["automatic_retries"] == 0
    assert terminal["counts"]["provider_requests"] == 0
    assert terminal["counts"]["docker_invocations"] == 0
    assert terminal["counts"]["database_invocations"] == 0


def test_controller_has_no_attempt_006_docker_database_or_product_import() -> None:
    source = Path(repair.__file__).read_text(encoding="utf-8")
    for forbidden in (
        "attempt_006",
        "docker.exe",
        "psycopg",
        "sqlalchemy",
        "app.routers",
        "app.models",
        "DEEPSEEK_API_KEY",
    ):
        assert forbidden not in source
