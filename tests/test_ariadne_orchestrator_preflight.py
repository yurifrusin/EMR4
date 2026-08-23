import json
import shutil
from pathlib import Path

import pytest
import yaml

from orchestration_harness.governance_clockwork_tick import (
    semantic_scalar_leaf_count,
)
from orchestration_harness.orchestrator_preflight import (
    SERIAL_CONTINUATION_INTENT_VERSION,
    SERIAL_CONTINUATION_PRESET,
    SerialContinuationIntentError,
    materialize_serial_continuation_runtime_state,
)
from scripts.ariadne_orchestrator_preflight import (
    build_receipt,
    build_serial_continuation_receipt,
    configured_continuation_events,
)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_STATE = (
    ROOT / "tests" / "fixtures" / "ariadne_harness" / "orchestrator_runtime_state.json"
)
MANUAL_SERIAL_STATE = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "ariadne-clockwork-typed-serial-continuation-state-projection-rehearsal-preplanning-runtime-state.json"
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


def _serial_intent() -> dict:
    return {
        "schema_version": SERIAL_CONTINUATION_INTENT_VERSION,
        "preset": SERIAL_CONTINUATION_PRESET,
        "continuation_event": "pre_sprint_planning",
        "planned_action": "freeze typed serial continuation projection",
        "assessed_stage": "typed serial projection test",
        "active_evidence_paths": [
            "docs/ariadne-clockwork-typed-serial-continuation-state-projection-rehearsal-plan.md",
            "docs/security/ariadne-clockwork-typed-serial-continuation-state-projection-rehearsal-threat-model-delta.md",
            "orchestration/continuity/ariadne-active-operation-latch/current.json",
        ],
        "lane_decision_overrides": [],
    }


def _materialize_serial(intent: dict) -> dict:
    settings = ROOT / "orchestration" / "harness_settings"
    requirements = yaml.safe_load(
        (settings / "orchestrator_requirements.yaml").read_text(encoding="utf-8")
    )
    adapters = yaml.safe_load(
        (settings / "transport_adapters.yaml").read_text(encoding="utf-8")
    )
    worker_pool = yaml.safe_load(
        (settings / "worker_pool.yaml").read_text(encoding="utf-8")
    )
    latch = json.loads(
        (
            ROOT
            / "orchestration"
            / "continuity"
            / "ariadne-active-operation-latch"
            / "current.json"
        ).read_text(encoding="utf-8")
    )
    return materialize_serial_continuation_runtime_state(
        intent=intent,
        requirements=requirements,
        adapters=adapters,
        worker_pool=worker_pool,
        active_operation=latch,
        repo_root=ROOT,
    )


def _write_serial_intent(tmp_path: Path, value: dict) -> Path:
    path = tmp_path / "serial-continuation-intent.json"
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return path


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
    assert receipt["git_refs_snapshot"]["status"] == "passed"
    assert receipt["git_refs_snapshot"]["protected_refs_aligned"] is True
    assert receipt["git_refs_snapshot"]["head"] == receipt[
        "git_object_resolution"
    ]["observed_head"]
    assert isinstance(receipt["git_refs_snapshot"]["untracked_path_count"], int)
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


def test_blocked_active_operation_never_permits_worker_dispatch(tmp_path: Path) -> None:
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    active = runtime_state["active_operation"]
    active["status"] = "blocked"
    active["user_attention"] = {
        "required": True,
        "reason": "The bounded verifier transport recovery is exhausted.",
    }
    active["terminal_response"] = {
        "permitted": True,
        "reason": "bounded_verifier_transport_recovery_exhausted",
    }
    path = tmp_path / "blocked-operation.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "passed"
    assert receipt["active_operation"]["status"] == "blocked"
    assert receipt["terminal_handback_permitted"] is True
    assert receipt["worker_dispatch_permitted"] is False


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


def test_stale_active_operation_settings_fingerprint_fails_closed(
    tmp_path: Path,
) -> None:
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state["active_operation"]["checkpoint"]["settings_fingerprint"] = (
        "sha256:" + "f" * 64
    )
    path = tmp_path / "runtime-state.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "revision_required"
    assert receipt["worker_dispatch_permitted"] is False
    assert "active_operation_settings_fingerprint_mismatch" in receipt["reasons"]


def test_unresolvable_full_commit_id_in_git_ref_evidence_fails_closed(
    tmp_path: Path,
) -> None:
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state["source_evidence"]["git_refs_and_worktree"] = (
        "Task HEAD is " + "f" * 40
    )
    path = tmp_path / "runtime-state.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "revision_required"
    assert receipt["worker_dispatch_permitted"] is False
    assert "git_refs_evidence_object_unresolvable" in receipt["reasons"]
    assert "git_refs_evidence_manual_object_id_forbidden" in receipt["reasons"]
    assert receipt["git_ref_evidence_binding"] == {
        "schema_version": "ariadne.git_ref_evidence_binding.v1",
        "status": "revision_required",
        "policy": "machine_snapshot_only",
        "manually_supplied_object_id_count": 1,
        "reason_codes": ["git_refs_evidence_manual_object_id_forbidden"],
    }


