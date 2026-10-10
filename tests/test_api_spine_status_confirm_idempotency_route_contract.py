import ast
from datetime import date, datetime, time, timezone
from pathlib import Path

import pytest

import app.routers.appointments as appointments_router
from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentCommandIdempotency,
    AppointmentStatus,
    BookingChannel,
)
from app.models.diary import WaitingArea
from tests.conftest import make_token


ROOT = Path(__file__).resolve().parents[1]
ROUTE_TEST_DOC = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_status_confirm_route_tests.md"
)
PREFLIGHT_DOC = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_status_confirm_preflight.md"
)
DEEPSEEK_REVIEW = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "review-deepseek-sprint136-status-confirm-idempotency-preflight.md"
)
ROUTER = ROOT / "app" / "routers" / "appointments.py"
STATUS_TESTS = ROOT / "tests" / "test_appointment_status_mutations.py"
REASON_CODE_TESTS = ROOT / "tests" / "test_reason_code_backend.py"
APPOINTMENT_AUDIT_TESTS = ROOT / "tests" / "test_appointment_audit.py"

OPERATION_ID = "confirmAppointmentStatusProposal"
ROUTE_FAMILY = "status-confirm"
CONFIRM_URL = "/api/v1/appointments/proposals/status/confirm"
STATUS_PROPOSAL_URL = "/api/v1/appointments/proposals/status/{appt_id}"
WAITING_AREA_PROPOSAL_URL = "/api/v1/appointments/proposals/waiting-area/{appt_id}"
CANONICAL_OPENAPI_PATH = "/api/v1/appointments/proposals/status/confirm"
THURSDAY = date(2026, 6, 25)

PASSING_CONTRACT_TESTS = {
    "test_status_confirm_route_test_contract_records_scope",
    "test_status_confirm_contract_lists_future_behavior_cases",
    "test_status_confirm_contract_records_deepseek_family_selection_review",
    "test_current_router_wires_status_confirm_idempotency_surface",
    "test_existing_status_confirm_tests_cover_semantics_to_preserve",
    "test_status_confirm_metadata_boundary_is_documented",
    "test_route_contract_test_inventory_matches_wired_surface",
    "test_missing_idempotency_key_blocks_before_status_or_audit_mutation",
    "test_invalid_status_confirm_payload_does_not_create_ledger_by_default",
    "test_first_confirmed_status_change_writes_status_audit_and_ledger",
    "test_waiting_area_variant_blocks_without_write_or_ledger",
    "test_same_key_same_body_status_replay_has_no_second_status_or_audit_write",
    "test_waiting_area_repeat_stays_blocked_without_write_or_ledger",
    "test_same_key_different_status_body_conflicts_without_mutation",
    "test_idempotency_key_does_not_bypass_confirmed_true_signed_evidence_or_freshness",
    "test_waiting_area_variant_cannot_reuse_status_key_to_reopen_write",
}


@pytest.fixture(autouse=True)
def _freeze_status_contract_clock(monkeypatch):
    def fixed_now(tz):
        return datetime(2026, 6, 22, 8, 0, 0, tzinfo=tz)

    monkeypatch.setattr(appointments_router, "_clinic_local_now", fixed_now)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _compact(text: str) -> str:
    return " ".join(text.split())


def _route_body(router_text: str, start_marker: str, end_marker: str) -> str:
    start = router_text.index(start_marker)
    end = router_text.index(end_marker, start)
    return router_text[start:end]


def _auth(token: str, idempotency_key: str | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    if idempotency_key is not None:
        headers["Idempotency-Key"] = idempotency_key
    return headers


def _make_appt(db, practice, practitioner, patient, *, status=AppointmentStatus.Booked):
    appt = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(THURSDAY, time(9, 0), tzinfo=timezone.utc),
        appointment_date=THURSDAY,
        start_time_local=time(9, 0),
        duration_minutes=15,
        status=status,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt)
    db.commit()
    return appt


