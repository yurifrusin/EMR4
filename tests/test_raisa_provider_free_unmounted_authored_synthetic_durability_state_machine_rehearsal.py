from __future__ import annotations

from dataclasses import asdict, replace
import copy
import inspect
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts.raisa_provider_free_unmounted_authored_synthetic_durability_state_machine_rehearsal_acceptance import (
    CASE_SPECS,
    CONTRACT_PATH,
    EVIDENCE_PATH,
    SCHEMA_PATH,
    generate,
)

from scripts.raisa_provider_free_unmounted_authored_synthetic_durability_state_machine_rehearsal import (
    EFFECT_CEILINGS,
    FAULT_MEMBERS,
    FRAME_TYPES,
    Candidate,
    GenerationCensus,
    KeyInterval,
    KeyScheduleTransition,
    RetainedRow,
    RetentionAnchor,
    apply_key_rotation,
    authoritative_retention_anchor,
    build_initial_state,
    candidate_for,
    digest_value,
    recovery_anchor,
    restart,
    retention_eligibility,
    seal_census,
    seal_state,
    synthetic_digest,
    transition,
    validate_key_schedule,
    verify_state,
)


def test_relevant_transition_selectively_retires_and_advances_atomically() -> None:
    state = build_initial_state()
    result = transition(state, candidate_for(state, position=5))

    assert result.mutation_committed is True
    assert result.state.last_classified_position == 5
    assert result.state.last_observation_digest == synthetic_digest("observation:5")
    assert dict(result.state.watermarks) == {
        FRAME_TYPES[0]: 5,
        FRAME_TYPES[1]: 0,
    }
    assert [frame.lifecycle for frame in result.state.frames] == ["RETIRED", "CURRENT"]
    assert len(result.state.obligations) == 1
    assert result.state.obligations[0].count_bucket == "ONE"
    assert result.state.generation_census.members[-1].checkpoint_position == 5
    assert verify_state(result.state)


def test_exact_redelivery_is_derived_and_returns_identical_state_value() -> None:
    first = transition(build_initial_state(), candidate_for(build_initial_state(), position=5))
    replay = candidate_for(first.state, position=5)
    result = transition(first.state, replay)

    assert result.disposition == "EXACT_REDELIVERY"
    assert result.mutation_committed is False
    assert result.state is first.state
    assert result.receipt == first.receipt


def test_no_intersection_receipts_audits_and_advances_without_invalidation() -> None:
    state = build_initial_state()
    candidate = candidate_for(
        state,
        position=5,
        decision="CONTIGUOUS_NO_INTERSECTION",
        affected_frame_types=(),
    )
    result = transition(state, candidate)

    assert result.disposition == "ADVANCE_AFTER_RECEIPT_AND_AUDIT"
    assert result.state.last_classified_position == 5
    assert result.state.frames == state.frames
    assert result.state.watermarks == state.watermarks
    assert result.state.obligations == ()
    assert len(result.state.receipts) == len(state.receipts) + 1
    assert len(result.state.audits) == 1


def test_later_relevant_cause_coalesces_one_obligation_and_never_reopens_frame() -> None:
    first = transition(build_initial_state(), candidate_for(build_initial_state(), position=5)).state
    second = transition(first, candidate_for(first, position=6)).state

    assert len(second.obligations) == 1
    obligation = second.obligations[0]
    assert obligation.first_position == 5
    assert obligation.latest_position == 6
    assert obligation.count_bucket == "TWO_TO_FOUR"
    assert second.frames[0].lifecycle == "RETIRED"


def test_full_invalidation_retires_both_frame_types() -> None:
    state = build_initial_state()
    candidate = candidate_for(
        state,
        position=5,
        decision="CONTIGUOUS_FULL_INVALIDATION",
        affected_frame_types=FRAME_TYPES,
    )
    result = transition(state, candidate)

    assert all(frame.lifecycle == "RETIRED" for frame in result.state.frames)
    assert dict(result.state.watermarks) == {FRAME_TYPES[0]: 5, FRAME_TYPES[1]: 5}
    assert len(result.state.obligations) == 2
    assert result.state.last_classified_position == 5