def test_resolvable_full_commit_id_in_git_ref_narrative_fails_closed(
    tmp_path: Path,
) -> None:
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state["source_evidence"]["git_refs_and_worktree"] = (
        "Task HEAD is " + runtime_state["active_operation"]["source_head"]
    )
    path = tmp_path / "runtime-state.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "revision_required"
    assert receipt["worker_dispatch_permitted"] is False
    assert "git_refs_evidence_object_unresolvable" not in receipt["reasons"]
    assert "git_refs_evidence_manual_object_id_forbidden" in receipt["reasons"]


def test_machine_snapshot_owns_exact_git_ids_without_narrative_tokens() -> None:
    receipt = build_receipt(runtime_state_path=RUNTIME_STATE)

    assert receipt["git_ref_evidence_binding"] == {
        "schema_version": "ariadne.git_ref_evidence_binding.v1",
        "status": "passed",
        "policy": "machine_snapshot_only",
        "manually_supplied_object_id_count": 0,
        "reason_codes": [],
    }
    assert receipt["git_refs_snapshot"]["head"]
    assert receipt["git_refs_snapshot"]["protected_expected_commit"]


def test_full_commit_ids_outside_git_ref_narrative_remain_admissible(
    tmp_path: Path,
) -> None:
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state["source_evidence"]["active_plan_and_acceptance"] = [
        "Accepted historical source "
        + runtime_state["active_operation"]["source_head"]
    ]
    path = tmp_path / "runtime-state.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "passed"
    assert receipt["git_ref_evidence_binding"]["status"] == "passed"


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


def test_typed_serial_intent_materializes_one_passing_existing_receipt(
    tmp_path: Path,
) -> None:
    intent = _serial_intent()
    runtime_state = _materialize_serial(intent)
    intent_path = _write_serial_intent(tmp_path, intent)

    receipt = build_serial_continuation_receipt(intent_path=intent_path)

    assert runtime_state["schema_version"] == "ariadne.orchestrator_runtime_state.v1"
    assert runtime_state["active_operation"] == json.loads(
        (
            ROOT
            / "orchestration"
            / "continuity"
            / "ariadne-active-operation-latch"
            / "current.json"
        ).read_text(encoding="utf-8")
    )
    assert runtime_state["source_evidence"]["git_refs_and_worktree"] == (
        "machine_snapshot_only"
    )
    assert all(
        not slot["active_instance_ids"] and not slot["stale_instance_ids"]
        for slot in runtime_state["worker_slots"]
    )
    assert runtime_state["workspace_receipts"] == []
    assert runtime_state["assigned_agent_ids"] == []
    assert receipt["status"] == "passed"
    assert receipt["rehydration_sources"] == REQUIRED_SOURCES
    assert receipt["terminal_handback_permitted"] is False
    assert receipt["git_ref_evidence_binding"]["status"] == "passed"
    assert receipt["git_object_resolution"]["status"] == "passed"
    assert receipt["git_refs_snapshot"]["protected_refs_aligned"] is True


def test_typed_serial_receipt_preserves_manual_safety_projections(
    tmp_path: Path,
) -> None:
    intent = _serial_intent()
    intent["planned_action"] = (
        "freeze_minimal_typed_serial_continuation_projection_contract_inside_existing_preflight"
    )
    intent["assessed_stage"] = "preplanning_after_fresh_successor_rehydration"
    intent_path = _write_serial_intent(tmp_path, intent)

    typed = build_serial_continuation_receipt(intent_path=intent_path)
    manual = build_receipt(runtime_state_path=MANUAL_SERIAL_STATE)

    for field in (
        "status",
        "settings_fingerprint",
        "rehydrated_from_receipt",
        "rehydration_sources",
        "active_operation",
        "terminal_handback_permitted",
        "worker_dispatch_permitted",
        "git_ref_evidence_binding",
        "git_refs_snapshot",
        "git_object_resolution",
    ):
        assert typed[field] == manual[field]
    assert [
        (lane["lane_id"], lane["disposition"], lane["expected_leverage"])
        for lane in typed["parallelism_assessment"]["lanes"]
    ] == [
        (lane["lane_id"], lane["disposition"], lane["expected_leverage"])
        for lane in manual["parallelism_assessment"]["lanes"]
    ]


def test_typed_serial_intent_meets_live_pair_reduction_thresholds(
    tmp_path: Path,
) -> None:
    intent = _serial_intent()
    intent_path = _write_serial_intent(tmp_path, intent)
    typed_receipt = build_serial_continuation_receipt(intent_path=intent_path)
    manual_state = json.loads(MANUAL_SERIAL_STATE.read_text(encoding="utf-8"))
    manual_receipt = build_receipt(runtime_state_path=MANUAL_SERIAL_STATE)

    compact_input = intent_path.read_text(encoding="utf-8")
    compact_receipt = json.dumps(typed_receipt, indent=2, sort_keys=True) + "\n"
    manual_input = MANUAL_SERIAL_STATE.read_text(encoding="utf-8")
    manual_receipt_text = json.dumps(manual_receipt, indent=2, sort_keys=True) + "\n"
    compact_leaves = semantic_scalar_leaf_count(intent)
    manual_leaves = semantic_scalar_leaf_count(manual_state)

    assert compact_leaves <= 25
    assert len(compact_input.splitlines()) <= 40
    assert 1 - (compact_leaves / manual_leaves) >= 0.75
    assert 1 - (
        len((compact_input + compact_receipt).splitlines())
        / len((manual_input + manual_receipt_text).splitlines())
    ) >= 0.40
    assert 1 - (
        len((compact_input + compact_receipt).encode("utf-8"))
        / len((manual_input + manual_receipt_text).encode("utf-8"))
    ) >= 0.40
    assert sorted(path.name for path in tmp_path.iterdir()) == [intent_path.name]


