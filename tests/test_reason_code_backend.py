from datetime import date, datetime, time, timedelta, timezone

import pytest

from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentAuditAction,
    AppointmentStatus,
    BookingChannel,
)
from app.schemas.appointments import (
    STATUS_REASON_CODES,
    STATUS_SPECIFIC_REASON_CODE_POLICY,
    validate_status_reason_code_for_status,
)
from tests.conftest import make_token


TODAY = date.today() + timedelta(days=14)
PAST_DATE = date(2026, 4, 15)
APPT_URL = "/api/v1/appointments"
DELETE_CONFIRM_URL = f"{APPT_URL}/proposals/delete-confirm"
STATUS_CONFIRM_URL = f"{APPT_URL}/proposals/status-confirm"


def _make_appt(
    db,
    practice,
    practitioner,
    patient,
    status=AppointmentStatus.Booked,
    appt_date=None,
    start_h=9,
):
    appt_date = appt_date if appt_date is not None else TODAY
    appt = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(appt_date, time(start_h, 0), tzinfo=timezone.utc),
        appointment_date=appt_date,
        start_time_local=time(start_h, 0),
        duration_minutes=15,
        status=status,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt)
    db.flush()
    return appt


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


_delete_confirm_key_counter = 0


def _auth_delete_confirm(token):
    global _delete_confirm_key_counter
    _delete_confirm_key_counter += 1
    headers = _auth(token)
    headers["Idempotency-Key"] = f"reason-delete-confirm-{_delete_confirm_key_counter}"
    return headers


_status_confirm_key_counter = 0


def _auth_status_confirm(token):
    global _status_confirm_key_counter
    _status_confirm_key_counter += 1
    headers = _auth(token)
    headers["Idempotency-Key"] = f"reason-status-confirm-{_status_confirm_key_counter}"
    return headers


def test_reason_code_taxonomy_contains_expected_codes():
    assert {
        "PATIENT_CANCELLED",
        "DID_NOT_ATTEND",
        "LEFT_WITHOUT_SEEN",
        "LEGACY_UNCLASSIFIED",
    }.issubset(STATUS_REASON_CODES)


