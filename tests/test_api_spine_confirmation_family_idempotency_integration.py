from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import import_module
from typing import Callable

import pytest

import app.routers.appointments as appointments_router
from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentCommandIdempotency,
)
from app.routers.appointments import _BERNIE_SESSION_STORE
from tests.conftest import make_token


staff_create = import_module("tests.test_api_spine_staff_create_confirm_idempotency_route_contract")
bernie_create = import_module("tests.test_api_spine_bernie_create_confirm_idempotency_route_contract")
status_confirm = import_module("tests.test_api_spine_status_confirm_idempotency_route_contract")
update_confirm = import_module("tests.test_api_spine_update_confirm_idempotency_route_contract")
delete_confirm = import_module("tests.test_api_spine_delete_confirm_idempotency_route_contract")


@dataclass(frozen=True)
class ConfirmationFamily:
    name: str
    confirm_url: str
    operation_id: str
    route_family: str
    build_payload: Callable
    build_conflict_payload: Callable
    preclaim: Callable


@pytest.fixture(autouse=True)
def _freeze_confirmation_family_clock(monkeypatch):
    def fixed_now(tz):
        return datetime(2026, 6, 22, 8, 0, 0, tzinfo=tz)

    monkeypatch.setattr(appointments_router, "_clinic_local_now", fixed_now)


