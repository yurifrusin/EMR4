"""External HTTP/PostgreSQL patient-binding integration checks.
Uses the accepted synthetic conftest fixtures; no real data or providers.
"""
from types import SimpleNamespace
from unittest.mock import AsyncMock
import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.models.billing import ClaimStatus, MbsClaim
from app.models.clinical import ClinicalDiagnosis, Encounter, EncounterStatus, Prescription
from app.models.patients import Patient
from app.routers import consultation
from tests.conftest import make_token


PATIENT_UNKNOWN = uuid.UUID("00000000-0000-4000-8000-000000009999")


def auth(user):
    return {"Authorization": f"Bearer {make_token(user)}"}


def finalize_body(patient_id):
    return {
        "document_id": "synthetic-doc",
        "text_delta": "Synthetic consultation text",
        "patient_id": str(patient_id),
        "clinician_overrides": {
            "consultation_type": "Synthetic review",
            "mbs_items": [],
            "diagnoses": [],
            "medications": [],
        },
    }


def clinical_counts(db):
    return tuple(
        db.query(model).count()
        for model in (Patient, Encounter, ClinicalDiagnosis, Prescription, MbsClaim)
    )


@pytest.mark.parametrize(
    "patient_id",
    [pytest.param(None, id="missing-patient-id"),
     pytest.param("malformed", id="malformed-patient-id")],
)
def test_finalize_rejects_missing_or_malformed_patient_id_without_writes(
    client, db, gp_user, patient_id
):
    body = finalize_body(PATIENT_UNKNOWN)
    if patient_id is None:
        del body["patient_id"]
    else:
        body["patient_id"] = patient_id
    before = clinical_counts(db)
    response = client.post(
        "/api/v1/finalize", json=body, headers=auth(gp_user)
    )
    assert response.status_code == 422
    assert clinical_counts(db) == before


@pytest.mark.parametrize(
    "patient_id",
    [pytest.param(PATIENT_UNKNOWN, id="unknown"), pytest.param("foreign", id="foreign")],
)
def test_finalize_unknown_and_foreign_patient_are_generic_404_without_writes(
    client, db, gp_user, patient_b, patient_id
):
    selected = patient_b.id if patient_id == "foreign" else patient_id
    before = clinical_counts(db)
    response = client.post(
        "/api/v1/finalize",
        json=finalize_body(selected),
        headers=auth(gp_user),
    )
    assert response.status_code == 404
    assert response.json() == {"_saved": False, "_save_error": "Patient not found."}
    assert clinical_counts(db) == before


