from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema

from scripts import (
    deepseek_native_harness_provider_free_edit_coordinate_integrated_runner_stock_headless_boot_rehearsal as subject,
)


def _paths() -> tuple[Path, Path, Path, Path]:
    root = Path("C:/typed/integrated-runner-stock-headless-boot")
    profile = root / "home" / "profiles" / "headless"
    return (
        profile,
        root / "readiness.jsonl",
        root / "integrated-edit-controls-loaded.json",
        root / "runner-terminal.json",
    )


def _runner_terminal() -> dict[str, object]:
    return {
        "schema_version": "ariadne.native_harness_tool_result_conclusion_runner_terminal.v1",
        "status": "failed",
        "failure_stage": "roots",
        "session_id_sha256": None,
        "provider": "deepseek-official",
        "model": "deepseek-v4-flash",
        "reasoning_effort": "high",
        "allowed_tool_names": ["edit", "glob", "read"],
        "target_path_sha256": "sha256:" + "0" * 64,
        "tool_lifecycle": {
            "input_result_kind": "unobserved",
            "post_execute_decision_kind": "unobserved",
            "conclusion_request_stage": "not_requested",
            "authoritative_final_result_kind": "unobserved",
            "coordinate": None,
        },
        "edit_argument_result": {
            "pre_dispatch_decision": "not_observed",
            "coordinate": None,
        },
        "request_count": 0,
        "tool_names": [],
        "tool_result_count": 0,
        "turn_kind": None,
    }


