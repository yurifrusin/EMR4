import asyncio
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


def run(coro):
    return asyncio.run(coro)


def test_invocation_denies_before_provider_call_when_role_not_allowed():
    provider = FakeProvider()
    service = AccessAiService(provider)

    result = run(service.invoke(
        request_for(
            actor(AiAccessRole.RECEPTION_USER),
            AiCapability.CLINICAL_EXTRACTION,
        )
    ))

    assert result.allowed is False
    assert result.raw is None
    assert result.denial_reason == "role_not_allowed"
    assert result.cost_envelope.request_units > 0
    assert result.latency_ms is None
    assert provider.calls == 0
    assert result.audit_events[0].event_type == AiAuditEventType.INVOCATION_BLOCKED
    assert result.audit_events[0].reason_code == "role_not_allowed"


def test_blocked_budgeted_invocation_records_budget_status_without_provider_call():
    provider = FakeProvider()
    service = AccessAiService(provider)

    result = run(service.invoke(
        request_for(
            actor(AiAccessRole.RECEPTION_USER),
            AiCapability.PROVIDER_LIVE_SMOKE,
            AiMethod.LIVE_SMOKE,
        )
    ))

    audit_metadata = result.audit_events[0].metadata

    assert result.allowed is False
    assert provider.calls == 0
    assert audit_metadata["budget_limit_present"] is True
    assert audit_metadata["budget_threshold_ratio"] is not None
    assert audit_metadata["budget_warning"] is False
    assert "non-phi fixture" not in str(audit_metadata)


def test_successful_invocation_calls_provider_and_records_allowed_event():
    provider = FakeProvider({"interpreted": True})
    service = AccessAiService(provider)
    correlation_id = uuid.uuid4()

    result = run(service.invoke(
        request_for(
            actor(AiAccessRole.RECEPTION_USER),
            AiCapability.BERNIE_BOOKING_INTERPRET,
            temperature=0.2,
            correlation_id=correlation_id,
            metadata={"provider": "fake"},
        )
    ))

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
    assert "interpreted" not in str(result.audit_events[0].metadata)
    assert "non-phi fixture" not in str(result.audit_events[0].metadata)


def test_dry_run_records_allowed_event_without_provider_call():
    provider = FakeProvider()
    service = AccessAiService(provider)

    result = run(service.invoke(
        request_for(
            actor(AiAccessRole.CLINICAL_USER),
            AiCapability.LETTER_DRAFTING,
            AiMethod.DRY_RUN,
        )
    ))

    assert result.allowed is True
    assert result.raw == {}
    assert result.cost_envelope.response_units == 0
    assert result.latency_ms == 0
    assert provider.calls == 0
    assert result.audit_events[0].event_type == AiAuditEventType.INVOCATION_ALLOWED
    assert result.audit_events[0].metadata["budget_limit_present"] is False
    assert "non-phi fixture" not in str(result.audit_events[0].metadata)


def test_provider_failure_records_failure_event_without_raw_payload():
    provider = FakeProvider(exc=RuntimeError("provider unavailable"))
    service = AccessAiService(provider)

    result = run(service.invoke(
        request_for(
            actor(AiAccessRole.DEV_OPERATOR),
            AiCapability.PROVIDER_LIVE_SMOKE,
            AiMethod.LIVE_SMOKE,
        )
    ))

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
    assert result.audit_events[0].metadata["budget_limit_present"] is True
    assert result.audit_events[1].metadata["budget_limit_present"] is True
    assert "provider unavailable" not in str(result.audit_events[1].metadata)


def test_audit_metadata_rejection_prevents_provider_call():
    provider = FakeProvider()
    service = AccessAiService(provider)

    with pytest.raises(ValidationError, match="audit-safe"):
        run(service.invoke(
            request_for(
                actor(AiAccessRole.CLINICAL_USER),
                AiCapability.AUDIO_SCRIBE,
                metadata={"raw_prompt": "do not audit this"},
            )
        ))

    assert provider.calls == 0


# ---- Adversarial test lane: Sprint Access AI audit/cost envelope hardening ----

