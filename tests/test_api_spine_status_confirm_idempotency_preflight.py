from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_status_confirm_preflight.md"
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


def test_status_confirm_preflight_selects_next_confirmation_family():
    text = _read(PREFLIGHT)

    assert "| Sprint | 136 |" in text
    assert "Preflight/review only; no route behavior changed" in text
    assert "POST /api/v1/appointments/proposals/status-confirm" in text
    assert "POST /api/v1/appointments/proposals/status/confirm" in text
    assert "confirm_status_proposal_route" in text
    assert "AppointmentStatusProposalConfirmationIn" in text
    assert "confirmAppointmentStatusProposal" in text
    assert "status-confirm" in text


def test_status_confirm_preflight_records_deepseek_pivot_and_family_comparison():
    text = _compact(_read(PREFLIGHT))

    for phrase in (
        "DeepSeek review changed the initial Ariadne preference",
        "self-contained handler",
        "smaller confirmation body with no `turn_ref` or `session_binding`",
        "no `propose_update_appointment()` revalidation window",
        "Update confirm",
        "Delete confirm",
        "high-traffic Bernie grammar path",
    ):
        assert phrase in text


def test_status_confirm_preflight_records_claim_order_and_commit_gotcha():
    text = _compact(_read(PREFLIGHT))

    for phrase in (
        "claim must happen after typed body validation",
        "before `confirmed=true`, signed evidence, freshness checks",
        "The current helper `_apply_appointment_status_update` commits internally",
        "raw `PATCH /api/v1/appointments/{appointment_id}/status`",
        "add a `commit=False` path for status-confirm",
        "complete the ledger with the final response body and target appointment id",
    ):
        assert phrase in text


def test_status_confirm_preflight_lists_required_future_route_tests():
    text = _compact(_read(PREFLIGHT))

    for phrase in (
        "missing `Idempotency-Key` blocks before ledger, appointment, or audit mutation",
        "invalid status confirmation payload does not create a ledger row",
        "one completed ledger row",
        "same-key/same-body replay returns the stored response",
        "`409 idempotency_key_conflict`",
        "active `in_progress`, stale `in_progress`, and `failed_transient`",
        "does not bypass `confirmed=true`, signed confirmation evidence",
        "union variants canonicalize stably",
        "`_STATUS_CONFIRM_METADATA_FIELDS` remains separate",
        "completed replay telemetry is distinguishable",
    ):
        assert phrase in text


def test_current_confirm_routes_supersede_sprint_136_header_exclusions():
    text = _read(PREFLIGHT)
    router_text = _read(ROUTER)

    for phrase in (
        "Do not enforce HTTP `Idempotency-Key` on `status-confirm` in Sprint 136",
        "update-confirm",
        "delete-confirm",
        "raw compatibility PUT/PATCH/DELETE routes",
        "GraphQL mutations",
        "H15/H-series runtime imports",
        "memory/RAG/GraphRAG runtime wiring",
        "model-to-database writes",
    ):
        assert phrase in text

    status_route = _route_body(
        router_text,
        "def confirm_status_proposal_route(",
        "def get_waiting_room(",
    )
    update_route = _route_body(
        router_text,
        "def confirm_update_proposal_route(",
        "def propose_update_appointment(",
    )
    delete_route = _route_body(
        router_text,
        "def confirm_delete_proposal_route(",
        "def propose_delete_appointment(",
    )

    assert "Header(" in status_route
    assert "Idempotency-Key" in status_route
    assert "claim_appointment_command(" in status_route
    assert "complete_appointment_command(" in status_route
    assert "_STATUS_CONFIRM_ROUTE_FAMILY" in status_route
    assert "Header(" in update_route
    assert "Idempotency-Key" in update_route
    assert "claim_appointment_command(" in update_route
    assert "complete_appointment_command(" in update_route
    assert "Header(" in delete_route
    assert "Idempotency-Key" in delete_route
    assert "claim_appointment_command(" in delete_route
    assert "complete_appointment_command(" in delete_route


def test_status_confirm_preflight_points_to_sprint_137_route_test_contract():
    text = _read(PREFLIGHT)

    assert "Recommended Sprint 137" in text
    assert "Status-confirm idempotency route-test contract" in text
    assert "before enforcing HTTP" in text
