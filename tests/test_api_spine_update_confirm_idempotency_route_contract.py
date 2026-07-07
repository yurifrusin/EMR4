from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ROUTE_TEST_DOC = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_update_confirm_route_tests.md"
)
PREFLIGHT_DOC = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_update_confirm_preflight.md"
)
DEEPSEEK_PREFLIGHT_REVIEW = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "review-deepseek-sprint139-update-confirm-idempotency-preflight.md"
)
DEEPSEEK_ROUTE_REVIEW = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "review-deepseek-sprint140-update-confirm-idempotency-route-contract.md"
)
ROUTER = ROOT / "app" / "routers" / "appointments.py"
UPDATE_TESTS = ROOT / "tests" / "test_appointment_update_proposal.py"

OPERATION_ID = "confirmAppointmentUpdateProposal"
ROUTE_FAMILY = "update-confirm"
CONFIRM_URL = "/api/v1/appointments/proposals/update/confirm"
RAW_UPDATE_URL = "PUT /api/v1/appointments/{appointment_id}"

PASSING_CONTRACT_TESTS = {
    "test_update_confirm_route_test_contract_records_scope",
    "test_update_confirm_contract_lists_future_behavior_cases",
    "test_update_confirm_contract_records_update_specific_gotchas",
    "test_update_confirm_contract_records_deepseek_family_selection_review",
    "test_update_confirm_contract_records_canonicalization_boundary",
    "test_current_router_has_not_wired_update_confirm_idempotency_yet",
    "test_current_router_keeps_proposal_delete_and_raw_update_out_of_scope",
    "test_existing_update_confirm_tests_cover_semantics_to_preserve",
    "test_route_contract_test_inventory_matches_guarded_surface",
}

