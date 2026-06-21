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
        "medicare_irn": "1",
        "ihi_number": "8003608833357361",
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
    practice_id = str(gp_user.practice_id)
    resp = client.post(
        "/api/v1/patients",
        json=_patient_payload(document_url="https://example.test/patient.docx"),
        headers=_auth(gp_user),
    )

    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["practice_id"] == practice_id
    assert data["first_name"] == "Tilly"
    assert data["document_url"] == "https://example.test/patient.docx"
    assert data["sms_consent"] is False
    assert data["medicare_irn"] == "1"
    assert data["ihi_number"] == "8003608833357361"

    saved = db.query(Patient).filter(Patient.id == data["id"]).one()
    assert str(saved.practice_id) == practice_id
    assert saved.medicare_number == "2950123456"
    assert saved.medicare_irn == "1"
    assert saved.ihi_number == "8003608833357361"


def test_create_patient_validates_required_fields(client, gp_user):
    payload = _patient_payload()
    payload.pop("last_name")

    resp = client.post("/api/v1/patients", json=payload, headers=_auth(gp_user))

    assert resp.status_code == 422


def test_create_patient_validates_medicare_irn_length(client, gp_user):
    resp = client.post(
        "/api/v1/patients",
        json=_patient_payload(medicare_irn="123"),
        headers=_auth(gp_user),
    )

    assert resp.status_code == 422


