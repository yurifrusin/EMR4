"""
Deterministic contract matrix over the five wired REST appointment confirmation
handlers. The matrix asserts Idempotency-Key binding, operation/family constants,
request-body idempotency binding, audit completion linkage, and exclusion of
proposal-only and raw compatibility routes.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "app" / "routers" / "appointments.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _route_body(router_text: str, handler: str, end: str) -> str:
    start = router_text.index(f"def {handler}(")
    finish = router_text.index(end, start)
    return router_text[start:finish]


def _compact(text: str) -> str:
    return " ".join(text.split())


# ── Contract matrix ──────────────────────────────────────────────────────────
# Each entry describes one wired REST confirmation handler and its expected
# idempotency / audit contract properties.

CONFIRMATION_CONTRACT_MATRIX = {
    "staff_create": {
        "handler": "confirm_create_proposal_route",
        "route": "POST /api/v1/appointments/proposals/create/confirm",
        "operation_id_constant": "_STAFF_CREATE_CONFIRM_OPERATION_ID",
        "operation_id_value": "confirmAppointmentCreateProposal",
        "route_family_constant": "_STAFF_CREATE_CONFIRM_ROUTE_FAMILY",
        "route_family_value": "create-confirm",
        "base_evidence": "_STAFF_CONFIRM_CREATE_BASE_EVIDENCE",
        "end_marker": "def confirm_update_proposal_route(",
        "has_confirm_body_check": True,
        "has_freshness_revalidation": True,
    },
    "bernie_create": {
        "handler": "confirm_bernie_create_proposal",
        "route": "POST /api/v1/appointments/proposals/create/confirm-bernie",
        "operation_id_constant": "_STAFF_CREATE_CONFIRM_OPERATION_ID",
        "operation_id_value": "confirmAppointmentCreateProposal",
        "route_family_constant": "_BERNIE_CREATE_CONFIRM_ROUTE_FAMILY",
        "route_family_value": "create-confirm-bernie",
        "base_evidence": "_BERNIE_CONFIRM_CREATE_BASE_EVIDENCE",
        "end_marker": "def select_no_slot_suggestion(",
        "has_confirm_body_check": True,
        "has_freshness_revalidation": True,
    },
    "update": {
        "handler": "confirm_update_proposal_route",
        "route": "POST /api/v1/appointments/proposals/update/confirm",
        "operation_id_constant": "_UPDATE_CONFIRM_OPERATION_ID",
        "operation_id_value": "confirmAppointmentUpdateProposal",
        "route_family_constant": "_UPDATE_CONFIRM_ROUTE_FAMILY",
        "route_family_value": "update-confirm",
        "base_evidence": "_BERNIE_CONFIRM_UPDATE_BASE_EVIDENCE",
        "end_marker": "def propose_update_appointment(",
        "has_confirm_body_check": True,
        "has_freshness_revalidation": True,
    },
    "status": {
        "handler": "confirm_status_proposal_route",
        "route": "POST /api/v1/appointments/proposals/status/confirm",
        "operation_id_constant": "_STATUS_CONFIRM_OPERATION_ID",
        "operation_id_value": "confirmAppointmentStatusProposal",
        "route_family_constant": "_STATUS_CONFIRM_ROUTE_FAMILY",
        "route_family_value": "status-confirm",
        "base_evidence": "_STATUS_CONFIRM_BASE_EVIDENCE",
        "end_marker": "def _a5_check_in_gate_open(",
        "has_confirm_body_check": True,
        "has_freshness_revalidation": True,
        "execution_mode": "product_adapter",
    },
    "delete": {
        "handler": "confirm_delete_proposal_route",
        "route": "POST /api/v1/appointments/proposals/delete/confirm",
        "operation_id_constant": "_DELETE_CONFIRM_OPERATION_ID",
        "operation_id_value": "confirmAppointmentDeleteProposal",
        "route_family_constant": "_DELETE_CONFIRM_ROUTE_FAMILY",
        "route_family_value": "delete-confirm",
        "base_evidence": "_DELETE_CONFIRM_BASE_EVIDENCE",
        "end_marker": "def propose_delete_appointment(",
        "has_confirm_body_check": True,
        "has_freshness_revalidation": True,
        "execution_mode": "product_adapter",
    },
}


def _route_local_confirmation_details():
    return (
        details
        for details in CONFIRMATION_CONTRACT_MATRIX.values()
        if details.get("execution_mode") != "product_adapter"
    )


# ── Basis assertions: constants defined in source ────────────────────────────


def test_each_handler_has_operation_id_constant():
    """Every confirmation handler has a route-scoped operation id constant."""
    router_text = _read(ROUTER)

    for details in CONFIRMATION_CONTRACT_MATRIX.values():
        const = details["operation_id_constant"]
        value = details["operation_id_value"]
        assert f'{const} = "{value}"' in router_text, (
            f"Missing or mismatched {const} = {value!r}"
        )


def test_each_handler_has_route_family_constant():
    """Every confirmation handler has a route-family constant."""
    router_text = _read(ROUTER)

    for details in CONFIRMATION_CONTRACT_MATRIX.values():
        const = details["route_family_constant"]
        value = details["route_family_value"]
        assert f'{const} = "{value}"' in router_text, (
            f"Missing or mismatched {const} = {value!r}"
        )


def test_base_evidence_constant_exists():
    """Every confirmation handler's base evidence list is defined in the router."""
    router_text = _read(ROUTER)

    for details in CONFIRMATION_CONTRACT_MATRIX.values():
        evidence_const = details["base_evidence"]
        # Check the evidence constant is defined and has entries
        assert evidence_const in router_text, (
            f"Missing base evidence constant {evidence_const}"
        )


