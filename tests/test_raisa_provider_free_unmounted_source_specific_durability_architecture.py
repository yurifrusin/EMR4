import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs/raisa-provider-free-unmounted-source-specific-durability-architecture-plan.md"
)
DESIGN = (
    ROOT
    / "docs/raisa-provider-free-unmounted-source-specific-durability-architecture-design.md"
)
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-unmounted-source-specific-durability-architecture-threat-model-delta.md"
)
CONTRACT_DIR = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-unmounted-source-specific-durability-architecture"
)
CONTRACT = CONTRACT_DIR / "durability-contract.json"
SCHEMA = CONTRACT_DIR / "durability-contract.schema.json"
CRITICAL_LIST_PATHS = (
    ("source_coordinate", "producer_transaction_members"),
    ("payload_free_projection", "allowed_fields"),
    ("payload_free_projection", "prohibited_fields"),
    ("checkpoint", "key_fields"),
    ("atomic_transaction", "commit_members"),
    ("audit", "allowed_fields"),
    ("audit", "prohibited_fields"),
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def contract() -> dict:
    return _json(CONTRACT)


@pytest.fixture(scope="module")
def validator() -> Draft202012Validator:
    schema = _json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def test_contract_is_closed_and_schema_valid(
    contract: dict, validator: Draft202012Validator
) -> None:
    assert list(validator.iter_errors(contract)) == []
    assert contract["schema_version"] == (
        "raisa.context_fabric.source_specific_durability_architecture.v1"
    )
    assert contract["status"] == "architecture_only"


def test_exact_source_rejects_existing_delivery_cursor(contract: dict) -> None:
    source = contract["source_profile"]
    assert source == {
        "source_system": "emr4-diary",
        "event_type": "diary.appointment_rescheduled",
        "event_schema_version": "diary.appointment_rescheduled.v1",
        "aggregate_class": "APPOINTMENT",
        "stream_id": "emr4:diary:appointment-rescheduled:v1",
        "stream_partition": "practice",
        "stream_epoch": 1,
        "existing_delivery_cursor_eligible": False,
        "existing_delivery_expiry_eligible": False,
        "existing_payload_eligible": False,
        "future_control_projection": "diary_context_observation_outbox_v1",
    }


def test_principals_preserve_observe_persist_and_read_separation(
    contract: dict,
) -> None:
    principals = contract["principals"]
    observer = principals["observation_integration"]
    coordinator = principals["durability_coordinator"]
    fresh = principals["fresh_read"]

    assert observer["select_payload_free_projection"] is True
    for field in (
        "select_payload_or_product_tables",
        "reuses_staff_jwt_or_application_session",
        "persistence_authority",
        "fresh_read_authority",
        "provider_authority",
        "command_authority",
    ):
        assert observer[field] is False
    assert coordinator["atomic_durability_transaction_only"] is True
    assert coordinator["select_source_payload"] is False
    assert fresh["fresh_context_scope_grant_required"] is True
    assert fresh["inherits_observer_or_checkpoint_authority"] is False
    assert len({observer["principal_id"], coordinator["principal_id"]}) == 2


def test_source_position_is_transactional_and_rollback_safe(contract: dict) -> None:
    coordinate = contract["source_coordinate"]
    assert coordinate["head_kind"] == "transactional_locked_row"
    assert coordinate["partition_key"] == ["practice_id", "stream_id"]
    assert coordinate["baseline_position"] == 0
    assert coordinate["next_position_rule"] == "last_position_plus_one"
    assert coordinate["predecessor_rule"] == "equals_last_position"
    assert coordinate["rollback_reuses_position"] is True
    assert coordinate["aggregate_revision_role"] == (
        "freshness_anomaly_only_not_stream_continuity"
    )
    assert set(coordinate["producer_transaction_members"]) == {
        "appointment_truth",
        "appointment_audit",
        "idempotency_completion",
        "existing_committed_event",
        "stream_head_update",
        "payload_free_control_row",
    }
    for field in (
        "postgres_sequence_or_identity_allowed",
        "occurred_at_or_event_id_allowed",
        "transaction_id_or_commit_timestamp_allowed",
        "wal_lsn_allowed",
        "counter_wrap_allowed",
    ):
        assert coordinate[field] is False


def test_projection_is_payload_free_and_excludes_product_coordinates(
    contract: dict,
) -> None:
    projection = contract["payload_free_projection"]
    allowed = set(projection["allowed_fields"])
    prohibited = set(projection["prohibited_fields"])
    assert allowed.isdisjoint(prohibited)
    assert {
        "transaction_position",
        "predecessor_position",
        "backend_aggregate_alias",
        "raw_nonsemantic_event_uuid",
    } <= allowed
    assert {
        "event_payload",
        "appointment_id",
        "practitioner_id",
        "location_id",
        "start_time",
        "end_time",
        "actor_user_id",
        "command_id",
        "correlation_id",
        "reason_text",
    } <= prohibited


def test_checkpoint_means_classified_not_observed(contract: dict) -> None:
    checkpoint = contract["checkpoint"]
    assert checkpoint["states"] == [
        "ACTIVE",
        "REBASE_REQUIRED",
        "CONSUMED",
        "REVOKED",
    ]
    assert checkpoint["means_classified_through_position"] is True
    assert checkpoint["observed_cursor_can_advance"] is False
    assert checkpoint["in_memory_decision_can_advance"] is False
    assert checkpoint["command_or_read_authority"] is False


def test_frame_currentness_uses_durable_watermark_and_read_fence(
    contract: dict,
) -> None:
    fence = contract["frame_fence"]
    assert fence["invalidation_state"] == "monotonic_durable_watermark"
    assert fence["watermark_key"] == [
        "practice_binding_digest",
        "stream_id",
        "stream_epoch",
        "observer_generation",
        "frame_type",
    ]
    assert fence["frame_requires_assembled_through_position"] is True
    assert fence["watermark_newer_than_frame_means_non_current"] is True
    assert fence["in_memory_only_retirement_allowed"] is False
    assert fence["replacement_read_fence"] == (
        "same_snapshot_or_equal_before_after_source_head"
    )
    assert fence["raced_or_unverifiable_replacement_release_allowed"] is False


def test_atomic_transaction_never_separates_invalidation_from_checkpoint(
    contract: dict,
) -> None:
    transaction = contract["atomic_transaction"]
    assert transaction["lock_checkpoint_first"] is True
    assert transaction["all_or_nothing"] is True
    assert set(transaction["commit_members"]) == {
        "classified_observation_receipt",
        "monotonic_invalidation_watermark",
        "coalesced_reassembly_obligation",
        "privacy_safe_audit",
        "positive_checkpoint_advance_or_hold",
    }
    assert transaction["one_obligation_per_frame_generation"] is True
    assert transaction["restore_retired_frame_allowed"] is False
    assert transaction["source_or_fresh_read_executed"] is False


def test_decision_dispositions_distinguish_known_invalidation_from_gap(
    contract: dict,
) -> None:
    outcomes = contract["decision_dispositions"]
    assert outcomes["contiguous_full_invalidation"] == (
        "advance_only_after_all_potentially_affected_frames_retired"
    )
    assert outcomes["coverage_gap"] == ("hold_checkpoint_full_invalidate_and_rebase")
    assert outcomes["exact_redelivery"] == ("return_existing_receipt_without_mutation")
    assert outcomes["same_position_identity_mismatch"] == outcomes["coverage_gap"]
    assert (
        outcomes["observation_digest_reused_at_new_position"]
        == outcomes["coverage_gap"]
    )
    assert outcomes["malformed_or_foreign_or_wrong_contract"] == (
        "no_checkpoint_change_and_stop_generation"
    )


def test_restart_retention_and_overflow_fail_closed(contract: dict) -> None:
    lifecycle = contract["restart_and_retention"]
    assert lifecycle["resume_requires_exact_next_retained_position"] is True
    assert lifecycle["resume_requires_predecessor_match"] is True
    assert (
        lifecycle[
            "resume_requires_policy_binding_registry_impact_and_key_schedule_match"
        ]
        is True
    )
    assert lifecycle["existing_event_ttl_controls_retention"] is False
    assert lifecycle["drop_or_sample_on_overflow"] is False
    assert lifecycle["missing_or_corrupt_checkpoint_disposition"] == (
        "full_invalidate_and_new_generation"
    )
    assert lifecycle["continuity_loss_disposition"] == (
        "full_invalidate_and_new_baseline"
    )


def test_key_rotation_is_position_bound_and_contains_no_key_material(
    contract: dict,
) -> None:
    rotation = contract["key_rotation"]
    assert rotation["schedule_basis"] == (
        "non_overlapping_transaction_position_intervals"
    )
    assert rotation["dedicated_identity_key_ring"] is True
    assert rotation["reuse_application_or_auth_or_provider_secret"] is False
    assert rotation["try_all_keys_allowed"] is False
    assert (
        rotation[
            "routine_rotation_preserves_generation_only_with_valid_position_fence_and_overlap"
        ]
        is True
    )
    assert rotation["key_material_in_source_checkpoint_audit_or_evidence"] is False
    assert rotation["raw_event_id_persisted_after_normalization"] is False
    assert rotation["old_key_destroyed_before_all_dependent_positions_drain"] is False
    assert rotation["retroactive_schedule_change_allowed"] is False
    assert rotation["missing_required_key_disposition"] == (
        "full_invalidate_and_new_generation"
    )


def test_audit_is_minimized_and_non_authoritative(contract: dict) -> None:
    audit = contract["audit"]
    allowed = set(audit["allowed_fields"])
    prohibited = set(audit["prohibited_fields"])
    assert allowed.isdisjoint(prohibited)
    assert {
        "checkpoint_disposition",
        "retired_coalesced_and_backlog_count_buckets",
        "prior_audit_record_digest",
    } <= allowed
    assert {
        "raw_event_id",
        "key_material",
        "event_payload",
        "aggregate_alias_or_resolved_id",
        "active_session_inventory",
        "frame_content",
        "free_text",
    } <= prohibited
    assert audit["bureau_memory_or_context_authority"] is False
    assert audit["read_or_command_evidence"] is False


def test_all_effect_ceilings_are_false(contract: dict) -> None:
    ceilings = contract["effect_ceilings"]
    assert len(ceilings) == 11
    assert set(ceilings.values()) == {False}


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("source_profile", "existing_delivery_cursor_eligible"), True),
        (("principals", "observation_integration", "persistence_authority"), True),
        (("principals", "durability_coordinator", "select_source_payload"), True),
        (("source_coordinate", "head_kind"), "postgres_sequence"),
        (("source_coordinate", "rollback_reuses_position"), False),
        (("frame_fence", "in_memory_only_retirement_allowed"), True),
        (("frame_fence", "raced_or_unverifiable_replacement_release_allowed"), True),
        (("checkpoint", "observed_cursor_can_advance"), True),
        (("atomic_transaction", "all_or_nothing"), False),
        (("restart_and_retention", "drop_or_sample_on_overflow"), True),
        (("key_rotation", "retroactive_schedule_change_allowed"), True),
        (("key_rotation", "reuse_application_or_auth_or_provider_secret"), True),
        (("audit", "read_or_command_evidence"), True),
        (("effect_ceilings", "database_or_source_contact"), True),
    ],
)
def test_schema_rejects_authority_or_durability_widening(
    contract: dict,
    validator: Draft202012Validator,
    path: tuple[str, ...],
    value: object,
) -> None:
    candidate = copy.deepcopy(contract)
    current = candidate
    for part in path[:-1]:
        current = current[part]
    current[path[-1]] = value
    assert list(validator.iter_errors(candidate))


