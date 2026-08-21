from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from scripts import (
    deepseek_native_harness_provider_free_preset_mount_root_service_forwarding_process_free_correction_rehearsal as subject,
)


def test_contract_contains_no_caller_authored_git_object_id() -> None:
    contract = subject.load_contract()
    serialized = json.dumps(contract, sort_keys=True)

    assert subject.FULL_OID.search(serialized) is None
    assert contract["git_binding_policy"] == {
        "mode": "machine_resolved_only",
        "plan_path": subject.PLAN_PATH.relative_to(subject.REPO_ROOT).as_posix(),
        "caller_authored_object_id_count": 0,
    }


def test_machine_git_binding_resolves_plan_and_candidate_commits() -> None:
    binding = subject.machine_git_bindings()

    assert len(binding["planning_source_commit"]) == 40
    assert len(binding["candidate_source_commit"]) == 40
    assert binding["caller_authored_object_id_count"] == 0
    assert binding["planning_source_is_ancestor_of_candidate"] is True
    assert binding["branch_origin_aligned"] is True
    assert binding["protected_refs_aligned"] is True
    assert binding["tracked_worktree_clean"] is True
    assert binding["docs_branding_preserved"] is True


def test_accepted_source_inventory_is_exact_and_read_only() -> None:
    payloads, observed = subject.accepted_source_inventory()
    contract = json.loads(subject.CONTRACT_PATH.read_bytes())

    assert set(payloads) == {
        "accepted_generated_runner",
        "accepted_generated_guard",
        "accepted_preset_mount_bridge",
        "accepted_preset_mount_sanitizer",
        "installed_agent_presets",
    }
    assert observed == contract["accepted_source_inventory"]


def test_prospective_sources_admit_every_closed_coordinate() -> None:
    accepted, _ = subject.accepted_source_inventory()
    derived = subject.derive_sources(accepted)
    checks = subject.source_semantics(accepted, derived)

    assert checks
    assert all(checks.values())


def test_missing_runner_anchor_fails_closed() -> None:
    accepted, _ = subject.accepted_source_inventory()
    accepted["accepted_generated_runner"] = accepted[
        "accepted_generated_runner"
    ].replace(
        b"assertEffectiveToolComposition(agentCtx, PRESET_ID, TOOLS)",
        b"assertEffectiveToolComposition(agentCtx, unknown, PRESET_ID, TOOLS)",
    )

    with pytest.raises(
        subject.ProspectiveCorrectionError,
        match="prospective_source_derivation_rejected",
    ):
        subject.derive_sources(accepted)


def test_guard_contains_no_private_service_dereference() -> None:
    accepted, _ = subject.accepted_source_inventory()
    derived = subject.derive_sources(accepted)
    guard = derived["derived_guard"].decode("utf-8")

    assert "agentCtx.agentPresets" not in guard
    assert subject.guard_private_count(derived) == 0
    assert "    presetService," in guard


def test_service_and_mount_validation_are_inside_bridge_try() -> None:
    accepted, _ = subject.accepted_source_inventory()
    bridge = subject.derive_sources(accepted)["derived_bridge"].decode("utf-8")

    try_index = bridge.index("  try {")
    service_index = bridge.index("      presetService === null")
    read_index = bridge.index("    const mount = presetService.mount;")
    check_index = bridge.index('    if (typeof mount !== "function")')
    call_index = bridge.index(
        "    await mount.call(presetService, agentCtx, presetId);"
    )
    catch_index = bridge.index("  } catch (error) {")

    assert try_index < service_index < read_index < check_index < call_index < catch_index
    assert "sanitizePresetMountError(error, PresetMountError)" in bridge


def test_deterministic_check_preserves_prospective_claim_boundary() -> None:
    reading = subject.deterministic_check()

    assert reading["result"] == subject.ADMITTED_RESULT
    assert reading["failed_source_coordinates"] == []
    assert reading["correction_projection"] == {
        "root_service_admitted_by_runner": True,
        "root_service_forwarded_explicitly": True,
        "guard_private_service_dereference_count": 0,
        "mount_handle_validation_inside_bridge": True,
        "invalid_service_terminal": "PRESET_MOUNT_UNCLASSIFIED",
        "javascript_materialized_or_executed": False,
    }
    assert reading["claim_boundary"] == {
        "prospective_source_correction_admitted": True,
        "javascript_executed": False,
        "native_harness_executed": False,
        "worker_model_provider_executed": False,
        "native_runtime_path_proved": False,
        "native_retry_authorized": False,
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
    assert subject.ADMITTED_RESULT in report_path.read_text(encoding="utf-8")
    with pytest.raises(subject.ProspectiveCorrectionError, match="immutable_output_exists"):
        subject.execute()


def test_plan_keeps_execution_and_product_authority_closed() -> None:
    plan = " ".join(subject.PLAN_PATH.read_text(encoding="utf-8").split())
    threat = " ".join(subject.THREAT_PATH.read_text(encoding="utf-8").split())

    for token in (
        "root_service_forwarding_correction_admitted",
        "contains no caller-authored Git object ID",
        "No Node/native-Harness/worker/model/provider process",
        "protected-ref movement is authorised",
    ):
        assert token in plan
    assert "derive plan and candidate commits only through the repository resolver" in threat