def _make_area(db, practice):
    area = WaitingArea(practice_id=practice.id, name="Sprint 138 Waiting")
    db.add(area)
    db.flush()
    return area


def _row_counts(db) -> tuple[int, int, int]:
    return (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
        db.query(AppointmentCommandIdempotency).count(),
    )


def _status_payload(client, token: str, appt_id, *, status_value="Confirmed") -> dict:
    proposal = client.post(
        STATUS_PROPOSAL_URL.format(appt_id=appt_id),
        json={"status": status_value},
        headers=_auth(token, f"status-prop-sprint142-{appt_id}"),
    )
    assert proposal.status_code == 200, proposal.text
    payload = proposal.json()["confirm_payload"]
    payload["confirmed"] = True
    return payload


def _waiting_area_payload(client, token: str, appt_id, area_id) -> dict:
    proposal = client.post(
        WAITING_AREA_PROPOSAL_URL.format(appt_id=appt_id),
        json={"waiting_area_id": str(area_id)},
        headers=_auth(token),
    )
    assert proposal.status_code == 200, proposal.text
    payload = proposal.json()["confirm_payload"]
    payload["confirmed"] = True
    return payload


def test_status_confirm_route_test_contract_records_scope():
    text = _read(ROUTE_TEST_DOC)
    preflight = _read(PREFLIGHT_DOC)

    assert "| Sprint | 137 |" in text
    assert CONFIRM_URL in text
    assert CANONICAL_OPENAPI_PATH in text
    assert "confirm_status_proposal_route" in text
    assert "AppointmentStatusProposalConfirmationIn" in text
    assert OPERATION_ID in text
    assert ROUTE_FAMILY in text
    assert "Status-confirm idempotency route-test contract" in preflight


def test_status_confirm_contract_lists_future_behavior_cases():
    text = _compact(_read(ROUTE_TEST_DOC))

    for phrase in (
        "missing `Idempotency-Key` returns a fail-closed error",
        "invalid status confirmation payload does not create a ledger row",
        "same-key/same-body status replay returns the stored response",
        "same-key/same-body waiting-area replay returns the stored response",
        "same-key/different-body returns `409 idempotency_key_conflict`",
        "`409 idempotency_key_in_progress`",
        "`409 idempotency_key_stale_in_progress`",
        "`503 idempotency_key_failed_transient`",
        "does not bypass `confirmed=true`",
        "union variants canonicalize",
    ):
        assert phrase in text


def test_status_confirm_contract_records_deepseek_family_selection_review():
    text = _compact(_read(ROUTE_TEST_DOC))
    review = _compact(_read(DEEPSEEK_REVIEW))

    assert "DeepSeek's review found that `status-confirm` has the cleanest" in review
    assert "status-confirm is self-contained" in review
    assert "no `turn_ref` or `session_binding`" in review
    assert "less destructive than delete-confirm" in review
    assert "DeepSeek" in text


def _source_function(module, name):
    return next(node for node in module.body
                if isinstance(node, ast.FunctionDef) and node.name == name)


def _source_call(function, name):
    calls = [node for node in ast.walk(function)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
             and node.func.id == name]
    assert len(calls) == 1
    return calls[0]


def _assert_source_statement(nodes, source):
    expected = ast.dump(ast.parse(source).body[0])
    assert any(ast.dump(node) == expected for node in nodes)


def _source_dict_value(mapping, key):
    assert isinstance(mapping, ast.Dict)
    return next(value for candidate, value in zip(mapping.keys, mapping.values)
                if isinstance(candidate, ast.Constant) and candidate.value == key)


def _source_keyword(call, name):
    values = [keyword.value for keyword in call.keywords if keyword.arg == name]
    assert len(values) == 1
    return values[0]