@pytest.mark.parametrize("fault", FAULT_MEMBERS)
def test_each_atomic_member_failure_leaves_exact_original_state(fault: str) -> None:
    state = build_initial_state()
    result = transition(state, candidate_for(state, position=5), fail_before=fault)

    assert result.disposition == "ROLLED_BACK"
    assert result.state is state
    assert result.receipt is None
    assert result.mutation_committed is False


def test_gap_same_position_mismatch_and_digest_reuse_hold_checkpoint_and_rebase() -> None:
    state = build_initial_state()
    gap = replace(candidate_for(state, position=7), predecessor_position=4)
    gap_result = transition(state, gap)
    assert gap_result.disposition == "REBASE_REQUIRED"
    assert gap_result.state.last_classified_position == 4
    assert gap_result.state.checkpoint_state == "REBASE_REQUIRED"
    assert all(frame.lifecycle == "RETIRED" for frame in gap_result.state.frames)

    mismatch = replace(
        candidate_for(state, position=4),
        observation_digest=synthetic_digest("replacement-at-four"),
    )
    mismatch_result = transition(state, mismatch)
    assert mismatch_result.disposition == "REBASE_REQUIRED"
    assert mismatch_result.state.last_classified_position == 4

    reused = replace(
        candidate_for(state, position=5),
        observation_digest=state.receipts[0].observation_digest,
    )
    reused_result = transition(state, reused)
    assert reused_result.disposition == "REBASE_REQUIRED"
    assert reused_result.state.last_classified_position == 4


def test_malformed_or_foreign_candidate_stops_without_suppression_marker() -> None:
    state = build_initial_state()
    foreign = replace(
        candidate_for(state, position=5),
        practice_binding_digest=synthetic_digest("foreign-practice"),
    )
    result = transition(state, foreign)
    assert result.disposition == "STOP_GENERATION"
    assert result.state is state
    assert result.receipt is None

    with pytest.raises(TypeError):
        Candidate(**(asdict(candidate_for(state, position=5)) | {"payload": "forbidden"}))


def test_resealed_state_mutations_fail_cross_link_and_lifecycle_validation() -> None:
    state = build_initial_state()
    wrong_schedule_digest = seal_state(
        replace(state, key_schedule_digest=synthetic_digest("different-schedule"))
    )
    assert not verify_state(wrong_schedule_digest)

    stale_current = seal_state(
        replace(
            state,
            watermarks=((FRAME_TYPES[0], 5), (FRAME_TYPES[1], 0)),
            integrity_digest="",
        )
    )
    assert not verify_state(stale_current)

    bad_receipt = replace(state.receipts[0], decision="CALLER_ASSERTED_REDELIVERY")
    resealed_receipt = seal_state(
        replace(state, receipts=(bad_receipt,), integrity_digest="")
    )
    assert not verify_state(resealed_receipt)

    wrong_member = replace(state.generation_census.members[-1], state="REBASE_REQUIRED")
    wrong_census = seal_census(
        replace(
            state.generation_census,
            members=(state.generation_census.members[0], wrong_member),
            census_digest="",
        )
    )
    resealed_census = seal_state(
        replace(state, generation_census=wrong_census, integrity_digest="")
    )
    assert not verify_state(resealed_census)


def test_resealed_receipt_order_and_digest_reuse_are_rejected() -> None:
    state = build_initial_state()
    state = transition(state, candidate_for(state, position=5)).state
    state = transition(state, candidate_for(state, position=6)).state

    reordered = seal_state(
        replace(
            state,
            receipts=(state.receipts[0], state.receipts[2], state.receipts[1]),
            integrity_digest="",
        )
    )
    assert not verify_state(reordered)

    reused_digest = replace(
        state.receipts[2],
        observation_digest=state.receipts[1].observation_digest,
    )
    duplicated = seal_state(
        replace(
            state,
            receipts=(state.receipts[0], state.receipts[1], reused_digest),
            integrity_digest="",
        )
    )
    assert not verify_state(duplicated)


