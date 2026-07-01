"""
Sprint 98 Bernie confirm-contract regression tests.

Proves four focused guarantees:
1. resolved practitioner_id — interpret-booking-instruction resolves a name to
   a practitioner_id and excludes it from missing_fields.
2. confirm payload round-trip — supervised-booking confirmation_ready
   staff_review.confirm_payload (confirmed=True) succeeds end-to-end and writes
   exactly one appointment.
3. stale/invalid entity safe failure — an entity that becomes missing between
   proposal and confirm returns a structured block (HTTP 200, not 404) and
   writes nothing.
4. no booking before confirm — supervised-booking alone (no confirm call) never
   writes rows.
"""

from datetime import date, datetime, time, timezone
import uuid

from app.config import settings
from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentStatus,
    BookingChannel,
)
import app.routers.appointments as appointments_router
import app.services.ai.service as ai_service
from tests.conftest import make_token

INTERPRET_URL = "/api/v1/appointments/proposals/bernie/interpret-booking-instruction"
SUPERVISED_URL = "/api/v1/appointments/proposals/bernie/supervised-booking"
CONFIRM_URL = "/api/v1/appointments/proposals/create/confirm-bernie"
REFERENCE_DATE = "2026-06-22"


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _row_counts(db) -> tuple[int, int]:
    return (db.query(Appointment).count(), db.query(AppointmentAuditLog).count())


def _install_forbidden_ai_provider_guard(monkeypatch) -> None:
    def forbidden_provider(*args, **kwargs):
        raise AssertionError("Bernie confirm must not call AI providers")
    monkeypatch.setattr(ai_service, "_get_default_provider", forbidden_provider)