def _assert_delegated_delete_route_family(router_text):
    router = ast.parse(router_text)
    adapter = ast.parse(_read(ROOT / "app" / "services" / "appointment_delete_product_adapter.py"))
    composition = ast.parse(_read(ROOT / "app" / "services" / "appointment_delete_composition.py"))
    for module, source, imported in (
        (router, "app.services.appointment_delete_product_adapter", "compose_product_delete_confirm"),
        (adapter, "app.services.appointment_delete_composition", "compose_delete_confirm"),
    ):
        assert any(isinstance(node, ast.ImportFrom) and node.module == source
                   and any(alias.name == imported and alias.asname is None for alias in node.names)
                   for node in module.body)
    for module in (adapter, composition):
        _assert_source_statement(module.body, 'DELETE_CONFIRM_ROUTE_FAMILY = "delete-confirm"')

    route = _source_function(router, "confirm_delete_proposal_route")
    product_call = _source_call(route, "compose_product_delete_confirm")
    assert ast.dump(product_call.args[0]) == ast.dump(ast.Name(id="body", ctx=ast.Load()))

    product = _source_function(adapter, "compose_product_delete_confirm")
    prepare = next(node for node in product.body
                   if isinstance(node, ast.FunctionDef) and node.name == "prepare_admission")
    _assert_source_statement(ast.walk(prepare),
                             "prepared_transport = _transport(body, idempotency_key=idempotency_key)")
    prepared_input = next(node.value for node in ast.walk(prepare)
                          if isinstance(node, ast.Assign)
                          and any(isinstance(target, ast.Name) and target.id == "adapter_input"
                                  for target in node.targets))
    assert ast.dump(_source_dict_value(prepared_input, "transport")) == ast.dump(
        ast.parse("copy.deepcopy(dict(prepared_transport))", mode="eval").body)
    _assert_source_statement(ast.walk(prepare),
                             "admission = delete_confirm_admission_adapter(adapter_input)")
    _assert_source_statement(prepare.body,
                             "return prepared_transport, prepared_ingress, admission")
    transport = _source_function(adapter, "_transport")
    transport_result = next(node.value for node in transport.body if isinstance(node, ast.Return))
    route_family = _source_dict_value(transport_result, "route_family")
    assert isinstance(route_family, ast.Name) and route_family.id == "DELETE_CONFIRM_ROUTE_FAMILY"
    compose_call = _source_call(product, "compose_delete_confirm")
    assert any(isinstance(node, ast.Return) and node.value is compose_call
               for node in ast.walk(product))
    assert ast.dump(compose_call.args[0]) == ast.dump(ast.Name(id="transport", ctx=ast.Load()))
    admission_adapter = _source_keyword(compose_call, "admission_adapter")
    assert isinstance(admission_adapter, ast.Name)
    assert admission_adapter.id == "delete_confirm_admission_adapter"
    deferred_factory = _source_keyword(compose_call, "deferred_admission_factory")
    assert isinstance(deferred_factory, ast.Name) and deferred_factory.id == prepare.name

    compose = _source_function(composition, "compose_delete_confirm")
    _assert_source_statement(ast.walk(compose),
                             "request = None if deferred else _validate_ready_request(admission, server_ingress)")
    resolve = next(node for node in ast.walk(compose)
                   if isinstance(node, ast.FunctionDef) and node.name == "resolve_admission")
    _assert_source_statement(ast.walk(resolve),
                             "prepared_transport, prepared_ingress, prepared_admission = deferred_admission_factory()")
    _assert_source_statement(ast.walk(resolve),
                             "prepared_request = _validate_ready_request(prepared_admission, prepared_ingress)")
    _assert_source_statement(ast.walk(resolve),
                             "_validate_ready_request(prepared_admission, server_ingress)")
    _assert_source_statement(ast.walk(resolve), "request = prepared_request")
    _assert_source_statement(ast.walk(resolve), "effective_transport = prepared_transport")
    _assert_source_statement(resolve.body, "return request")
    new_command = next(node for node in ast.walk(compose)
                       if isinstance(node, ast.If)
                       and ast.dump(node.test) == ast.dump(
                           ast.parse('decision.kind == "new_command"', mode="eval").body))
    _assert_source_statement(new_command.body, "request = resolve_admission()")
    locked_input = next(node.value for node in ast.walk(new_command)
                        if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == "locked_input"
                                for target in node.targets))
    assert ast.dump(_source_dict_value(locked_input, "transport")) == ast.dump(
        ast.parse("copy.deepcopy(dict(effective_transport))", mode="eval").body)
    _assert_source_statement(ast.walk(new_command),
                             "locked_admission = admission_adapter(locked_input)")
    _assert_source_statement(ast.walk(new_command),
                             "locked_request = _validate_ready_request(locked_admission, server_ingress)")
    validator = _source_function(composition, "_validate_ready_request")
    expected = next(node.value for node in validator.body
                    if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "expected"
                            for target in node.targets))
    family = _source_dict_value(expected, "route_family")
    assert isinstance(family, ast.Name) and family.id == "DELETE_CONFIRM_ROUTE_FAMILY"
    _assert_source_statement(validator.body,
        'for field, value in expected.items():\n'
        '    if request.get(field) != value:\n'
        '        raise ValueError(f"admitted request disagrees with server-owned {field}")')