def test_schema_rejects_unknown_fields(
    contract: dict, validator: Draft202012Validator
) -> None:
    candidate = copy.deepcopy(contract)
    candidate["source_profile"]["cursor"] = "not-allowed"
    assert list(validator.iter_errors(candidate))


@pytest.mark.parametrize("path", CRITICAL_LIST_PATHS)
@pytest.mark.parametrize("operation", ("append", "remove", "replace", "reorder"))
def test_schema_rejects_every_critical_list_mutation(
    contract: dict,
    validator: Draft202012Validator,
    path: tuple[str, str],
    operation: str,
) -> None:
    candidate = copy.deepcopy(contract)
    values = candidate[path[0]][path[1]]
    if operation == "append":
        values.append("patient_id")
    elif operation == "remove":
        values.pop()
    elif operation == "replace":
        values[0] = "patient_id"
    else:
        values.reverse()
    assert list(validator.iter_errors(candidate))


def test_documents_freeze_exact_durability_and_later_gate() -> None:
    joined = "\n".join((_text(PLAN), _text(DESIGN), _text(THREAT))).lower()
    for phrase in (
        "transactionally updated row",
        "not a postgresql `sequence`",
        "payload-free control projection",
        "persistence_authority: false",
        "atomic decision-invalidation-checkpoint transaction",
        "all nine effects commit or roll back together",
        "rebase_required",
        "minimum eligible checkpoint",
        "non-overlapping position intervals",
        "privacy-safe audit",
        "separate later migration",
        "architecture-only",
    ):
        assert phrase in joined


def test_forbidden_runtime_surfaces_remain_closed() -> None:
    joined = "\n".join((_text(PLAN), _text(THREAT))).lower()
    for phrase in (
        "no `app/**`",
        "`alembic/**`",
        "no `docs/diary/**`",
        "database migration",
        "outbox, feed",
        "checkpoint store",
        "product/source read",
        "patient/product/protected",
        "provider/external retrieval",
        "command/write",
        "runtime wiring",
        "deployment",
        "production",
        "release",
        "pages",
        "protected-ref movement",
        "preserve and\nexclude `docs/branding/`",
    ):
        assert phrase in joined
