from __future__ import annotations

import ast
import copy
import dataclasses
import hashlib
import json
import subprocess
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import raisa_provider_free_check_in_relay_free_recovery_attempt_007 as attempt
from scripts import (
    raisa_provider_free_check_in_prospective_success_redaction_and_typed_cleanup_projection_conformance_repair as repair,
)
from scripts import (
    raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal as base,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN_SOURCE = "23eb45724c39b0788c32f253229ca43e4a41288f"
DIAGNOSIS_SOURCE = "ca7970b3520b2c38e9abd6fee3462ebb743792e0"
SAFE_BOUNDARY = "live_sensitive_material_existing_hosted_or_product_database_used"
OLD_BOUNDARY = "live_secret_existing_hosted_or_product_database_used"


def _git_show(source: str, path: str) -> str:
    completed = subprocess.run(
        ["git", "show", f"{source}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
        shell=False,
    )
    return completed.stdout


def _function_dump(source: str, name: str) -> str:
    tree = ast.parse(source)
    matches = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    assert len(matches) == 1
    return ast.dump(matches[0], include_attributes=False)


def _cleanup(status: str = "cleanup_verified") -> dict[str, object]:
    return {
        "role_absent_before_teardown": True,
        "attachments_absent": True,
        "sidecars_absent": True,
        "server_absent": True,
        "network_absent": True,
        "matching_owned_resources": 0,
        "status": status,
    }


def _bind_terminal_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(base, "FAILURE_PATH", tmp_path / "failure.json")
    monkeypatch.setattr(base, "EVIDENCE_PATH", tmp_path / "evidence.json")
    monkeypatch.setattr(base, "ATTESTATION_PATH", tmp_path / "attestation.json")


def test_static_admission_proves_complete_projection_before_occupation() -> None:
    result = base.static_check()
    assert result["status"] == "passed"
    assert result["prospective_projection"] == {
        "path_count": 67,
        "runtime_path_count": 67,
        "redaction_status": "passed",
        "schema_status": "passed",
        "hostile_attempted": 66,
        "hostile_rejected": 66,
    }
    source = Path(base.__file__).read_text(encoding="utf-8")
    run = base._ast_function(ast.parse(source), "run_rehearsal")
    calls = [
        node.func.id
        for node in ast.walk(run)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    ]
    assert calls.index("static_check") < calls.index("_docker_executable")


def test_safe_boundary_preserves_all_ten_false_defaults_and_redactor_ast() -> None:
    contract = json.loads(base.CONTRACT_PATH.read_text(encoding="utf-8"))
    assert set(contract["closed_boundaries"]) == {
        SAFE_BOUNDARY,
        "host_listener_forwarder_relay_exec_bridge_process_or_queue_used",
        "ordinary_practice_enabled",
        "feature_flag_or_allowlist_changed",
        "ordinary_admission_released",
        "product_relation_record_or_configuration_changed",
        "api_openapi_graphql_async_or_client_changed",
        "provider_or_external_network_used",
        "production_runtime_deployment_release_or_pages",
        "protected_evidence_or_ref_movement",
    }
    assert OLD_BOUNDARY not in contract["closed_boundaries"]
    assert len(contract["closed_boundaries"]) == 10
    assert all(value is False for value in contract["closed_boundaries"].values())
    current = Path(base.__file__).read_text(encoding="utf-8")
    historical = _git_show(
        DIAGNOSIS_SOURCE,
        "scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_"
        "relay_free_rollback_unknown_commit_recovery_rehearsal.py",
    )
    assert _function_dump(current, "_assert_redacted") == _function_dump(
        historical, "_assert_redacted"
    )
    current_tree = ast.parse(current)
    historical_tree = ast.parse(historical)
    current_forbidden = next(
        node
        for node in current_tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "FORBIDDEN_EVIDENCE_KEYS"
            for target in node.targets
        )
    )
    historical_forbidden = next(
        node
        for node in historical_tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "FORBIDDEN_EVIDENCE_KEYS"
            for target in node.targets
        )
    )
    assert ast.dump(current_forbidden.value, include_attributes=False) == ast.dump(
        historical_forbidden.value, include_attributes=False
    )