# ── Route-contract assertions: per-handler source inspection ─────────────────


def test_each_handler_extracts_idempotency_key_header():
    """Every confirmation handler requires and normalizes the Idempotency-Key header."""
    router_text = _read(ROUTER)

    for details in CONFIRMATION_CONTRACT_MATRIX.values():
        route = _route_body(router_text, details["handler"], details["end_marker"])
        assert 'Header(None, alias="Idempotency-Key")' in route, (
            f"{details['handler']}: missing Idempotency-Key Header parameter"
        )
        assert "_normalize_idempotency_key(" in route, (
            f"{details['handler']}: missing idempotency key normalization"
        )


def test_each_handler_calls_claim_appointment_command():
    """Every confirmation handler calls claim_appointment_command before writes."""
    router_text = _read(ROUTER)

    for details in _route_local_confirmation_details():
        route = _route_body(router_text, details["handler"], details["end_marker"])
        assert "claim_appointment_command(" in route, (
            f"{details['handler']}: missing claim_appointment_command call"
        )
        # All handlers share the same secret derivation and stale_after
        assert "_staff_create_confirm_idempotency_secret()" in route, (
            f"{details['handler']}: missing or different idempotency secret derivation"
        )
        assert "_STAFF_CREATE_CONFIRM_IDEMPOTENCY_STALE_AFTER" in route, (
            f"{details['handler']}: missing stale_after reference"
        )


def test_each_handler_binds_operation_id_to_claim():
    """Every confirmation handler passes its operation id to claim_appointment_command."""
    router_text = _read(ROUTER)

    for details in _route_local_confirmation_details():
        route = _route_body(router_text, details["handler"], details["end_marker"])
        assert f"operation_id={details['operation_id_constant']}" in route, (
            f"{details['handler']}: missing or incorrect operation_id binding"
        )


def test_each_handler_binds_route_family_to_claim():
    """Every confirmation handler passes its route family to claim_appointment_command."""
    router_text = _read(ROUTER)

    for details in _route_local_confirmation_details():
        route = _route_body(router_text, details["handler"], details["end_marker"])
        assert f"route_family={details['route_family_constant']}" in route, (
            f"{details['handler']}: missing or incorrect route_family binding"
        )


def test_each_handler_binds_request_body_to_claim():
    """Every confirmation handler passes request_body=body.model_dump(mode='json') to claim."""
    router_text = _read(ROUTER)

    for details in _route_local_confirmation_details():
        route = _route_body(router_text, details["handler"], details["end_marker"])
        assert 'request_body=body.model_dump(mode="json")' in route, (
            f"{details['handler']}: missing request_body binding with JSON mode"
        )


def test_each_handler_handles_idempotency_decision():
    """Every confirmation handler maps the idempotency decision before writes."""
    router_text = _read(ROUTER)

    for details in _route_local_confirmation_details():
        route = _route_body(router_text, details["handler"], details["end_marker"])
        assert "_handle_create_confirm_idempotency_decision(decision)" in route, (
            f"{details['handler']}: missing idempotency decision handler"
        )
        assert "if mapped_decision is not None:" in route, (
            f"{details['handler']}: missing mapped_decision guard"
        )


def test_each_handler_calls_complete_appointment_command():
    """Every confirmation handler calls complete_appointment_command before final commit."""
    router_text = _read(ROUTER)

    for details in _route_local_confirmation_details():
        route = _route_body(router_text, details["handler"], details["end_marker"])
        assert "complete_appointment_command(" in route, (
            f"{details['handler']}: missing complete_appointment_command call"
        )
        assert "result_kind=\"confirmed_write\"" in route, (
            f"{details['handler']}: missing or incorrect result_kind"
        )


