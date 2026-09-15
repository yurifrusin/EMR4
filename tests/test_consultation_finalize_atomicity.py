"""External HTTP/PostgreSQL patient-binding integration checks.
Uses the accepted synthetic conftest fixtures; no real data or providers.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
import hashlib
import json
from threading import Barrier
from types import SimpleNamespace
from unittest.mock import AsyncMock
import uuid

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.attributes import flag_modified

from app.dependencies import get_command_session_factory, get_current_user, get_db
from app.main import app
from app.models.ai_audit import AccessAiAuditLog
from app.models.billing import ClaimStatus, MbsClaim
from app.models.clinical import ClinicalDiagnosis, Encounter, EncounterStatus, Prescription
from app.models.patients import Patient
from app.models.tenancy import Practitioner, UserRole
from app.routers import consultation
from app.services.ai.audit_events import AiAuditDecision, AiAuditEventType, AiAuditSourceSurface
from tests.conftest import make_token


PATIENT_UNKNOWN = uuid.UUID("00000000-0000-4000-8000-000000009999")
COMMAND_ID = uuid.UUID("20000000-0000-4000-8000-000000000001")
DOCUMENT_CONTEXT = "https://synthetic.invalid/fictional-patient/document.docx?view=exact#context"


@pytest.fixture(autouse=True)
def bind_fictional_patient_document(db, patient):
    patient.first_name = "Fictional"
    patient.last_name = "Context Patient"
    patient.document_url = DOCUMENT_CONTEXT
    db.commit()


@pytest.fixture()
def practitioner(db, practice):
    """Synthetic active GP link; no professional credential is asserted."""
    row = Practitioner(
        practice_id=practice.id,
        first_name="Synthetic",
        last_name="Test GP",
        is_active=True,
    )
    db.add(row)
    db.flush()
    return row


def auth(user):
    return {"Authorization": f"Bearer {make_token(user)}"}


def finalize_body(patient_id, *, command_id=COMMAND_ID, document_context=DOCUMENT_CONTEXT):
    return {
        "document_id": str(command_id),
        "document_context": document_context,
        "text_delta": "Synthetic consultation text",
        "patient_id": str(patient_id),
        "clinician_attested": True,
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
    db.commit()
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
    db.commit()
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
    assert encounter.google_doc_id == str(COMMAND_ID)
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
    db.commit()
    body = finalize_body(patient_id)
    body["document_id"] = str(
        uuid.uuid5(uuid.NAMESPACE_URL, f"synthetic-atomic-failure-{override_name}")
    )
    body["clinician_overrides"][override_name] = [child_payload]
    engine = db.get_bind()
    CommandSession = sessionmaker(bind=engine)
    injected = {"raised": False}

    def command_factory():
        command_db = CommandSession()
        original_flush = command_db.flush

        def fail_selected_child_flush(objects=None):
            if not injected["raised"] and any(
                isinstance(pending, child_model) for pending in command_db.new
            ):
                injected["raised"] = True
                raise RuntimeError("synthetic child flush failure")
            return original_flush(objects)

        monkeypatch.setattr(command_db, "flush", fail_selected_child_flush)
        return command_db

    app.dependency_overrides[get_command_session_factory] = lambda: command_factory
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
    Session_ = sessionmaker(bind=engine)
    with Session_() as fresh:
        fresh.execute(
            text("SELECT set_config('app.current_practice_id', :practice_id, true)"),
            {"practice_id": str(practice_id)},
        )
        assert fresh.query(AccessAiAuditLog).count() == 0


def test_finalize_all_children_commit_once_with_linked_patient_and_practice(
    client, db, gp_user, patient, practice, monkeypatch,
):
    patient_id = patient.id
    practice_id = practice.id
    db.commit()
    body = finalize_body(patient_id)
    body["document_id"] = str(COMMAND_ID)
    body["clinician_overrides"].update(
        mbs_items=[{"item_number": "23", "description": "Synthetic claim"}],
        diagnoses=[{"term": "Synthetic diagnosis", "snomed_ct_au_code": "999"}],
        medications=[{"drug_name": "Synthetic medicine", "dosage_text": "once"}],
    )
    engine = db.get_bind()
    CommandSession = sessionmaker(bind=engine)
    commits = []

    def counted_commit(session):
        commits.append(session)

    event.listen(CommandSession.class_, "after_commit", counted_commit)
    app.dependency_overrides[get_command_session_factory] = lambda: CommandSession
    event_timestamp_before = datetime.now(timezone.utc)
    response = client.post(
        "/api/v1/finalize",
        json=body,
        headers=auth(gp_user),
    )
    event_timestamp_after = datetime.now(timezone.utc)
    event.remove(CommandSession.class_, "after_commit", counted_commit)

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
        assert fresh.execute(text("SHOW transaction_isolation")).scalar_one() == (
            "read committed"
        )
        encounter = fresh.query(Encounter).filter(Encounter.id == encounter_id).one()
        claim = fresh.query(MbsClaim).one()
        diagnosis = fresh.query(ClinicalDiagnosis).one()
        prescription = fresh.query(Prescription).one()
        audit = fresh.query(AccessAiAuditLog).one()

        assert encounter.patient_id == patient_id
        assert encounter.practice_id == practice_id
        assert encounter.practitioner_id == gp_user.practitioner_id
        assert encounter.status == EncounterStatus.Finalized
        assert encounter.is_finalized is True
        assert claim.encounter_id == encounter_id
        assert claim.patient_id == patient_id
        assert claim.practice_id == practice_id
        assert claim.practitioner_id == gp_user.practitioner_id
        assert claim.claim_status == ClaimStatus.Submitted
        assert claim.submitted_at is not None
        assert claim.submitted_at.tzinfo is not None
        assert diagnosis.encounter_id == encounter_id
        assert diagnosis.patient_id == patient_id
        assert diagnosis.practice_id == practice_id
        assert prescription.encounter_id == encounter_id
        assert prescription.patient_id == patient_id
        assert prescription.practice_id == practice_id
        assert prescription.prescribed_by == gp_user.practitioner_id

        expected_projection = {
            "consultation_type": "Synthetic review",
            "document_id": str(COMMAND_ID),
            "document_context": DOCUMENT_CONTEXT,
            "normalization_policy_id": (
                "emr4.clinical-finalization.saved-projection.v1"
            ),
            "overrides": {
                "diagnoses": [
                    {
                        "snomed_ct_au_code": "999",
                        "term": "Synthetic diagnosis",
                    }
                ],
                "mbs_items": [
                    {
                        "description": "Synthetic claim",
                        "item_number": "23",
                    }
                ],
                "medications": [
                    {
                        "dosage_text": "once",
                        "drug_name": "Synthetic medicine",
                    }
                ],
            },
            "patient_id": str(patient_id),
            "text": "Synthetic consultation text",
        }
        expected_hash = hashlib.sha256(
            json.dumps(
                expected_projection,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        expected_metadata = {
            "attested": True,
            "normalization_policy_id": (
                "emr4.clinical-finalization.saved-projection.v1"
            ),
            "patient_id": str(patient_id),
            "practitioner_id": str(gp_user.practitioner_id),
            "reviewed_content_sha256": expected_hash,
            "server_policy_id": (
                "emr4.clinical-finalization.gp-linked-practitioner.v1"
            ),
        }
        assert consultation.CLINICAL_FINALIZATION_POLICY_ID == (
            "emr4.clinical-finalization.gp-linked-practitioner.v1"
        )
        assert consultation.CLINICAL_FINALIZATION_NORMALIZATION_POLICY_ID == (
            "emr4.clinical-finalization.saved-projection.v1"
        )
        assert consultation.CLINICAL_FINALIZATION_IDEMPOTENCY_NAME == (
            "emr4.clinical-finalization.receipt.v1"
        )
        assert consultation.CLINICAL_FINALIZATION_IDEMPOTENCY_NAMESPACE == uuid.UUID(
            "7b56fb23-fdc5-5bd9-951f-80a7b9b94b2e"
        )
        assert audit.event_id == consultation._clinical_finalization_event_id(
            practice_id, COMMAND_ID
        )
        assert audit.event_timestamp.tzinfo is not None
        assert audit.event_timestamp.utcoffset() is not None
        assert event_timestamp_before <= audit.event_timestamp <= event_timestamp_after
        assert audit.event_type == AiAuditEventType.CLINICAL_CONSULTATION_ATTESTED.value
        assert audit.decision == AiAuditDecision.RECORDED.value
        assert audit.source_surface == AiAuditSourceSurface.API.value
        assert audit.actor_user_id == gp_user.id
        assert audit.actor_roles == [UserRole.GP.value]
        assert audit.practice_id == practice_id
        assert audit.target_resource_type == "encounter"
        assert audit.target_resource_id == str(encounter_id)
        assert audit.capability is None
        assert audit.method is None
        assert audit.reason_code is None
        assert audit.metadata_json == expected_metadata
        serialized_metadata = json.dumps(audit.metadata_json, sort_keys=True)
        assert "Synthetic consultation text" not in serialized_metadata
        assert "Synthetic diagnosis" not in serialized_metadata
        assert "Synthetic medicine" not in serialized_metadata


@pytest.mark.parametrize(
    "attestation",
    [pytest.param(None, id="missing"), pytest.param("true", id="string"), pytest.param(1, id="integer")],
)
def test_finalize_requires_strict_boolean_attestation_without_writes(
    client, db, gp_user, patient, attestation,
):
    body = finalize_body(patient.id)
    if attestation is None:
        del body["clinician_attested"]
    else:
        body["clinician_attested"] = attestation
    before = clinical_counts(db)
    response = client.post("/api/v1/finalize", json=body, headers=auth(gp_user))
    assert response.status_code == 422
    assert clinical_counts(db) == before


def test_finalize_false_attestation_is_generic_403_before_writes(client, db, gp_user, patient):
    body = finalize_body(patient.id)
    body["clinician_attested"] = False
    before = clinical_counts(db)
    response = client.post("/api/v1/finalize", json=body, headers=auth(gp_user))
    assert response.status_code == 403
    assert response.json() == {"detail": "Clinical finalization is not permitted."}
    assert clinical_counts(db) == before


@pytest.mark.parametrize(
    "field",
    [pytest.param("practitioner_id", id="practitioner-id"),
     pytest.param("prescribed_by", id="prescriber-id"),
     pytest.param("actor_user_id", id="actor-user-id"),
     pytest.param("role", id="role")],
)
def test_finalize_rejects_client_supplied_authority_fields(client, db, gp_user, patient, field):
    body = finalize_body(patient.id)
    body[field] = "GP" if field == "role" else str(uuid.uuid4())
    before = clinical_counts(db)
    response = client.post("/api/v1/finalize", json=body, headers=auth(gp_user))
    assert response.status_code == 422
    assert clinical_counts(db) == before


@pytest.mark.parametrize(
    "role",
    [
        pytest.param(UserRole.Receptionist, id="receptionist"),
        pytest.param(UserRole.Nurse, id="nurse"),
        pytest.param(UserRole.Admin, id="admin"),
        pytest.param(UserRole.PracticeOwner, id="practice-owner"),
    ],
)
def test_finalize_rejects_non_gp_role_without_writes(
    client, db, receptionist_user, patient, role,
):
    receptionist_user.role = role
    db.commit()
    before = clinical_counts(db)
    response = client.post(
        "/api/v1/finalize", json=finalize_body(patient.id), headers=auth(receptionist_user)
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Clinical finalization is not permitted."}
    assert clinical_counts(db) == before


@pytest.mark.parametrize(
    "authority_state",
    [pytest.param("inactive-user", id="inactive-user"),
     pytest.param("changed-role", id="changed-role"),
     pytest.param("inactive-practitioner", id="inactive-practitioner"),
     pytest.param("missing-link", id="missing-link"),
     pytest.param("cross-practice-link", id="cross-practice-link")],
)
def test_finalize_rechecks_fresh_user_and_practitioner_authority(
    client, db, gp_user, practitioner, patient, practice_b, authority_state,
):
    stale_locator = SimpleNamespace(id=gp_user.id, practice_id=gp_user.practice_id)
    if authority_state == "inactive-user":
        gp_user.is_active = False
    elif authority_state == "changed-role":
        gp_user.role = UserRole.Nurse
    elif authority_state == "inactive-practitioner":
        practitioner.is_active = False
    elif authority_state == "missing-link":
        gp_user.practitioner_id = None
    else:
        foreign = Practitioner(
            practice_id=practice_b.id, first_name="Synthetic", last_name="Foreign", is_active=True
        )
        db.add(foreign)
        db.flush()
        gp_user.practitioner_id = foreign.id
    db.commit()
    app.dependency_overrides[get_current_user] = lambda: stale_locator
    response = client.post("/api/v1/finalize", json=finalize_body(patient.id))
    assert response.status_code == 403
    assert response.json() == {"detail": "Clinical finalization is not permitted."}
    assert fresh_clinical_counts(db.get_bind(), stale_locator.practice_id) == (0, 0, 0, 0)


@pytest.mark.parametrize(
    "failure_point",
    [pytest.param("builder", id="builder"), pytest.param("store", id="store"),
     pytest.param("audit-flush", id="audit-flush")],
)
def test_finalize_audit_failure_rolls_back_all_clinical_rows(
    client, db, gp_user, patient, practice, monkeypatch, failure_point,
):
    db.commit()
    engine = db.get_bind()
    body = finalize_body(patient.id)
    body["clinician_overrides"].update(
        mbs_items=[{"item_number": "23", "description": "Synthetic claim"}],
        diagnoses=[{"term": "Synthetic diagnosis", "snomed_ct_au_code": "999"}],
        medications=[{"drug_name": "Synthetic medicine", "dosage_text": "once"}],
    )
    injected = {"raised": False}
    clinical_writer_calls = []
    original_save_encounter = consultation._save_encounter

    def track_save_encounter(*args, **kwargs):
        clinical_writer_calls.append((args, kwargs))
        return original_save_encounter(*args, **kwargs)

    monkeypatch.setattr(consultation, "_save_encounter", track_save_encounter)

    def fail_injected(*args, **kwargs):
        injected["raised"] = True
        raise RuntimeError(f"synthetic {failure_point} failure")

    if failure_point == "builder":
        monkeypatch.setattr(
            consultation, "build_access_ai_audit_event", fail_injected,
        )
    elif failure_point == "store":
        monkeypatch.setattr(
            consultation, "persist_access_ai_audit_events", fail_injected,
        )
    else:
        CommandSession = sessionmaker(bind=engine)

        def command_factory():
            command_db = CommandSession()
            original_flush = command_db.flush

            def fail_audit_flush(objects=None):
                if any(isinstance(row, AccessAiAuditLog) for row in command_db.new):
                    injected["raised"] = True
                    raise RuntimeError("synthetic audit flush failure")
                return original_flush(objects)

            monkeypatch.setattr(command_db, "flush", fail_audit_flush)
            return command_db

        app.dependency_overrides[get_command_session_factory] = lambda: command_factory

    response = client.post(
        "/api/v1/finalize", json=body, headers=auth(gp_user)
    )
    assert injected["raised"] is True
    assert clinical_writer_calls == []
    assert response.status_code == 200
    assert response.json() == {
        "_saved": False,
        "_save_error": "Encounter save failed. Please contact support.",
    }
    assert fresh_clinical_counts(engine, practice.id) == (0, 0, 0, 0)
    Session_ = sessionmaker(bind=engine)
    with Session_() as fresh:
        fresh.execute(
            text("SELECT set_config('app.current_practice_id', :practice_id, true)"),
            {"practice_id": str(practice.id)},
        )
        assert fresh.query(AccessAiAuditLog).count() == 0



def test_finalize_matching_replay_returns_exact_json_and_one_rowset(
    client, db, gp_user, patient, practice,
):
    db.commit()
    body = finalize_body(patient.id)
    body["clinician_overrides"].update(
        mbs_items=[{"item_number": "23", "description": "Synthetic claim"}],
        diagnoses=[{"term": "Synthetic diagnosis", "snomed_ct_au_code": "999"}],
        medications=[{"drug_name": "Synthetic medicine", "dosage_text": "once"}],
    )
    first = client.post("/api/v1/finalize", json=body, headers=auth(gp_user))
    replay = client.post("/api/v1/finalize", json=body, headers=auth(gp_user))
    assert first.status_code == replay.status_code == 200
    assert replay.json() == first.json()
    Session_ = sessionmaker(bind=db.get_bind())
    with Session_() as fresh:
        fresh.execute(
            text("SELECT set_config('app.current_practice_id', :practice_id, true)"),
            {"practice_id": str(practice.id)},
        )
        assert tuple(
            fresh.query(model).count()
            for model in (
                Encounter, ClinicalDiagnosis, Prescription, MbsClaim, AccessAiAuditLog,
            )
        ) == (1, 1, 1, 1, 1)


def test_finalize_compatible_aliases_replay_same_canonical_hash(
    client, db, gp_user, patient,
):
    db.commit()
    canonical = finalize_body(patient.id)
    canonical["clinician_overrides"].update(
        mbs_items=[{"item_number": "23", "description": ""}],
        diagnoses=[{"term": "Synthetic diagnosis", "snomed_ct_au_code": "999"}],
        medications=[{"drug_name": "Synthetic medicine", "dosage_text": ""}],
    )
    aliased = json.loads(json.dumps(canonical))
    overrides = aliased["clinician_overrides"]
    overrides["mbs_item_candidates"] = [{"item": "23", "description": ""}]
    del overrides["mbs_items"]
    overrides["clinical_diagnoses"] = [
        {"concept_name": "Synthetic diagnosis", "concept_id": "999"}
    ]
    del overrides["diagnoses"]
    overrides["medications_and_prescriptions"] = [
        {"drug": "Synthetic medicine", "dosage": ""}
    ]
    del overrides["medications"]
    first = client.post("/api/v1/finalize", json=canonical, headers=auth(gp_user))
    replay = client.post("/api/v1/finalize", json=aliased, headers=auth(gp_user))
    assert first.status_code == replay.status_code == 200
    assert replay.json() == first.json()
    audit = db.query(AccessAiAuditLog).one()
    projection = consultation._effective_finalization_projection(
        consultation.FinalizePayload(**canonical), patient_id=patient.id,
    )
    assert audit.metadata_json["reviewed_content_sha256"] == (
        consultation._reviewed_content_sha256(projection)
    )


def test_finalize_changed_content_patient_and_context_are_same_generic_conflict(
    client, db, gp_user, patient, practice,
):
    second_patient = Patient(
        practice_id=practice.id,
        first_name="Fictional",
        last_name="Second Context Patient",
        date_of_birth=date(2000, 1, 1),
        document_url=DOCUMENT_CONTEXT,
    )
    db.add(second_patient)
    db.commit()
    first = client.post(
        "/api/v1/finalize", json=finalize_body(patient.id), headers=auth(gp_user),
    )
    assert first.status_code == 200
    changed_content = finalize_body(patient.id)
    changed_content["text_delta"] = "Different synthetic consultation text"
    changed_patient = finalize_body(second_patient.id)
    changed_context = finalize_body(
        patient.id,
        document_context="https://synthetic.invalid/different-context.docx",
    )
    responses = [
        client.post("/api/v1/finalize", json=body, headers=auth(gp_user))
        for body in (changed_content, changed_patient, changed_context)
    ]
    assert [response.status_code for response in responses] == [409, 409, 409]
    assert all(
        response.json() == {
            "_saved": False, "_save_error": "Finalization command conflict.",
        }
        for response in responses
    )
    assert db.query(Encounter).count() == 1
    assert db.query(AccessAiAuditLog).count() == 1


def test_finalize_different_gp_replay_is_generic_conflict(
    client, db, gp_user, receptionist_user, patient, practice,
):
    second_practitioner = Practitioner(
        practice_id=practice.id,
        first_name="Synthetic",
        last_name="Second Test GP",
        is_active=True,
    )
    db.add(second_practitioner)
    db.flush()
    receptionist_user.role = UserRole.GP
    receptionist_user.practitioner_id = second_practitioner.id
    receptionist_user.is_active = True
    db.commit()
    first = client.post(
        "/api/v1/finalize", json=finalize_body(patient.id), headers=auth(gp_user),
    )
    replay = client.post(
        "/api/v1/finalize",
        json=finalize_body(patient.id),
        headers=auth(receptionist_user),
    )
    assert first.status_code == 200
    assert replay.status_code == 409
    assert replay.json() == {
        "_saved": False, "_save_error": "Finalization command conflict.",
    }
    assert db.query(Encounter).count() == 1
    assert db.query(AccessAiAuditLog).count() == 1


@pytest.mark.parametrize(
    "corruption",
    [
        pytest.param("attested-int", id="attested-integer"),
        pytest.param("policy-version", id="policy-version"),
        pytest.param("hash", id="malformed-hash"),
        pytest.param("target", id="missing-target"),
    ],
)
def test_finalize_corrupt_receipt_fails_closed_without_field_or_target_leak(
    client, db, gp_user, patient, corruption,
):
    body = finalize_body(patient.id)
    headers = auth(gp_user)
    db.commit()
    first = client.post(
        "/api/v1/finalize", json=body, headers=headers,
    )
    assert first.status_code == 200
    target_id = first.json()["encounter_id"]
    audit = db.query(AccessAiAuditLog).one()
    metadata = dict(audit.metadata_json)
    if corruption == "attested-int":
        metadata["attested"] = 1
        audit.metadata_json = metadata
        # True and 1 compare equal in Python; force this JSONB corruption to persist.
        flag_modified(audit, "metadata_json")
    elif corruption == "policy-version":
        metadata["server_policy_id"] = "emr4.clinical-finalization.invalid.v0"
        audit.metadata_json = metadata
    elif corruption == "hash":
        metadata["reviewed_content_sha256"] = "not-a-64-character-lowercase-hash"
        audit.metadata_json = metadata
    else:
        audit.target_resource_id = str(uuid.uuid4())
    db.commit()
    if corruption == "attested-int":
        db.refresh(audit)
        assert type(audit.metadata_json["attested"]) is int
        assert audit.metadata_json["attested"] == 1
        db.rollback()
    replay = client.post(
        "/api/v1/finalize", json=body, headers=headers,
    )
    assert replay.status_code == 409
    assert replay.json() == {
        "_saved": False, "_save_error": "Finalization command conflict.",
    }
    assert target_id not in replay.text
    assert corruption not in replay.text
    assert db.query(Encounter).count() == 1
    assert db.query(AccessAiAuditLog).count() == 1


def _independent_session_clients(engine):
    RequestSession = sessionmaker(bind=engine, expire_on_commit=False)
    CommandSession = sessionmaker(bind=engine, expire_on_commit=False)

    def request_db():
        request_session = RequestSession()
        try:
            yield request_session
        finally:
            request_session.close()

    previous = dict(app.dependency_overrides)
    app.dependency_overrides[get_db] = request_db
    app.dependency_overrides[get_command_session_factory] = lambda: CommandSession
    return [TestClient(app), TestClient(app)], previous


def _close_independent_session_clients(clients, previous):
    for independent_client in clients:
        independent_client.close()
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous)


def test_finalize_same_gp_overlapping_matching_commands_are_identical(
    db, gp_user, patient, practice, monkeypatch,
):
    db.commit()
    engine = db.get_bind()
    clients, previous = _independent_session_clients(engine)
    headers = auth(gp_user)
    body = finalize_body(patient.id)
    start_barrier = Barrier(2, timeout=10)
    original_derivation = consultation._clinical_finalization_event_id

    def synchronized_derivation(*args):
        start_barrier.wait()
        return original_derivation(*args)

    monkeypatch.setattr(
        consultation, "_clinical_finalization_event_id", synchronized_derivation,
    )
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [
                pool.submit(
                    clients[index].post,
                    "/api/v1/finalize",
                    json=body,
                    headers=headers,
                )
                for index in range(2)
            ]
            responses = [future.result(timeout=20) for future in futures]
    finally:
        _close_independent_session_clients(clients, previous)
    assert [response.status_code for response in responses] == [200, 200]
    assert responses[0].json() == responses[1].json()
    assert fresh_clinical_counts(engine, practice.id) == (1, 0, 0, 0)
    Session_ = sessionmaker(bind=engine)
    with Session_() as fresh:
        fresh.execute(
            text("SELECT set_config('app.current_practice_id', :practice_id, true)"),
            {"practice_id": str(practice.id)},
        )
        assert fresh.query(AccessAiAuditLog).count() == 1


def test_finalize_different_gps_distinct_patients_same_command_race_is_bounded(
    db, gp_user, receptionist_user, patient, practice,
):
    second_practitioner = Practitioner(
        practice_id=practice.id,
        first_name="Synthetic",
        last_name="Racing Test GP",
        is_active=True,
    )
    second_context = "https://synthetic.invalid/second-fictional/document.docx"
    second_patient = Patient(
        practice_id=practice.id,
        first_name="Fictional",
        last_name="Racing Patient",
        date_of_birth=date(2001, 2, 3),
        document_url=second_context,
    )
    db.add_all([second_practitioner, second_patient])
    db.flush()
    receptionist_user.role = UserRole.GP
    receptionist_user.practitioner_id = second_practitioner.id
    receptionist_user.is_active = True
    db.commit()
    engine = db.get_bind()
    clients, previous = _independent_session_clients(engine)
    headers = [auth(gp_user), auth(receptionist_user)]
    bodies = [
        finalize_body(patient.id),
        finalize_body(second_patient.id, document_context=second_context),
    ]
    receipt_barrier = Barrier(2, timeout=10)
    receipt_selects = {"count": 0}

    def synchronize_receipt_lookup(
        conn, cursor, statement, parameters, context, executemany,
    ):
        if (
            receipt_selects["count"] < 2
            and "FROM access_ai_audit_log" in statement
            and "FOR UPDATE" in statement
        ):
            receipt_selects["count"] += 1
            receipt_barrier.wait()

    event.listen(engine, "before_cursor_execute", synchronize_receipt_lookup)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [
                pool.submit(
                    clients[index].post,
                    "/api/v1/finalize",
                    json=bodies[index],
                    headers=headers[index],
                )
                for index in range(2)
            ]
            responses = [future.result(timeout=20) for future in futures]
    finally:
        event.remove(engine, "before_cursor_execute", synchronize_receipt_lookup)
        _close_independent_session_clients(clients, previous)
    assert sorted(response.status_code for response in responses) == [200, 409]
    loser = next(response for response in responses if response.status_code == 409)
    assert loser.json() == {
        "_saved": False, "_save_error": "Finalization command conflict.",
    }
    Session_ = sessionmaker(bind=engine)
    with Session_() as fresh:
        fresh.execute(
            text("SELECT set_config('app.current_practice_id', :practice_id, true)"),
            {"practice_id": str(practice.id)},
        )
        audit = fresh.query(AccessAiAuditLog).one()
        encounter = fresh.query(Encounter).one()
        assert audit.target_resource_id == str(encounter.id)
        assert encounter.patient_id in {patient.id, second_patient.id}
        assert fresh.query(ClinicalDiagnosis).count() == 0
        assert fresh.query(Prescription).count() == 0
        assert fresh.query(MbsClaim).count() == 0


@pytest.mark.parametrize(
    "mutation",
    [
        pytest.param("missing-command", id="missing-command-uuid"),
        pytest.param("malformed-command", id="malformed-command-uuid"),
        pytest.param("missing-context", id="missing-document-context"),
        pytest.param("nonstring-context", id="nonstring-document-context"),
    ],
)
def test_finalize_rejects_invalid_command_or_context_without_writes(
    client, db, gp_user, patient, mutation,
):
    body = finalize_body(patient.id)
    if mutation == "missing-command":
        del body["document_id"]
    elif mutation == "malformed-command":
        body["document_id"] = "not-a-uuid"
    elif mutation == "missing-context":
        del body["document_context"]
    else:
        body["document_context"] = True
    before = clinical_counts(db)
    response = client.post("/api/v1/finalize", json=body, headers=auth(gp_user))
    assert response.status_code == 422
    assert clinical_counts(db) == before
    assert db.query(AccessAiAuditLog).count() == 0


@pytest.mark.parametrize(
    "stored_context",
    [
        pytest.param(None, id="unbound-patient-document"),
        pytest.param(
            "https://synthetic.invalid/other.docx?view=exact#context",
            id="mismatched-patient-document",
        ),
    ],
)
def test_finalize_rejects_unbound_or_mismatched_document_context_generically(
    client, db, gp_user, patient, stored_context,
):
    patient.document_url = stored_context
    db.commit()
    before = clinical_counts(db)
    response = client.post(
        "/api/v1/finalize",
        json=finalize_body(patient.id),
        headers=auth(gp_user),
    )
    assert response.status_code == 409
    assert response.json() == {
        "_saved": False, "_save_error": "Finalization command conflict.",
    }
    assert DOCUMENT_CONTEXT not in response.text
    assert clinical_counts(db) == before
    assert db.query(AccessAiAuditLog).count() == 0