@pytest.mark.parametrize(
    "mutation",
    (
        "reorder",
        "duplicate_id",
        "prior_chain",
        "receipt_link",
        "decision_detach",
        "state_control",
        "future_revision",
    ),
)
def test_resealed_audit_chain_and_receipt_links_are_rejected(mutation: str) -> None:
    state = build_initial_state()
    state = transition(state, candidate_for(state, position=5)).state
    state = transition(state, candidate_for(state, position=6)).state
    first, second = state.audits

    if mutation == "reorder":
        audits = (second, first)
    elif mutation == "duplicate_id":
        audits = (first, replace(second, opaque_audit_id=first.opaque_audit_id))
    elif mutation == "prior_chain":
        audits = (
            first,
            replace(second, prior_audit_digest=synthetic_digest("forged-prior")),
        )
    elif mutation == "receipt_link":
        forged_digest = synthetic_digest("unlinked-observation")
        audits = (
            first,
            replace(
                second,
                observation_digest=forged_digest,
                opaque_audit_id=(
                    "audit:"
                    + digest_value(
                        [state.observer_generation, second.position, forged_digest]
                    )[7:31]
                ),
            ),
        )
    elif mutation == "decision_detach":
        forged_first = replace(
            first,
            decision="FULL_INVALIDATION_REQUIRED",
            reason="COVERAGE_GAP",
            affected_frame_types=FRAME_TYPES,
            checkpoint_disposition="HOLD_AND_REBASE",
        )
        audits = (
            forged_first,
            replace(second, prior_audit_digest=digest_value(asdict(forged_first))),
        )
    elif mutation == "state_control":
        forged_first = replace(
            first,
            policy_digest=synthetic_digest("detached-policy"),
        )
        audits = (
            forged_first,
            replace(second, prior_audit_digest=digest_value(asdict(forged_first))),
        )
    else:
        audits = (
            first,
            replace(second, lifecycle_revision=state.lifecycle_revision + 1),
        )
    resealed = seal_state(replace(state, audits=audits, integrity_digest=""))
    assert not verify_state(resealed)


@pytest.mark.parametrize(
    "mutation",
    (
        "joint_no_intersection",
        "joint_wrong_disposition",
        "audit_schedule_digest",
        "audit_key_id",
        "audit_predecessor",
        "audit_lifecycle",
        "prefix_audit_deleted",
        "state_lifecycle_inflated",
        "frame_order",
        "obligation_semantics",
    ),
)
def test_resealed_semantic_effect_and_lifecycle_forgeries_are_rejected(
    mutation: str,
) -> None:
    state = build_initial_state()
    state = transition(state, candidate_for(state, position=5)).state
    receipt = state.receipts[-1]
    audit = state.audits[-1]

    if mutation == "joint_no_intersection":
        forged_receipt = replace(
            receipt,
            decision="CONTIGUOUS_NO_INTERSECTION",
            reason="NO_INTERSECTION",
            affected_frame_types=(),
            checkpoint_disposition="ADVANCE_AFTER_RECEIPT_AND_AUDIT",
        )
        forged_audit = replace(
            audit,
            decision=forged_receipt.decision,
            reason=forged_receipt.reason,
            affected_frame_types=forged_receipt.affected_frame_types,
            checkpoint_disposition=forged_receipt.checkpoint_disposition,
        )
        forged = replace(
            state,
            receipts=(state.receipts[0], forged_receipt),
            audits=(forged_audit,),
        )
    elif mutation == "joint_wrong_disposition":
        forged_receipt = replace(
            receipt,
            checkpoint_disposition="ADVANCE_AFTER_RECEIPT_AND_AUDIT",
        )
        forged = replace(
            state,
            receipts=(state.receipts[0], forged_receipt),
            audits=(
                replace(
                    audit,
                    checkpoint_disposition=forged_receipt.checkpoint_disposition,
                ),
            ),
        )
    elif mutation == "audit_schedule_digest":
        forged = replace(
            state,
            audits=(
                replace(
                    audit,
                    key_schedule_digest=synthetic_digest("detached-schedule"),
                ),
            ),
        )
    elif mutation == "audit_key_id":
        forged = replace(state, audits=(replace(audit, key_id="key:detached"),))
    elif mutation == "audit_predecessor":
        forged = replace(state, audits=(replace(audit, predecessor_position=0),))
    elif mutation == "audit_lifecycle":
        forged = replace(state, audits=(replace(audit, lifecycle_revision=1),))
    elif mutation == "prefix_audit_deleted":
        later = transition(state, candidate_for(state, position=6)).state
        remaining = replace(
            later.audits[-1],
            prior_audit_digest=synthetic_digest("audit:genesis"),
        )
        forged = replace(later, audits=(remaining,))
    elif mutation == "state_lifecycle_inflated":
        forged = replace(state, lifecycle_revision=state.lifecycle_revision + 9)
    elif mutation == "frame_order":
        forged = replace(state, frames=tuple(reversed(state.frames)))
    else:
        forged_obligation = replace(
            state.obligations[0],
            count_bucket="FIVE_PLUS",
        )
        forged = replace(state, obligations=(forged_obligation,))
    assert not verify_state(seal_state(replace(forged, integrity_digest="")))