def test_typed_serial_lane_override_is_closed_and_never_assigns_work() -> None:
    intent = _serial_intent()
    intent["lane_decision_overrides"] = [
        {
            "lane_id": "gemini_verifier",
            "decision_code": "reserved_required_independence",
        }
    ]

    runtime_state = _materialize_serial(intent)
    lane = next(
        item
        for item in runtime_state["parallelism_assessment"]["lanes"]
        if item["lane_id"] == "gemini_verifier"
    )

    assert lane["disposition"] == "reserved"
    assert lane["expected_leverage"] == "required_independence"
    assert lane["work_packages"] == []
    assert runtime_state["parallelism_assessment"]["parallel_work_packages"] == []


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        ("extra_key", "serial_continuation_intent_keys_invalid"),
        ("invalid_preset", "serial_continuation_preset_invalid"),
        ("worker_dispatch", "serial_continuation_worker_dispatch_forbidden"),
        ("missing_path", "serial_continuation_evidence_path_missing"),
        ("absolute_path", "serial_continuation_evidence_path_invalid"),
        ("invalid_decision", "serial_continuation_lane_decision_invalid"),
        ("duplicate_lane", "serial_continuation_lane_override_duplicate"),
    ],
)
def test_typed_serial_intent_rejects_nonserial_or_untyped_choices(
    mutation: str,
    reason: str,
) -> None:
    intent = _serial_intent()
    if mutation == "extra_key":
        intent["unexpected"] = True
    elif mutation == "invalid_preset":
        intent["preset"] = "free_form"
    elif mutation == "worker_dispatch":
        intent["continuation_event"] = "pre_worker_dispatch"
    elif mutation == "missing_path":
        intent["active_evidence_paths"] = ["docs/does-not-exist.json"]
    elif mutation == "absolute_path":
        intent["active_evidence_paths"] = [str(ROOT / "AGENTS.md")]
    elif mutation == "invalid_decision":
        intent["lane_decision_overrides"] = [
            {"lane_id": "deepseek_flash", "decision_code": "planned_positive"}
        ]
    elif mutation == "duplicate_lane":
        intent["lane_decision_overrides"] = [
            {"lane_id": "deepseek_flash", "decision_code": "declined_negative"},
            {"lane_id": "deepseek_flash", "decision_code": "declined_neutral"},
        ]

    with pytest.raises(SerialContinuationIntentError, match=reason):
        _materialize_serial(intent)


def test_typed_serial_projection_fails_closed_on_adapter_or_worker_drift() -> None:
    settings = ROOT / "orchestration" / "harness_settings"
    requirements = yaml.safe_load(
        (settings / "orchestrator_requirements.yaml").read_text(encoding="utf-8")
    )
    adapters = yaml.safe_load(
        (settings / "transport_adapters.yaml").read_text(encoding="utf-8")
    )
    worker_pool = yaml.safe_load(
        (settings / "worker_pool.yaml").read_text(encoding="utf-8")
    )
    latch = json.loads(
        (
            ROOT
            / "orchestration"
            / "continuity"
            / "ariadne-active-operation-latch"
            / "current.json"
        ).read_text(encoding="utf-8")
    )
    external = next(
        item
        for item in adapters["adapters"]
        if item["adapter_id"] != "codex_primary_session"
    )
    external["allowed_probe_methods"].remove("synthetic_fixture")

    with pytest.raises(
        SerialContinuationIntentError,
        match="serial_continuation_adapter_method_missing",
    ):
        materialize_serial_continuation_runtime_state(
            intent=_serial_intent(),
            requirements=requirements,
            adapters=adapters,
            worker_pool=worker_pool,
            active_operation=latch,
            repo_root=ROOT,
        )

    adapters = yaml.safe_load(
        (settings / "transport_adapters.yaml").read_text(encoding="utf-8")
    )
    worker_pool["workers"] = [
        item
        for item in worker_pool["workers"]
        if item["resource_id"] != "deepseek-flash-workers"
    ]
    with pytest.raises(
        SerialContinuationIntentError,
        match="serial_continuation_managed_worker_missing",
    ):
        materialize_serial_continuation_runtime_state(
            intent=_serial_intent(),
            requirements=requirements,
            adapters=adapters,
            worker_pool=worker_pool,
            active_operation=latch,
            repo_root=ROOT,
        )
