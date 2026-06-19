from datetime import date

from app.config import settings
from app.models.patients import Patient
from tests.conftest import make_token


def _auth(user):
    return {"Authorization": f"Bearer {make_token(user)}"}


def _patient_payload(**overrides):
    payload = {
        "first_name": "Tilly",
        "last_name": "Tester",
        "date_of_birth": "1990-01-02",
        "sex": "Female",
        "medicare_number": "2950123456",
        "phone_mobile": "0400 123 456",
        "address_line1": "12 Test Street",
        "address_suburb": "Brisbane",
        "address_state": "QLD",
        "address_postcode": "4000",
    }
    payload.update(overrides)
    return payload


def _add_patient(db, practice, **overrides):
    data = {
        "practice_id": practice.id,
        "first_name": "Ada",
        "last_name": "Lovelace",
        "date_of_birth": date(1815, 12, 10),
    }
    data.update(overrides)
    patient = Patient(**data)
    db.add(patient)
    db.flush()
    return patient


def test_create_patient_requires_auth(client):
    resp = client.post("/api/v1/patients", json=_patient_payload())
    assert resp.status_code == 401


def test_create_patient_persists_in_current_practice(client, db, gp_user):
    resp = client.post(
        "/api/v1/patients",
        json=_patient_payload(document_url="https://example.test/patient.docx"),
        headers=_auth(gp_user),
    )

    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["practice_id"] == str(gp_user.practice_id)
    assert data["first_name"] == "Tilly"
    assert data["document_url"] == "https://example.test/patient.docx"
    assert data["sms_consent"] is False

    saved = db.query(Patient).filter(Patient.id == data["id"]).one()
    assert saved.practice_id == gp_user.practice_id
    assert saved.medicare_number == "2950123456"


def test_create_patient_validates_required_fields(client, gp_user):
    payload = _patient_payload()
    payload.pop("last_name")

    resp = client.post("/api/v1/patients", json=payload, headers=_auth(gp_user))

    assert resp.status_code == 422


def test_patient_search_matches_name_medicare_and_phone(client, db, practice, gp_user):
    _add_patient(
        db,
        practice,
        first_name="Ada",
        last_name="Lovelace",
        medicare_number="2950123456",
        phone_mobile="0400 123 456",
        phone_home="07 3000 1111",
    )
    _add_patient(
        db,
        practice,
        first_name="Grace",
        last_name="Hopper",
        medicare_number="1876543210",
        phone_mobile="0411 222 333",
    )

    for query in ("lovelace", "295012", "123 456", "3000"):
        resp = client.get(
            "/api/v1/patients/search",
            params={"q": query},
            headers=_auth(gp_user),
        )
        assert resp.status_code == 200
        names = {(p["first_name"], p["last_name"]) for p in resp.json()}
        assert ("Ada", "Lovelace") in names


def test_patient_search_is_practice_scoped(
    client,
    db,
    practice,
    practice_b,
    gp_user,
):
    _add_patient(db, practice, first_name="Visible", last_name="Patient")
    _add_patient(db, practice_b, first_name="Hidden", last_name="Patient")

    resp = client.get(
        "/api/v1/patients/search",
        params={"q": "Patient"},
        headers=_auth(gp_user),
    )

    assert resp.status_code == 200
    returned_names = {p["first_name"] for p in resp.json()}
    assert returned_names == {"Visible"}


def test_patient_search_validates_query_and_limit(client, gp_user):
    missing_q = client.get("/api/v1/patients/search", headers=_auth(gp_user))
    assert missing_q.status_code == 422

    too_large = client.get(
        "/api/v1/patients/search",
        params={"q": "a", "limit": 51},
        headers=_auth(gp_user),
    )
    assert too_large.status_code == 422


def test_create_patient_with_file_returns_filename_and_leaves_document_url_null(
    client,
    db,
    gp_user,
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(settings, "patient_files_dir", str(tmp_path))

    resp = client.post(
        "/api/v1/patients/with-file",
        json=_patient_payload(document_url="https://example.test/should-not-stick.docx"),
        headers=_auth(gp_user),
    )

    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["generated_filename"] == "TILLY TESTER 02-01-1990.docx"
    assert data["document_url"] is None

    generated = tmp_path / data["generated_filename"]
    assert generated.exists()
    assert generated.suffix == ".docx"

    saved = db.query(Patient).filter(Patient.id == data["id"]).one()
    assert saved.practice_id == gp_user.practice_id
    assert saved.document_url is None


def test_create_patient_with_file_is_practice_scoped(client, gp_user_b, monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "patient_files_dir", str(tmp_path))

    resp = client.post(
        "/api/v1/patients/with-file",
        json=_patient_payload(first_name="Other", last_name="Practice"),
        headers=_auth(gp_user_b),
    )

    assert resp.status_code == 201, resp.text
    assert resp.json()["practice_id"] == str(gp_user_b.practice_id)
