import json
import shutil
from pathlib import Path

import pytest
import yaml

from scripts.ariadne_orchestrator_preflight import (
    build_receipt,
    configured_continuation_events,
)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_STATE = (
    ROOT / "tests" / "fixtures" / "ariadne_harness" / "orchestrator_runtime_state.json"
)
REQUIRED_SOURCES = [
    "live_handover_current_baton",
    "current_authority_allocation",
    "active_plan_and_acceptance",
    "protected_evidence_boundaries",
    "git_refs_and_worktree",
]
CONTINUATION_EVENTS = yaml.safe_load(
    (
        ROOT / "orchestration" / "harness_settings" / "orchestrator_requirements.yaml"
    ).read_text(encoding="utf-8")
)["continuation_events"]


def test_receipt_cli_exposes_the_exact_configured_event_vocabulary() -> None:
    assert configured_continuation_events() == tuple(CONTINUATION_EVENTS)
    assert configured_continuation_events()[4] == "pre_sprint_planning"


def test_generic_orchestrator_receipt_passes_with_explicit_adapter_slot_and_workspace_evidence():
    receipt = build_receipt(runtime_state_path=RUNTIME_STATE)

    assert receipt["status"] == "passed"
    assert receipt["worker_dispatch_permitted"] is True
    assert (
        receipt["authority_boundary"]
        == "receipt_only_no_worker_control_or_integration_authority"
    )
    assert receipt["rehydrated_from_receipt"] is True
    assert receipt["rehydration_sources"] == REQUIRED_SOURCES
    assert list(receipt["source_evidence"]) == REQUIRED_SOURCES
    assert receipt["active_operation"]["operation_id"] == "fixture-operation"
    assert receipt["active_operation"]["status"] == "in_progress"
    assert receipt["parallelism_assessment"]["operation_id"] == "fixture-operation"
    assert [lane["lane_id"] for lane in receipt["parallelism_assessment"]["lanes"]] == [
        "deepseek_flash",
        "gemini_verifier",
        "native_subagents",
    ]
    assert receipt["terminal_handback_permitted"] is False
    assert receipt["git_object_resolution"] == {
        "schema_version": "ariadne.git_object_resolution.v1",
        "status": "passed",
        "source_field": "active_operation.source_head",
        "supplied_object_id": "17add9baf2cc3616f7ee4fb8eda3481e2eb13715",
        "resolved_commit": "17add9baf2cc3616f7ee4fb8eda3481e2eb13715",
        "observed_head": receipt["git_object_resolution"]["observed_head"],
        "source_is_ancestor_of_head": True,
        "reason_codes": [],
    }


def test_every_continuation_fails_closed_without_parallelism_assessment(
    tmp_path: Path,
) -> None:
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state.pop("parallelism_assessment")
    for event in CONTINUATION_EVENTS:
        runtime_state["continuation_event"] = event
        path = tmp_path / f"parallelism-{event}.json"
        path.write_text(json.dumps(runtime_state), encoding="utf-8")

        receipt = build_receipt(runtime_state_path=path)

        assert receipt["status"] == "revision_required"
        assert receipt["parallelism_assessment"] == {}
        assert "parallelism_assessment_missing" in receipt["reasons"]


def test_parallelism_assessment_requires_all_three_distinct_lanes(
    tmp_path: Path,
) -> None:
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state["parallelism_assessment"]["lanes"] = runtime_state[
        "parallelism_assessment"
    ]["lanes"][:2]
    path = tmp_path / "missing-native-lane.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "revision_required"
    assert "parallelism_lane_inventory_invalid" in receipt["reasons"]


def test_serial_execution_requires_an_explicit_efficacy_basis(tmp_path: Path) -> None:
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    for lane in runtime_state["parallelism_assessment"]["lanes"]:
        lane["disposition"] = "declined"
        lane["expected_leverage"] = "negative"
        lane["work_packages"] = []
    runtime_state["parallelism_assessment"]["parallel_work_packages"] = []
    runtime_state["parallelism_assessment"]["serial_constraints"] = []
    path = tmp_path / "implicit-serial.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "revision_required"
    assert "parallelism_efficacy_basis_missing" in receipt["reasons"]


