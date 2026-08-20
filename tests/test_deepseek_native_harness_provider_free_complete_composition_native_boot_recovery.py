from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
import yaml

import scripts.deepseek_native_harness_provider_free_preterminal_observable_composition_recovery_boot as base
from scripts.deepseek_native_harness_provider_free_complete_composition_native_boot_recovery import (
    ATTEMPT_ID,
    CONTRACT_PATH,
    EVIDENCE_PATH,
    REPORT_PATH,
    build_patch_pair,
    configured_base,
    deterministic_check,
    load_contract,
    validate_patch_pair,
    validate_predecessors,
)
from scripts.deepseek_native_harness_provider_free_effective_tool_composition_native_boot_proof import (
    DISPOSABLE_PARENT,
)
from scripts.deepseek_native_harness_provider_free_emr4_bounded_worker_preset_materialisation_recovery import (
    PRESET_BYTES,
    PRESET_RELATIVE_PATH,
)
from scripts.deepseek_native_harness_provider_free_required_service_injection_recovery import (
    REQUIRED_SERVICES,
    future_runner_source,
)


def test_contract_freezes_one_nonretryable_process_and_exact_services() -> None:
    contract = load_contract()

    assert contract["attempt"] == {
        "attempt_id": ATTEMPT_ID,
        "native_process_count": 1,
        "automatic_retry": False,
        "manual_retry": False,
        "resume": False,
    }
    assert contract["required_services"] == list(REQUIRED_SERVICES)
    assert contract["preset"]["install_relative_path"] == PRESET_RELATIVE_PATH
    assert contract["preset"]["selected_tools"] == ["edit", "glob", "read"]


def test_all_sources_are_full_objects_and_predecessor_bytes_are_exact() -> None:
    contract = load_contract()
    projection = validate_predecessors(contract)

    assert len(contract["planning_source"]) == 40
    assert len(contract["frozen_plan_source"]) == 40
    assert all(len(value) == 40 for value in contract["accepted_sources"].values())
    assert projection["predecessor_sha256"] == contract["predecessor_bytes"]
    assert projection["implementation_sha256"] == contract["implementation_bytes"]
    assert projection["required_services"] == list(REQUIRED_SERVICES)
    assert projection["immutable_predecessor_unchanged"] is True


def test_exact_materialised_preset_is_bound_without_approximation() -> None:
    contract = load_contract()

    assert len(PRESET_BYTES) == 158
    assert contract["preset"]["bytes"] == 158
    assert contract["preset"]["sha256"] == (
        "3de182eb702e6f2b397941c73393b87f65acb9b401565f966059d2bd46f649d1"
    )


def _patch_pair(tmp_path: Path) -> tuple[bytes, bytes]:
    profile = tmp_path / "home" / "profiles" / "headless"
    modules = tmp_path / "installation" / "proof"
    return build_patch_pair(
        profile,
        tmp_path / "readiness.jsonl",
        tmp_path / "activation.jsonl",
        tmp_path / "terminal.json",
        modules / "sentinel.mjs",
        modules / "runner.mjs",
    )


def test_patch_has_exact_readiness_then_complete_composition_rows(tmp_path: Path) -> None:
    initial, changed = _patch_pair(tmp_path)
    validate_patch_pair(initial, changed)
    initial_rows = yaml.safe_load(initial)
    changed_rows = yaml.safe_load(changed)

    assert [row["id"] for row in initial_rows[:3]] == [
        "headless-runner",
        "code-runtime",
        "session-telemetry-otel",
    ]
    assert [row["id"] for row in initial_rows[-1]["insert"]] == [
        "provider-free-effective-tool-hmr-sentinel"
    ]
    assert [row["id"] for row in changed_rows[-1]["insert"]] == [
        "provider-free-effective-tool-hmr-sentinel",
        "agent-presets",
        "provider-free-complete-composition-runner",
    ]
    assert changed_rows[-1]["insert"][1]["config"] == {"default": "standard"}
    assert changed_rows[-1]["insert"][2]["inject"] == list(REQUIRED_SERVICES)


