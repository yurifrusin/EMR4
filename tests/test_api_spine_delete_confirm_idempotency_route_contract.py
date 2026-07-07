from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ROUTE_TEST_DOC = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_delete_confirm_route_tests.md"
)
PREFLIGHT_DOC = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_delete_confirm_preflight.md"
)
DEEPSEEK_PREFLIGHT_REVIEW = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "review-deepseek-sprint142-delete-confirm-idempotency-preflight.md"
)
DEEPSEEK_ROUTE_REVIEW = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "review-deepseek-sprint143-delete-confirm-idempotency-route-contract.md"
)
ROUTER = ROOT / "app" / "routers" / "appointments.py"
DELETE_TESTS = ROOT / "tests" / "test_appointment_status_mutations.py"
AUDIT_TESTS = ROOT / "tests" / "test_appointment_audit.py"
REASON_TESTS = ROOT / "tests" / "test_reason_code_backend.py"

OPERATION_ID = "confirmAppointmentDeleteProposal"
ROUTE_FAMILY = "delete-confirm"
CONFIRM_URL = "/api/v1/appointments/proposals/delete-confirm"
RAW_DELETE_DOC = "DELETE /api/v1/appointments/{appointment_id}"

PASSING_CONTRACT_TESTS = {
    "test_delete_confirm_route_test_contract_records_scope",
    "test_delete_confirm_contract_lists_future_behavior_cases",
    "test_delete_confirm_contract_records_delete_specific_gotchas",
    "test_delete_confirm_contract_records_deepseek_preflight_review",
    "test_current_router_has_not_wired_delete_confirm_idempotency_yet",
    "test_existing_delete_confirm_tests_cover_semantics_to_preserve",
    "test_route_contract_test_inventory_matches_guarded_surface",
}

