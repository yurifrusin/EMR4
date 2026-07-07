from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_delete_confirm_preflight.md"
)
ROUTER = ROOT / "app" / "routers" / "appointments.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _compact(text: str) -> str:
    return " ".join(text.split())


def _route_body(router_text: str, start_marker: str, end_marker: str) -> str:
    start = router_text.index(start_marker)
    end = router_text.index(end_marker, start)
    return router_text[start:end]


def test_delete_confirm_preflight_selects_next_confirmation_family():
    text = _read(PREFLIGHT)

    assert "| Sprint | 142 |" in text
    assert "Preflight/review only; no route behavior changed" in text
    assert "POST /api/v1/appointments/proposals/delete-confirm" in text
    assert "confirm_delete_proposal_route" in text
    assert "_apply_appointment_delete" in text
    assert "AppointmentDeleteProposalConfirmationIn" in text
    assert "confirmAppointmentDeleteProposal" in text
    assert "delete-confirm" in text


def test_delete_confirm_preflight_records_destructive_soft_cancel_boundary():
    text = _compact(_read(PREFLIGHT))

    for phrase in (
        "soft-cancels the appointment",
        "clears waiting-area state",
        "optional cancellation/status reason evidence",
        "AppointmentAuditAction.delete",
        "`_apply_appointment_delete()` currently commits internally",
    ):
        assert phrase in text


def test_delete_confirm_preflight_records_claim_order_and_commit_gotcha():
    text = _compact(_read(PREFLIGHT))

    for phrase in (
        "claim the appointment command ledger with operation id",
        "before `confirmed=true`, signed evidence, freshness, waiting-area state",
        "call `db.rollback()` before returning the blocked",
        "add a scoped `commit=False` path to `_apply_appointment_delete`",
        "return the stored response without re-running delete checks",
    ):
        assert phrase in text


def test_delete_confirm_preflight_lists_required_future_route_tests():
    text = _compact(_read(PREFLIGHT))

    for phrase in (
        "missing `Idempotency-Key` blocks before ledger, appointment, or audit mutation",
        "blank/whitespace `Idempotency-Key` is treated as missing",
        "invalid delete confirmation payload does not create a ledger row",
        "one soft-cancel, one audit row",
        "same-key/same-body replay returns the stored response",
        "intervening raw `DELETE /api/v1/appointments/{id}`",
        "`409 idempotency_key_conflict`",
        "active `in_progress`, stale `in_progress`, and `failed_transient`",
        "does not bypass `confirmed=true`, signed confirmation",
        "blocked checks after a started claim roll back the claim",
        "raw `DELETE /api/v1/appointments/{appointment_id}` keeps default",
        "full validated confirmation-body hashing remains consistent",
    ):
        assert phrase in text


def test_delete_confirm_preflight_keeps_closed_gates_and_no_route_wiring_yet():
    text = _read(PREFLIGHT)
    router_text = _read(ROUTER)

    for phrase in (
        "Do not enforce HTTP `Idempotency-Key` on `delete-confirm` in Sprint 142",
        "raw compatibility `DELETE /api/v1/appointments/{appointment_id}`",
        "proposal-only",
        "GraphQL mutations",
        "H15/H-series runtime imports",
        "memory/RAG/GraphRAG runtime wiring",
        "model-to-database writes",
    ):
        assert phrase in text

    delete_route = _route_body(
        router_text,
        "def confirm_delete_proposal_route(",
        "def propose_delete_appointment(",
    )
    raw_delete_route = _route_body(
        router_text,
        "def cancel_appointment(",
        "@router.post(\n    \"/proposals/delete-confirm\"",
    )

    assert "Header(" not in delete_route
    assert "Idempotency-Key" not in delete_route
    assert "claim_appointment_command(" not in delete_route
    assert "complete_appointment_command(" not in delete_route
    assert "Idempotency-Key" not in raw_delete_route


def test_delete_confirm_preflight_points_to_sprint_143_route_test_contract():
    text = _read(PREFLIGHT)

    assert "Recommended Sprint 143" in text
    assert "Delete-confirm idempotency route-test contract" in text
    assert "before enforcing HTTP" in text