def test_restart_requires_integrity_anchor_exact_next_row_and_sole_key() -> None:
    state = transition(build_initial_state(), candidate_for(build_initial_state(), position=5)).state
    anchor = recovery_anchor(state)
    row = RetainedRow(True, 6, 5, synthetic_digest("observation:6"), "key:alpha")
    resumed = restart(state, anchor, row)
    assert resumed.disposition == "RESUME"
    assert resumed.state is state

    gap = restart(state, anchor, replace(row, position=7))
    assert gap.disposition == "REBASE_REQUIRED"
    assert gap.state is not None
    assert gap.state.last_classified_position == anchor.last_classified_position

    missing = restart(state, anchor, None)
    assert missing.disposition == "REBASE_REQUIRED"
    assert missing.state is not None
    assert missing.state.last_classified_position == anchor.last_classified_position


def test_corrupt_or_unanchored_restart_never_adopts_candidate_coordinate() -> None:
    state = build_initial_state()
    anchor = recovery_anchor(state)
    corrupt = replace(
        state,
        last_classified_position=999,
        integrity_digest=synthetic_digest("forged-state"),
    )
    result = restart(corrupt, anchor, None)
    assert result.disposition == "NEW_GENERATION_REQUIRED"
    assert result.state is None

    wrong_anchor = replace(anchor, last_classified_position=999)
    result = restart(state, wrong_anchor, None)
    assert result.disposition == "NEW_GENERATION_REQUIRED"
    assert result.state is None


def test_key_intervals_and_atomic_future_fenced_rotation() -> None:
    state = build_initial_state()
    successor = (
        KeyInterval("key:alpha", 0, 7),
        KeyInterval("key:beta", 7, None),
    )
    rotation = KeyScheduleTransition(
        predecessor_schedule_digest=digest_value([asdict(item) for item in state.key_schedule]),
        successor_schedule=successor,
        activation_position=7,
        predecessor_key_id="key:alpha",
        successor_key_id="key:beta",
        maximum_dependent_position=6,
        predecessor_key_available_through_position=9,
        safety_overlap_positions=2,
    )
    result = apply_key_rotation(state, rotation)
    assert result.disposition == "ROTATION_COMMITTED"
    assert result.state.key_schedule == successor
    assert verify_state(result.state)

    for invalid in (
        replace(rotation, activation_position=4),
        replace(rotation, predecessor_key_available_through_position=7),
        replace(rotation, predecessor_key_id="key:missing"),
        replace(
            rotation,
            successor_schedule=(
                KeyInterval("key:alpha", 0, 6),
                KeyInterval("key:beta", 7, None),
            ),
        ),
        replace(
            rotation,
            successor_schedule=(
                KeyInterval("key:changed", 0, 7),
                KeyInterval("key:beta", 7, None),
            ),
        ),
    ):
        failed = apply_key_rotation(state, invalid)
        assert failed.disposition == "REBASE_REQUIRED"
        assert failed.state.last_classified_position == state.last_classified_position
        assert failed.state.checkpoint_state == "REBASE_REQUIRED"

    assert not validate_key_schedule(
        (KeyInterval("key:alpha", 0, 6), KeyInterval("key:beta", 7, None))
    )


