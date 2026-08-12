from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIARY_JS = ROOT / "docs" / "diary" / "diary.js"
PREFLIGHT = (
    ROOT / "orchestration" / "api_spine_appointment_idempotency_diary_header_gap_preflight.md"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _function_source(source: str, name: str) -> str:
    marker = f"function {name}("
    start = source.index(marker)
    next_start = source.find("\nfunction ", start + len(marker))
    if next_start == -1:
        return source[start:]
    return source[start:next_start]


def _contains_idempotency_header(block: str) -> bool:
    return '"Idempotency-Key"' in block or "'Idempotency-Key'" in block


def _block(source: str, start_marker: str, end_marker: str) -> str:
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    return source[start:end]


def test_frontend_booking_proposals_and_create_confirm_emit_http_idempotency_headers():
    source = _read(DIARY_JS)
    save_booking = _function_source(source, "saveBooking")

    assert "function generateClientIdempotencyKey()" in source
    assert "function ensureElementIdempotencyKey(element)" in source
    assert "function idempotencyHeadersFor(key)" in source
    assert "const headers = idempotencyHeadersFor(ensureElementIdempotencyKey(saveBtn));" in save_booking
    assert save_booking.index("const headers = idempotencyHeadersFor") < save_booking.index(
        'const propRes = await apiFetch(url, {'
    )

    create_confirm_block = _block(
        save_booking,
        "const confirmHeaders = isCreateConfirmEndpoint",
        "if (!createRes.ok)",
    )
    assert "isCreateConfirmEndpoint(confirmEndpoint)" in create_confirm_block
    assert "idempotencyHeadersFor(ensureElementConfirmIdempotencyKey(saveBtn))" in create_confirm_block
    assert "headers: confirmHeaders" in create_confirm_block


def test_frontend_create_confirm_bernie_review_caller_emits_stable_header():
    source = _read(DIARY_JS)
    review_confirm_block = _block(
        source,
        "if (isConfirmAdapter && payload.confirm_endpoint && payload.confirm_payload) {",
        "if (response.ok) {",
    )

    assert "isCreateConfirmEndpoint(payload.confirm_endpoint)" in review_confirm_block
    assert 'bernieSession.getServerRouteIdempotencyKey(' in review_confirm_block
    assert '"create-confirm-bernie"' in review_confirm_block
    assert "headers: confirmHeaders" in review_confirm_block


def test_frontend_status_and_delete_confirm_callers_emit_stable_headers():
    source = _read(DIARY_JS)
    status_confirm = _function_source(source, "applySignedStatusProposal")
    delete_confirm = _function_source(source, "applySignedDeleteProposal")

    assert "statusConfirmIdempotencyKey(proposal, confirmPayload)" in status_confirm
    assert "headers: confirmHeaders" in status_confirm
    assert "deleteConfirmIdempotencyKey(proposal, confirmPayload)" in delete_confirm
    assert "headers: confirmHeaders" in delete_confirm
    assert "function confirmIdempotencyKeyFromFreshness(" in source
    assert "function ensureProposalConfirmIdempotencyKey(proposal, kind)" in source


def test_frontend_update_confirm_callers_emit_stable_headers():
    source = _read(DIARY_JS)
    save_booking = _function_source(source, "saveBooking")
    move_resize = _function_source(source, "handleMoveResize")
    tool_intent = _function_source(source, "confirmBernieToolIntentChange")

    update_confirm_block = _block(
        save_booking,
        "const confirmHeaders = idempotencyHeadersFor(\n          updateConfirmIdempotencyKey",
        "if (!updateRes.ok)",
    )
    move_resize_confirm_block = _block(
        move_resize,
        "const confirmHeaders = idempotencyHeadersFor(\n        updateConfirmIdempotencyKey",
        "if (!updateRes.ok)",
    )

    assert "function updateConfirmIdempotencyKey(proposal, confirmPayload)" in source
    assert "updateConfirmIdempotencyKey(proposal, confirmPayload)" in update_confirm_block
    assert "headers: confirmHeaders" in update_confirm_block
    assert "updateConfirmIdempotencyKey(proposal, confirmPayload)" in move_resize_confirm_block
    assert "headers: confirmHeaders" in move_resize_confirm_block
    assert "updateConfirmIdempotencyKey(envelope, confirmPayload)" in tool_intent
    assert "headers: confirmHeaders" in tool_intent


def test_frontend_update_confirm_falls_back_to_proposal_scoped_key():
    source = _read(DIARY_JS)
    update_key = _function_source(source, "updateConfirmIdempotencyKey")
    freshness_helper = _function_source(source, "confirmIdempotencyKeyFromFreshness")

    assert '"update-confirm"' in update_key
    assert "confirmPayload?.update_proposal_freshness_id" in update_key
    assert "proposal?.update_proposal_freshness_id" in update_key
    assert "return ensureProposalConfirmIdempotencyKey(proposal, kind);" in freshness_helper


def test_frontend_confirm_callers_are_wired_or_explicitly_tracked():
    source = _read(DIARY_JS)
    preflight = _read(PREFLIGHT)

    tool_intent = _function_source(source, "confirmBernieToolIntentChange")
    assert "apiFetch(allowlistedConfirmApiPath(" in tool_intent
    assert "updateConfirmIdempotencyKey(envelope, confirmPayload)" in tool_intent
    assert "headers: confirmHeaders" in tool_intent

    for phrase in (
        "confirm_create_proposal_route",
        "confirm_bernie_create_proposal",
        "confirm_update_proposal_route",
        "confirm_status_proposal_route",
        "confirm_delete_proposal_route",
        "confirmBernieToolIntentChange",
    ):
        assert phrase in preflight


def test_frontend_proposal_only_callers_all_emit_headers_and_are_currently_tracked():
    source = _read(DIARY_JS)
    preflight = _read(PREFLIGHT)

    save_booking = _function_source(source, "saveBooking")
    move_resize = _function_source(source, "handleMoveResize")
    set_status = _function_source(source, "setAppointmentStatus")
    delete_booking = _function_source(source, "deleteBooking")
    follow_up_status = _function_source(source, "applyBookingStatusAfterConfirmedBase")

    for route_fragment in (
        "/appointments/proposals/update/",
        "/appointments/proposals/status/",
        "/appointments/proposals/waiting-area/",
        "/appointments/proposals/delete/",
    ):
        assert route_fragment in source

    for handler in (
        "propose_create_appointment",
        "propose_update_appointment",
        "propose_status_update",
        "propose_waiting_area_update",
        "propose_delete_appointment",
    ):
        assert handler in preflight

    assert "idempotencyHeadersFor(ensureElementIdempotencyKey(saveBtn))" in save_booking
    assert "headers: idempotencyHeadersFor(generateClientIdempotencyKey())" in move_resize
    assert set_status.count("headers: proposalHeaders") == 2
    assert delete_booking.count("headers: proposalHeaders") == 2
    assert "headers: idempotencyHeadersFor(generateClientIdempotencyKey())" in follow_up_status
    assert "The native Diary header gap is closed." in preflight
    assert "identify an attempt only" in preflight


def test_frontend_header_preflight_keeps_closed_gates_closed():
    text = _read(PREFLIGHT)

    for phrase in (
        "raw compatibility",
        "slot-search reservation or replay semantics",
        "Bernie interpreter/session command idempotency expansion",
        "OpenAPI `minLength: 8` runtime enforcement",
        "provider calls",
        "GraphQL mutations",
        "H15/H-series runtime imports",
        "memory/RAG/GraphRAG runtime wiring",
        "broad historical diary trove mining",
    ):
        assert phrase in text

    assert "Bernie tool-intent update confirm" in text
    assert "Waiting-area proposal enforcement and strict `minLength: 8` runtime enforcement" in text
