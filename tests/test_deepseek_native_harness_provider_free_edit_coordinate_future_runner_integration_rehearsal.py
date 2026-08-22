from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

from orchestration_harness import native_edit_argument_result_coordinate as coordinate
from orchestration_harness.governance_clockwork_tick import validate_tick_intent
from orchestration_harness.governance_live_adoption import (
    validate_contract as validate_governance_contract,
)
from scripts import (
    deepseek_native_harness_provider_free_edit_coordinate_future_runner_integration_rehearsal
    as integration,
)


ROOT = Path(__file__).resolve().parents[1]
CLOSEOUT_INTENT_PATH = integration.TOPIC / "closeout" / "closeout-intent.json"
GOVERNANCE_CONTRACT_PATH = ROOT / (
    "orchestration/continuity/ariadne-provider-free-clockwork-live-canonical-"
    "adoption-retirement/contract.json"
)
BATON_COMPACTION_MANIFEST_PATH = (
    ROOT / "docs/handover-ledgers/current-baton-acceptance-index.manifest.json"
)
REGISTER_REVISION_PATH = ROOT / "docs/ariadne-agent-error-correction-register-revision-619.md"


def test_contract_and_schemas_are_closed_canonical_and_valid() -> None:
    contract = integration.validate_contract()
    assert integration.CONTRACT_PATH.read_bytes() == integration.canonical_bytes(contract)
    assert contract["coordinates"] == list(coordinate.COORDINATES)
    assert [row["variant_id"] for row in contract["variants"]] == list(
        integration.VARIANT_IDS
    )
    assert sum(row["tool_execution_expected"] for row in contract["variants"]) == 6
    for path in (
        integration.CONTRACT_SCHEMA_PATH,
        integration.EVIDENCE_SCHEMA_PATH,
        integration.FAILURE_SCHEMA_PATH,
    ):
        jsonschema.Draft202012Validator.check_schema(json.loads(path.read_bytes()))


def test_closeout_intent_is_typed_indexed_and_binds_register_revision() -> None:
    governance = validate_governance_contract(
        json.loads(GOVERNANCE_CONTRACT_PATH.read_bytes())
    )
    intent = validate_tick_intent(json.loads(CLOSEOUT_INTENT_PATH.read_bytes()), governance)
    label = intent["baton_acceptance"]["label"]
    manifest = json.loads(BATON_COMPACTION_MANIFEST_PATH.read_bytes())
    assert label == "Current DeepSeek native Harness acceptance"
    assert label in manifest["active_labels"]
    register_path = REGISTER_REVISION_PATH.relative_to(ROOT).as_posix()
    assert intent["baton_acceptance"]["paths"].count(register_path) == 1
    assert len(intent["agent_error_observations"]) == 1
    marker = REGISTER_REVISION_PATH.read_text(encoding="utf-8")
    assert "revision: 619" in marker
    assert "incident_count: 964" in marker
    assert "new_incident_ids: AER-0964" in marker


def test_preflight_binds_inputs_attempts_packages_and_derivation() -> None:
    value = integration.provider_free_check()
    assert value["status"] == "passed"
    assert value["source_checks"] and all(value["source_checks"].values())
    assert value["derived_bytes"] == integration.DERIVED_RUNNER_PATH.read_bytes()
    assert set(value["input_bindings"]["consumed_attempt_bindings"]) == {
        "attempt_001_preparation",
        "attempt_001_rejection",
        "attempt_002_terminal",
        "attempt_002_consumed",
    }
    assert set(value["input_bindings"]["packages"]) == {
        "dsh_tools",
        "dsh_tool_fs",
        "dsh_fs",
        "dsh_fs_local",
        "third_party_source_text_retained",
    }


def test_derived_runner_integrates_typed_preflight_and_result_classifier() -> None:
    contract = integration.validate_contract()
    base = integration._resolve_owned(
        contract["accepted_inputs"]["future_runner"]["path"]
    ).read_bytes()
    derived = integration.derive_runner(base)
    checks = integration.validate_derived_source(derived)
    assert all(checks.values())
    source = derived.decode("utf-8")
    assert source.count("export function preflightEditArguments(args)") == 1
    assert source.count("export function classifyEditArgumentResult(observation)") == 1
    assert source.count('reason: "EDIT_ARGUMENT_CONSTRAINT"') == 1
    assert source.count("edit_argument_result:") == 2
    assert "error.message" not in source
    assert "api.deepseek" not in source.lower()


