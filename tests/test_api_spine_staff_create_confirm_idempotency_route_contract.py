from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ROUTE_TEST_DOC = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_staff_create_confirm_route_tests.md"
)
ROUTER = ROOT / "app" / "routers" / "appointments.py"
CONTRACT_TEST = Path(__file__).name

SKIP_REASON = (
    "Sprint 131 defines the staff create-confirm idempotency route tests before "
    "Sprint 132 route wiring; remove this skip when wiring starts."
)
PASSING_CONTRACT_TESTS = (
    "test_staff_create_confirm_route_test_contract_records_scope",
    "test_staff_create_confirm_route_test_contract_lists_future_cases",
    "test_staff_create_confirm_guarded_tests_remain_skipped_until_wiring",
    "test_current_router_remains_unwired_while_route_tests_are_guarded",
)
GUARDED_BEHAVIOR_TESTS = (
    "test_missing_idempotency_key_blocks_before_writes",
    "test_first_confirmed_create_writes_appointment_audit_and_ledger",
    "test_same_key_same_body_replays_stored_response_without_second_write",
    "test_same_key_different_body_conflicts_without_second_write",
    "test_active_in_progress_key_fails_closed_without_second_write",
    "test_stale_in_progress_key_fails_closed_without_second_write",
    "test_failed_transient_key_fails_closed_without_second_write",
    "test_business_rule_failure_after_claim_removes_or_rolls_back_claim",
    "test_proposal_only_create_route_remains_out_of_scope",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_staff_create_confirm_route_test_contract_records_scope():
    text = _read(ROUTE_TEST_DOC)

    assert "| Sprint | 131 |" in text
    assert "Guarded route-test contract only; route implementation still unwired" in text
    assert "POST /api/v1/appointments/proposals/create/confirm" in text
    assert "confirm_create_proposal_route" in text
    assert "confirmAppointmentCreateProposal" in text
    assert "create-confirm" in text
    assert "confirm-bernie" in text
    assert "proposal-only `POST /api/v1/appointments/proposals/create`" in text


def test_staff_create_confirm_route_test_contract_lists_future_cases():
    text = _read(ROUTE_TEST_DOC)

    for phrase in (
        "missing `Idempotency-Key` returns a fail-closed error",
        "one appointment, one audit",
        "same-key/same-body replay returns the stored response",
        "same-key/different-body returns `409 idempotency_key_conflict`",
        "same-key active in-progress returns",
        "stale `in_progress` returns `409 idempotency_key_stale_in_progress`",
        "`failed_transient` returns `503 idempotency_key_failed_transient`",
        "signed evidence, warning acknowledgement, and role/tenant checks",
        "business-rule failures after a started claim roll back or remove the claim",
        "proposal-only create route behavior remains unchanged",
    ):
        assert phrase in text


def test_staff_create_confirm_guarded_tests_remain_skipped_until_wiring():
    source = _read(ROOT / "tests" / CONTRACT_TEST)

    for test_name in GUARDED_BEHAVIOR_TESTS:
        assert f"def {test_name}" in source
    skip_decorators = [
        line for line in source.splitlines() if line.strip().startswith("@pytest.mark.skip")
    ]
    assert len(skip_decorators) == len(GUARDED_BEHAVIOR_TESTS)
    assert "Sprint 131 defines the staff create-confirm idempotency route tests" in source
    assert "Sprint 132 route wiring" in source


def test_current_router_remains_unwired_while_route_tests_are_guarded():
    router_text = _read(ROUTER)

    assert "Idempotency-Key" not in router_text
    assert "AppointmentCommandIdempotency" not in router_text
    assert "claim_appointment_command" not in router_text
    assert "complete_appointment_command" not in router_text
    assert "appointment_idempotency" not in router_text


def test_skip_metadata_exactly_matches_contract_until_wiring():
    test_functions = [
        (name, value)
        for name, value in globals().items()
        if name.startswith("test_") and callable(value)
    ]
    skipped = {
        name
        for name, value in test_functions
        if any(
            getattr(mark, "name", None) == "skip"
            and mark.kwargs.get("reason") == SKIP_REASON
            for mark in getattr(value, "pytestmark", [])
        )
    }
    passing = {name for name, _ in test_functions} - skipped

    assert skipped == set(GUARDED_BEHAVIOR_TESTS)
    assert passing == set(PASSING_CONTRACT_TESTS) | {
        "test_skip_metadata_exactly_matches_contract_until_wiring",
    }


@pytest.mark.skip(reason=SKIP_REASON)
def test_missing_idempotency_key_blocks_before_writes():
    raise AssertionError("Enable with Sprint 132 route wiring.")


@pytest.mark.skip(reason=SKIP_REASON)
def test_first_confirmed_create_writes_appointment_audit_and_ledger():
    raise AssertionError("Enable with Sprint 132 route wiring.")


@pytest.mark.skip(reason=SKIP_REASON)
def test_same_key_same_body_replays_stored_response_without_second_write():
    raise AssertionError("Enable with Sprint 132 route wiring.")


@pytest.mark.skip(reason=SKIP_REASON)
def test_same_key_different_body_conflicts_without_second_write():
    raise AssertionError("Enable with Sprint 132 route wiring.")


@pytest.mark.skip(reason=SKIP_REASON)
def test_active_in_progress_key_fails_closed_without_second_write():
    raise AssertionError("Enable with Sprint 132 route wiring.")


@pytest.mark.skip(reason=SKIP_REASON)
def test_stale_in_progress_key_fails_closed_without_second_write():
    raise AssertionError("Enable with Sprint 132 route wiring.")


@pytest.mark.skip(reason=SKIP_REASON)
def test_failed_transient_key_fails_closed_without_second_write():
    raise AssertionError("Enable with Sprint 132 route wiring.")


@pytest.mark.skip(reason=SKIP_REASON)
def test_business_rule_failure_after_claim_removes_or_rolls_back_claim():
    raise AssertionError("Enable with Sprint 132 route wiring.")


@pytest.mark.skip(reason=SKIP_REASON)
def test_proposal_only_create_route_remains_out_of_scope():
    raise AssertionError("Enable with Sprint 132 route wiring.")
