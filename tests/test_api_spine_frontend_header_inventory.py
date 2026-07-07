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


def test_frontend_create_proposal_and_create_confirm_emit_http_idempotency_headers():
    source = _read(DIARY_JS)
    save_booking = _function_source(source, "saveBooking")

    assert "function generateClientIdempotencyKey()" in source
    assert "function ensureElementIdempotencyKey(element)" in source
    assert "function idempotencyHeadersFor(key)" in source
    assert 'headers["Idempotency-Key"] = ensureElementIdempotencyKey(saveBtn);' in save_booking
    assert save_booking.index('headers["Idempotency-Key"]') < save_booking.index(
        'const propRes = await apiFetch(url, {'
    )

    create_confirm_block = _block(
        save_booking,
        "let createRes;",
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


def test_frontend_remaining_confirm_callers_are_explicitly_tracked_as_missing_headers():
    source = _read(DIARY_JS)
    preflight = _read(PREFLIGHT)

    confirm_blocks = {
        "saveBooking update confirm branch": _block(
            _function_source(source, "saveBooking"),
            "if (confirmEndpoint && confirmPayload) {",
            "if (!updateRes.ok)",
        ),
        "confirmBernieToolIntentChange": _function_source(source, "confirmBernieToolIntentChange"),
    }

    for label, block in confirm_blocks.items():
        assert "apiFetch(normalizeApiPath(" in block, label
        assert not _contains_idempotency_header(block), label
        assert label.split()[0] in preflight or label in preflight

    for phrase in (
        "confirm_create_proposal_route",
        "confirm_bernie_create_proposal",
        "confirm_update_proposal_route",
        "confirm_status_proposal_route",
        "confirm_delete_proposal_route",
        "Missing frontend header",
    ):
        assert phrase in preflight


def test_frontend_proposal_only_callers_are_explicitly_tracked_as_deferred():
    source = _read(DIARY_JS)
    preflight = _read(PREFLIGHT)

    for route_fragment in (
        "/appointments/proposals/update/",
        "/appointments/proposals/status/",
        "/appointments/proposals/waiting-area/",
        "/appointments/proposals/delete/",
    ):
        assert route_fragment in source

    for handler in (
        "propose_update_appointment",
        "propose_status_update",
        "propose_waiting_area_update",
        "propose_delete_appointment",
    ):
        assert handler in preflight

    assert "proposal-only routes remain a deferred binding gap" in preflight


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

    assert "Sprint 155 should wire the create-confirm client header path first" in text
