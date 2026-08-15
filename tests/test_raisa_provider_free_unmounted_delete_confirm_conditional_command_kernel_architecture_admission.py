import ast
import hashlib
import json
from datetime import datetime
from pathlib import Path

from scripts.raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission import (
    CANCELLED_REASON_CODES,
    EVIDENCE_PATH,
    LOCK_ORDER,
    MAX_FREE_TEXT_LENGTH,
    PACKET_PATH,
    ROOT,
    SCHEMA_PATH,
    build_report,
    hostile_mutations,
    simulate_schedule,
    validate_packet,
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _decision(packet: dict, scenario_id: str) -> dict:
    return next(
        item for item in packet["decision_scenarios"] if item["id"] == scenario_id
    )


def _schedule(packet: dict, schedule_id: str) -> dict:
    return next(
        item for item in packet["transaction_schedules"] if item["id"] == schedule_id
    )


def test_packet_schema_and_evidence_gate_pass() -> None:
    packet = _load(PACKET_PATH)
    schema = _load(SCHEMA_PATH)
    evidence = _load(EVIDENCE_PATH)

    assert validate_packet(packet, schema) == []
    report = build_report(packet, schema)
    assert report == evidence
    assert report["status"] == "passed"
    assert report["decision_scenario_count"] >= 24
    assert report["transaction_schedule_count"] >= 12
    assert report["hostile_mutation_count"] >= 40
    assert report["admitted_hostile_mutations"] == []
    assert not any(report["effect_boundary"].values())
    assert report["runtime_or_command_authority_granted"] is False


def test_source_hashes_are_exact_and_bound() -> None:
    packet = _load(PACKET_PATH)
    assert len(packet["source_bindings"]) == 7
    for binding in packet["source_bindings"]:
        actual = hashlib.sha256((ROOT / binding["path"]).read_bytes()).hexdigest()
        assert actual == binding["sha256"], binding["path"]
    assert packet["canonical_operation_id"] == "confirmAppointmentDeleteProposal"
    assert packet["canonical_ingress"] == "delete-confirm"


def test_both_authority_checks_and_authority_before_replay_non_disclosure() -> None:
    packet = _load(PACKET_PATH)
    first_failure = next(
        s for s in packet["decision_scenarios"] if not s["authority_after_target_lock"]
    )
    second_failure = next(
        s
        for s in packet["decision_scenarios"]
        if s["authority_after_target_lock"] and not s["authority_all_locks_held"]
    )
    assert first_failure["expected"]["outcome"] == "authority_revoked"
    assert first_failure["expected"]["receipt_disclosed"] is False
    assert "authority_revoked_after_target_lock" in first_failure["expected"]["reason"]
    assert second_failure["expected"]["outcome"] == "authority_revoked"
    assert second_failure["expected"]["receipt_disclosed"] is False
    assert "authority_revoked_all_locks_held" in second_failure["expected"]["reason"]

    replay = _decision(packet, "ddc-024-authority-before-replay")
    assert replay["idempotency"] == "same_digest_completed"
    assert replay["authority_after_target_lock"] is False
    assert replay["expected"]["outcome"] == "authority_revoked"
    assert replay["expected"]["receipt_disclosed"] is False
    assert replay["expected"]["planned_effect"] is False


def test_exact_current_authority_and_signed_evidence_contracts_are_closed() -> None:
    packet = _load(PACKET_PATH)
    authority = packet["authority_contract"]
    evidence = packet["signed_evidence_contract"]

    assert authority["server_owned_identity_fields"] == [
        "practice_id",
        "actor_user_id",
        "actor_role",
        "authenticated_session_id",
    ]
    assert authority["request_body_authority_fields_accepted"] == []
    assert authority["allowed_actor_roles"] == [
        "Receptionist",
        "GP",
        "Nurse",
        "Admin",
        "PracticeOwner",
    ]
    assert authority["required_capability"] == "appointment.cancel.confirm"
    assert authority["check_points"] == [
        "after_practice_scoped_appointment_lock",
        "while_practice_appointment_and_idempotency_locks_held",
    ]
    assert authority["authority_and_practice_scoped_target_precede_receipt_disclosure"]

    assert evidence["required_fields"] == [
        "schema_version",
        "purpose",
        "key_id",
        "practice_id",
        "actor_user_id",
        "authenticated_session_digest",
        "operation_id",
        "route_family",
        "target_appointment_id",
        "proposal_nonce",
        "proposal_generated_at",
        "signed_at",
        "expires_at",
        "pre_state_version",
        "pre_status",
        "pre_waiting_area_id",
        "pre_cancellation_reason",
        "pre_status_reason_code",
        "proposed_status_reason_code",
        "proposed_cancellation_reason",
        "required_warning_codes",
        "proposal_freshness_id",
        "command_digest",
        "signature",
    ]
    assert evidence["freshness_interval"] == (
        "proposal_generated_at_le_signed_at_le_confirmed_at_le_expires_at"
    )
    assert evidence["event_or_model_evidence_accepted"] is False


def test_canonical_confirmation_time_is_inside_evidence_validity_interval() -> None:
    packet = _load(PACKET_PATH)
    timestamps = {
        key: datetime.fromisoformat(value.replace("Z", "+00:00"))
        for key, value in packet["fixed_timestamps_utc"].items()
    }
    assert (
        timestamps["proposal_generated_at"]
        <= timestamps["signed_at"]
        <= timestamps["confirmed_at"]
        <= timestamps["expires_at"]
    )
    assert timestamps["committed_at"] >= timestamps["confirmed_at"]

    schema = _load(SCHEMA_PATH)
    expired = json.loads(json.dumps(packet))
    expired["fixed_timestamps_utc"]["expires_at"] = "2026-08-15T01:52:49Z"
    assert validate_packet(expired, schema)


def test_transaction_idempotency_atomic_readback_and_ingress_contracts_are_exact() -> (
    None
):
    packet = _load(PACKET_PATH)
    assert packet["transaction_contract"]["global_lock_order"] == [
        "practice",
        "schedule_domain",
        "appointment",
        "idempotency_record",
    ]
    assert packet["transaction_contract"]["kernel_lock_plan"] == LOCK_ORDER
    assert (
        packet["transaction_contract"]["authority_fence_physical_mapping_proven"]
        is False
    )
    assert packet["idempotency_contract"][
        "receipt_disclosure_requires_current_authority"
    ]
    assert packet["idempotency_contract"]["in_progress_on_rollback"] == (
        "discarded_with_transaction"
    )
    assert packet["atomic_effect_contract"]["publish_together"] == [
        "appointment_soft_cancel",
        "attributable_delete_audit",
        "completed_idempotency_receipt",
    ]
    assert packet["atomic_effect_contract"]["post_state_version_rule"] == (
        "pre_state_version_plus_one"
    )
    assert packet["readback_contract"]["transaction_proof"] is False
    assert packet["readback_contract"]["timing"] == "after_atomic_commit"
    assert packet["compatibility_ingress_policy"]["admitted_ingress"] == [
        "delete-confirm"
    ]
    assert (
        packet["compatibility_ingress_policy"]["second_cancellation_kernel_allowed"]
        is False
    )


def test_exact_lock_order_on_every_schedule_and_both_authority_checks_before_replay() -> (
    None
):
    packet = _load(PACKET_PATH)
    assert packet["kernel_lock_plan"] == LOCK_ORDER
    assert packet["global_lock_order"] == [
        "practice",
        "schedule_domain",
        "appointment",
        "idempotency_record",
    ]
    assert packet["unused_lock_rule"] == "skip_schedule_domain_without_reordering"
    for schedule in packet["transaction_schedules"]:
        assert schedule["lock_plan"] == LOCK_ORDER
        trace = schedule["trace"]
        assert trace.index("lock:practice") < trace.index("lock:appointment")
        assert trace.index("lock:appointment") < trace.index(
            "check:authority_after_target_lock"
        )
        assert trace.index("check:authority_after_target_lock") < trace.index(
            "lock:idempotency_record"
        )
        assert trace.index("lock:idempotency_record") < trace.index(
            "check:authority_all_locks_held"
        )
        assert trace.index("check:authority_all_locks_held") < trace.index(
            "inspect:idempotency"
        )


def test_structured_reason_allowlist_optional_text_bound_and_cross_artifact_preservation() -> (
    None
):
    packet = _load(PACKET_PATH)
    missing = _decision(packet, "ddc-003-reason-missing")
    assert missing["expected"]["outcome"] == "validation_rejected"
    assert missing["expected"]["reason"] == "structured_reason_required"
    assert missing["expected"]["planned_effect"] is False

    allowlist = _decision(packet, "ddc-004-reason-allowlist-invalid")
    assert allowlist["expected"]["reason"] == "reason_allowlist_invalid"
    legacy = _decision(packet, "ddc-006-reason-legacy-unclassified")
    assert legacy["expected"]["reason"] == "legacy_reason_code_rejected"
    family = _decision(packet, "ddc-005-reason-status-family")
    assert family["expected"]["reason"] == "status_family_reason_rejected"
    too_long = _decision(packet, "ddc-007-optional-text-too-long")
    assert too_long["expected"]["reason"] == "cancellation_reason_too_long"
    assert too_long["expected"]["outcome"] == "validation_rejected"

    assert "LEGACY_UNCLASSIFIED" not in CANCELLED_REASON_CODES
    assert packet["max_cancellation_reason_length"] == MAX_FREE_TEXT_LENGTH == 500

    committed = _schedule(packet, "ddt-001-clean-commit-no-waiting-area")
    state = committed["expected"]["durable_state"]
    assert state["claim_state"] == "completed"
    artifacts = state["artifacts"]
    reason_values = {
        artifacts["appointment"]["cancellation_reason"],
        artifacts["audit"]["cancellation_reason"],
        artifacts["receipt"]["cancellation_reason"],
    }
    assert len(reason_values) == 1
    assert len(artifacts["appointment"]["cancellation_reason"]) <= 500
    code_values = {
        artifacts["appointment"]["status_reason_code"],
        artifacts["audit"]["status_reason_code"],
        artifacts["receipt"]["status_reason_code"],
    }
    assert len(code_values) == 1
    assert code_values.pop() in CANCELLED_REASON_CODES


def test_optional_null_cancellation_text_commits_and_is_preserved_exactly() -> None:
    packet = _load(PACKET_PATH)
    decision = _decision(packet, "ddc-046-optional-null-text-commit")
    assert decision["cancellation_text"] == "null"
    assert decision["expected"]["outcome"] == "committed"
    schedule = _schedule(packet, "ddt-015-clean-commit-null-cancellation-text")
    assert schedule["cancellation_text"] == "null"
    artifacts = schedule["expected"]["durable_state"]["artifacts"]
    assert artifacts is not None
    for name in ("appointment", "audit", "receipt"):
        assert artifacts[name]["cancellation_reason"] is None


def test_waiting_area_is_cleared_in_appointment_audit_and_receipt() -> None:
    packet = _load(PACKET_PATH)
    with_waiting = _schedule(packet, "ddt-002-clean-commit-with-waiting-area")
    assert with_waiting["waiting_area_present"] is True
    state = with_waiting["expected"]["durable_state"]
    assert state["appointment_status"] == "Cancelled"
    assert state["waiting_area_id"] is None
    artifacts = state["artifacts"]
    assert artifacts["appointment"]["waiting_area_id"] is None
    assert artifacts["audit"]["waiting_area_id_after"] is None
    assert artifacts["receipt"]["waiting_area_id"] is None
    for key in ("appointment", "audit", "receipt"):
        assert artifacts[key]["cancellation_reason"] is not None
        assert artifacts[key]["status_reason_code"] == "PATIENT_CANCELLED"
    assert artifacts["audit"]["confirmed_warning_codes"] == ["waiting_area_cleared"]


def test_completed_artifacts_have_exact_identity_and_field_sets() -> None:
    packet = _load(PACKET_PATH)
    required = packet["atomic_effect_contract"]
    state = _schedule(packet, "ddt-001-clean-commit-no-waiting-area")["expected"][
        "durable_state"
    ]
    artifacts = state["artifacts"]
    assert artifacts is not None
    assert set(artifacts["appointment"]) == set(required["appointment_required_fields"])
    assert set(artifacts["audit"]) == set(required["audit_required_fields"])
    assert set(artifacts["receipt"]) == set(required["receipt_required_fields"])
    assert artifacts["appointment"]["practice_id"] == artifacts["audit"]["practice_id"]
    assert artifacts["audit"]["practice_id"] == artifacts["receipt"]["practice_id"]
    assert (
        artifacts["appointment"]["appointment_id"]
        == artifacts["audit"]["appointment_id"]
    )
    assert (
        artifacts["audit"]["appointment_id"]
        == artifacts["receipt"]["target_appointment_id"]
    )
    assert artifacts["audit"]["audit_id"] == artifacts["receipt"]["audit_id"]
    for name in ("appointment", "audit", "receipt"):
        assert artifacts[name]["post_state_version"] == (
            artifacts[name]["pre_state_version"] + 1
        )


def test_every_precommit_injection_rolls_back_appointment_audit_receipt_and_claim() -> (
    None
):
    packet = _load(PACKET_PATH)
    precommit = {
        "before_locks",
        "after_staged_mutation",
        "after_staged_audit",
        "after_staged_receipt",
    }
    seen = set()
    for schedule in packet["transaction_schedules"]:
        if schedule["injection"] not in precommit:
            continue
        seen.add(schedule["injection"])
        result = simulate_schedule(schedule)
        durable = result["durable_state"]
        assert result["participant_results"] == ["transaction_rolled_back"]
        assert result["response_delivered"] is False
        assert result["readback"]["authorised"] is False
        assert durable["mutation_count"] == 0
        assert durable["audit_count"] == 0
        assert durable["completed_receipt_count"] == 0
        assert durable["appointment_version"] == 7
        assert durable["receipt_id"] is None
        assert durable["claim_state"] == "none"
        assert durable["artifacts"] is None
    assert seen == precommit


def test_lost_response_is_durable_and_retry_is_one_commit_plus_one_replay() -> None:
    packet = _load(PACKET_PATH)
    lost = _schedule(packet, "ddt-007-response-loss-after-commit")
    retry = _schedule(packet, "ddt-008-retry-after-lost-response")
    lost_result = simulate_schedule(lost)
    retry_result = simulate_schedule(retry)
    assert lost_result["participant_results"] == ["committed"]
    assert lost_result["response_delivered"] is False
    assert lost_result["durable_state"]["mutation_count"] == 1
    assert lost_result["durable_state"]["audit_count"] == 1
    assert lost_result["durable_state"]["completed_receipt_count"] == 1
    assert retry_result["participant_results"] == ["committed", "idempotent_replay"]
    assert retry_result["durable_state"]["mutation_count"] == 1
    assert retry_result["durable_state"]["audit_count"] == 1
    assert retry_result["durable_state"]["completed_receipt_count"] == 1


def test_same_key_conflict_and_different_key_overlap_winner_loser() -> None:
    packet = _load(PACKET_PATH)
    expected = {
        "ddt-009-same-key-same-digest": "idempotent_replay",
        "ddt-010-same-key-different-digest": "idempotency_conflict",
        "ddt-011-different-key-overlap": "stale_precondition",
        "ddt-012-authority-loss-while-waiting": "authority_revoked",
    }
    for schedule_id, loser in expected.items():
        schedule = _schedule(packet, schedule_id)
        result = simulate_schedule(schedule)
        assert result["participant_results"] == ["committed", loser]
        assert result["durable_state"]["mutation_count"] == 1
        assert result["durable_state"]["audit_count"] == 1
        assert result["durable_state"]["completed_receipt_count"] == 1


def test_post_commit_readback_is_separately_authorised() -> None:
    packet = _load(PACKET_PATH)
    current = _schedule(packet, "ddt-013-readback-current-authority")
    denied = _schedule(packet, "ddt-014-readback-denied-after-revocation")
    current_result = simulate_schedule(current)
    denied_result = simulate_schedule(denied)
    assert current_result["readback"]["authorised"] is True
    assert current_result["readback"]["status"] == "Cancelled"
    assert current_result["readback"]["state_version"] == 8
    assert denied_result["readback"]["authorised"] is False
    assert denied_result["durable_state"]["appointment_status"] == "Cancelled"
    assert denied_result["durable_state"]["mutation_count"] == 1


def test_raw_status_event_model_channel_ingress_cannot_self_confirm_or_execute() -> (
    None
):
    packet = _load(PACKET_PATH)
    for scenario_id in (
        "ddc-028-raw-delete-rejected",
        "ddc-029-status-fallback-rejected",
        "ddc-030-event-evidence-rejected",
        "ddc-031-model-channel-confirmation-rejected",
    ):
        scenario = _decision(packet, scenario_id)
        assert scenario["expected"]["admission"] == "admission_rejected"
        assert scenario["expected"]["outcome"] is None
        assert scenario["expected"]["planned_effect"] is False
        assert scenario["expected"]["receipt_disclosed"] is False


def test_every_hostile_mutation_fails_closed() -> None:
    packet = _load(PACKET_PATH)
    schema = _load(SCHEMA_PATH)
    mutations = hostile_mutations(packet)
    assert len(mutations) >= 40
    for name, candidate in mutations:
        assert validate_packet(candidate, schema), name


def test_script_has_no_application_database_network_or_provider_import() -> None:
    tree = ast.parse(
        (
            ROOT
            / "scripts/raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission.py"
        ).read_text(encoding="utf-8")
    )
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    forbidden_roots = {
        "app",
        "sqlalchemy",
        "psycopg",
        "requests",
        "httpx",
        "socket",
        "subprocess",
        "google",
        "anthropic",
        "openai",
    }
    assert not {name.split(".")[0] for name in imported}.intersection(forbidden_roots)
