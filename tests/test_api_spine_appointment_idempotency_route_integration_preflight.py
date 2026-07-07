from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_route_integration_preflight.md"
)
ROUTER = ROOT / "app" / "routers" / "appointments.py"
HELPER = ROOT / "app" / "services" / "appointment_idempotency.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_route_integration_preflight_names_first_staff_create_confirm_family():
    text = _read(PREFLIGHT)

    assert "| Sprint | 130 |" in text
    assert "Route integration preflight only; no appointment route wiring changed" in text
    assert "POST /api/v1/appointments/proposals/create/confirm" in text
    assert "confirm_create_proposal_route" in text
    assert "confirmAppointmentCreateProposal" in text
    assert "create-confirm" in text
    assert "Do not wire `confirm-bernie`, update, status, delete" in text


def test_route_integration_preflight_requires_helper_before_writes_and_atomic_completion():
    text = _read(PREFLIGHT)

    ordered = (
        "authenticate and authorize actor/practice",
        "require and normalize HTTP `Idempotency-Key`",
        "call `claim_appointment_command()` before `_create_appointment_record()`",
        "map `replay` to the stored response",
        "map `conflict` to `409 idempotency_key_conflict`",
        "map `in_progress` to `409 idempotency_key_in_progress`",
        "map `stale_in_progress` to a fail-closed response",
        "map `failed_transient` to a fail-closed retry/escalation response",
        "run existing signed-evidence, freshness, conflict, role/tenant",
        "perform appointment write, audit write, and",
        "commit only after appointment, audit, and ledger completion",
    )
    cursor = -1
    for phrase in ordered:
        next_pos = text.find(phrase)
        assert next_pos > cursor
        cursor = next_pos
    assert "`expires_at` remains unused for confirmation-write rows" in text


def test_route_integration_preflight_requires_route_tests_before_wiring():
    text = _read(PREFLIGHT)

    for phrase in (
        "missing `Idempotency-Key` blocks before writing",
        "one appointment, one audit row, and one",
        "same-key/same-body replay returns the same stored response",
        "same-key/different-body returns `409 idempotency_key_conflict`",
        "same-key active in-progress returns",
        "stale `in_progress` returns the selected fail-closed response",
        "`failed_transient` returns the selected fail-closed response",
        "not bypassed by idempotency",
        "business-rule failures after a started claim roll back or remove the claim",
        "proposal-only create route behavior remains unchanged",
    ):
        assert phrase in text


def test_route_integration_preflight_pins_fail_closed_response_map():
    text = _read(PREFLIGHT)

    for phrase in (
        "| `replay` | Stored status | Stored response body |",
        "| `conflict` | 409 | `idempotency_key_conflict` |",
        "| `in_progress` | 409 or 425 | `idempotency_key_in_progress` |",
        "| `stale_in_progress` | 409 | `idempotency_key_stale_in_progress` |",
        "| `failed_transient` | 503 | `idempotency_key_failed_transient` |",
        "silently expire by default",
        "Proposal-only route idempotency remains a separate concern",
    ):
        assert phrase in text


def test_current_router_wires_only_approved_confirmation_families():
    router_text = _read(ROUTER)
    helper_start = router_text.index("def _idempotency_key_required_error(")
    staff_start = router_text.index("def confirm_create_proposal_route(")
    update_start = router_text.index("def confirm_update_proposal_route(")
    update_end = router_text.index("def propose_update_appointment(")
    bernie_start = router_text.index("def confirm_bernie_create_proposal(")
    bernie_end = router_text.index("def select_no_slot_suggestion(")
    status_start = router_text.index("def confirm_status_proposal_route(")
    status_end = router_text.index("def get_waiting_room(")
    helper_and_staff = router_text[helper_start:update_start]
    bernie_route = router_text[bernie_start:bernie_end]
    status_route = router_text[status_start:status_end]
    update_route = router_text[update_start:update_end]
    rest = (
        router_text[:helper_start]
        + router_text[update_end:status_start]
        + router_text[status_end:bernie_start]
        + router_text[bernie_end:]
    )

    assert "Idempotency-Key" in helper_and_staff
    assert "claim_appointment_command(" in helper_and_staff
    assert "complete_appointment_command(" in helper_and_staff
    assert "_STAFF_CREATE_CONFIRM_OPERATION_ID" in helper_and_staff
    assert "_STAFF_CREATE_CONFIRM_ROUTE_FAMILY" in helper_and_staff
    assert "Idempotency-Key" in bernie_route
    assert "claim_appointment_command(" in bernie_route
    assert "complete_appointment_command(" in bernie_route
    assert "_BERNIE_CREATE_CONFIRM_ROUTE_FAMILY" in bernie_route
    assert "Idempotency-Key" in status_route
    assert "claim_appointment_command(" in status_route
    assert "complete_appointment_command(" in status_route
    assert "_STATUS_CONFIRM_ROUTE_FAMILY" in status_route
    assert "Idempotency-Key" in update_route
    assert "claim_appointment_command(" in update_route
    assert "complete_appointment_command(" in update_route
    assert "_UPDATE_CONFIRM_ROUTE_FAMILY" in update_route
    assert "Idempotency-Key" not in rest
    assert "claim_appointment_command(" not in rest
    assert "complete_appointment_command(" not in rest
    assert "AppointmentCommandIdempotency" not in router_text


def test_helper_surface_exists_for_future_route_preflight():
    helper_text = _read(HELPER)

    assert "def claim_appointment_command(" in helper_text
    assert "def complete_appointment_command(" in helper_text
    assert ".with_for_update()" in helper_text
    assert "db.commit(" not in helper_text