FUTURE_BEHAVIOR_TESTS = {
    "test_missing_idempotency_key_blocks_before_update_or_audit_mutation",
    "test_invalid_update_confirm_payload_does_not_create_ledger_by_default",
    "test_first_confirmed_update_writes_update_audit_and_ledger",
    "test_same_key_same_body_update_replay_has_no_second_update_or_audit_write",
    "test_same_key_different_update_body_conflicts_without_mutation",
    "test_active_in_progress_update_key_fails_closed_without_mutation",
    "test_stale_in_progress_update_key_fails_closed_without_mutation",
    "test_failed_transient_update_key_fails_closed_without_mutation",
    "test_idempotency_key_does_not_bypass_confirmed_true_signed_evidence_freshness_or_revalidation",
    "test_revalidation_block_after_started_claim_rolls_back_or_removes_claim",
    "test_empty_idempotency_key_is_treated_as_missing",
    "test_confirmed_warnings_are_part_of_same_key_body_conflict",
    "test_replay_after_intervening_raw_update_returns_stored_response_without_revalidation",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _compact(text: str) -> str:
    return " ".join(text.split())


def _route_body(router_text: str, start_marker: str, end_marker: str) -> str:
    start = router_text.index(start_marker)
    end = router_text.index(end_marker, start)
    return router_text[start:end]


def test_update_confirm_route_test_contract_records_scope():
    text = _read(ROUTE_TEST_DOC)
    preflight = _read(PREFLIGHT_DOC)

    assert "| Sprint | 140 |" in text
    assert "Guarded route-test contract only" in text
    assert CONFIRM_URL in text
    assert "confirm_update_proposal_route" in text
    assert "confirm_update_proposal" in text
    assert "BernieUpdateProposalConfirmationIn" in text
    assert OPERATION_ID in text
    assert ROUTE_FAMILY in text
    assert "Recommended Sprint 140" in preflight


def test_update_confirm_contract_lists_future_behavior_cases():
    text = _compact(_read(ROUTE_TEST_DOC))

    for phrase in (
        "missing `Idempotency-Key` returns a fail-closed error",
        "invalid update confirmation payload does not create a ledger row",
        "one completed ledger row",
        "same-key/same-body replay returns the stored response",
        "without a second appointment update, audit row, helper call, or revalidation pass",
        "same-key/different-body returns `409 idempotency_key_conflict`",
        "`409 idempotency_key_in_progress`",
        "`409 idempotency_key_stale_in_progress`",
        "`503 idempotency_key_failed_transient`",
        "does not bypass `confirmed=true`, signed confirmation",
        "blocked revalidation after a started claim rolls back or removes the claim",
        "full validated confirmation-body hashing remains consistent",
    ):
        assert phrase in text


def test_update_confirm_contract_records_update_specific_gotchas():
    text = _compact(_read(ROUTE_TEST_DOC))

    for phrase in (
        "`confirm_update_proposal_route` currently delegates directly to",
        "`confirm_update_proposal` re-runs `propose_update_appointment()`",
        "replay must return at the route wrapper before that revalidation step",
        "must use `db.rollback()`",
        "_apply_appointment_update()` currently commits internally",
        "add a scoped `commit=False` path",
        "raw `PUT /api/v1/appointments/{appointment_id}` must keep default",
        "_UPDATE_CONFIRM_METADATA_FIELDS` is signed-evidence payload shaping only",
        "date, time, duration, practitioner",
    ):
        assert phrase in text


def test_update_confirm_contract_records_deepseek_family_selection_review():
    text = _compact(_read(ROUTE_TEST_DOC))
    preflight_review = _compact(_read(DEEPSEEK_PREFLIGHT_REVIEW))
    route_review = _compact(_read(DEEPSEEK_ROUTE_REVIEW))
    review = f"{preflight_review} {route_review}"

    assert "DeepSeek" in review
    assert "update-confirm" in review
    assert "delete-confirm" in review
    assert "revalidation" in review
    assert "Replay must short-circuit" in route_review
    assert "Full validated confirmation-body hashing" in route_review
    assert "Sprint 140" in text


def test_update_confirm_contract_records_canonicalization_boundary():
    text = _compact(_read(ROUTE_TEST_DOC))
    router_text = _read(ROUTER)

    for phrase in (
        "Use full validated confirmation-body hashing",
        '`request_body=body.model_dump(mode="json")`',
        "`signed_confirmation_evidence`",
        "`update_proposal_freshness_id`",
        "`turn_ref`",
        "`session_binding`",
        "`confirmed_warnings`",
        "`409 idempotency_key_conflict`",
    ):
        assert phrase in text
    assert "_UPDATE_CONFIRM_METADATA_FIELDS" in router_text


def test_current_router_has_not_wired_update_confirm_idempotency_yet():
    router_text = _read(ROUTER)
    update_route = _route_body(
        router_text,
        "def confirm_update_proposal_route(",
        "def propose_update_appointment(",
    )
    update_helper = _route_body(
        router_text,
        "def confirm_update_proposal(",
        "def _appointment_status_command_payload(",
    )
    apply_update = _route_body(
        router_text,
        "def _apply_appointment_update(",
        "@router.put",
    )
    delete_route = _route_body(
        router_text,
        "def confirm_delete_proposal_route(",
        "def propose_delete_appointment(",
    )

    assert "Header(" not in update_route
    assert "Idempotency-Key" not in update_route
    assert "claim_appointment_command(" not in update_route
    assert "complete_appointment_command(" not in update_route
    assert "claim_appointment_command(" not in update_helper
    assert "complete_appointment_command(" not in update_helper
    assert "Header(" not in update_helper
    assert "propose_update_appointment(" in update_helper
    assert "_apply_appointment_update(" in update_helper
    assert "db.commit()" in apply_update
    assert "commit: bool" not in apply_update
    assert "Header(" not in delete_route
    assert "Idempotency-Key" not in delete_route
    assert RAW_UPDATE_URL not in update_route


def test_current_router_keeps_proposal_delete_and_raw_update_out_of_scope():
    router_text = _read(ROUTER)
    update_confirm_route = _route_body(
        router_text,
        "def confirm_update_proposal_route(",
        "def propose_update_appointment(",
    )
    update_proposal_route = _route_body(
        router_text,
        "def propose_update_appointment(",
        "def _block_bernie_update_confirmation(",
    )
    raw_update_route = _route_body(
        router_text,
        "def update_appointment(",
        "def get_checkin_defaults(",
    )
    delete_route = _route_body(
        router_text,
        "def confirm_delete_proposal_route(",
        "def propose_delete_appointment(",
    )

    assert "confirmAppointmentUpdateProposal" not in router_text
    assert "update-confirm" not in update_confirm_route
    assert "Idempotency-Key" not in update_proposal_route
    assert "claim_appointment_command(" not in update_proposal_route
    assert "Idempotency-Key" not in raw_update_route
    assert "claim_appointment_command(" not in raw_update_route
    assert "_apply_appointment_update(" in raw_update_route
    assert "commit=False" not in raw_update_route
    assert "Idempotency-Key" not in delete_route


def test_existing_update_confirm_tests_cover_semantics_to_preserve():
    update_tests = _read(UPDATE_TESTS)

    for phrase in (
        "test_update_proposal_confirm_payload_writes_with_signed_audit_evidence",
        "test_update_confirm_revalidates_same_day_elapsed_window_without_write",
        "UPDATE_CONFIRM_URL",
        "signed_confirmation_evidence",
        "update_proposal_freshness_id",
        "AppointmentAuditLog",
        "AppointmentAuditAction.update",
    ):
        assert phrase in update_tests or phrase in _read(ROUTER)


def test_route_contract_test_inventory_matches_guarded_surface():
    test_functions = {
        name
        for name, value in globals().items()
        if name.startswith("test_") and callable(value)
    }
    assert PASSING_CONTRACT_TESTS <= test_functions
    assert FUTURE_BEHAVIOR_TESTS <= test_functions


@pytest.mark.skip(reason="Sprint 141 wiring: update-confirm must require Idempotency-Key.")
def test_missing_idempotency_key_blocks_before_update_or_audit_mutation():
    raise AssertionError("Enable when update-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 141 wiring: validation should precede ledger claim.")
def test_invalid_update_confirm_payload_does_not_create_ledger_by_default():
    raise AssertionError("Enable when update-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 141 wiring: first confirmed update should complete ledger.")
def test_first_confirmed_update_writes_update_audit_and_ledger():
    raise AssertionError("Enable when update-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 141 wiring: replay must avoid second update/audit/revalidation.")
def test_same_key_same_body_update_replay_has_no_second_update_or_audit_write():
    raise AssertionError("Enable when update-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 141 wiring: same-key/different-body must conflict.")
def test_same_key_different_update_body_conflicts_without_mutation():
    raise AssertionError("Enable when update-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 141 wiring: active in-progress rows fail closed.")
def test_active_in_progress_update_key_fails_closed_without_mutation():
    raise AssertionError("Enable when update-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 141 wiring: stale in-progress rows fail closed.")
def test_stale_in_progress_update_key_fails_closed_without_mutation():
    raise AssertionError("Enable when update-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 141 wiring: failed transient rows fail closed.")
def test_failed_transient_update_key_fails_closed_without_mutation():
    raise AssertionError("Enable when update-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 141 wiring: idempotency must not bypass update-confirm blocks.")
def test_idempotency_key_does_not_bypass_confirmed_true_signed_evidence_freshness_or_revalidation():
    raise AssertionError("Enable when update-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 141 wiring: post-claim revalidation block must roll back claim.")
def test_revalidation_block_after_started_claim_rolls_back_or_removes_claim():
    raise AssertionError("Enable when update-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 141 wiring: blank keys normalize to missing.")
def test_empty_idempotency_key_is_treated_as_missing():
    raise AssertionError("Enable when update-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 141 wiring: confirmed_warnings are semantic request body.")
def test_confirmed_warnings_are_part_of_same_key_body_conflict():
    raise AssertionError("Enable when update-confirm idempotency is wired.")


@pytest.mark.skip(reason="Sprint 141 wiring: replay returns stored body before revalidation.")
def test_replay_after_intervening_raw_update_returns_stored_response_without_revalidation():
    raise AssertionError("Enable when update-confirm idempotency is wired.")