def test_patch_validator_rejects_missing_service_injection(tmp_path: Path) -> None:
    initial, changed = _patch_pair(tmp_path)
    rows = yaml.safe_load(changed)
    rows[-1]["insert"][-1]["inject"] = ["hmr", "tools"]

    with pytest.raises(base.RecoveryBootError, match="runner_injection_mismatch"):
        validate_patch_pair(initial, yaml.safe_dump(rows, sort_keys=False).encode())


def test_module_and_loader_declarations_are_identical_and_ordered() -> None:
    source = future_runner_source()

    assert b'export const inject = ["hmr", "agentPresets", "tools"];' in source
    assert source.count(b"export const inject =") == 1


def test_configured_base_is_scoped_and_restores_every_binding() -> None:
    original = {
        "OPERATION_ID": base.OPERATION_ID,
        "load_contract": base.load_contract,
        "build_patch_pair": base.build_patch_pair,
        "corrected_runner_source": base.corrected_runner_source,
    }
    with configured_base():
        assert base.OPERATION_ID != original["OPERATION_ID"]
        assert base.load_contract is load_contract
        assert base.build_patch_pair is build_patch_pair
        assert base.corrected_runner_source is future_runner_source
    assert base.OPERATION_ID == original["OPERATION_ID"]
    assert base.load_contract is original["load_contract"]
    assert base.build_patch_pair is original["build_patch_pair"]
    assert base.corrected_runner_source is original["corrected_runner_source"]


def test_deterministic_check_is_cache_only_and_creates_no_attempt_output() -> None:
    cache_root = DISPOSABLE_PARENT.parent / "AppData" / "Local" / "npm-cache"
    assert not EVIDENCE_PATH.exists()
    assert not REPORT_PATH.exists()

    projection = deterministic_check(cache_root)

    assert projection["package_count"] == 4
    assert projection["controller"]["single_popen"] is True
    assert projection["controller"]["no_retry_loop"] is True
    assert projection["contract"]["required_services"] == list(REQUIRED_SERVICES)
    assert not EVIDENCE_PATH.exists()
    assert not REPORT_PATH.exists()


def test_plan_and_threat_delta_keep_execution_and_authority_closed() -> None:
    plan = Path(
        "docs/deepseek-native-harness-provider-free-complete-composition-native-boot-recovery-plan.md"
    ).read_text(encoding="utf-8")
    threat = Path(
        "docs/security/deepseek-native-harness-provider-free-complete-composition-native-boot-recovery-threat-model-delta.md"
    ).read_text(encoding="utf-8")

    for phrase in (
        "exactly one offline, network-denied",
        "The first `Popen` consumes the new attempt id",
        "There is no\nautomatic or manual second process",
        "No second native process; no agent/session/turn, WorkOrder, broker, DeepSeek",
        "no production, deployment,\nrelease, Pages",
    ):
        assert phrase in plan
    assert "More than one native process" in threat
    assert "No task prompt" in threat


def test_evidence_schema_accepts_only_the_new_operation_identity() -> None:
    schema = json.loads(
        CONTRACT_PATH.with_name("evidence.schema.json").read_text(encoding="utf-8")
    )
    contract = load_contract()
    payload = {
        "schema_version": "ariadne.deepseek_native_harness_provider_free_complete_composition_native_boot_recovery_evidence.v1",
        "operation_id": "deepseek-native-harness-provider-free-complete-composition-native-boot-recovery",
        "planning_source": contract["planning_source"],
        "attempt_id": ATTEMPT_ID,
        "result": "pass",
        "failure_classification": None,
        "package": {},
        "source_contract": {},
        "launch": {},
        "composition": {},
        "readiness": {},
        "activation": {},
        "terminal": {},
        "provider_boundary": {},
        "cleanup": {},
    }

    jsonschema.validate(payload, schema)
