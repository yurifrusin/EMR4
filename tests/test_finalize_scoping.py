"""
POST /api/v1/finalize must be scoped to the authenticated user's practice.
A patient from Practice B is invisible to a GP from Practice A — the
finalize call should report _saved=False rather than writing an encounter
under the wrong practice.
"""

from tests.conftest import make_token


FINALIZE_BODY = {
    "document_id": "test-doc-001",
    "text_delta": "Patient presents with sore throat.",
    "clinician_overrides": {
        "consultation_type": "Standard Consultation",
        "mbs_items": [{"item_number": "23", "description": "Level B"}],
        "diagnoses": [{"term": "Pharyngitis", "snomed_ct_au_code": "405737000"}],
        "medications": [],
    },
}


def test_finalize_own_patient_succeeds(client, gp_user, patient):
    """GP can finalise a consultation for a patient in their own practice."""
    token = make_token(gp_user)
    body = {**FINALIZE_BODY, "patient_id": str(patient.id)}
    resp = client.post(
        "/api/v1/finalize",
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["_saved"] is True
    assert "encounter_id" in data


def test_finalize_cross_practice_patient_rejected(client, gp_user, patient_b):
    """GP cannot finalise for a patient belonging to a different practice."""
    token = make_token(gp_user)
    body = {**FINALIZE_BODY, "patient_id": str(patient_b.id)}
    resp = client.post(
        "/api/v1/finalize",
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["_saved"] is False
    assert "not found" in data.get("_save_error", "").lower()


def test_finalize_without_patient_id_uses_default(client, gp_user):
    """Omitting patient_id falls back to the John Citizen default patient."""
    token = make_token(gp_user)
    resp = client.post(
        "/api/v1/finalize",
        json=FINALIZE_BODY,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["_saved"] is True