def _auth(token: str, idempotency_key: str | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    if idempotency_key is not None:
        headers["Idempotency-Key"] = idempotency_key
    return headers


def _row_counts(db) -> tuple[int, int, int]:
    return (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
        db.query(AppointmentCommandIdempotency).count(),
    )


def _session_event_count(payload: dict) -> int | None:
    binding = payload.get("session_binding")
    if not binding:
        selection = payload.get("selection_proposal") or {}
        binding = selection.get("session_binding")
    if not binding:
        return None
    session = _BERNIE_SESSION_STORE.get_session(binding["session_id"])
    assert session is not None
    return len(session.events)


def _effect_snapshot(db, payload: dict) -> tuple[tuple[int, int, int], int | None]:
    return _row_counts(db), _session_event_count(payload)


def _assert_effect_snapshot(db, payload: dict, expected):
    assert _effect_snapshot(db, payload) == expected


def _append_warning(payload: dict, warning: str) -> dict:
    changed = deepcopy(payload)
    changed["confirmed_warnings"] = [warning]
    return changed


def _build_staff_create(context) -> dict:
    proposal = staff_create._proposal(
        context["client"],
        context["token"],
        context["patient"],
        context["practitioner"],
    )
    return staff_create._confirm_payload(proposal)


def _build_staff_create_conflict(context) -> dict:
    proposal = staff_create._proposal(
        context["client"],
        context["token"],
        context["patient"],
        context["practitioner"],
        start="09:30:00",
    )
    return staff_create._confirm_payload(proposal)


def _build_bernie_create(context) -> dict:
    return bernie_create._bound_confirm_payload(
        context["client"],
        context["token"],
        context["practitioner"],
        context["patient"],
        surface_id=f"s146-{context['case']}",
    )


def _build_status(context) -> dict:
    appt = status_confirm._make_appt(
        context["db"],
        context["practice"],
        context["practitioner"],
        context["patient"],
    )
    context["appointment"] = appt
    return status_confirm._status_payload(context["client"], context["token"], appt.id)


def _build_status_conflict(context) -> dict:
    return status_confirm._status_payload(
        context["client"],
        context["token"],
        context["appointment"].id,
        status_value="Arrived",
    )


def _build_update(context) -> dict:
    appt = update_confirm._make_appt(
        context["db"],
        context["practice"],
        context["practitioner"],
        context["patient"],
    )
    context["appointment"] = appt
    return update_confirm._update_payload(context["client"], context["token"], appt.id)


def _build_delete(context) -> dict:
    appt = delete_confirm._make_appt(
        context["db"],
        context["practice"],
        context["practitioner"],
        context["patient"],
    )
    context["appointment"] = appt
    return delete_confirm._delete_payload(context["client"], context["token"], appt.id)


CONFIRMATION_FAMILIES = [
    ConfirmationFamily(
        name="staff_create",
        confirm_url=staff_create.CONFIRM_URL,
        operation_id=staff_create.OPERATION_ID,
        route_family=staff_create.ROUTE_FAMILY,
        build_payload=_build_staff_create,
        build_conflict_payload=_build_staff_create_conflict,
        preclaim=staff_create._preclaim,
    ),
    ConfirmationFamily(
        name="bernie_create",
        confirm_url=bernie_create.CONFIRM_URL,
        operation_id=bernie_create.OPERATION_ID,
        route_family=bernie_create.ROUTE_FAMILY,
        build_payload=_build_bernie_create,
        # Minimum viable body-hash conflict for the session-bound Bernie shape.
        # Strengthen this if Bernie selection/session payload variants expand.
        build_conflict_payload=lambda context: _append_warning(context["payload"], "changed-body"),
        preclaim=bernie_create._preclaim,
    ),
    ConfirmationFamily(
        name="status",
        confirm_url=status_confirm.CONFIRM_URL,
        operation_id=status_confirm.OPERATION_ID,
        route_family=status_confirm.ROUTE_FAMILY,
        build_payload=_build_status,
        build_conflict_payload=_build_status_conflict,
        preclaim=status_confirm._preclaim,
    ),
    ConfirmationFamily(
        name="update",
        confirm_url=update_confirm.CONFIRM_URL,
        operation_id=update_confirm.OPERATION_ID,
        route_family=update_confirm.ROUTE_FAMILY,
        build_payload=_build_update,
        build_conflict_payload=lambda context: _append_warning(context["payload"], "changed-body"),
        preclaim=update_confirm._preclaim,
    ),
    ConfirmationFamily(
        name="delete",
        confirm_url=delete_confirm.CONFIRM_URL,
        operation_id=delete_confirm.OPERATION_ID,
        route_family=delete_confirm.ROUTE_FAMILY,
        build_payload=_build_delete,
        build_conflict_payload=lambda context: _append_warning(context["payload"], "changed-body"),
        preclaim=delete_confirm._preclaim,
    ),
]


@pytest.fixture(params=CONFIRMATION_FAMILIES, ids=[family.name for family in CONFIRMATION_FAMILIES])
def family(request):
    return request.param


@pytest.fixture
def family_context(client, db, gp_user, practice, practitioner, patient, schedule, family):
    return {
        "client": client,
        "db": db,
        "gp_user": gp_user,
        "practice": practice,
        "practitioner": practitioner,
        "patient": patient,
        "schedule": schedule,
        "family": family,
        "token": make_token(gp_user),
        "case": f"{family.name}-base",
    }


def _post_confirm(context, payload: dict, key: str | None):
    family = context["family"]
    return context["client"].post(
        family.confirm_url,
        json=payload,
        headers=_auth(context["token"], key),
    )


def _preclaim(context, payload: dict, key: str):
    return context["family"].preclaim(context["db"], context["gp_user"], payload, key=key)


def test_all_confirmation_families_require_idempotency_key_before_side_effects(
    family_context,
):
    payload = family_context["family"].build_payload(family_context)
    before = _effect_snapshot(family_context["db"], payload)

    resp = _post_confirm(family_context, payload, None)

    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_required"
    _assert_effect_snapshot(family_context["db"], payload, before)


def test_all_confirmation_families_replay_same_key_same_body_without_second_side_effect(
    family_context,
):
    payload = family_context["family"].build_payload(family_context)
    key = f"s146-{family_context['family'].name}-replay"

    first = _post_confirm(family_context, payload, key)
    assert first.status_code == 200, first.text
    assert first.json()["safe"] is True
    after_first = _effect_snapshot(family_context["db"], payload)

    second = _post_confirm(family_context, payload, key)

    assert second.status_code == 200, second.text
    assert second.json() == first.json()
    _assert_effect_snapshot(family_context["db"], payload, after_first)
    ledger = family_context["db"].query(AppointmentCommandIdempotency).one()
    assert ledger.operation_id == family_context["family"].operation_id
    assert ledger.route_family == family_context["family"].route_family
    assert ledger.state == "completed"
    assert ledger.response_body_json == first.json()


def test_all_confirmation_families_conflict_same_key_different_body_without_side_effect(
    family_context,
):
    payload = family_context["family"].build_payload(family_context)
    family_context["payload"] = payload
    key = f"s146-{family_context['family'].name}-conflict"
    first = _post_confirm(family_context, payload, key)
    assert first.status_code == 200, first.text
    after_first = _effect_snapshot(family_context["db"], payload)

    changed = family_context["family"].build_conflict_payload(family_context)
    second = _post_confirm(family_context, changed, key)

    assert second.status_code == 409, second.text
    assert second.json()["detail"]["code"] == "idempotency_key_conflict"
    _assert_effect_snapshot(family_context["db"], payload, after_first)


@pytest.mark.parametrize(
    ("state", "expected_status", "expected_code"),
    [
        ("in_progress", 409, "idempotency_key_in_progress"),
        ("stale_in_progress", 409, "idempotency_key_stale_in_progress"),
        ("failed_transient", 503, "idempotency_key_failed_transient"),
    ],
)
def test_all_confirmation_families_fail_closed_for_non_replay_ledger_states(
    family_context,
    state,
    expected_status,
    expected_code,
):
    payload = family_context["family"].build_payload(family_context)
    key = f"s146-{family_context['family'].name}-{state}"
    claim = _preclaim(family_context, payload, key)
    assert claim.kind == "started"
    if state == "stale_in_progress":
        claim.record.updated_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
        family_context["db"].flush()
    elif state == "failed_transient":
        claim.record.state = "failed_transient"
        family_context["db"].flush()
    before = _effect_snapshot(family_context["db"], payload)

    resp = _post_confirm(family_context, payload, key)

    assert resp.status_code == expected_status, resp.text
    assert resp.json()["detail"]["code"] == expected_code
    _assert_effect_snapshot(family_context["db"], payload, before)