def test_generic_orchestrator_receipt_fails_closed_for_stale_worker_slots(
    tmp_path: Path,
):
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state["worker_slots"][0]["stale_instance_ids"] = ["stale-deepseek-1"]
    path = tmp_path / "runtime-state.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "revision_required"
    assert receipt["worker_dispatch_permitted"] is False
    assert (
        "stale_worker_resolution_required:deepseek-flash-workers" in receipt["reasons"]
    )


def test_unassigned_platform_workspaces_do_not_block_sprint_planning(tmp_path: Path):
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state["assigned_agent_ids"] = []
    for workspace in runtime_state["workspace_receipts"]:
        workspace["at_handoff_current"] = False
    path = tmp_path / "runtime-state.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "passed"


def test_assigned_agent_requires_clean_current_workspace_receipt(tmp_path: Path):
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state["assigned_agent_ids"] = ["claude"]
    claude = next(
        item
        for item in runtime_state["workspace_receipts"]
        if item["agent_id"] == "claude"
    )
    claude["at_handoff_current"] = False
    path = tmp_path / "runtime-state.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "revision_required"
    assert "workspace_not_at_handoff:claude" in receipt["reasons"]


def test_context_health_requires_rehydration_for_unknown_context_before_integration(
    tmp_path: Path,
):
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state["continuation_event"] = "pre_sprint_planning"
    runtime_state["planned_action"] = "integration"
    runtime_state["context_health"]["agent_contexts"][0] = {
        "agent_id": "orchestrator",
        "measurement_source": "unknown",
        "rehydrated_from_receipt": False,
    }
    path = tmp_path / "runtime-state.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "revision_required"
    assert "context_rehydration_required:orchestrator" in receipt["reasons"]


def test_context_health_requires_a_new_continuation_when_provider_meter_is_critical(
    tmp_path: Path,
):
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state["continuation_event"] = "pre_sprint_planning"
    runtime_state["planned_action"] = "worker_dispatch"
    runtime_state["context_health"]["agent_contexts"][0] = {
        "agent_id": "orchestrator",
        "measurement_source": "provider_reported",
        "input_tokens": 86,
        "context_limit_tokens": 100,
        "rehydrated_from_receipt": True,
    }
    path = tmp_path / "runtime-state.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "revision_required"
    assert "context_mandatory_rehydration_threshold:orchestrator" in receipt["reasons"]


def test_post_compaction_requires_named_live_rehydration_sources(tmp_path: Path):
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state["context_health"]["agent_contexts"][0]["rehydration_sources"] = [
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ]
    path = tmp_path / "runtime-state.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "revision_required"
    assert receipt["worker_dispatch_permitted"] is False
    assert (
        "rehydration_source_missing:orchestrator:live_handover_current_baton"
        in receipt["reasons"]
    )
    assert (
        "rehydration_source_missing:orchestrator:current_authority_allocation"
        in receipt["reasons"]
    )


def test_every_configured_continuation_event_requires_and_emits_five_sources(
    tmp_path: Path,
):
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    for event in CONTINUATION_EVENTS:
        runtime_state["continuation_event"] = event
        path = tmp_path / f"{event}.json"
        path.write_text(json.dumps(runtime_state), encoding="utf-8")

        receipt = build_receipt(runtime_state_path=path)

        assert receipt["status"] == "passed"
        assert receipt["rehydrated_from_receipt"] is True
        assert receipt["rehydration_sources"] == REQUIRED_SOURCES
        assert list(receipt["source_evidence"]) == REQUIRED_SOURCES
        assert receipt["active_operation"]["operation_id"] == "fixture-operation"
        assert receipt["terminal_handback_permitted"] is False
        assert receipt["git_object_resolution"]["status"] == "passed"


def test_every_continuation_fails_closed_for_unresolvable_full_source_object(
    tmp_path: Path,
) -> None:
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state["active_operation"]["source_head"] = "f" * 40
    for event in CONTINUATION_EVENTS:
        runtime_state["continuation_event"] = event
        path = tmp_path / f"unresolvable-{event}.json"
        path.write_text(json.dumps(runtime_state), encoding="utf-8")

        receipt = build_receipt(runtime_state_path=path)

        assert receipt["status"] == "revision_required"
        assert receipt["worker_dispatch_permitted"] is False
        assert receipt["git_object_resolution"]["status"] == "revision_required"
        assert "git_object_command_failed" in receipt["reasons"]