class TestBlockedEntitlementVariations:
    """Every denial reason produces cost/audit metadata and provider.calls == 0."""

    def test_blocked_entitlement_method_not_allowed(self):
        provider = FakeProvider()
        service = AccessAiService(provider)
        result = run(service.invoke(
            request_for(actor(AiAccessRole.CLINICAL_USER), AiCapability.CLINICAL_EXTRACTION, method=AiMethod.LIVE_SMOKE),
        ))
        assert result.allowed is False
        assert result.raw is None
        assert result.denial_reason == "method_not_allowed"
        assert result.cost_envelope.request_units > 0
        assert result.latency_ms is None
        assert provider.calls == 0
        assert result.audit_events[0].event_type == AiAuditEventType.INVOCATION_BLOCKED
        assert result.audit_events[0].reason_code == "method_not_allowed"
        assert "estimated_cost_usd" in result.audit_events[0].metadata

    def test_blocked_entitlement_environment_not_allowed(self):
        provider = FakeProvider()
        service = AccessAiService(provider)
        dev_actor = actor(AiAccessRole.CLINICAL_USER, environment="production")
        result = run(service.invoke(request_for(dev_actor, AiCapability.CLINICAL_EXTRACTION)))
        assert result.allowed is False
        assert result.denial_reason == "environment_not_allowed"
        assert result.cost_envelope.request_units > 0
        assert provider.calls == 0
        assert result.audit_events[0].event_type == AiAuditEventType.INVOCATION_BLOCKED
        assert result.audit_events[0].reason_code == "environment_not_allowed"
        assert "estimated_cost_usd" in result.audit_events[0].metadata

    def test_blocked_entitlement_actor_disabled(self):
        provider = FakeProvider()
        service = AccessAiService(provider)
        result = run(service.invoke(
            request_for(actor(AiAccessRole.DISABLED), AiCapability.BERNIE_BOOKING_INTERPRET),
        ))
        assert result.allowed is False
        assert result.denial_reason == "actor_disabled"
        assert result.cost_envelope.request_units > 0
        assert provider.calls == 0
        assert result.audit_events[0].event_type == AiAuditEventType.INVOCATION_BLOCKED
        assert result.audit_events[0].reason_code == "actor_disabled"

    def test_blocked_entitlement_has_cost_and_risk_tier_metadata(self):
        provider = FakeProvider()
        service = AccessAiService(provider)
        result = run(service.invoke(
            request_for(actor(AiAccessRole.RECEPTION_USER), AiCapability.CLINICAL_EXTRACTION),
        ))
        assert result.allowed is False
        assert provider.calls == 0
        meta = result.audit_events[0].metadata
        assert meta["estimated_cost_usd"] >= 0
        assert meta["request_units"] > 0
        assert meta["response_units"] == 0
        assert meta["risk_tier"] == "clinical_read"
        assert meta["default_provider"] == "gemini_vertex"
        assert "latency_ms" not in meta


def test_estimate_cost_never_calls_provider_when_blocked_by_entitlement():
    """ESTIMATE_COST is not in any capability's allowed_methods, so it is
    blocked by entitlement. The key invariant is zero provider calls."""
    provider = FakeProvider()
    service = AccessAiService(provider)
    result = run(service.invoke(
        request_for(
            actor(AiAccessRole.CLINICAL_USER),
            AiCapability.CLINICAL_EXTRACTION,
            AiMethod.ESTIMATE_COST,
        ),
    ))
    assert result.allowed is False
    assert result.denial_reason == "method_not_allowed"
    assert provider.calls == 0
    assert result.audit_events[0].event_type == AiAuditEventType.INVOCATION_BLOCKED


def test_provider_failure_audit_events_have_no_phi_keys_in_metadata():
    """Both allowed and failed audit events must not expose PHI-like metadata keys."""
    provider = FakeProvider(exc=ValueError("provider unavailable"))
    service = AccessAiService(provider)
    result = run(service.invoke(
        request_for(actor(AiAccessRole.DEV_OPERATOR), AiCapability.PROVIDER_LIVE_SMOKE, AiMethod.LIVE_SMOKE),
    ))
    assert result.allowed is True
    assert result.raw is None
    assert provider.calls == 1
    assert len(result.audit_events) == 2
    phi_fragments = {
        "raw",
        "prompt",
        "transcript",
        "note_text",
        "letter_text",
        "patient_name",
        "medicare",
        "ihi",
        "dob",
        "phone",
        "address",
    }
    for event in result.audit_events:
        for key in event.metadata:
            normalized = key.lower()
            for fragment in phi_fragments:
                assert fragment not in normalized


def test_budget_threshold_appears_for_capped_capability():
    from app.services.ai.registry import get_capability_metadata
    metadata = get_capability_metadata(AiCapability.PROVIDER_LIVE_SMOKE)
    assert metadata.max_estimated_cost_usd == 1.0
    provider = FakeProvider({"smoke": "ok"})
    service = AccessAiService(provider)
    result = run(service.invoke(
        request_for(actor(AiAccessRole.DEV_OPERATOR), AiCapability.PROVIDER_LIVE_SMOKE, AiMethod.LIVE_SMOKE),
    ))
    assert result.allowed is True
    assert result.cost_envelope.max_estimated_cost_usd == 1.0
    assert "max_estimated_cost_usd" in result.audit_events[0].metadata
    assert result.audit_events[0].metadata["max_estimated_cost_usd"] == 1.0


def test_blocked_entitlement_metadata_rejects_phi_keys():
    """PHI-like keys in request metadata are rejected even for blocked invocations."""
    provider = FakeProvider()
    service = AccessAiService(provider)
    with pytest.raises(ValidationError, match="audit-safe"):
        run(service.invoke(
            request_for(
                actor(AiAccessRole.RECEPTION_USER),
                AiCapability.CLINICAL_EXTRACTION,
                metadata={"patient_name": "John Doe"},
            ),
        ))
    assert provider.calls == 0