def test_contract_and_schemas_are_closed_and_valid() -> None:
    contract = json.loads(subject.CONTRACT_PATH.read_bytes())
    contract_schema = json.loads(subject.CONTRACT_SCHEMA_PATH.read_bytes())
    evidence_schema = json.loads(subject.EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(contract_schema)
    jsonschema.Draft202012Validator.check_schema(evidence_schema)
    jsonschema.Draft202012Validator(contract_schema).validate(contract)
    assert contract_schema["additionalProperties"] is False
    assert evidence_schema["additionalProperties"] is False


def test_one_process_latch_has_no_retry_resume_or_fallback() -> None:
    contract = json.loads(subject.CONTRACT_PATH.read_bytes())
    assert contract["execution_attempt"] == {
        "attempt_id": subject.ATTEMPT_ID,
        "native_process_count": 1,
        "automatic_retry": False,
        "manual_retry": False,
        "resume": False,
    }
    source = Path(subject.__file__).read_text(encoding="utf-8")
    assert source.count("subprocess.Popen(") == 1
    assert "stdout=subprocess.DEVNULL" in source
    assert "stderr=subprocess.DEVNULL" in source


def test_exact_integrated_runner_and_adapter_bindings() -> None:
    contract = json.loads(subject.CONTRACT_PATH.read_bytes())
    payloads = subject.source_payloads(contract)
    assert len(payloads["integrated_runner"]) == 14077
    assert subject.sha256_bytes(payloads["integrated_runner"]) == (
        "115cbf245ca6a2e218b2f2989093cea651bf4fe0aed796204dce1f83826e6be0"
    )
    projection = subject.validate_adapter_source(payloads["adapter"])
    assert projection["bytes"] < 2000


def test_adapter_only_records_export_load_then_delegates() -> None:
    source = subject.ADAPTER_PATH.read_text(encoding="utf-8")
    load = source.index("writeControlLoad(config.controlLoadPath)")
    delegate = source.index("return integratedRunner.apply(ctx, config)")
    assert load < delegate
    assert "agents.create" not in source
    assert "fetch(" not in source
    assert "retry" not in source.lower()
    assert "fallback" not in source.lower()


def test_patch_adds_one_deliberately_single_root_service_and_probe() -> None:
    profile, readiness, control_load, terminal = _paths()
    initial, changed = subject.build_patch_pair(
        profile_dir=profile,
        readiness_path=readiness,
        control_load_path=control_load,
        terminal_path=terminal,
    )
    subject.validate_patch_pair(
        initial,
        changed,
        control_load_path=control_load,
        terminal_path=terminal,
    )
    _, initial_inserted = subject._patch_rows(initial)
    _, changed_inserted = subject._patch_rows(changed)
    assert len(initial_inserted) == 1
    assert changed_inserted[1]["config"]["includeUserRoot"] is False
    assert changed_inserted[2]["inject"] == [
        "hmr",
        "headlessStartup",
        "agents",
        "sessions",
        "agentPresets",
    ]


def test_control_load_reader_accepts_only_exact_coordinate(tmp_path: Path) -> None:
    path = tmp_path / "control.json"
    exact = {
        "schema_version": "ariadne.native_harness_integrated_edit_controls_loaded.v1",
        "coordinate": "integrated_edit_controls_loaded",
        "exports": subject.EXPECTED_EXPORTS,
        "apply_loaded": True,
        "preflight_edit_arguments_loaded": True,
        "classify_edit_argument_result_loaded": True,
    }
    path.write_text(json.dumps(exact) + "\n", encoding="utf-8")
    assert subject.read_control_load(path) == exact
    exact["coordinate"] = "controls_loaded"
    path.write_text(json.dumps(exact) + "\n", encoding="utf-8")
    assert subject.read_control_load(path) is None


def test_runner_terminal_reader_accepts_only_roots_stage_zero_request(tmp_path: Path) -> None:
    path = tmp_path / "terminal.json"
    exact = _runner_terminal()
    path.write_text(json.dumps(exact) + "\n", encoding="utf-8")
    assert subject.read_runner_terminal(path) == exact
    for field, value in (
        ("failure_stage", "factory"),
        ("request_count", 1),
        ("tool_names", ["edit"]),
        ("turn_kind", "error"),
    ):
        variant = copy.deepcopy(exact)
        variant[field] = value
        path.write_text(json.dumps(variant) + "\n", encoding="utf-8")
        assert subject.read_runner_terminal(path) is None


def test_success_classifier_requires_every_containment_reading() -> None:
    exact = {
        "process_started": True,
        "readiness_events": subject.READINESS_EVENTS,
        "hmr_mutation_count": 1,
        "control_load": {"coordinate": "integrated_edit_controls_loaded"},
        "terminal": _runner_terminal(),
        "network_attempt_count": 0,
        "network_ledger_valid": True,
        "source_copies_equal": True,
        "process_absent": True,
        "root_absent": True,
        "seed_unchanged": True,
        "canonical_runner_unchanged": True,
    }
    assert subject._failure_coordinate(**exact) is None
    for field, value in (
        ("readiness_events", ["sentinel_activated"]),
        ("hmr_mutation_count", 0),
        ("control_load", None),
        ("terminal", None),
        ("network_attempt_count", 1),
        ("source_copies_equal", False),
        ("process_absent", False),
        ("root_absent", False),
        ("seed_unchanged", False),
        ("canonical_runner_unchanged", False),
    ):
        variant = dict(exact)
        variant[field] = value
        assert subject._failure_coordinate(**variant) is not None


def test_required_zero_count_roster_is_exact() -> None:
    contract = json.loads(subject.CONTRACT_PATH.read_bytes())
    assert contract["required_zero_counts"] == [
        "network_attempts",
        "agent_create",
        "sessions",
        "turns",
        "tool_calls",
        "tool_results",
        "broker_processes",
        "broker_requests",
        "workers",
        "model_requests",
        "provider_requests",
        "database_invocations",
        "docker_invocations",
        "retries",
        "resumes",
        "fallbacks",
    ]


def test_canonical_evidence_if_present_is_a_clean_hold() -> None:
    if not subject.EVIDENCE_PATH.exists():
        return
    evidence = json.loads(subject.EVIDENCE_PATH.read_bytes())
    schema = json.loads(subject.EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator(schema).validate(evidence)
    assert evidence["result"] == "pass"
    assert evidence["coordinate"] == subject.EXPECTED_COORDINATE
    assert evidence["failure_classification"] is None
    assert evidence["runner_terminal"]["failure_stage"] == "roots"
    assert all(
        value == 0
        for key, value in evidence["provider_boundary"].items()
        if key.endswith("_count") and key != "credential_environment_names_removed_count"
    )


def test_contract_authorizes_no_product_or_occupied_surface() -> None:
    contract = json.loads(subject.CONTRACT_PATH.read_bytes())
    text = json.dumps(contract, sort_keys=True)
    assert "product_data" not in text
    assert "patient_data" not in text
    assert "clinical_data" not in text
    assert contract["launch"]["online_package_fallback"] is False