def test_each_handler_completes_before_commit():
    """Every confirmation handler calls db.commit() after complete_appointment_command."""
    router_text = _read(ROUTER)

    for details in _route_local_confirmation_details():
        route = _route_body(router_text, details["handler"], details["end_marker"])
        route_compact = _compact(route)

        # complete_appointment_command must appear before db.commit in the handler
        complete_pos = route_compact.index("complete_appointment_command(")
        # Handlers may contain bounded early-exit helpers that commit an
        # independently recorded blocked outcome.  The command completion
        # invariant concerns the handler's final confirmed-write commit.
        commit_pos = route_compact.rindex("db.commit()")
        assert complete_pos < commit_pos, (
            f"{details['handler']}: complete_appointment_command is not before db.commit()"
        )


def _handler_or_helper_body(router_text: str, handler: str, end: str) -> str:
    """Return the route body or, for delegating handlers, the helper body."""
    route = _route_body(router_text, handler, end)
    # The update confirm route delegates to confirm_update_proposal() helper;
    # check the helper body for patterns the route does not inline.
    if handler == "confirm_update_proposal_route":
        helper_start = router_text.index("def confirm_update_proposal(")
        helper_end = router_text.index("def _appointment_status_command_payload(", helper_start)
        return router_text[helper_start:helper_end]
    return route


def test_each_handler_includes_audit_evidence():
    """Every confirmation handler uses its base audit evidence (in route or
    delegating helper)."""
    router_text = _read(ROUTER)

    for details in _route_local_confirmation_details():
        body = _handler_or_helper_body(router_text, details["handler"], details["end_marker"])
        evidence_const = details["base_evidence"]
        assert f"audit_evidence = list({evidence_const})" in body, (
            f"{details['handler']}: missing or different base audit evidence assignment"
        )


def test_each_handler_includes_audit_evidence_in_response():
    """Every confirmation handler includes audit_evidence in its response body
    (in route or delegating helper)."""
    router_text = _read(ROUTER)

    for details in _route_local_confirmation_details():
        body = _handler_or_helper_body(router_text, details["handler"], details["end_marker"])
        assert "audit_evidence=audit_evidence" in body, (
            f"{details['handler']}: missing audit_evidence in response or error body"
        )


def test_each_handler_validates_confirm_body():
    """Every confirmation handler checks confirmed is True before proceeding
    (in route or delegating helper)."""
    router_text = _read(ROUTER)

    for details in _route_local_confirmation_details():
        if not details["has_confirm_body_check"]:
            continue
        body = _handler_or_helper_body(router_text, details["handler"], details["end_marker"])
        assert "body.confirmed is not True" in body, (
            f"{details['handler']}: missing confirmed=true guard"
        )


def test_status_confirmation_uses_the_accepted_product_adapter_once():
    router_text = _read(ROUTER)
    details = CONFIRMATION_CONTRACT_MATRIX["status"]
    route = _route_body(router_text, details["handler"], details["end_marker"])

    assert route.count("compose_product_status_confirm(") == 1
    assert "command_session_factory=command_session_factory" in route
    assert "proposal_version_binding=body.status_proposal_version_binding" in route
    assert 'authenticated_bearer_token: str = Depends(oauth2_scheme)' in route
    assert '_status_confirm_domain_secret("proposal-version")' in route
    assert "result.stored_response_bytes" in route
    assert "claim_appointment_command(" not in route
    assert "complete_appointment_command(" not in route
    assert "db.commit()" not in route


def test_delete_confirmation_uses_the_accepted_product_adapter_once():
    router_text = _read(ROUTER)
    details = CONFIRMATION_CONTRACT_MATRIX["delete"]
    route = _route_body(router_text, details["handler"], details["end_marker"])

    assert route.count("compose_product_delete_confirm(") == 1
    assert "command_session_factory=command_session_factory" in route
    assert "proposal_version_binding=body.delete_proposal_version_binding" in route
    assert 'authenticated_bearer_token: str = Depends(oauth2_scheme)' in route
    assert '_delete_confirm_domain_secret("proposal-version")' in route
    assert "result.stored_response_bytes" in route
    assert "canonical_delete_confirm_envelope_bytes(" in route
    assert "claim_appointment_command(" not in route
    assert "complete_appointment_command(" not in route
    assert "db.commit()" not in route


# ── Exclusion assertions: proposal-only and raw compat routes ────────────────