def test_every_continuation_event_fails_closed_without_active_operation_latch(
    tmp_path: Path,
) -> None:
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state.pop("active_operation")
    for event in CONTINUATION_EVENTS:
        runtime_state["continuation_event"] = event
        path = tmp_path / f"{event}.json"
        path.write_text(json.dumps(runtime_state), encoding="utf-8")

        receipt = build_receipt(runtime_state_path=path)

        assert receipt["status"] == "revision_required"
        assert receipt["terminal_handback_permitted"] is None
        assert "active_operation_latch_missing" in receipt["reasons"]


def test_inconsistent_active_operation_latch_fails_closed(tmp_path: Path) -> None:
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state["active_operation"]["terminal_response"]["permitted"] = True
    path = tmp_path / "runtime-state.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "revision_required"
    assert receipt["active_operation"] == {}
    assert receipt["terminal_handback_permitted"] is None
    assert "active_operation_latch_invalid" in receipt["reasons"]


def test_named_source_without_evidence_fails_closed(tmp_path: Path):
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state["source_evidence"]["active_plan_and_acceptance"] = []
    path = tmp_path / "runtime-state.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "revision_required"
    assert receipt["rehydrated_from_receipt"] is False
    assert (
        "rehydration_source_evidence_missing:orchestrator:active_plan_and_acceptance"
    ) in receipt["reasons"]


@pytest.mark.parametrize("malformed", [None, " ", [], [""], [1]])
def test_malformed_source_evidence_fails_closed(tmp_path: Path, malformed: object):
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state["source_evidence"]["active_plan_and_acceptance"] = malformed
    path = tmp_path / "runtime-state.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "revision_required"
    assert (
        "rehydration_source_evidence_missing:orchestrator:active_plan_and_acceptance"
    ) in receipt["reasons"]


def test_primary_session_prefixed_evidence_is_emitted_without_manual_patch(
    tmp_path: Path,
):
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state.pop("source_evidence")
    primary = next(
        item
        for item in runtime_state["adapter_observations"]
        if item["adapter_id"] == "codex_primary_session"
    )
    primary["evidence"] = [
        f"{source}: authored evidence for {source}" for source in REQUIRED_SOURCES
    ]
    path = tmp_path / "runtime-state.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "passed"
    assert receipt["rehydrated_from_receipt"] is True
    assert receipt["rehydration_sources"] == REQUIRED_SOURCES
    assert list(receipt["source_evidence"]) == REQUIRED_SOURCES


def test_duplicate_primary_session_source_prefix_fails_closed(tmp_path: Path):
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state.pop("source_evidence")
    primary = next(
        item
        for item in runtime_state["adapter_observations"]
        if item["adapter_id"] == "codex_primary_session"
    )
    primary["evidence"] = [
        *(f"{source}: authored evidence" for source in REQUIRED_SOURCES),
        "active_plan_and_acceptance: conflicting duplicate evidence",
    ]
    path = tmp_path / "runtime-state.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "revision_required"
    assert (
        "rehydration_source_evidence_ambiguous:orchestrator:active_plan_and_acceptance"
    ) in receipt["reasons"]


def test_hard_event_without_source_policy_fails_closed(tmp_path: Path):
    settings_dir = tmp_path / "settings"
    shutil.copytree(ROOT / "orchestration" / "harness_settings", settings_dir)
    requirements_path = settings_dir / "orchestrator_requirements.yaml"
    requirements = yaml.safe_load(requirements_path.read_text(encoding="utf-8"))
    requirements["context_health"]["required_rehydration_sources_by_event"].pop(
        "pre_push"
    )
    requirements_path.write_text(
        yaml.safe_dump(requirements, sort_keys=False), encoding="utf-8"
    )
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state["continuation_event"] = "pre_push"
    path = tmp_path / "runtime-state.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path, settings_dir=settings_dir)

    assert receipt["status"] == "revision_required"
    assert receipt["rehydrated_from_receipt"] is False
    assert "rehydration_source_policy_missing:pre_push" in receipt["reasons"]
