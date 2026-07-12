import json
from pathlib import Path

from scripts.ariadne_orchestrator_preflight import build_receipt


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_STATE = ROOT / "tests" / "fixtures" / "ariadne_harness" / "orchestrator_runtime_state.json"


def test_generic_orchestrator_receipt_passes_with_explicit_adapter_slot_and_workspace_evidence():
    receipt = build_receipt(runtime_state_path=RUNTIME_STATE)

    assert receipt["status"] == "passed"
    assert receipt["worker_dispatch_permitted"] is True
    assert receipt["authority_boundary"] == "receipt_only_no_worker_control_or_integration_authority"


def test_generic_orchestrator_receipt_fails_closed_for_stale_worker_slots(tmp_path: Path):
    runtime_state = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime_state["worker_slots"][0]["stale_instance_ids"] = ["stale-deepseek-1"]
    path = tmp_path / "runtime-state.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "revision_required"
    assert receipt["worker_dispatch_permitted"] is False
    assert "stale_worker_resolution_required:deepseek-flash-workers" in receipt["reasons"]


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
    claude = next(item for item in runtime_state["workspace_receipts"] if item["agent_id"] == "claude")
    claude["at_handoff_current"] = False
    path = tmp_path / "runtime-state.json"
    path.write_text(json.dumps(runtime_state), encoding="utf-8")

    receipt = build_receipt(runtime_state_path=path)

    assert receipt["status"] == "revision_required"
    assert "workspace_not_at_handoff:claude" in receipt["reasons"]


def test_context_health_requires_rehydration_for_unknown_context_before_integration(tmp_path: Path):
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


def test_context_health_requires_a_new_continuation_when_provider_meter_is_critical(tmp_path: Path):
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