def test_current_router_wires_status_confirm_idempotency_surface():
    router_text = _read(ROUTER)
    status_route = _route_body(
        router_text,
        "def confirm_status_proposal_route(",
        "def _a5_check_in_gate_open(",
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
    assert "compose_product_status_confirm(" in status_route
    assert "claim_appointment_command(" not in status_route
    assert "complete_appointment_command(" not in status_route
    assert "_STATUS_CONFIRM_OPERATION_ID" in router_text
    assert "_STATUS_CONFIRM_ROUTE_FAMILY" in router_text
    assert "stored_response_bytes" in status_route
    assert "Header(" in update_route
    assert "Idempotency-Key" in update_route
    assert "_UPDATE_CONFIRM_ROUTE_FAMILY" in update_route
    assert "Header(" in delete_route
    assert "Idempotency-Key" in delete_route
    _assert_delegated_delete_route_family(router_text)


def test_existing_status_confirm_tests_cover_semantics_to_preserve():
    status_tests = _read(STATUS_TESTS)
    reason_tests = _read(REASON_CODE_TESTS)
    audit_tests = _read(APPOINTMENT_AUDIT_TESTS)
    combined = "\n".join([status_tests, reason_tests, audit_tests])

    for phrase in (
        "test_status_confirm_route_writes_once_with_signed_evidence",
        "test_status_confirm_route_blocks_tampered_status_without_write",
        "test_status_confirm_preserves_waiting_area_when_field_omitted",
        "test_status_confirm_clears_waiting_area_when_null_supplied",
        "test_r9_status_confirm_allows_past_date_with_signed_evidence_and_audit",
        "test_r9_status_confirm_past_date_blocks_tampered_status_without_write",
        "status_reason_code",
        "AppointmentAuditAction.status_change",
    ):
        assert phrase in combined


def test_status_confirm_metadata_boundary_is_documented():
    text = _read(ROUTE_TEST_DOC)
    compact = _compact(text)
    router_text = _read(ROUTER)

    assert "_STATUS_CONFIRM_METADATA_FIELDS" in text
    assert "must not be treated as the idempotency request-body canonicalizer" in text
    assert "full validated confirmation body" in compact
    for field in (
        "confirm_endpoint",
        "confirm_payload",
        "status_proposal_freshness_id",
        "signed_confirmation_evidence",
        "signed_confirmation_evidence_required",
    ):
        assert field in router_text


def test_route_contract_test_inventory_matches_wired_surface():
    test_functions = [
        (name, value)
        for name, value in globals().items()
        if name.startswith("test_") and callable(value)
    ]
    assert {name for name, _ in test_functions} == PASSING_CONTRACT_TESTS


def test_missing_idempotency_key_blocks_before_status_or_audit_mutation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _status_payload(client, token, appt.id)
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token))

    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_required"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == before


