from app.models.ai_audit import AccessAiAuditLog
from app.routers import letters as letters_router
from app.services.ai.audit_events import (
    AiAuditDecision,
    AiAuditEventType,
    AiAuditSourceSurface,
    build_access_ai_audit_event,
)
from app.services.ai.contracts import AiCapability, AiMethod, AiResult, LetterDraftingData
from tests.conftest import make_token


class FakeLetterService:
    def __init__(self, event):
        self.event = event
        self.actor_context = None

    async def draft_letter(self, prompt: str, actor_context=None):
        self.actor_context = actor_context
        raw = {
            "subject_line": "Re: Test referral",
            "letter_text": "Dear Colleague,\n\nFixture letter.",
        }
        return AiResult(
            raw=raw,
            data=LetterDraftingData.model_validate(raw),
            audit_events=(self.event,),
        )


def test_draft_letter_persists_access_ai_audit_event(
    client,
    db,
    gp_user,
    patient,
    monkeypatch,
):
    event = build_access_ai_audit_event(
        event_type=AiAuditEventType.INVOCATION_ALLOWED,
        source_surface=AiAuditSourceSurface.TASKPANE,
        decision=AiAuditDecision.ALLOWED,
        actor_user_id=gp_user.id,
        actor_roles=("ai.clinical_user",),
        practice_id=gp_user.practice_id,
        capability=AiCapability.LETTER_DRAFTING,
        method=AiMethod.INVOKE,
        metadata={"clinical_surface": "draft_letter"},
    )
    fake_service = FakeLetterService(event)
    monkeypatch.setattr(letters_router, "_ai_service", fake_service)

    response = client.post(
        f"/api/v1/patients/{patient.id}/letters/draft",
        json={
            "letter_type": "Referral",
            "reason": "Fixture referral reason",
            "recipient_name": "Dr Fixture",
        },
        headers={"Authorization": f"Bearer {make_token(gp_user)}"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["subject_line"] == "Re: Test referral"
    assert fake_service.actor_context.user_id == gp_user.id
    saved = db.query(AccessAiAuditLog).one()
    assert saved.event_type == "ai.invocation.allowed"
    assert saved.capability == "clinical.letter.draft"
    assert saved.method == "invoke"
    assert saved.metadata_json["clinical_surface"] == "draft_letter"