def _do_supervised_booking(client, token, practitioner, patient):
    """Run supervised-booking to confirmation_ready with a selected candidate."""
    from tests.test_bernie_confirm_create_proposal import _search_and_select

    search_resp = client.post(
        "/api/v1/appointments/proposals/slot-search/normalized",
        params={"reference_date": REFERENCE_DATE},
        json={
            "practitioner_id": str(practitioner.id),
            "date_from": "today",
            "duration_minutes": "15",
            "patient_id": str(patient.id),
        },
        headers=_auth(token),
    )
    assert search_resp.status_code == 200, search_resp.text
    search = search_resp.json()
    assert search["safe"] is True
    candidates = search["proposal"]["candidates"]
    assert candidates, "No candidate slots — check practitioner schedule fixture"

    resp = client.post(
        SUPERVISED_URL,
        json={
            "reference_date": REFERENCE_DATE,
            "command": {
                "practitioner_id": str(practitioner.id),
                "date_from": "today",
                "duration_minutes": "15",
                "patient_id": str(patient.id),
            },
            "selected_candidate": candidates[0],
            "patient_id": str(patient.id),
        },
        headers=_auth(token),
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


# ── Test 1: resolved practitioner_id ──────────────────────────────────────────

def test_interpret_resolves_practitioner_name_to_id(
    client,
    db,
    gp_user,
    practitioner,
    patient,
    monkeypatch,
):
    """'Dr Shera' in instruction resolves to practitioner_id; missing_fields excludes it."""
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")

    resp = client.post(
        INTERPRET_URL,
        json={
            "instruction": f"Make an appointment for {patient.first_name} {patient.last_name} with Dr {practitioner.last_name}",
            "reference_date": REFERENCE_DATE,
        },
        headers=_auth(make_token(gp_user)),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    candidate = data["command_candidate"]
    assert candidate["practitioner_id"] == str(practitioner.id), (
        "practitioner_id must be resolved from name, not remain null"
    )
    assert "practitioner_id" not in data["missing_fields"], (
        "missing_fields must not list practitioner_id when it has been resolved"
    )
    warning_codes = [w["code"] for w in data["warnings"]]
    assert "practitioner_name_resolved" in warning_codes, (
        "practitioner_name_resolved warning must be emitted on successful name resolution"
    )


# ── Test 2: confirm payload round-trip success ────────────────────────────────

def test_supervised_booking_confirm_payload_round_trip_writes_one_appointment(
    client,
    db,
    gp_user,
    practitioner,
    patient,
    schedule,
    monkeypatch,
):
    """staff_review.confirm_payload from supervised-booking (confirmed=True) confirms and writes one appointment."""
    _install_forbidden_ai_provider_guard(monkeypatch)
    token = make_token(gp_user)
    counts_before = _row_counts(db)

    supervised = _do_supervised_booking(client, token, practitioner, patient)

    assert supervised["result"] == "confirmation_ready", (
        f"Expected confirmation_ready, got: {supervised['result']}"
    )
    staff_review = supervised["staff_review"]
    assert staff_review["confirmation_ready"] is True
    confirm_payload = staff_review["confirm_payload"]
    assert confirm_payload is not None, "confirm_payload must be present when confirmation_ready"

    confirm_payload["confirmed"] = True
    resp = client.post(CONFIRM_URL, json=confirm_payload, headers=_auth(token))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["requires_confirmation"] is False
    assert data["autonomy_tier"] == "confirmed_write"
    assert data["appointment"] is not None
    assert data["appointment"]["practitioner_id"] == str(practitioner.id)
    assert data["appointment"]["patient_id"] == str(patient.id)
    assert data["blocks"] == []
    assert "bernie_confirm_create_proposal" in data["audit_evidence"]

    appts_after, audits_after = _row_counts(db)
    assert appts_after == counts_before[0] + 1, "Exactly one appointment row must be written"
    assert audits_after == counts_before[1] + 1, "Exactly one audit row must be written"


# ── Test 3: stale/invalid entity → structured block, no write ─────────────────

def test_confirm_stale_practitioner_returns_structured_block_not_404(
    client,
    db,
    gp_user,
    practice,
    practitioner,
    patient,
    schedule,
    monkeypatch,
):
    """A practitioner_id that was valid at proposal time but is now gone (or out of
    scope) returns HTTP 200 with a practitioner_not_found block — not a bare 404
    — and writes nothing."""
    _install_forbidden_ai_provider_guard(monkeypatch)
    token = make_token(gp_user)

    supervised = _do_supervised_booking(client, token, practitioner, patient)
    assert supervised["result"] == "confirmation_ready"
    confirm_payload = supervised["staff_review"]["confirm_payload"]

    # Simulate stale entity: replace practitioner_id with one that doesn't exist.
    stale_id = str(uuid.uuid4())
    confirm_payload["selection_proposal"]["create_proposal"]["command"]["practitioner_id"] = stale_id
    confirm_payload["confirmed"] = True
    counts_before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=confirm_payload, headers=_auth(token))

    assert resp.status_code == 200, (
        f"confirm-bernie must return HTTP 200 with structured block, not 404. Got {resp.status_code}: {resp.text}"
    )
    data = resp.json()
    assert data["safe"] is False
    assert data["appointment"] is None
    block_codes = [b["code"] for b in data["blocks"]]
    assert "practitioner_not_found" in block_codes, (
        f"Expected practitioner_not_found block. Got blocks: {block_codes}"
    )
    assert _row_counts(db) == counts_before, "No rows must be written when entity is stale"


def test_confirm_stale_patient_returns_structured_block_not_404(
    client,
    db,
    gp_user,
    practice,
    practitioner,
    patient,
    schedule,
    monkeypatch,
):
    """A patient_id that was valid at proposal time but is now gone (or out of
    scope) returns HTTP 200 with a patient_not_found block — not a bare 404
    — and writes nothing."""
    _install_forbidden_ai_provider_guard(monkeypatch)
    token = make_token(gp_user)

    supervised = _do_supervised_booking(client, token, practitioner, patient)
    assert supervised["result"] == "confirmation_ready"
    confirm_payload = supervised["staff_review"]["confirm_payload"]

    # Simulate stale entity: replace patient_id with one that doesn't exist.
    stale_id = str(uuid.uuid4())
    confirm_payload["selection_proposal"]["create_proposal"]["command"]["patient_id"] = stale_id
    confirm_payload["confirmed"] = True
    counts_before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=confirm_payload, headers=_auth(token))

    assert resp.status_code == 200, (
        f"confirm-bernie must return HTTP 200 with structured block, not 404. Got {resp.status_code}: {resp.text}"
    )
    data = resp.json()
    assert data["safe"] is False
    assert data["appointment"] is None
    block_codes = [b["code"] for b in data["blocks"]]
    assert "patient_not_found" in block_codes, (
        f"Expected patient_not_found block. Got blocks: {block_codes}"
    )
    assert _row_counts(db) == counts_before, "No rows must be written when entity is stale"


# ── Test 4: no booking before confirm ─────────────────────────────────────────

def test_supervised_booking_alone_writes_no_rows(
    client,
    db,
    gp_user,
    practitioner,
    patient,
    schedule,
    monkeypatch,
):
    """supervised-booking, even reaching confirmation_ready, must never write appointment or audit rows."""
    _install_forbidden_ai_provider_guard(monkeypatch)
    token = make_token(gp_user)
    counts_before = _row_counts(db)

    supervised = _do_supervised_booking(client, token, practitioner, patient)

    assert supervised["result"] == "confirmation_ready"
    assert _row_counts(db) == counts_before, (
        "supervised-booking must write zero rows — no appointment or audit created without confirm"
    )