def test_invalid_status_confirm_payload_does_not_create_ledger_by_default(client, db, gp_user):
    token = make_token(gp_user)

    resp = client.post(
        CONFIRM_URL,
        json={"confirmed": True, "status_proposal": {"not": "valid"}},
        headers=_auth(token, "status-invalid-key"),
    )

    assert resp.status_code == 422, resp.text
    assert db.query(AppointmentCommandIdempotency).count() == 0


def test_first_confirmed_status_change_writes_status_audit_and_ledger(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _status_payload(client, token, appt.id)
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "status-first-key"))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Confirmed
    assert _row_counts(db) == (before[0], before[1] + 1, before[2] + 1)
    ledger = db.query(AppointmentCommandIdempotency).one()
    assert ledger.state == "completed"
    assert ledger.operation_id == OPERATION_ID
    assert ledger.route_family == ROUTE_FAMILY
    assert ledger.response_body_json == data
    assert ledger.target_appointment_id == appt.id


def test_waiting_area_variant_blocks_without_write_or_ledger(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _waiting_area_payload(client, token, appt.id, area.id)
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "waiting-first-key"))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["blocks"][0]["code"] == "unsupported_status_confirm_variant"
    db.refresh(appt)
    assert appt.waiting_area_id is None
    assert _row_counts(db) == before


def test_same_key_same_body_status_replay_has_no_second_status_or_audit_write(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _status_payload(client, token, appt.id)

    first = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "status-replay-key"))
    assert first.status_code == 200, first.text
    after_first = _row_counts(db)

    second = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "status-replay-key"))

    assert second.status_code == 200, second.text
    assert second.content == first.content
    assert second.json() == first.json()
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Confirmed
    assert _row_counts(db) == after_first


def test_waiting_area_repeat_stays_blocked_without_write_or_ledger(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _waiting_area_payload(client, token, appt.id, area.id)
    before = _row_counts(db)

    first = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "waiting-replay-key"))
    assert first.status_code == 200, first.text
    assert first.json()["blocks"][0]["code"] == "unsupported_status_confirm_variant"
    assert _row_counts(db) == before

    second = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "waiting-replay-key"))

    assert second.status_code == 200, second.text
    assert second.content == first.content
    db.refresh(appt)
    assert appt.waiting_area_id is None
    assert _row_counts(db) == before


def test_same_key_different_status_body_conflicts_without_mutation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    first_payload = _status_payload(client, token, appt.id, status_value="Confirmed")
    first = client.post(CONFIRM_URL, json=first_payload, headers=_auth(token, "status-conflict-key"))
    assert first.status_code == 200, first.text
    after_first = _row_counts(db)

    second_payload = _status_payload(client, token, appt.id, status_value="Arrived")
    second = client.post(CONFIRM_URL, json=second_payload, headers=_auth(token, "status-conflict-key"))

    assert second.status_code == 409, second.text
    assert second.json()["detail"]["code"] == "idempotency_key_conflict"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Confirmed
    assert _row_counts(db) == after_first


def test_idempotency_key_does_not_bypass_confirmed_true_signed_evidence_or_freshness(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _status_payload(client, token, appt.id)
    payload["confirmed"] = False
    db.commit()
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "status-block-key"))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert any(block["code"] == "explicit_confirmation_required" for block in data["blocks"])
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == before


def test_waiting_area_variant_cannot_reuse_status_key_to_reopen_write(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient)
    status_payload = _status_payload(client, token, appt.id)
    waiting_payload = _waiting_area_payload(client, token, appt.id, area.id)
    first = client.post(
        CONFIRM_URL,
        json=status_payload,
        headers=_auth(token, "status-union-key"),
    )
    assert first.status_code == 200, first.text
    after_first = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=waiting_payload, headers=_auth(token, "status-union-key"))

    assert resp.status_code == 200, resp.text
    assert resp.json()["blocks"][0]["code"] == "unsupported_status_confirm_variant"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Confirmed
    assert appt.waiting_area_id is None
    assert _row_counts(db) == after_first
