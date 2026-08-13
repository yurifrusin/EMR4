from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_update_confirm_preflight.md"
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


def test_update_confirm_preflight_selects_next_confirmation_family():
    text = _read(PREFLIGHT)

    assert "| Sprint | 139 |" in text
    assert "Consumed by Sprint 141 route wiring" in text
    assert "POST /api/v1/appointments/proposals/update/confirm" in text
    assert "confirm_update_proposal_route" in text
    assert "confirm_update_proposal" in text
    assert "BernieUpdateProposalConfirmationIn" in text
    assert "confirmAppointmentUpdateProposal" in text
    assert "update-confirm" in text


def test_update_confirm_preflight_records_comparison_and_rationale():
    text = _compact(_read(PREFLIGHT))

    for phrase in (
        "should come before `delete-confirm` because it is reversible",
        "re-runs `propose_update_appointment()` before writing",
        "`_apply_appointment_update()`, which commits internally",
        "Delete confirm",
        "more destructive workflow semantics",
    ):
        assert phrase in text


def test_update_confirm_preflight_records_claim_order_and_commit_gotcha():
    text = _compact(_read(PREFLIGHT))

    for phrase in (
        "claim the appointment command ledger with operation id",
        "before confirmation checks, signed evidence, freshness checks, revalidation",
        "add a scoped `commit=False` path to `_apply_appointment_update`",
        "complete the ledger with the final response body and target appointment id",
        "return the stored response without re-running revalidation",
    ):
        assert phrase in text


def test_update_confirm_preflight_lists_required_future_route_tests():
    text = _compact(_read(PREFLIGHT))

    for phrase in (
        "missing `Idempotency-Key` blocks before ledger, appointment, or audit mutation",
        "invalid update confirmation payload does not create a ledger row",
        "one completed ledger row",
        "same-key/same-body replay returns the stored response",
        "`409 idempotency_key_conflict`",
        "active `in_progress`, stale `in_progress`, and `failed_transient`",
        "does not bypass `confirmed=true`, signed confirmation",
        "blocked revalidation after a started claim",
        "full validated confirmation-body hashing remains consistent",
    ):
        assert phrase in text


def test_update_confirm_preflight_records_historical_gates_and_current_route_wiring():
    text = _read(PREFLIGHT)
    router_text = _read(ROUTER)

    for phrase in (
        "Do not enforce HTTP `Idempotency-Key` on `update-confirm` in Sprint 139",
        "delete-confirm",
        "raw compatibility PUT/PATCH/DELETE routes",
        "proposal-only",
        "GraphQL mutations",
        "H15/H-series runtime imports",
        "memory/RAG/GraphRAG runtime wiring",
        "model-to-database writes",
    ):
        assert phrase in text

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

    assert "Header(" in update_route
    assert "Idempotency-Key" in update_route
    assert "claim_appointment_command(" in update_route
    assert "complete_appointment_command(" in update_route
    assert "_UPDATE_CONFIRM_OPERATION_ID" in router_text
    assert "_UPDATE_CONFIRM_ROUTE_FAMILY" in router_text
    # The Sprint 139 document preserves its historical sequencing decision,
    # while the current router has since completed the separately accepted
    # delete-confirm idempotency descendant.
    assert "Header(" in delete_route
    assert "Idempotency-Key" in delete_route
    assert "claim_appointment_command(" in delete_route
    assert "complete_appointment_command(" in delete_route


def test_update_confirm_preflight_points_to_sprint_140_route_test_contract():
    text = _read(PREFLIGHT)

    assert "Recommended Sprint 140" in text
    assert "Update-confirm idempotency route-test contract" in text
    assert "before enforcing HTTP" in text
