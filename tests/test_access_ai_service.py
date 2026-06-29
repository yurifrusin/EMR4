import uuid

import pytest
from pydantic import ValidationError

from app.services.ai.access_service import AccessAiRequest, AccessAiService
from app.services.ai.audit_events import (
    AiAuditEventType,
    AiAuditSourceSurface,
)
from app.services.ai.contracts import AiCapability, AiMethod
from app.services.ai.entitlements import AiAccessRole, AiActorContext


class FakeProvider:
    def __init__(self, response: dict | None = None, exc: Exception | None = None):
        self.response = response or {"ok": True}
        self.exc = exc
        self.calls = 0
        self.last_contents = None
        self.last_temperature = None

    def generate_json(self, contents, temperature: float) -> dict:
        self.calls += 1
        self.last_contents = contents
        self.last_temperature = temperature
        if self.exc:
            raise self.exc
        return self.response


def actor(*roles: str, environment: str = "dev") -> AiActorContext:
    return AiActorContext(
        user_id=uuid.uuid4(),
        practice_id=uuid.uuid4(),
        roles=roles,
        environment=environment,
    )


def request_for(
    context: AiActorContext,
    capability: AiCapability,
    method: AiMethod = AiMethod.INVOKE,
    **kwargs,
) -> AccessAiRequest:
    return AccessAiRequest(
        actor=context,
        capability=capability,
        method=method,
        contents={"input": "non-phi fixture"},
        source_surface=AiAuditSourceSurface.API,
        **kwargs,
    )


@pytest.mark.asyncio
async def test_invocation_denies_before_provider_call_when_role_not_allowed():
    provider = FakeProvider()
    service = AccessAiService(provider)

    result = await service.invoke(
        request_for(
            actor(AiAccessRole.RECEPTION_USER),
            AiCapability.CLINICAL_EXTRACTION,
        )
    )

    assert result.allowed is False
    assert result.raw is None
    assert result.denial_reason == "role_not_allowed"
    assert result.cost_envelope.request_units > 0
    assert result.latency_ms is None
    assert provider.calls == 0
    assert result.audit_events[0].event_type == AiAuditEventType.INVOCATION_BLOCKED
    assert result.audit_events[0].reason_code == "role_not_allowed"


@pytest.mark.asyncio
async def test_successful_invocation_calls_provider_and_records_allowed_event():
    provider = FakeProvider({"interpreted": True})
    service = AccessAiService(provider)
    correlation_id = uuid.uuid4()

    result = await service.invoke(
        request_for(
            actor(AiAccessRole.RECEPTION_USER),
            AiCapability.BERNIE_BOOKING_INTERPRET,
            temperature=0.2,
            correlation_id=correlation_id,
            metadata={"provider": "fake"},
        )
    )

    assert result.allowed is True
    assert result.raw == {"interpreted": True}
    assert result.denial_reason is None
    assert provider.calls == 1
    assert provider.last_contents == {"input": "non-phi fixture"}
    assert provider.last_temperature == 0.2
    assert result.cost_envelope.default_provider == "gemini_vertex"
    assert result.cost_envelope.response_units > 0
    assert result.latency_ms is not None
    assert result.audit_events[0].event_type == AiAuditEventType.INVOCATION_ALLOWED
    assert result.audit_events[0].correlation_id == correlation_id
    assert result.audit_events[0].metadata["latency_ms"] == result.latency_ms
    assert result.audit_events[0].metadata["estimated_cost_usd"] >= 0


@pytest.mark.asyncio
async def test_dry_run_records_allowed_event_without_provider_call():
    provider = FakeProvider()
    service = AccessAiService(provider)

    result = await service.invoke(
        request_for(
            actor(AiAccessRole.CLINICAL_USER),
            AiCapability.LETTER_DRAFTING,
            AiMethod.DRY_RUN,
        )
    )

    assert result.allowed is True
    assert result.raw == {}
    assert result.cost_envelope.response_units == 0
    assert result.latency_ms == 0
    assert provider.calls == 0
    assert result.audit_events[0].event_type == AiAuditEventType.INVOCATION_ALLOWED


@pytest.mark.asyncio
async def test_provider_failure_records_failure_event_without_raw_payload():
    provider = FakeProvider(exc=RuntimeError("provider unavailable"))
    service = AccessAiService(provider)

    result = await service.invoke(
        request_for(
            actor(AiAccessRole.DEV_OPERATOR),
            AiCapability.PROVIDER_LIVE_SMOKE,
            AiMethod.LIVE_SMOKE,
        )
    )

    assert result.allowed is True
    assert result.raw is None
    assert result.denial_reason == "RuntimeError"
    assert provider.calls == 1
    assert result.cost_envelope.response_units == 0
    assert result.latency_ms is not None
    assert [event.event_type for event in result.audit_events] == [
        AiAuditEventType.INVOCATION_ALLOWED,
        AiAuditEventType.INVOCATION_FAILED,
    ]
    assert result.audit_events[1].reason_code == "RuntimeError"
    assert result.audit_events[0].correlation_id == result.audit_events[1].correlation_id
    assert result.audit_events[1].metadata["latency_ms"] == result.latency_ms


@pytest.mark.asyncio
async def test_audit_metadata_rejection_prevents_provider_call():
    provider = FakeProvider()
    service = AccessAiService(provider)

    with pytest.raises(ValidationError, match="audit-safe"):
        await service.invoke(
            request_for(
                actor(AiAccessRole.CLINICAL_USER),
                AiCapability.AUDIO_SCRIBE,
                metadata={"raw_prompt": "do not audit this"},
            )
        )

    assert provider.calls == 0
