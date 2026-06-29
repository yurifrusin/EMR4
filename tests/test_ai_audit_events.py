from datetime import datetime
import uuid

import pytest
from pydantic import ValidationError

from app.services.ai.audit_events import (
    AccessAiAuditEvent,
    AiAuditDecision,
    AiAuditEventType,
    AiAuditSourceSurface,
    build_access_ai_audit_event,
)
from app.services.ai.contracts import AiCapability, AiMethod


def test_allowed_invocation_event_has_required_shape_and_correlation_id():
    correlation_id = uuid.uuid4()

    event = build_access_ai_audit_event(
        event_type=AiAuditEventType.INVOCATION_ALLOWED,
        source_surface=AiAuditSourceSurface.DIARY,
        decision=AiAuditDecision.ALLOWED,
        actor_user_id=uuid.uuid4(),
        actor_roles=("ai.reception_user",),
        practice_id=uuid.uuid4(),
        capability=AiCapability.BERNIE_BOOKING_INTERPRET,
        method=AiMethod.INVOKE,
        correlation_id=correlation_id,
        metadata={"provider": "fake", "estimated_cost_usd": 0.0},
    )

    assert event.event_type == AiAuditEventType.INVOCATION_ALLOWED
    assert event.decision == AiAuditDecision.ALLOWED
    assert event.capability == AiCapability.BERNIE_BOOKING_INTERPRET
    assert event.method == AiMethod.INVOKE
    assert event.correlation_id == correlation_id
    assert event.timestamp.tzinfo is not None
    assert event.metadata == {"provider": "fake", "estimated_cost_usd": 0.0}


def test_blocked_event_requires_reason_code():
    with pytest.raises(ValidationError, match="reason_code"):
        build_access_ai_audit_event(
            event_type=AiAuditEventType.INVOCATION_BLOCKED,
            source_surface=AiAuditSourceSurface.API,
            decision=AiAuditDecision.BLOCKED,
            capability=AiCapability.CLINICAL_EXTRACTION,
            method=AiMethod.INVOKE,
        )


def test_ai_events_require_capability_and_method():
    with pytest.raises(ValidationError, match="capability and method"):
        build_access_ai_audit_event(
            event_type=AiAuditEventType.INVOCATION_ALLOWED,
            source_surface=AiAuditSourceSurface.API,
            decision=AiAuditDecision.ALLOWED,
        )


@pytest.mark.parametrize(
    "key",
    [
        "raw_prompt",
        "transcript",
        "patient_name",
        "medicare_card",
        "date_of_birth",
        "phone_number",
    ],
)
def test_metadata_rejects_raw_prompt_and_patient_identifier_keys(key):
    with pytest.raises(ValidationError, match="audit-safe"):
        build_access_ai_audit_event(
            event_type=AiAuditEventType.INVOCATION_ALLOWED,
            source_surface=AiAuditSourceSurface.TASKPANE,
            decision=AiAuditDecision.ALLOWED,
            capability=AiCapability.AUDIO_SCRIBE,
            method=AiMethod.INVOKE,
            metadata={key: "do not store this"},
        )


def test_non_ai_events_can_record_without_capability():
    event = build_access_ai_audit_event(
        event_type=AiAuditEventType.IDENTITY_PATIENT_VERIFIED_BY_STAFF,
        source_surface=AiAuditSourceSurface.DIARY,
        decision=AiAuditDecision.RECORDED,
        actor_roles=("ai.reception_user",),
        target_resource_type="patient_candidate",
        target_resource_id="candidate-1",
        metadata={"candidate_count": 2, "verified_by_staff": True},
    )

    assert event.capability is None
    assert event.method is None
    assert event.metadata["candidate_count"] == 2


def test_naive_timestamps_are_rejected():
    with pytest.raises(ValidationError, match="timezone-aware"):
        AccessAiAuditEvent(
            event_type=AiAuditEventType.INVOCATION_ALLOWED,
            timestamp=datetime(2026, 6, 29, 9, 0, 0),
            source_surface=AiAuditSourceSurface.API,
            decision=AiAuditDecision.ALLOWED,
            capability=AiCapability.PROVIDER_LIVE_SMOKE,
            method=AiMethod.LIVE_SMOKE,
        )