def test_real_edit_replay_denies_three_before_dispatch_and_executes_six(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "deepseek-edit-coordinate-runner-integration-001"
    monkeypatch.setattr(integration, "DISPOSABLE_PARENT", tmp_path)
    monkeypatch.setattr(integration, "DISPOSABLE_ROOT", root)
    preflight = integration.provider_free_check()
    rows, fixture = integration.run_node_fixture(
        integration.validate_contract(), preflight["packages_root"]
    )
    assert [row["variant_id"] for row in rows] == list(integration.VARIANT_IDS)
    assert {row["coordinate"] for row in rows} == set(coordinate.COORDINATES)
    assert sum(row["tool_executed"] for row in rows) == 6
    assert sum(not row["tool_executed"] for row in rows) == 3
    assert fixture["real_edit_tool_execution_count"] == 6
    assert fixture["pre_dispatch_denial_count"] == 3
    assert fixture["hostile_rejection_count"] == 5
    assert fixture["synthetic_edit_registration_count"] == 0
    assert fixture["cordis_disposed"] is True
    assert fixture["disposable_root_absent"] is True
    assert not root.exists()


def test_persisted_evidence_is_schema_valid_provider_free_and_state_exact() -> None:
    evidence = json.loads(integration.EVIDENCE_PATH.read_bytes())
    schema = json.loads(integration.EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator(schema).validate(evidence)
    assert integration.EVIDENCE_PATH.read_bytes() == integration.canonical_bytes(evidence)
    assert evidence["process_counts"] == integration.validate_contract()[
        "process_limits"
    ]
    assert evidence["derived_runner"]["syntax_check_passed"] is True
    assert evidence["derived_runner"]["import_check_passed"] is True
    assert evidence["fixture"]["real_edit_tool_execution_count"] == 6
    assert evidence["fixture"]["pre_dispatch_denial_count"] == 3
    assert evidence["cleanup"]["disposable_root_absent"] is True
    assert all(row["python_coordinate_agreement"] for row in evidence["variants"])
    for row in evidence["variants"]:
        if row["result_kind"] == "success":
            assert row["target_changed"] is True
            assert row["before"] != row["after"]
        else:
            assert row["target_changed"] is False
            assert row["before"] == row["after"]
    forbidden = {"arguments", "content", "value", "message", "stack", "environment"}
    assert not any(forbidden & set(row) for row in evidence["variants"])


def test_mutated_contract_and_runner_fail_closed(tmp_path: Path) -> None:
    contract = copy.deepcopy(integration.validate_contract())
    contract["variants"][0]["pre_dispatch_decision"] = "deny_blank_file_path"
    path = tmp_path / "contract.json"
    path.write_bytes(integration.canonical_bytes(contract))
    with pytest.raises(
        integration.EditCoordinateIntegrationError, match="contract_rejected"
    ):
        integration.validate_contract(path)

    base = integration._resolve_owned(
        integration.validate_contract()["accepted_inputs"]["future_runner"]["path"]
    ).read_bytes()
    with pytest.raises(
        integration.EditCoordinateIntegrationError,
        match="runner_derivation_rejected",
    ):
        integration.derive_runner(base.replace(b"export function apply", b"function apply"))


def test_failure_terminal_has_closed_coordinate_and_no_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    failure = tmp_path / "failure.json"
    root = tmp_path / "deepseek-edit-coordinate-runner-integration-001"
    monkeypatch.setattr(integration, "FAILURE_PATH", failure)
    monkeypatch.setattr(integration, "DISPOSABLE_ROOT", root)
    value = integration.write_failure_terminal("free_form_failure")
    assert value["failure_coordinate"] == "unexpected_provider_free_failure"
    assert value["worker_model_provider_request_count"] == 0
    assert value["retry_count"] == 0
    assert value["resume_count"] == 0
    assert value["fallback_count"] == 0
    jsonschema.Draft202012Validator(
        json.loads(integration.FAILURE_SCHEMA_PATH.read_bytes())
    ).validate(json.loads(failure.read_bytes()))
