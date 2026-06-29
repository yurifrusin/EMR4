"""
Access AI invocation service.

This is the first backend choke point for future model calls. It combines the
capability registry, product entitlement checks, provider protocol, and typed
audit event contract. Current routers are not migrated yet; tests use injected
fake providers only.
"""
import asyncio
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.services.ai.audit_events import (
    AccessAiAuditEvent,
    AiAuditDecision,
    AiAuditEventType,
    AiAuditSourceSurface,
    build_access_ai_audit_event,
)
from app.services.ai.contracts import AiCapability, AiMethod, AiProvider
from app.services.ai.entitlements import AiActorContext, decide_ai_entitlement
from app.services.ai.registry import get_capability_metadata


@dataclass(frozen=True)
class AccessAiRequest:
    actor: AiActorContext
    capability: AiCapability
    method: AiMethod
    contents: Any
    source_surface: AiAuditSourceSurface
    temperature: float = 0.1
    target_resource_type: str | None = None
    target_resource_id: UUID | str | None = None
    correlation_id: UUID | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class AccessAiInvocationResult:
    allowed: bool
    raw: dict | None
    denial_reason: str | None
    audit_events: tuple[AccessAiAuditEvent, ...]


class AccessAiService:
    def __init__(self, provider: AiProvider) -> None:
        self._provider = provider

    async def invoke(self, request: AccessAiRequest) -> AccessAiInvocationResult:
        entitlement = decide_ai_entitlement(
            request.actor,
            request.capability,
            request.method,
        )
        metadata = get_capability_metadata(request.capability)

        common_event = {
            "actor_user_id": request.actor.user_id,
            "actor_roles": request.actor.roles,
            "practice_id": request.actor.practice_id,
            "capability": request.capability,
            "method": request.method,
            "source_surface": request.source_surface,
            "target_resource_type": request.target_resource_type,
            "target_resource_id": request.target_resource_id,
            "correlation_id": request.correlation_id,
        }

        if not entitlement.allowed:
            event = build_access_ai_audit_event(
                event_type=AiAuditEventType.INVOCATION_BLOCKED,
                decision=AiAuditDecision.BLOCKED,
                reason_code=entitlement.reason,
                metadata={
                    **(request.metadata or {}),
                    "default_provider": metadata.default_provider,
                    "risk_tier": metadata.risk_tier.value,
                },
                **common_event,
            )
            return AccessAiInvocationResult(
                allowed=False,
                raw=None,
                denial_reason=entitlement.reason,
                audit_events=(event,),
            )

        allowed_event = build_access_ai_audit_event(
            event_type=AiAuditEventType.INVOCATION_ALLOWED,
            decision=AiAuditDecision.ALLOWED,
            metadata={
                **(request.metadata or {}),
                "default_provider": metadata.default_provider,
                "risk_tier": metadata.risk_tier.value,
                "phi_allowed": metadata.phi_allowed,
            },
            **common_event,
        )

        if request.method in {AiMethod.DRY_RUN, AiMethod.ESTIMATE_COST}:
            return AccessAiInvocationResult(
                allowed=True,
                raw={},
                denial_reason=None,
                audit_events=(allowed_event,),
            )

        try:
            raw = await asyncio.to_thread(
                self._provider.generate_json,
                request.contents,
                request.temperature,
            )
        except Exception as exc:
            failed_event = build_access_ai_audit_event(
                event_type=AiAuditEventType.INVOCATION_FAILED,
                decision=AiAuditDecision.FAILED,
                reason_code=exc.__class__.__name__,
                metadata={
                    "default_provider": metadata.default_provider,
                    "risk_tier": metadata.risk_tier.value,
                },
                **common_event,
            )
            return AccessAiInvocationResult(
                allowed=True,
                raw=None,
                denial_reason=failed_event.reason_code,
                audit_events=(allowed_event, failed_event),
            )

        return AccessAiInvocationResult(
            allowed=True,
            raw=raw,
            denial_reason=None,
            audit_events=(allowed_event,),
        )
