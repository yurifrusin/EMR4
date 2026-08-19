from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from scripts.deepseek_native_harness_provider_free_preterminal_observability_recovery import (
    CONTRACT_PATH,
    FAILED_EVIDENCE_PATH,
    corrected_runner_source,
    deterministic_projection,
    diagnose_failed_attempt,
    load_contract,
    scenario_matrix,
    validate_corrected_runner,
)


def test_contract_and_schema_freeze_no_native_process_recovery() -> None:
    contract = load_contract()
    schema = json.loads(CONTRACT_PATH.with_name("contract.schema.json").read_text(encoding="utf-8"))

    jsonschema.validate(contract, schema)
    assert contract["probe"] == {
        "offline_materialisation_count": 1,
        "non_harness_node_import_count": 1,
        "native_harness_process_count": 0,
        "online_fallback": False,
        "lifecycle_scripts": False,
    }
    assert len(contract["immutable_attempt"]["source_commit"]) == 40


def test_immutable_failed_attempt_is_bound_and_not_reclassified() -> None:
    diagnosis = diagnose_failed_attempt(load_contract())

    assert diagnosis["causal_classification"] == "indeterminate_preterminal_failure"
    assert diagnosis["retained_events"] == ["sentinel_activated", "stock_headless_hmr_ready"]
    assert diagnosis["guard_terminal_retained"] is False
    assert diagnosis["permitted_root_cause_claims"] == []


def test_failed_evidence_still_has_zero_prohibited_counts_and_cleanup() -> None:
    evidence = json.loads(FAILED_EVIDENCE_PATH.read_text(encoding="utf-8"))

    boundary = evidence["provider_boundary"]
    assert all(
        boundary[field] == 0
        for field in (
            "network_attempt_count",
            "agent_session_count",
            "turn_count",
            "broker_request_count",
            "model_request_count",
            "provider_request_count",
            "occupied_worker_count",
            "docker_invocation_count",
            "database_invocation_count",
        )
    )
    assert evidence["cleanup"]["process_absent"] is True
    assert evidence["cleanup"]["disposable_root_absent"] is True


def test_corrected_runner_records_bootstrap_before_dynamic_import() -> None:
    source = corrected_runner_source().decode()

    assert source.index("BOOTSTRAP_APPLY_ENTERED") < source.index(
        'await import("@deepseek-ai/dsh-scope")'
    )
    assert 'await import("./effective-tool-guard.mjs")' in source
    prefix = source.split("export const name", maxsplit=1)[0]
    assert "@deepseek-ai/" not in prefix


def test_corrected_runner_has_single_writers_and_lifecycle_calls() -> None:
    projection = validate_corrected_runner(corrected_runner_source())

    assert all(projection["checks"].values())
    assert projection["checks"]["single_activation_writer"] is True
    assert projection["checks"]["single_terminal_exclusive_writer"] is True


def test_corrected_runner_preserves_accepted_guard_vocabulary_boundary() -> None:
    source = corrected_runner_source().decode()

    assert "sanitizeEffectiveToolTerminal" in source
    assert "CUSTOM_RUNNER_FAILURE" not in source
    assert 'stage: "preterminal_activation"' in source
    assert 'stage: "pre_provider_tool_composition"' not in source


def test_scenario_matrix_partitions_every_preterminal_failure() -> None:
    rows = scenario_matrix()
    names = {row["scenario"] for row in rows}

    assert names == {
        "missing_hmr",
        "missing_app_exit",
        "missing_services",
        "module_import_rejected",
        "scope_creation_rejected",
        "guard_failure",
        "terminal_write_rejected",
        "scope_disposal_rejected",
        "success",
        "unknown_exception",
    }
    assert all(row["safe"] is True for row in rows)


def test_every_scenario_coordinate_is_closed() -> None:
    admitted = set(load_contract()["activation_coordinates"])

    assert all(
        coordinate in admitted
        for row in scenario_matrix()
        for coordinate in row["coordinates"]
    )


def test_deterministic_projection_starts_no_process() -> None:
    projection = deterministic_projection()

    assert projection["diagnosis"]["retained_duration_reliable"] is False
    assert len(projection["scenario_matrix"]) == 10
    assert projection["runner"]["sha256"]


def test_plan_and_threat_delta_keep_native_and_product_surfaces_closed() -> None:
    plan = Path(
        "docs/deepseek-native-harness-provider-free-preterminal-activation-observability-recovery-plan.md"
    ).read_text(encoding="utf-8")
    threat = Path(
        "docs/security/deepseek-native-harness-provider-free-preterminal-activation-observability-recovery-threat-model-delta.md"
    ).read_text(encoding="utf-8")

    for phrase in (
        "It may not start the native Harness CLI",
        "cannot retry, resume or reclassify",
        "No Docker/database",
        "native Harness process count, which",
    ):
        assert phrase in plan
    assert "native Harness process count must remain zero" in threat


def test_evidence_schema_requires_zero_native_recovery_shape() -> None:
    schema = json.loads(CONTRACT_PATH.with_name("evidence.schema.json").read_text(encoding="utf-8"))
    payload = {
        "schema_version": "ariadne.deepseek_native_harness_preterminal_observability_recovery_evidence.v1",
        "operation_id": "deepseek-native-harness-provider-free-preterminal-activation-observability-recovery",
        "planning_source": load_contract()["planning_source"],
        "result": "pass",
        "immutable_attempt": {},
        "diagnosis": {},
        "corrected_design": {},
        "scenario_matrix": [{} for _ in range(10)],
        "offline_probe": {},
        "provider_boundary": {},
        "cleanup": {},
    }

    jsonschema.validate(payload, schema)
