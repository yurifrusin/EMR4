import uuid

from app.models.ai_audit import AccessAiAuditLog
from app.services.ai.audit_events import (
    AiAuditDecision,
    AiAuditEventType,
    AiAuditSourceSurface,
    build_access_ai_audit_event,
)
from app.services.ai.audit_store import persist_access_ai_audit_events
from app.services.ai.contracts import AiCapability, AiMethod


def test_persist_access_ai_audit_event_stores_bounded_metadata(db, practice, gp_user):
    correlation_id = uuid.uuid4()
    event = build_access_ai_audit_event(
        event_type=AiAuditEventType.INVOCATION_ALLOWED,
        source_surface=AiAuditSourceSurface.DIARY,
        decision=AiAuditDecision.ALLOWED,
        actor_user_id=gp_user.id,
        actor_roles=("ai.reception_user",),
        practice_id=practice.id,
        capability=AiCapability.BERNIE_BOOKING_INTERPRET,
        method=AiMethod.INVOKE,
        target_resource_type="booking_instruction",
        target_resource_id="fixture-instruction",
        correlation_id=correlation_id,
        metadata={
            "default_provider": "gemini_vertex",
            "request_units": 42,
            "response_units": 9,
            "estimated_cost_usd": 0.000014,
            "latency_ms": 31,
        },
    )

    rows = persist_access_ai_audit_events(db, (event,))

    assert len(rows) == 1
    saved = db.query(AccessAiAuditLog).filter_by(event_id=event.event_id).one()
    assert saved.practice_id == practice.id
    assert saved.actor_user_id == gp_user.id
    assert saved.event_type == "ai.invocation.allowed"
    assert saved.capability == "admin.booking.interpret"
    assert saved.method == "invoke"
    assert saved.decision == "allowed"
    assert saved.source_surface == "diary"
    assert saved.target_resource_type == "booking_instruction"
    assert saved.target_resource_id == "fixture-instruction"
    assert saved.correlation_id == correlation_id
    assert saved.actor_roles == ["ai.reception_user"]
    assert saved.metadata_json["default_provider"] == "gemini_vertex"
    assert "prompt" not in saved.metadata_json
    assert "transcript" not in saved.metadata_json


def test_persist_multiple_events_keeps_shared_correlation_id(db, practice, gp_user):
    correlation_id = uuid.uuid4()
    allowed = build_access_ai_audit_event(
        event_type=AiAuditEventType.INVOCATION_ALLOWED,
        source_surface=AiAuditSourceSurface.API,
        decision=AiAuditDecision.ALLOWED,
        actor_user_id=gp_user.id,
        practice_id=practice.id,
        capability=AiCapability.PROVIDER_LIVE_SMOKE,
        method=AiMethod.LIVE_SMOKE,
        correlation_id=correlation_id,
    )
    failed = build_access_ai_audit_event(
        event_type=AiAuditEventType.INVOCATION_FAILED,
        source_surface=AiAuditSourceSurface.API,
        decision=AiAuditDecision.FAILED,
        reason_code="RuntimeError",
        actor_user_id=gp_user.id,
        practice_id=practice.id,
        capability=AiCapability.PROVIDER_LIVE_SMOKE,
        method=AiMethod.LIVE_SMOKE,
        correlation_id=correlation_id,
    )

    persist_access_ai_audit_events(db, (allowed, failed))

    rows = (
        db.query(AccessAiAuditLog)
        .filter(AccessAiAuditLog.correlation_id == correlation_id)
        .order_by(AccessAiAuditLog.event_timestamp)
        .all()
    )
    assert [row.event_type for row in rows] == [
        "ai.invocation.allowed",
        "ai.invocation.failed",
    ]
    assert rows[1].reason_code == "RuntimeError"