def test_raw_patch_status_persists_status_reason_code(
    client, db, gp_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = client.patch(
        f"{APPT_URL}/{appt.id}/status",
        json={"status": "Cancelled", "status_reason_code": "PATIENT_CANCELLED"},
        headers=_auth(token),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status_reason_code"] == "PATIENT_CANCELLED"
    db.refresh(appt)
    assert appt.status_reason_code == "PATIENT_CANCELLED"

    entries = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).all()
    assert len(entries) == 1
    assert entries[0].action == AppointmentAuditAction.status_change
    assert entries[0].status_reason_code == "PATIENT_CANCELLED"


def test_raw_patch_status_rejects_invalid_status_reason_code(
    client, db, gp_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = client.patch(
        f"{APPT_URL}/{appt.id}/status",
        json={"status": "Cancelled", "status_reason_code": "patient_cancelled"},
        headers=_auth(token),
    )
    assert resp.status_code == 422


def test_raw_patch_status_omitted_reason_code_stays_null(
    client, db, gp_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = client.patch(
        f"{APPT_URL}/{appt.id}/status",
        json={"status": "Cancelled"},
        headers=_auth(token),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status_reason_code"] is None
    db.refresh(appt)
    assert appt.status_reason_code is None


def test_status_proposal_confirm_persists_status_reason_code(
    client, db, gp_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    proposal_resp = client.post(
        f"{APPT_URL}/proposals/status/{appt.id}",
        json={"status": "NoShow", "status_reason_code": "DID_NOT_ATTEND"},
        headers=_auth(token),
    )
    assert proposal_resp.status_code == 200, proposal_resp.text
    assert proposal_resp.json()["command"]["status_reason_code"] == "DID_NOT_ATTEND"
    payload = proposal_resp.json()["confirm_payload"]
    payload["confirmed"] = True

    confirm_resp = client.post(STATUS_CONFIRM_URL, json=payload, headers=_auth_status_confirm(token))
    assert confirm_resp.status_code == 200, confirm_resp.text
    assert confirm_resp.json()["appointment"]["status_reason_code"] == "DID_NOT_ATTEND"

    entries = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).all()
    assert len(entries) == 1
    assert entries[0].status_after == AppointmentStatus.NoShow
    assert entries[0].status_reason_code == "DID_NOT_ATTEND"


def test_delete_proposal_confirm_persists_status_reason_code_and_text_reason(
    client, db, gp_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient, appt_date=PAST_DATE)
    token = make_token(gp_user)

    proposal_resp = client.post(
        f"{APPT_URL}/proposals/delete/{appt.id}",
        json={
            "cancellation_reason": "Duplicate booking",
            "status_reason_code": "DUPLICATE_BOOKING",
        },
        headers=_auth(token),
    )
    assert proposal_resp.status_code == 200, proposal_resp.text
    assert proposal_resp.json()["command"]["status_reason_code"] == "DUPLICATE_BOOKING"
    payload = proposal_resp.json()["confirm_payload"]
    payload["confirmed"] = True

    confirm_resp = client.post(DELETE_CONFIRM_URL, json=payload, headers=_auth_delete_confirm(token))
    assert confirm_resp.status_code == 200, confirm_resp.text
    appointment = confirm_resp.json()["appointment"]
    assert appointment["status_reason_code"] == "DUPLICATE_BOOKING"
    assert appointment["cancellation_reason"] == "Duplicate booking"

    entries = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).all()
    assert len(entries) == 1
    assert entries[0].action == AppointmentAuditAction.delete
    assert entries[0].status_reason_code == "DUPLICATE_BOOKING"
    assert entries[0].cancellation_reason == "Duplicate booking"


@pytest.mark.parametrize("path_builder,payload", [
    (
        lambda appt_id: f"{APPT_URL}/proposals/status/{appt_id}",
        {"status": "Cancelled", "status_reason_code": "COVID_SYMPTOMS"},
    ),
    (
        lambda appt_id: f"{APPT_URL}/proposals/delete/{appt_id}",
        {
            "cancellation_reason": "Patient called",
            "status_reason_code": "COVID_SYMPTOMS",
        },
    ),
])
def test_proposals_reject_invalid_status_reason_code(
    path_builder, payload, client, db, gp_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = client.post(path_builder(appt.id), json=payload, headers=_auth(token))
    assert resp.status_code == 422


def test_past_date_status_and_delete_allow_null_status_reason_code(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    status_appt = _make_appt(db, practice, practitioner, patient, appt_date=PAST_DATE, start_h=9)
    delete_appt = _make_appt(db, practice, practitioner, patient, appt_date=PAST_DATE, start_h=10)

    status_resp = client.patch(
        f"{APPT_URL}/{status_appt.id}/status",
        json={"status": "DNA"},
        headers=_auth(token),
    )
    assert status_resp.status_code == 200, status_resp.text
    assert status_resp.json()["status_reason_code"] is None

    delete_resp = client.request(
        "DELETE",
        f"{APPT_URL}/{delete_appt.id}",
        json={"cancellation_reason": "Historical correction"},
        headers=_auth(token),
    )
    assert delete_resp.status_code == 204


def test_policy_cancelled_rejects_dna_code():
    """Cancelled appointments must not accept DID_NOT_ATTEND."""
    with pytest.raises(ValueError, match="not valid for status"):
        validate_status_reason_code_for_status(AppointmentStatus.Cancelled, "DID_NOT_ATTEND")


def test_policy_cancelled_rejects_left_without_seen():
    with pytest.raises(ValueError, match="not valid for status"):
        validate_status_reason_code_for_status(AppointmentStatus.Cancelled, "LEFT_WITHOUT_SEEN")


def test_policy_cancelled_accepts_own_codes():
    """All codes in the Cancelled policy set must be accepted."""
    allowed = STATUS_SPECIFIC_REASON_CODE_POLICY[AppointmentStatus.Cancelled]
    for code in allowed:
        result = validate_status_reason_code_for_status(AppointmentStatus.Cancelled, code)
        assert result == code


def test_policy_dna_rejects_cancellation_code():
    with pytest.raises(ValueError, match="not valid for status"):
        validate_status_reason_code_for_status(AppointmentStatus.DNA, "PATIENT_CANCELLED")


def test_policy_dna_accepts_own_codes():
    allowed = STATUS_SPECIFIC_REASON_CODE_POLICY[AppointmentStatus.DNA]
    for code in allowed:
        result = validate_status_reason_code_for_status(AppointmentStatus.DNA, code)
        assert result == code


def test_policy_noshow_rejects_cancellation_code():
    with pytest.raises(ValueError, match="not valid for status"):
        validate_status_reason_code_for_status(AppointmentStatus.NoShow, "PATIENT_CANCELLED")


def test_policy_noshow_accepts_own_codes():
    allowed = STATUS_SPECIFIC_REASON_CODE_POLICY[AppointmentStatus.NoShow]
    for code in allowed:
        result = validate_status_reason_code_for_status(AppointmentStatus.NoShow, code)
        assert result == code


def test_policy_null_is_always_accepted():
    """None status_reason_code must pass for every status, including terminal ones."""
    for status in AppointmentStatus:
        result = validate_status_reason_code_for_status(status, None)
        assert result is None


def test_policy_non_terminal_status_is_unrestricted():
    """Booked, Confirmed, Arrived, InConsult, Completed should pass any valid code."""
    non_terminal = [
        AppointmentStatus.Booked,
        AppointmentStatus.Confirmed,
        AppointmentStatus.Arrived,
        AppointmentStatus.InConsult,
        AppointmentStatus.Completed,
    ]
    for status in non_terminal:
        result = validate_status_reason_code_for_status(status, "DID_NOT_ATTEND")
        assert result == "DID_NOT_ATTEND"
        result = validate_status_reason_code_for_status(status, None)
        assert result is None


# --- End-to-end status-proposal rejection tests ---

@pytest.mark.parametrize("invalid_code", [
    "DID_NOT_ATTEND",
    "LEFT_WITHOUT_SEEN",
])
def test_raw_patch_cancelled_rejects_dna_reason_codes(
    invalid_code, client, db, gp_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = client.patch(
        f"{APPT_URL}/{appt.id}/status",
        json={"status": "Cancelled", "status_reason_code": invalid_code},
        headers=_auth(token),
    )
    assert resp.status_code == 422, resp.text


@pytest.mark.parametrize("status,valid_code", [
    ("Cancelled", "PATIENT_CANCELLED"),
    ("Cancelled", "ADMIN_ERROR"),
    ("DNA", "DID_NOT_ATTEND"),
    ("DNA", "LEFT_WITHOUT_SEEN"),
    ("NoShow", "DID_NOT_ATTEND"),
    ("NoShow", "ADMIN_ERROR"),
])
def test_raw_patch_status_accepts_valid_status_code_combos(
    status, valid_code, client, db, gp_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = client.patch(
        f"{APPT_URL}/{appt.id}/status",
        json={"status": status, "status_reason_code": valid_code},
        headers=_auth(token),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status_reason_code"] == valid_code


@pytest.mark.parametrize("valid_code", [
    "PATIENT_RESCHEDULED",
    "PATIENT_UNWELL",
    "CLINIC_RESCHEDULED",
])
def test_raw_patch_cancelled_accepts_cancellation_policy_codes(
    valid_code, client, db, gp_user, practice, practitioner, patient
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = client.patch(
        f"{APPT_URL}/{appt.id}/status",
        json={"status": "Cancelled", "status_reason_code": valid_code},
        headers=_auth(token),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status_reason_code"] == valid_code


# --- Frontend-drift detection ---

def _parse_diary_js_status_options(path="docs/diary/diary.js"):
    """Parse STATUS_SPECIFIC_REASON_CODE_OPTIONS from diary.js.

    Returns dict[str, set[str]] mapping status label to its code set.
    """
    import re
    with open(path, encoding="utf-8") as f:
        text = f.read()

    pattern = r"const STATUS_SPECIFIC_REASON_CODE_OPTIONS\s*=\s*\{([^;]+?)\};"
    match = re.search(pattern, text, re.DOTALL)
    assert match, f"Could not find STATUS_SPECIFIC_REASON_CODE_OPTIONS in {path}"

    body = match.group(1)
    result = {}

    status_pattern = re.compile(
        r"(?P<status>\w+)\s*:\s*\[(?P<codes>[^\]]+)\]"
    )
    for status_match in status_pattern.finditer(body):
        status = status_match.group("status")
        codes_raw = status_match.group("codes")
        codes = set()
        for code_match in re.finditer(r'"([^"]+)"', codes_raw):
            codes.add(code_match.group(1))
        result[status] = codes

    return result


def test_frontend_status_specific_options_match_backend_policy():
    """Every status+code pair in diary.js STATUS_SPECIFIC_REASON_CODE_OPTIONS
    must exist in the backend STATUS_SPECIFIC_REASON_CODE_POLICY, and vice
    versa. This catches silent drift between the frontend UI dropdown and the
    server-side source of truth."""
    frontend = _parse_diary_js_status_options()

    status_label_map = {s: s.value for s in AppointmentStatus}

    for status_enum, backend_codes in STATUS_SPECIFIC_REASON_CODE_POLICY.items():
        label = status_label_map[status_enum]
        frontend_codes = frontend.get(label)
        assert frontend_codes is not None, (
            f"Missing frontend entry for status '{label}' "
            f"(backend has {sorted(backend_codes)})"
        )
        extra_in_backend = backend_codes - frontend_codes
        extra_in_frontend = frontend_codes - backend_codes
        assert not extra_in_backend, (
            f"Backend policy for '{label}' has codes {sorted(extra_in_backend)} "
            f"that frontend does not offer"
        )
        assert not extra_in_frontend, (
            f"Frontend options for '{label}' include codes {sorted(extra_in_frontend)} "
            f"that backend policy does not allow"
        )