def test_projection_parity_and_hostile_fields_are_fail_closed() -> None:
    contract = base.validate_contract(json.loads(base.CONTRACT_PATH.read_text()))
    source = Path(base.__file__).read_text(encoding="utf-8")
    projection = base._prospective_success_evidence_projection(
        contract, subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    )
    assert base._projection_key_paths(projection) == base._runtime_success_key_paths(
        source, contract
    )
    assert len(base._projection_key_paths(projection)) == 67
    assert base.hostile_prospective_projection_keys_rejected(projection) == (66, 66)
    for safe in ("secretion", "credentialsafe", "patiently", "network_identity_safe"):
        candidate = copy.deepcopy(projection)
        candidate[safe] = False
        base._assert_redacted(candidate, forbidden_values=())


def test_postfinalization_terminal_type_is_frozen_and_exact() -> None:
    assert dataclasses.is_dataclass(base.PostFinalizationTerminal)
    assert base.PostFinalizationTerminal.__dataclass_params__.frozen is True
    assert [field.name for field in dataclasses.fields(base.PostFinalizationTerminal)] == [
        "evidence",
        "attestation",
    ]


def test_late_redaction_failure_preserves_finalized_cleanup(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _bind_terminal_paths(monkeypatch, tmp_path)
    contract = base.validate_contract(json.loads(base.CONTRACT_PATH.read_text()))
    candidate = base._prospective_success_evidence_projection(contract, PLAN_SOURCE)
    candidate["secret_material"] = False
    cleanup = _cleanup()
    terminal = base._finalize_post_cleanup_terminal(
        error=None,
        result=candidate,
        attestation={"bounded": True},
        lifecycle=["cleanup_finalized"],
        cleanup=cleanup,
        elapsed_seconds=1.25,
        forbidden_values=(),
    )
    assert isinstance(terminal, base.PostFinalizationTerminal)
    assert terminal.attestation is None
    assert terminal.evidence["stage"] == "redaction"
    assert terminal.evidence["code"] == "forbidden_field"
    assert terminal.evidence["cleanup"] == cleanup
    assert base.FAILURE_PATH.exists()
    assert not base.EVIDENCE_PATH.exists()
    assert not base.ATTESTATION_PATH.exists()


def test_late_schema_failure_preserves_finalized_cleanup(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _bind_terminal_paths(monkeypatch, tmp_path)
    contract = base.validate_contract(json.loads(base.CONTRACT_PATH.read_text()))
    candidate = base._prospective_success_evidence_projection(contract, PLAN_SOURCE)
    candidate["source_binding_count"] = 14
    cleanup = _cleanup()
    terminal = base._finalize_post_cleanup_terminal(
        error=None,
        result=candidate,
        attestation={"bounded": True},
        lifecycle=["cleanup_finalized"],
        cleanup=cleanup,
        elapsed_seconds=1.25,
        forbidden_values=(),
    )
    assert terminal.attestation is None
    assert terminal.evidence["stage"] == "evidence"
    assert terminal.evidence["code"] == "parent_schema_invalid"
    assert terminal.evidence["cleanup"] == cleanup


def test_failure_evidence_redaction_fallback_remains_typed_and_keeps_cleanup(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _bind_terminal_paths(monkeypatch, tmp_path)
    cleanup = _cleanup("cleanup_incomplete")
    terminal = base._finalize_post_cleanup_terminal(
        error=base.RehearsalFailure("execution", "bounded_failure"),
        result=None,
        attestation=None,
        lifecycle=["contains-sensitive-token"],
        cleanup=cleanup,
        elapsed_seconds=2.0,
        forbidden_values=("sensitive-token",),
    )
    assert terminal.attestation is None
    assert terminal.evidence["stage"] == "redaction"
    assert terminal.evidence["code"] == "failure_evidence_rejected"
    assert terminal.evidence["cleanup"] == cleanup
    assert "sensitive-token" not in base.FAILURE_PATH.read_text(encoding="utf-8")


def test_valid_candidate_writes_only_typed_success(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _bind_terminal_paths(monkeypatch, tmp_path)
    contract = base.validate_contract(json.loads(base.CONTRACT_PATH.read_text()))
    candidate = base._prospective_success_evidence_projection(contract, PLAN_SOURCE)
    attestation = {"bounded": True}
    cleanup = _cleanup()
    terminal = base._finalize_post_cleanup_terminal(
        error=None,
        result=candidate,
        attestation=attestation,
        lifecycle=["cleanup_finalized"],
        cleanup=cleanup,
        elapsed_seconds=1.25,
        forbidden_values=(),
    )
    assert terminal.attestation == attestation
    assert terminal.evidence["result"] == base.PASS_RESULT
    assert terminal.evidence["cleanup"] == cleanup
    assert base.EVIDENCE_PATH.exists()
    assert base.ATTESTATION_PATH.exists()
    assert not base.FAILURE_PATH.exists()


def test_attempt_wrapper_projects_base_owned_finalized_cleanup(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _bind_terminal_paths(monkeypatch, tmp_path)
    contract = base.validate_contract(json.loads(base.CONTRACT_PATH.read_text()))
    candidate = base._prospective_success_evidence_projection(contract, PLAN_SOURCE)
    candidate["secret_material"] = False
    terminal = base._finalize_post_cleanup_terminal(
        error=None,
        result=candidate,
        attestation={"bounded": True},
        lifecycle=["cleanup_finalized"],
        cleanup=_cleanup(),
        elapsed_seconds=1.25,
        forbidden_values=(),
    )
    terminal_path = base.FAILURE_PATH
    monkeypatch.undo()
    envelope = attempt._build_execution_envelope(
        source_head=PLAN_SOURCE,
        evidence=terminal.evidence,
        terminal_path=terminal_path,
        terminal_kind="rehearsal_failure_evidence",
    )
    assert envelope["cleanup_status"] == "cleanup_verified"
    assert envelope["base_result"] == "failed_closed"
    assert envelope["result"] == "failed_closed"


def test_attempt_007_terminal_artifacts_remain_immutable() -> None:
    bindings = {
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-007/rehearsal-failure-evidence.json": "86e5e1342eb54e062e35d73390ebceb141d097d03e180e4fe3c0ed64b465f422",
        "orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-007/attempt-007-execution-envelope.json": "3338c58054dea96b3845827dacfe184889ee328e5a4463966464b560d0a2c2c5",
    }
    for relative, expected in bindings.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected


def test_repair_contract_and_evidence_builder_are_closed() -> None:
    contract = json.loads(repair.CONTRACT_PATH.read_text(encoding="utf-8"))
    contract_schema = json.loads(
        repair.CONTRACT_SCHEMA_PATH.read_text(encoding="utf-8")
    )
    assert not list(Draft202012Validator(contract_schema).iter_errors(contract))
    assert len(contract["closed_boundaries"]) == 10
    assert all(value is False for value in contract["closed_boundaries"].values())
    evidence = repair.build_evidence()
    evidence_schema = json.loads(
        repair.EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8")
    )
    assert not list(Draft202012Validator(evidence_schema).iter_errors(evidence))
    assert evidence["result"] == contract["result"]
    assert evidence["efficacy"] == {
        "diagnosed_forbidden_field_occupied_escape_before": 1,
        "diagnosed_forbidden_field_occupied_escape_after": 0,
        "diagnosed_cleanup_collapse_before": 1,
        "diagnosed_cleanup_collapse_after": 0,
        "occupied_runs_used_for_repair": 0,
    }


def test_direct_cli_check_is_provider_free_and_passes() -> None:
    completed = subprocess.run(
        ["python", str(Path(repair.__file__)), "--check"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
        shell=False,
    )
    assert completed.returncode == 0, completed.stderr
    reading = json.loads(completed.stdout)
    assert reading == {
        "result": "raisa_provider_free_check_in_prospective_success_redaction_and_typed_cleanup_projection_conformance_repair_pass",
        "projection_paths": 67,
        "late_failure_escapes": 0,
        "occupied_runs": 0,
    }
