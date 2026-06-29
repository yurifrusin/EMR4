from app.models.ai_audit import AccessAiAuditLog
from app.models.clinical import Encounter
from app.routers import consultation as consultation_router
from app.services.ai.audit_events import (
    AiAuditDecision,
    AiAuditEventType,
    AiAuditSourceSurface,
    build_access_ai_audit_event,
)
from app.services.ai.contracts import AiCapability, AiMethod, AiResult, ClinicalExtractionData
from tests.conftest import make_token


class FakeAnalyzeService:
    def __init__(self, event):
        self.event = event
        self.actor_context = None

    async def analyze_consultation_text(self, prompt: str, actor_context=None):
        self.actor_context = actor_context
        raw = {
            "encounter_metadata": {"consultation_type": "Standard Consultation"},
            "clinical_diagnoses": [],
            "medications_and_prescriptions": [],
        }
        return AiResult(
            raw=raw,
            data=ClinicalExtractionData.model_validate(raw),
            audit_events=(self.event,),
        )


def test_analyze_consultation_persists_access_ai_audit_event(
    client,
    db,
    gp_user,
    monkeypatch,
):
    monkeypatch.setattr(consultation_router, "_search_mbs_rules", lambda query, db: "")
    event = build_access_ai_audit_event(
        event_type=AiAuditEventType.INVOCATION_ALLOWED,
        source_surface=AiAuditSourceSurface.TASKPANE,
        decision=AiAuditDecision.ALLOWED,
        actor_user_id=gp_user.id,
        actor_roles=("ai.clinical_user",),
        practice_id=gp_user.practice_id,
        capability=AiCapability.CLINICAL_EXTRACTION,
        method=AiMethod.INVOKE,
        metadata={"clinical_surface": "analyze_consultation"},
    )
    fake_service = FakeAnalyzeService(event)
    monkeypatch.setattr(consultation_router, "_ai_service", fake_service)

    response = client.post(
        "/api/v1/analyze-consultation",
        json={
            "document_id": "doc-1",
            "text_delta": "Patient presents with hypertension review.",
            "is_finalized": False,
        },
        headers={"Authorization": f"Bearer {make_token(gp_user)}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["encounter_metadata"]["consultation_type"] == "Standard Consultation"
    assert fake_service.actor_context.user_id == gp_user.id
    assert fake_service.actor_context.practice_id == gp_user.practice_id
    assert db.query(Encounter).count() == 0

    saved = db.query(AccessAiAuditLog).one()
    assert saved.event_id == event.event_id
    assert saved.event_type == "ai.invocation.allowed"
    assert saved.capability == "clinical.note.extract"
    assert saved.method == "invoke"
    assert saved.metadata_json["clinical_surface"] == "analyze_consultation"