def test_rotation_preserves_historical_audit_binding_and_future_transitions() -> None:
    state = build_initial_state()
    state = transition(state, candidate_for(state, position=5)).state
    predecessor_audit_digest = state.audits[-1].key_schedule_digest
    successor = (
        KeyInterval("key:alpha", 0, 7),
        KeyInterval("key:beta", 7, None),
    )
    rotation = KeyScheduleTransition(
        predecessor_schedule_digest=digest_value(
            [asdict(item) for item in state.key_schedule]
        ),
        successor_schedule=successor,
        activation_position=7,
        predecessor_key_id="key:alpha",
        successor_key_id="key:beta",
        maximum_dependent_position=6,
        predecessor_key_available_through_position=9,
        safety_overlap_positions=2,
    )
    state = apply_key_rotation(state, rotation).state
    assert verify_state(state)
    assert state.audits[-1].key_schedule_digest == predecessor_audit_digest

    state = transition(state, candidate_for(state, position=6)).state
    state = transition(state, candidate_for(state, position=7)).state
    assert state.audits[-1].key_id == "key:beta"
    assert verify_state(state)


def test_retention_uses_complete_integrity_bound_census_and_is_inert() -> None:
    state = build_initial_state()
    common = {
        "source_row_position": 0,
        "anchor": authoritative_retention_anchor(),
        "recovery_pin": False,
        "audit_pin": False,
        "key_overlap_closed": True,
        "safety_grace_elapsed": True,
    }
    eligible = retention_eligibility(state, **common)
    assert eligible.disposition == "ELIGIBLE"
    assert eligible.deletion_executed is False

    behind = retention_eligibility(state, **(common | {"source_row_position": 1}))
    assert behind.disposition == "DENIED"
    assert "MINIMUM_CHECKPOINT_BEHIND_ROW" in behind.reasons

    for change, reason in (
        ({"recovery_pin": True}, "RECOVERY_PIN_PRESENT"),
        ({"audit_pin": True}, "AUDIT_PIN_PRESENT"),
        ({"key_overlap_closed": False}, "KEY_OVERLAP_OPEN"),
        ({"safety_grace_elapsed": False}, "SAFETY_GRACE_PENDING"),
    ):
        denied = retention_eligibility(state, **(common | change))
        assert reason in denied.reasons


def test_omitted_or_duplicate_generation_census_cannot_authorize_retention() -> None:
    state = build_initial_state()
    anchor = authoritative_retention_anchor()
    omitted_census = seal_census(
        replace(
            state.generation_census,
            members=state.generation_census.members[1:],
            census_digest="",
        )
    )
    omitted_state = seal_state(
        replace(state, generation_census=omitted_census, integrity_digest="")
    )
    denied = retention_eligibility(
        omitted_state,
        source_row_position=4,
        anchor=anchor,
        recovery_pin=False,
        audit_pin=False,
        key_overlap_closed=True,
        safety_grace_elapsed=True,
    )
    assert denied.disposition == "DENIED"
    assert "COMPLETE_CENSUS_DIGEST_MISMATCH" in denied.reasons

    duplicate = GenerationCensus(
        registry_digest=state.registry_digest,
        members=(state.generation_census.members[0],) * 2,
        census_digest="",
    )
    duplicate = seal_census(duplicate)
    duplicate_state = seal_state(
        replace(state, generation_census=duplicate, integrity_digest="")
    )
    denied = retention_eligibility(
        duplicate_state,
        source_row_position=0,
        anchor=anchor,
        recovery_pin=False,
        audit_pin=False,
        key_overlap_closed=True,
        safety_grace_elapsed=True,
    )
    assert denied.disposition == "DENIED"
    assert "STATE_OR_CENSUS_INTEGRITY_INVALID" in denied.reasons

    self_echoed_anchor = RetentionAnchor(
        authority_kind="BACKEND_AUTHORED_RETENTION_CENSUS_ANCHOR",
        registry_digest=omitted_census.registry_digest,
        census_digest=omitted_census.census_digest,
        expected_observer_generations=(2,),
    )
    denied = retention_eligibility(
        omitted_state,
        source_row_position=4,
        anchor=self_echoed_anchor,
        recovery_pin=False,
        audit_pin=False,
        key_overlap_closed=True,
        safety_grace_elapsed=True,
    )
    assert denied.disposition == "DENIED"
    assert "RETENTION_ANCHOR_INVALID" in denied.reasons


