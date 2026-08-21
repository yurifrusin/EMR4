from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from scripts import (
    deepseek_native_harness_provider_free_preset_mount_composition_unclassified_source_reconciliation_rehearsal as subject,
)


def test_source_inventory_is_exact_and_package_seed_is_read_only() -> None:
    payloads, observed = subject.source_inventory()
    contract = json.loads(subject.CONTRACT_PATH.read_bytes())

    assert set(payloads) == {
        "generated_runner",
        "generated_guard",
        "preset_mount_bridge",
        "preset_mount_sanitizer",
        "installed_agent_loop",
        "installed_scope",
        "installed_agent_presets",
    }
    assert observed == contract["source_inventory"]
    assert subject.PACKAGE_SEED_ROOT.is_dir()


def test_exact_source_chain_attributes_the_prebridge_service_gap() -> None:
    payloads, _ = subject.source_inventory()
    checks = subject.source_semantics(payloads)

    assert checks
    assert all(checks.values())


def test_missing_root_service_forwarding_anchor_fails_closed() -> None:
    payloads, _ = subject.source_inventory()
    payloads["generated_runner"] = payloads["generated_runner"].replace(
        b"assertEffectiveToolComposition(agentCtx, PRESET_ID, TOOLS)",
        b"assertEffectiveToolComposition(agentCtx, presets, PRESET_ID, TOOLS)",
    )

    checks = subject.source_semantics(payloads)
    assert checks["runner_guard_call_omits_root_presets_once"] is False


def test_changed_agent_loop_dependency_surface_fails_closed() -> None:
    payloads, _ = subject.source_inventory()
    payloads["installed_agent_loop"] = payloads["installed_agent_loop"].replace(
        b'"systemPrompt"', b'"systemPrompt", "agentPresets"', 1
    )

    checks = subject.source_semantics(payloads)
    assert checks["agent_loop_dependency_surface_excludes_agent_presets"] is False


def test_deterministic_check_preserves_claim_boundary() -> None:
    reading = subject.deterministic_check()

    assert reading["result"] == subject.ATTRIBUTION
    assert reading["failed_source_coordinates"] == []
    assert reading["accepted_terminal"]["safe_guard_coordinate"] == (
        "EFFECTIVE_TOOL_COMPOSITION_UNCLASSIFIED"
    )
    assert reading["claim_boundary"] == {
        "deterministic_source_route_explained": True,
        "exact_runtime_exception_observed": False,
        "private_context_value_observed": False,
        "new_bridge_runtime_path_proved": False,
        "prospective_correction_applied": False,
        "native_retry_authorized": False,
        "worker_model_provider_process_authorized": False,
        "product_authority": False,
    }
    assert set(reading["process_boundary"].values()) == {0}


def test_evidence_projection_validates_schema() -> None:
    evidence = subject._evidence_projection(subject.deterministic_check())
    schema = json.loads(subject.EVIDENCE_SCHEMA_PATH.read_bytes())

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(evidence)


def test_execute_writes_one_immutable_pair(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    evidence_path = tmp_path / "evidence.json"
    report_path = tmp_path / "report.md"
    monkeypatch.setattr(subject, "EVIDENCE_PATH", evidence_path)
    monkeypatch.setattr(subject, "REPORT_PATH", report_path)

    evidence = subject.execute()

    assert json.loads(evidence_path.read_bytes()) == evidence
    assert subject.ATTRIBUTION in report_path.read_text(encoding="utf-8")
    with pytest.raises(subject.SourceReconciliationError, match="immutable_output_exists"):
        subject.execute()


def test_contract_binds_full_planning_source_and_implementation() -> None:
    contract = subject.load_contract()

    assert len(contract["planning_source"]) == 40
    assert contract["predecessor_bindings"] == subject.predecessor_bindings()
    assert contract["implementation_bindings"] == subject.implementation_bindings()


def test_plan_keeps_process_and_product_authority_closed() -> None:
    plan = subject.PLAN_PATH.read_text(encoding="utf-8")
    threat = subject.THREAT_PATH.read_text(encoding="utf-8")
    normalized_plan = " ".join(plan.replace("-\n", "-").split())
    normalized_threat = " ".join(threat.replace("-\n", "-").split())

    for token in (
        "source_evidence_insufficient",
        "No Node/native-Harness/worker/model/provider process",
        "protected-ref movement is authorised",
    ):
        assert token in normalized_plan
    assert "Permit Python/PowerShell file and Git reads only" in normalized_threat