def test_patient_search_matches_name_medicare_and_phone(client, db, practice, gp_user):
    _add_patient(
        db,
        practice,
        first_name="Ada",
        last_name="Lovelace",
        medicare_number="2950123456",
        medicare_irn="4",
        ihi_number="8003608833357361",
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

    for query in ("lovelace", "295012", "4", "8003608833357361", "123 456", "3000"):
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


def test_update_patient_accepts_identity_fields(client, db, practice, gp_user):
    patient = _add_patient(db, practice, medicare_number="2950123456")

    resp = client.put(
        f"/api/v1/patients/{patient.id}",
        json={
            "medicare_irn": "2",
            "ihi_number": "8003608833357361",
        },
        headers=_auth(gp_user),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["medicare_irn"] == "2"
    assert data["ihi_number"] == "8003608833357361"

    db.refresh(patient)
    assert patient.medicare_irn == "2"
    assert patient.ihi_number == "8003608833357361"


def test_update_patient_allows_resaving_own_strong_identifiers(client, db, practice, gp_user):
    patient = _add_patient(
        db,
        practice,
        medicare_number="2950123456",
        medicare_irn="1",
        ihi_number="8003608833357361",
    )

    resp = client.put(
        f"/api/v1/patients/{patient.id}",
        json={
            "medicare_number": "2950 123 456",
            "medicare_irn": "1",
            "ihi_number": "8003 6088 3335 7361",
        },
        headers=_auth(gp_user),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["medicare_number"] == "2950 123 456"
    assert data["medicare_irn"] == "1"
    assert data["ihi_number"] == "8003 6088 3335 7361"


def test_update_patient_blocks_duplicate_ihi_from_other_patient(client, db, practice, gp_user):
    existing = _add_patient(
        db,
        practice,
        first_name="Existing",
        last_name="Strong",
        ihi_number="8003608833357361",
    )
    target = _add_patient(
        db,
        practice,
        first_name="Target",
        last_name="Patient",
        ihi_number="8003608833357362",
    )

    resp = client.put(
        f"/api/v1/patients/{target.id}",
        json={"ihi_number": "8003 6088 3335 7361"},
        headers=_auth(gp_user),
    )

    assert resp.status_code == 409, resp.text
    detail = resp.json()["detail"]
    assert detail["existing_patient_id"] == str(existing.id)
    assert detail["match_reasons"] == ["same_ihi"]

    db.refresh(target)
    assert target.ihi_number == "8003608833357362"


def test_update_patient_blocks_duplicate_medicare_card_and_irn_from_partial_edit(
    client,
    db,
    practice,
    gp_user,
):
    existing = _add_patient(
        db,
        practice,
        first_name="Existing",
        last_name="Strong",
        medicare_number="2950123456",
        medicare_irn="1",
    )
    target = _add_patient(
        db,
        practice,
        first_name="Target",
        last_name="Patient",
        medicare_number="2950123456",
        medicare_irn="2",
    )

    resp = client.put(
        f"/api/v1/patients/{target.id}",
        json={"medicare_irn": "1"},
        headers=_auth(gp_user),
    )

    assert resp.status_code == 409, resp.text
    detail = resp.json()["detail"]
    assert detail["existing_patient_id"] == str(existing.id)
    assert detail["match_reasons"] == ["same_medicare_card_and_irn"]

    db.refresh(target)
    assert target.medicare_irn == "2"


def test_update_patient_blocks_duplicate_medicare_card_and_irn_from_full_edit(
    client,
    db,
    practice,
    gp_user,
):
    existing = _add_patient(
        db,
        practice,
        first_name="Existing",
        last_name="Strong",
        medicare_number="2950123456",
        medicare_irn="1",
    )
    target = _add_patient(
        db,
        practice,
        first_name="Target",
        last_name="Patient",
        medicare_number="1876543210",
        medicare_irn="2",
    )

    resp = client.put(
        f"/api/v1/patients/{target.id}",
        json={
            "medicare_number": "2950 123 456",
            "medicare_irn": "1",
        },
        headers=_auth(gp_user),
    )

    assert resp.status_code == 409, resp.text
    detail = resp.json()["detail"]
    assert detail["existing_patient_id"] == str(existing.id)
    assert detail["match_reasons"] == ["same_medicare_card_and_irn"]

    db.refresh(target)
    assert target.medicare_number == "1876543210"
    assert target.medicare_irn == "2"


def test_update_patient_duplicate_check_is_practice_scoped(
    client,
    db,
    practice,
    practice_b,
    gp_user,
):
    target = _add_patient(db, practice, first_name="Visible", last_name="Patient")
    _add_patient(
        db,
        practice_b,
        first_name="Hidden",
        last_name="Patient",
        ihi_number="8003608833357361",
    )

    resp = client.put(
        f"/api/v1/patients/{target.id}",
        json={"ihi_number": "8003608833357361"},
        headers=_auth(gp_user),
    )

    assert resp.status_code == 200, resp.text
    assert resp.json()["ihi_number"] == "8003608833357361"


def test_duplicate_candidates_report_identity_reasons_and_hard_block_creation(
    client,
    db,
    practice,
    gp_user,
):
    existing = _add_patient(
        db,
        practice,
        first_name="Tilly",
        last_name="Tester",
        date_of_birth=date(1990, 1, 2),
        medicare_number="2950123456",
        medicare_irn="1",
        ihi_number="8003608833357361",
        phone_mobile="0400 123 456",
    )

    candidates = client.get(
        "/api/v1/patients/duplicate-candidates",
        params={
            "first_name": "tilly",
            "last_name": "tester",
            "date_of_birth": "1990-01-02",
            "medicare_number": "2950123456",
            "medicare_irn": "1",
            "ihi_number": "8003608833357361",
            "phone_mobile": "0400 123 456",
        },
        headers=_auth(gp_user),
    )

    assert candidates.status_code == 200, candidates.text
    data = candidates.json()
    assert len(data) == 1
    assert data[0]["patient"]["id"] == str(existing.id)
    assert set(data[0]["match_reasons"]) == {
        "same_ihi",
        "same_medicare_card_and_irn",
        "same_name_and_dob",
        "same_phone_and_dob",
    }

    create_resp = client.post(
        "/api/v1/patients",
        json=_patient_payload(),
        headers=_auth(gp_user),
    )
    assert create_resp.status_code == 409, create_resp.text
    assert create_resp.json()["detail"]["match_reasons"] == [
        "same_ihi",
        "same_medicare_card_and_irn",
    ]


def test_create_patient_allows_warning_only_duplicate_signals(
    client,
    db,
    practice,
    gp_user,
):
    _add_patient(
        db,
        practice,
        first_name="Tilly",
        last_name="Tester",
        date_of_birth=date(1990, 1, 2),
        medicare_number="2950123456",
        medicare_irn="1",
        phone_mobile="0400 123 456",
        address_line1="12 Test Street",
    )

    create_resp = client.post(
        "/api/v1/patients",
        json=_patient_payload(
            medicare_number="2950123456",
            medicare_irn="2",
            ihi_number=None,
        ),
        headers=_auth(gp_user),
    )

    assert create_resp.status_code == 201, create_resp.text


def test_duplicate_candidates_are_practice_scoped(client, db, practice, practice_b, gp_user):
    visible = _add_patient(
        db,
        practice,
        first_name="Visible",
        last_name="Patient",
        date_of_birth=date(1990, 1, 2),
        ihi_number="8003608833357361",
    )
    _add_patient(
        db,
        practice_b,
        first_name="Hidden",
        last_name="Patient",
        date_of_birth=date(1990, 1, 2),
        ihi_number="8003608833357361",
    )

    resp = client.get(
        "/api/v1/patients/duplicate-candidates",
        params={"ihi_number": "8003608833357361"},
        headers=_auth(gp_user),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert [candidate["patient"]["id"] for candidate in data] == [str(visible.id)]


def test_duplicate_candidates_normalise_formatted_identifiers(client, db, practice, gp_user):
    existing = _add_patient(
        db,
        practice,
        first_name="Tilly",
        last_name="Tester",
        date_of_birth=date(1990, 1, 2),
        medicare_number="2950123456",
        medicare_irn="1",
        phone_mobile="0400123456",
    )

    resp = client.get(
        "/api/v1/patients/duplicate-candidates",
        params={
            "date_of_birth": "1990-01-02",
            "medicare_number": "2950 123 456",
            "medicare_irn": "1",
            "phone_mobile": "0400 123 456",
        },
        headers=_auth(gp_user),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 1
    assert data[0]["patient"]["id"] == str(existing.id)
    assert set(data[0]["match_reasons"]) == {
        "same_medicare_card_and_irn",
        "same_phone_and_dob",
    }


def test_duplicate_candidates_require_identity_signal(client, gp_user):
    resp = client.get(
        "/api/v1/patients/duplicate-candidates",
        params={"first_name": "Tilly"},
        headers=_auth(gp_user),
    )

    assert resp.status_code == 422


def test_create_patient_with_file_returns_filename_and_leaves_document_url_null(
    client,
    db,
    gp_user,
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(settings, "patient_files_dir", str(tmp_path))
    practice_id = str(gp_user.practice_id)

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
    assert str(saved.practice_id) == practice_id
    assert saved.document_url is None


def test_create_patient_with_file_blocks_hard_duplicate_before_file_generation(
    client,
    db,
    practice,
    gp_user,
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(settings, "patient_files_dir", str(tmp_path))
    _add_patient(
        db,
        practice,
        first_name="Existing",
        last_name="Patient",
        date_of_birth=date(1980, 1, 1),
        medicare_number="2950123456",
        medicare_irn="1",
    )

    resp = client.post(
        "/api/v1/patients/with-file",
        json=_patient_payload(
            first_name="Other",
            last_name="Person",
            date_of_birth="1985-02-03",
            ihi_number=None,
        ),
        headers=_auth(gp_user),
    )

    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"]["match_reasons"] == ["same_medicare_card_and_irn"]
    assert list(tmp_path.glob("*.docx")) == []


def test_create_patient_with_file_is_practice_scoped(client, gp_user_b, monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "patient_files_dir", str(tmp_path))
    practice_id = str(gp_user_b.practice_id)

    resp = client.post(
        "/api/v1/patients/with-file",
        json=_patient_payload(first_name="Other", last_name="Practice"),
        headers=_auth(gp_user_b),
    )

    assert resp.status_code == 201, resp.text
    assert resp.json()["practice_id"] == practice_id