FUTURE_BEHAVIOR_TESTS = {
    "test_missing_idempotency_key_blocks_before_delete_or_audit_mutation",
    "test_blank_idempotency_key_is_treated_as_missing",
    "test_invalid_delete_confirm_payload_does_not_create_ledger_by_default",
    "test_first_confirmed_delete_writes_soft_cancel_audit_and_ledger",
    "test_same_key_same_body_delete_replay_has_no_second_audit_or_side_effect",
    "test_replay_after_intervening_raw_delete_returns_stored_response_without_revalidation",
    "test_same_key_different_delete_body_conflicts_without_mutation",
    "test_active_in_progress_delete_key_fails_closed_without_mutation",
    "test_stale_in_progress_delete_key_fails_closed_without_mutation",
    "test_failed_transient_delete_key_fails_closed_without_mutation",
    "test_idempotency_key_does_not_bypass_confirmed_signed_freshness_or_waiting_area_checks",
    "test_blocked_delete_checks_after_started_claim_roll_back_claim",
    "test_already_cancelled_delete_confirm_blocks_without_ledger_or_audit",
    "test_nonexistent_delete_confirm_blocks_without_ledger_or_audit",
    "test_confirmed_warnings_are_part_of_delete_same_key_body_conflict",
    "test_nested_delete_proposal_is_part_of_same_key_body_conflict",
    "test_same_key_replay_preserves_merged_confirmed_warnings",
    "test_invalid_status_reason_code_blocks_without_ledger",
    "test_missing_signed_delete_evidence_blocks_and_rolls_back_claim",
    "test_waiting_area_clear_true_without_waiting_area_blocks",
    "test_waiting_area_clear_false_with_waiting_area_blocks",
    "test_concurrent_different_keys_on_same_delete_are_appointment_write_concurrency",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _compact(text: str) -> str:
    return " ".join(text.split())


def _route_body(router_text: str, start_marker: str, end_marker: str) -> str:
    start = router_text.index(start_marker)
    end = router_text.index(end_marker, start)
    return router_text[start:end]


def test_delete_confirm_route_test_contract_records_scope():
    text = _read(ROUTE_TEST_DOC)
    preflight = _read(PREFLIGHT_DOC)

    assert "| Sprint | 143 |" in text
    assert "Guarded route-test contract only" in text
    assert CONFIRM_URL in text
    assert "confirm_delete_proposal_route" in text
    assert "_apply_appointment_delete" in text
    assert "AppointmentDeleteProposalConfirmationIn" in text
    assert OPERATION_ID in text
    assert ROUTE_FAMILY in text
    assert "Recommended Sprint 143" in preflight


def test_delete_confirm_contract_lists_future_behavior_cases():
    text = _compact(_read(ROUTE_TEST_DOC))

    for phrase in (
        "missing `Idempotency-Key` returns a fail-closed error",
        "blank/whitespace `Idempotency-Key` is treated as missing",
        "invalid delete confirmation payload does not create a ledger row",
        "one completed ledger row",
        "clears `waiting_area_id`",
        "same-key/same-body replay returns the stored response",
        "intervening raw delete returns the stored response",
        "same-key/different-body returns `409 idempotency_key_conflict`",
        "`409 idempotency_key_in_progress`",
        "`409 idempotency_key_stale_in_progress`",
        "`503 idempotency_key_failed_transient`",
        "does not bypass `confirmed=true`, signed confirmation",
        "call `db.rollback()`",
    ):
        assert phrase in text


def test_delete_confirm_contract_records_delete_specific_gotchas():
    text = _compact(_read(ROUTE_TEST_DOC))

    for phrase in (
        "`_apply_appointment_delete()` currently commits internally",
        "add a scoped `commit=False` path",
        "Raw `DELETE /api/v1/appointments/{appointment_id}` must keep default",
        "does not re-run `propose_delete_appointment()`",
        "Replay must return before those destructive checks can run again",
        "duplicate audit rows or repeated clearing are release-blocking",
    ):
        assert phrase in text


def test_delete_confirm_contract_records_deepseek_preflight_review():
    review = _compact(_read(DEEPSEEK_PREFLIGHT_REVIEW))
    route_review = _compact(_read(DEEPSEEK_ROUTE_REVIEW))

    assert "DeepSeek" in review
    assert "delete-confirm" in review
    assert "_apply_appointment_delete()" in review
    assert "soft-cancel" in review
    assert "Raw `DELETE" in review
    assert "already-cancelled" in route_review
    assert "confirmed_warnings" in route_review
    assert "waiting-area mismatch" in route_review


def test_current_router_has_not_wired_delete_confirm_idempotency_yet():
    router_text = _read(ROUTER)
    delete_route = _route_body(
        router_text,
        "def confirm_delete_proposal_route(",
        "def propose_delete_appointment(",
    )
    apply_delete = _route_body(
        router_text,
        "def _apply_appointment_delete(",
        "@router.delete",
    )
    raw_delete = _route_body(
        router_text,
        "def cancel_appointment(",
        "@router.post(\n    \"/proposals/delete-confirm\"",
    )

    assert "Header(" not in delete_route
    assert "Idempotency-Key" not in delete_route
    assert "claim_appointment_command(" not in delete_route
    assert "complete_appointment_command(" not in delete_route
    assert "confirmAppointmentDeleteProposal" not in router_text
    assert "delete-confirm" not in delete_route
    assert "db.commit()" in apply_delete
    assert "commit: bool" not in apply_delete
    assert "Idempotency-Key" not in raw_delete
    assert "claim_appointment_command(" not in raw_delete
    assert RAW_DELETE_DOC not in delete_route


def test_existing_delete_confirm_tests_cover_semantics_to_preserve():
    combined = "\n".join([
        _read(DELETE_TESTS),
        _read(AUDIT_TESTS),
        _read(REASON_TESTS),
        _read(ROUTER),
    ])

    for phrase in (
        "DELETE_CONFIRM_URL",
        "test_delete_proposal_returns_signed_confirm_payload",
        "test_delete_confirm_soft_cancels_once_with_signed_evidence",
        "stale_delete_proposal_freshness_id",
        "stale_delete_waiting_area_state",
        "diary_confirm_delete_proposal",
        "source_delete_proposal",
        "status_reason_code",
        "AppointmentAuditAction.delete",
    ):
        assert phrase in combined


def test_route_contract_test_inventory_matches_guarded_surface():
    test_functions = {
        name
        for name, value in globals().items()
        if name.startswith("test_") and callable(value)
    }
    assert PASSING_CONTRACT_TESTS <= test_functions
    assert FUTURE_BEHAVIOR_TESTS <= test_functions


@pytest.mark.skip(reason="Sprint 144 wiring: delete-confirm must require Idempotency-Key.")
def test_missing_idempotency_key_blocks_before_delete_or_audit_mutation():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: blank keys normalize to missing.")
def test_blank_idempotency_key_is_treated_as_missing():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: validation should precede ledger claim.")
def test_invalid_delete_confirm_payload_does_not_create_ledger_by_default():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: first confirmed delete should complete ledger.")
def test_first_confirmed_delete_writes_soft_cancel_audit_and_ledger():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: replay must avoid second delete/audit side effect.")
def test_same_key_same_body_delete_replay_has_no_second_audit_or_side_effect():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: replay returns stored body before delete checks.")
def test_replay_after_intervening_raw_delete_returns_stored_response_without_revalidation():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: same-key/different-body must conflict.")
def test_same_key_different_delete_body_conflicts_without_mutation():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: active in-progress rows fail closed.")
def test_active_in_progress_delete_key_fails_closed_without_mutation():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: stale in-progress rows fail closed.")
def test_stale_in_progress_delete_key_fails_closed_without_mutation():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: failed transient rows fail closed.")
def test_failed_transient_delete_key_fails_closed_without_mutation():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: idempotency must not bypass delete-confirm blocks.")
def test_idempotency_key_does_not_bypass_confirmed_signed_freshness_or_waiting_area_checks():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: post-claim block must roll back claim.")
def test_blocked_delete_checks_after_started_claim_roll_back_claim():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: already-cancelled stale proposals block without ledger/audit.")
def test_already_cancelled_delete_confirm_blocks_without_ledger_or_audit():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: missing appointment blocks without ledger/audit.")
def test_nonexistent_delete_confirm_blocks_without_ledger_or_audit():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: confirmed_warnings are semantic request body.")
def test_confirmed_warnings_are_part_of_delete_same_key_body_conflict():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: nested delete_proposal is semantic request body.")
def test_nested_delete_proposal_is_part_of_same_key_body_conflict():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: replay preserves stored merged warning response.")
def test_same_key_replay_preserves_merged_confirmed_warnings():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: invalid status reason code blocks without ledger.")
def test_invalid_status_reason_code_blocks_without_ledger():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: missing signed evidence blocks and rolls back claim.")
def test_missing_signed_delete_evidence_blocks_and_rolls_back_claim():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: clears_waiting_area true/no area blocks.")
def test_waiting_area_clear_true_without_waiting_area_blocks():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: clears_waiting_area false/area present blocks.")
def test_waiting_area_clear_false_with_waiting_area_blocks():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 144 wiring: different keys are appointment concurrency, not idempotency.")
def test_concurrent_different_keys_on_same_delete_are_appointment_write_concurrency():
    raise AssertionError("Enable when delete-confirm idempotency is wired.")
