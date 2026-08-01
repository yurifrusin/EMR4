from __future__ import annotations

from datetime import datetime
import json

from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_readonly_synthetic_context_bridge as bridge
from scripts import reception_one_receptionist_first_v68 as frozen


def test_model_visible_context_is_minimal_and_fresh_on_frozen_clock() -> None:
    frame = json.loads(bridge.FRAME_PATH.read_text(encoding="utf-8"))
    turn_input = frozen.build_turn_input(frame)
    frozen.validate_turn_input(frame, turn_input)
    desk = turn_input["task"]["desk_context"]

    observed = datetime.fromisoformat(
        frame["observed_at"].replace("Z", "+00:00")
    )
    expires = datetime.fromisoformat(
        frame["expires_at"].replace("Z", "+00:00")
    )
    assert observed <= typed_plan.EVIDENCE_NOW < expires
    assert desk["current_diary"]["authority_label"] == "fixture_intercepted"
    assert desk["recent_dialogue"]["authority_label"] == "staff_selected"
    assert desk["selected_appointment"]["authority_label"] == "staff_selected"
    assert "appointments" not in desk
    assert "candidate_slots" not in desk
    assert "full_diary" in desk["excluded_context"]
    assert "unselected_appointments" in desk["excluded_context"]


def test_provider_free_bridge_releases_only_exact_resize_proposal() -> None:
    frame = json.loads(bridge.FRAME_PATH.read_text(encoding="utf-8"))
    oracle = bridge._provider_free_oracle(frame)
    output = oracle["expected_final_output"]
    assert oracle["proofreader_disposition"] == "admit"
    assert oracle["context_frame_review"][
        "same_packet_seen_by_model_and_proofreader"
    ] is True
    assert output["proposal_family"] == "resize"
    assert output["duration_minutes"] == 45
    assert output["requires_human_confirmation"] is True
    assert output["write_performed"] is False


def test_persisted_provider_blocked_evidence_and_cleanup_are_bound() -> None:
    evidence = json.loads(
        bridge.PROVIDER_BLOCKED_PATH.read_text(encoding="utf-8")
    )
    cleanup = json.loads(
        bridge.DATABASE_CLEANUP_PATH.read_text(encoding="utf-8")
    )
    assert evidence["evidence_hash"] == bridge._content_hash(evidence)
    assert evidence["provider_calls"] == 0
    assert evidence["credential_reads"] == 0
    assert evidence["database"]["truth_counts_before"] == evidence[
        "database"
    ]["truth_counts_after"]
    assert evidence["frame"]["raw_database_ids_serialized"] is False
    assert evidence["frame"]["handle_map_serialized"] is False
    assert all(value is False for value in evidence["boundaries"].values())
    assert cleanup["ownership_marker_verified"] is True
    assert cleanup["database_absent"] is True


def test_closed_occupied_bridge_is_exact_and_non_mutating() -> None:
    evidence = json.loads(bridge.OCCUPIED_PATH.read_text(encoding="utf-8"))
    assert evidence["evidence_hash"] == bridge._content_hash(evidence)
    assert evidence["actual_provider_calls"] == 1
    assert evidence["expected_safe_outcome"] is True
    assert evidence["all_ledgers_consumed"] is True
    assert evidence["database_absent_before_occupied_call"] is True
    assert evidence["model_database_access"] is False
    assert evidence["write_performed"] is False
    assert evidence["confirmation_performed"] is False
    observation = evidence["observation"]
    assert observation["final_proofreader_disposition"] == "admit"
    assert observation["final_violation_codes"] == []
    assert observation["release"]["proposal_family"] == "resize"
    assert observation["release"]["duration_minutes"] == 45
    assert observation["release"]["requires_human_confirmation"] is True
    assert observation["release"]["write_performed"] is False
    ledgers = sorted(bridge.OCCUPIED_DIR.glob("*-ledger.json"))
    assert len(ledgers) == 1
    assert json.loads(ledgers[0].read_text(encoding="utf-8"))["status"] == (
        "consumed"
    )