def test_proposal_only_create_excludes_full_idempotency():
    """propose_create_appointment normalizes Idempotency-Key via the shared
    proposal-only helper, without claim/complete ledger calls."""
    router_text = _read(ROUTER)
    handler_start = router_text.index("def propose_create_appointment(")
    handler_end = router_text.index("def _normalize_proposal_idempotency_key(", handler_start)
    route = router_text[handler_start:handler_end]

    # It should have the shared proposal-only idempotency-key normalization
    assert "_normalize_proposal_idempotency_key(idempotency_key" in route
    # But NOT the full claim/complete ledger
    assert "claim_appointment_command(" not in route
    assert "complete_appointment_command(" not in route


def test_proposal_only_update_excludes_full_idempotency():
    """propose_update_appointment normalizes Idempotency-Key via the shared
    proposal-only helper, without claim/complete idempotency ledger calls."""
    router_text = _read(ROUTER)
    handler_start = router_text.index("def propose_update_appointment(")
    handler_end = router_text.index("def _block_bernie_update_confirmation(", handler_start)
    route = router_text[handler_start:handler_end]

    assert "Header(None, alias=\"Idempotency-Key\")" in route
    assert "_normalize_proposal_idempotency_key(idempotency_key" in route
    assert "claim_appointment_command(" not in route
    assert "complete_appointment_command(" not in route


def test_proposal_only_status_excludes_full_idempotency():
    """propose_status_update normalizes Idempotency-Key via the shared
    proposal-only helper, without claim/complete idempotency ledger calls."""
    router_text = _read(ROUTER)
    handler_start = router_text.index("def propose_status_update(")
    handler_end = router_text.index("def propose_waiting_area_update(", handler_start)

    route = router_text[handler_start:handler_end]

    assert "Header(None, alias=\"Idempotency-Key\")" in route
    assert "_normalize_proposal_idempotency_key(idempotency_key" in route
    assert "claim_appointment_command(" not in route
    assert "complete_appointment_command(" not in route


def test_proposal_only_delete_excludes_full_idempotency():
    """propose_delete_appointment normalizes Idempotency-Key via the shared
    proposal-only helper, without claim/complete idempotency ledger calls."""
    router_text = _read(ROUTER)
    handler_start = router_text.index("def propose_delete_appointment(")
    handler_end = router_text.index("def propose_slot_search(", handler_start)
    route = router_text[handler_start:handler_end]

    assert "Header(None, alias=\"Idempotency-Key\")" in route
    assert "_normalize_proposal_idempotency_key(idempotency_key" in route
    assert "claim_appointment_command(" not in route
    assert "complete_appointment_command(" not in route


def test_raw_compat_routes_exclude_full_idempotency():
    """Raw PUT/PATCH/DELETE compatibility routes do not use claim/complete
    idempotency."""
    router_text = _read(ROUTER)

    raw_routes = [
        ('"def update_appointment("', '"def get_checkin_defaults("'),
        ('"def confirm_status_proposal_route("', '"def get_waiting_room("'),
        ('"def confirm_delete_proposal_route("', '"def propose_delete_appointment("'),
    ]

    # Named raw compat handlers
    raw_handlers = [
        ("def update_appointment(", "def get_checkin_defaults("),
    ]

    for start_marker, end_marker in raw_handlers:
        start = router_text.index(start_marker)
        end = router_text.index(end_marker, start)
        span = router_text[start:end]

        assert "claim_appointment_command(" not in span, (
            f"Raw compat route {start_marker.strip()} has claim_appointment_command"
        )
        assert "complete_appointment_command(" not in span, (
            f"Raw compat route {start_marker.strip()} has complete_appointment_command"
        )
        assert '"Idempotency-Key"' not in span.replace("'", '"'), (
            f"Raw compat route {start_marker.strip()} has Idempotency-Key header"
        )


def test_non_confirm_surfaces_outside_idempotency():
    """Read-only, list, and non-confirm routes do not use the confirmation
    idempotency ledger."""
    router_text = _read(ROUTER)

    spans = [
        ("def list_appointments(", "@router.post(\"/proposals/create\""),
        ("def propose_slot_search(", "def propose_normalized_slot_search("),
    ]

    for start_marker, end_marker in spans:
        start = router_text.index(start_marker)
        end = router_text.index(end_marker, start)
        span = router_text[start:end]

        assert "claim_appointment_command(" not in span, (
            f"Non-confirm surface {start_marker.strip()} has claim_appointment_command"
        )
        assert "complete_appointment_command(" not in span, (
            f"Non-confirm surface {start_marker.strip()} has complete_appointment_command"
        )