def test_audit_is_minimized_and_all_effect_ceilings_are_false() -> None:
    state = transition(build_initial_state(), candidate_for(build_initial_state(), position=5)).state
    audit_keys = set(asdict(state.audits[-1]))
    prohibited = {
        "raw_event_id",
        "payload",
        "patient",
        "appointment",
        "practitioner",
        "location",
        "session",
        "provider_output",
        "free_text",
        "command",
    }
    assert not audit_keys & prohibited
    assert EFFECT_CEILINGS
    assert all(value is False for value in EFFECT_CEILINGS.values())

    source = inspect.getsource(
        __import__(
            "scripts.raisa_provider_free_unmounted_authored_synthetic_"
            "durability_state_machine_rehearsal",
            fromlist=["*"],
        )
    ).lower()
    for forbidden_import in (
        "import sqlalchemy",
        "import requests",
        "import httpx",
        "import socket",
        "import subprocess",
        "from app",
    ):
        assert forbidden_import not in source


def test_generated_contract_and_evidence_recompute_and_validate_draft_2020_12() -> None:
    contract, schema, evidence = generate()
    committed_contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    committed_schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    committed_evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))

    assert contract == committed_contract
    assert schema == committed_schema
    assert evidence == committed_evidence
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    assert not list(validator.iter_errors(contract))
    assert not list(validator.iter_errors(evidence))
    assert evidence["case_count"] == len(CASE_SPECS) == 33
    assert evidence["passed_case_count"] == evidence["case_count"]
    assert [case["case_id"] for case in evidence["cases"]] == [
        spec[0] for spec in CASE_SPECS
    ]


@pytest.mark.parametrize(
    "mutation",
    (
        "root_unknown",
        "case_unknown",
        "case_replace",
        "case_remove",
        "case_reorder",
        "effect_true",
        "contract_atomic_remove",
        "contract_frame_replace",
    ),
)
def test_closed_schema_rejects_adversarial_contract_or_evidence_mutation(
    mutation: str,
) -> None:
    contract, schema, evidence = generate()
    validator = Draft202012Validator(schema)
    candidate = copy.deepcopy(evidence)
    if mutation == "root_unknown":
        candidate["payload"] = {}
    elif mutation == "case_unknown":
        candidate["cases"][0]["patient"] = "forbidden"
    elif mutation == "case_replace":
        candidate["cases"][0]["case_id"] = "replacement"
    elif mutation == "case_remove":
        candidate["cases"].pop()
    elif mutation == "case_reorder":
        candidate["cases"][0], candidate["cases"][1] = (
            candidate["cases"][1],
            candidate["cases"][0],
        )
    elif mutation == "effect_true":
        candidate["effect_ceilings"]["provider_called"] = True
    else:
        candidate = copy.deepcopy(contract)
        if mutation == "contract_atomic_remove":
            candidate["atomic_members"].pop()
        elif mutation == "contract_frame_replace":
            candidate["frame_types"][0] = "patient_projection"
    assert list(validator.iter_errors(candidate))


def test_frozen_surface_contains_only_pure_rehearsal_artifacts() -> None:
    root = Path(__file__).resolve().parents[1]
    expected = {
        root
        / "scripts"
        / "raisa_provider_free_unmounted_authored_synthetic_durability_state_machine_rehearsal.py",
        root
        / "scripts"
        / "raisa_provider_free_unmounted_authored_synthetic_durability_state_machine_rehearsal_acceptance.py",
        root
        / "tests"
        / "test_raisa_provider_free_unmounted_authored_synthetic_durability_state_machine_rehearsal.py",
        CONTRACT_PATH,
        SCHEMA_PATH,
        EVIDENCE_PATH,
    }
    assert all(path.is_file() for path in expected)
    for path in expected:
        normalized = path.relative_to(root).as_posix()
        assert not normalized.startswith(("app/", "alembic/", "docs/diary/"))