def test_finalize_same_practice_persists_selected_patient_and_practice(
    client, db, gp_user, patient, practice
):
    response = client.post(
        "/api/v1/finalize",
        json=finalize_body(patient.id),
        headers=auth(gp_user),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["_saved"] is True
    encounter = db.query(Encounter).one()
    assert encounter.id == uuid.UUID(payload["encounter_id"])
    assert encounter.patient_id == patient.id
    assert encounter.practice_id == practice.id
    assert encounter.google_doc_id == "synthetic-doc"
    assert encounter.is_finalized is True


def test_finalize_requires_authentication(client, db, patient):
    before = clinical_counts(db)
    response = client.post("/api/v1/finalize", json=finalize_body(patient.id))
    assert response.status_code == 401
    assert clinical_counts(db) == before


def test_analyze_rejects_finalized_payload_with_422(client, db, gp_user):
    before = clinical_counts(db)
    response = client.post(
        "/api/v1/analyze-consultation",
        json={
            "document_id": "synthetic-doc",
            "text_delta": "Synthetic consultation text",
            "is_finalized": True,
        },
        headers=auth(gp_user),
    )
    assert response.status_code == 422
    assert clinical_counts(db) == before


def test_draft_analyze_strips_save_markers_and_does_not_persist_clinical_records(
    client, db, gp_user, monkeypatch
):
    ai_result = SimpleNamespace(
        raw={
            "_saved": True,
            "_save_error": "synthetic marker",
            "encounter_metadata": {
                "consultation_type": "Synthetic draft",
                "mbs_item_candidates": [],
            },
            "clinical_diagnoses": [
                {"term": "Synthetic diagnosis", "snomed_ct_au_code": "999"}
            ],
            "medications_and_prescriptions": [
                {"drug_name": "Synthetic medicine", "dosage_text": "once"}
            ],
        },
        audit_events=[],
    )
    monkeypatch.setattr(
        consultation,
        "_search_mbs_rules",
        lambda text, session: "synthetic MBS context",
    )
    ai_stub = AsyncMock(return_value=ai_result)
    monkeypatch.setattr(
        consultation._ai_service,
        "analyze_consultation_text",
        ai_stub,
    )
    before = clinical_counts(db)
    response = client.post(
        "/api/v1/analyze-consultation",
        json={
            "document_id": "synthetic-doc",
            "text_delta": "Synthetic consultation text",
            "is_finalized": False,
        },
        headers=auth(gp_user),
    )
    assert response.status_code == 200
    payload = response.json()
    assert "_saved" not in payload
    assert "_save_error" not in payload
    assert payload["encounter_metadata"]["consultation_type"] == "Synthetic draft"
    ai_stub.assert_awaited_once()
    assert clinical_counts(db) == before

CHILD_FAILURE_CASES = (
    pytest.param(
        MbsClaim,
        "mbs_items",
        {"item_number": "23", "description": "Synthetic claim"},
        id="mbs-claim",
    ),
    pytest.param(
        ClinicalDiagnosis,
        "diagnoses",
        {"term": "Synthetic diagnosis", "snomed_ct_au_code": "999"},
        id="clinical-diagnosis",
    ),
    pytest.param(
        Prescription,
        "medications",
        {"drug_name": "Synthetic medicine", "dosage_text": "once"},
        id="prescription",
    ),
)


def fresh_clinical_counts(engine, practice_id):
    Session_ = sessionmaker(bind=engine)
    with Session_() as fresh:
        fresh.execute(
            text("SELECT set_config('app.current_practice_id', :practice_id, true)"),
            {"practice_id": str(practice_id)},
        )
        return tuple(
            fresh.query(model).count()
            for model in (Encounter, ClinicalDiagnosis, Prescription, MbsClaim)
        )


@pytest.mark.parametrize(
    "child_model, override_name, child_payload",
    CHILD_FAILURE_CASES,
)
def test_finalize_child_flush_failure_rolls_back_encounter_and_children(
    client, db, gp_user, patient, practice, monkeypatch,
    child_model, override_name, child_payload,
):
    patient_id = patient.id
    practice_id = practice.id
    body = finalize_body(patient_id)
    body["document_id"] = f"synthetic-atomic-failure-{override_name}"
    body["clinician_overrides"][override_name] = [child_payload]
    engine = db.get_bind()
    original_flush = db.flush
    injected = {"raised": False}

    def fail_selected_child_flush(objects=None):
        if not injected["raised"] and any(
            isinstance(pending, child_model) for pending in db.new
        ):
            injected["raised"] = True
            raise RuntimeError("synthetic child flush failure")
        return original_flush(objects)

    monkeypatch.setattr(db, "flush", fail_selected_child_flush)
    response = client.post(
        "/api/v1/finalize",
        json=body,
        headers=auth(gp_user),
    )

    assert injected["raised"] is True
    assert response.status_code == 200
    assert response.json() == {
        "_saved": False,
        "_save_error": "Encounter save failed. Please contact support.",
    }
    assert fresh_clinical_counts(engine, practice_id) == (0, 0, 0, 0)


def test_finalize_all_children_commit_once_with_linked_patient_and_practice(
    client, db, gp_user, patient, practice, monkeypatch,
):
    patient_id = patient.id
    practice_id = practice.id
    body = finalize_body(patient_id)
    body["document_id"] = "synthetic-atomic-success"
    body["clinician_overrides"].update(
        mbs_items=[{"item_number": "23", "description": "Synthetic claim"}],
        diagnoses=[{"term": "Synthetic diagnosis", "snomed_ct_au_code": "999"}],
        medications=[{"drug_name": "Synthetic medicine", "dosage_text": "once"}],
    )
    engine = db.get_bind()
    original_commit = db.commit
    commits = []

    def counted_commit():
        result = original_commit()
        commits.append(None)
        return result

    monkeypatch.setattr(db, "commit", counted_commit)
    response = client.post(
        "/api/v1/finalize",
        json=body,
        headers=auth(gp_user),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["_saved"] is True
    encounter_id = uuid.UUID(payload["encounter_id"])
    assert len(commits) == 1

    Session_ = sessionmaker(bind=engine)
    with Session_() as fresh:
        fresh.execute(
            text("SELECT set_config('app.current_practice_id', :practice_id, true)"),
            {"practice_id": str(practice_id)},
        )
        encounter = fresh.query(Encounter).filter(Encounter.id == encounter_id).one()
        claim = fresh.query(MbsClaim).one()
        diagnosis = fresh.query(ClinicalDiagnosis).one()
        prescription = fresh.query(Prescription).one()

        assert encounter.patient_id == patient_id
        assert encounter.practice_id == practice_id
        assert encounter.status == EncounterStatus.Finalized
        assert encounter.is_finalized is True
        assert claim.encounter_id == encounter_id
        assert claim.patient_id == patient_id
        assert claim.practice_id == practice_id
        assert claim.claim_status == ClaimStatus.Submitted
        assert diagnosis.encounter_id == encounter_id
        assert diagnosis.patient_id == patient_id
        assert diagnosis.practice_id == practice_id
        assert prescription.encounter_id == encounter_id
        assert prescription.patient_id == patient_id
        assert prescription.practice_id == practice_id

