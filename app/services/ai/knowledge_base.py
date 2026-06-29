"""Provider-neutral Access AI knowledge-base adapter contracts.

This module is deliberately provider-light. It defines the EMR4-owned request,
answer, citation, and adapter boundary for future licensed knowledge sources
such as AWS-backed clinical evidence products without adding live provider
credentials or provider SDK dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.services.ai.access_service import AccessAiRequest, AccessAiService
from app.services.ai.audit_events import (
    AccessAiAuditEvent,
    AiAuditDecision,
    AiAuditEventType,
    AiAuditSourceSurface,
    build_access_ai_audit_event,
)
from app.services.ai.contracts import AiCapability, AiMethod
from app.services.ai.costing import AiCostEnvelope, estimate_ai_cost
from app.services.ai.entitlements import AiActorContext
from app.services.ai.registry import get_capability_metadata


class KnowledgeBasePolicyError(ValueError):
    """Raised when a knowledge-base request or answer violates EMR4 policy."""


class KnowledgeBaseCitation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    citation_id: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=300)
    provider: str = Field(min_length=1, max_length=80)
    source_uri: str | None = Field(default=None, max_length=500)
    licence_scope: str | None = Field(default=None, max_length=120)


class KnowledgeBaseQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    knowledge_base_id: str = Field(min_length=1, max_length=120)
    query_text: str = Field(min_length=1, max_length=2000)
    source_collection: str | None = Field(default=None, max_length=120)
    requires_citations: bool = True
    contains_phi: bool = False
    retrieval_text_storage: str = Field(default="transient_only", max_length=40)

    @model_validator(mode="after")
    def require_transient_retrieval_storage(self) -> "KnowledgeBaseQuery":
        if self.retrieval_text_storage != "transient_only":
            raise KnowledgeBasePolicyError("retrieved_text_must_be_transient")
        return self


class KnowledgeBaseAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer_text: str = Field(min_length=1, max_length=6000)
    provider: str = Field(min_length=1, max_length=80)
    knowledge_base_id: str = Field(min_length=1, max_length=120)
    citations: tuple[KnowledgeBaseCitation, ...] = ()
    confidence: str | None = Field(default=None, max_length=40)
    retrieved_text_stored: bool = False

    @model_validator(mode="after")
    def prohibit_retrieved_text_storage(self) -> "KnowledgeBaseAnswer":
        if self.retrieved_text_stored:
            raise KnowledgeBasePolicyError("retrieved_text_storage_not_allowed")
        return self


@runtime_checkable
class KnowledgeBaseAdapter(Protocol):
    provider_name: str

    def retrieve(self, request: KnowledgeBaseQuery) -> KnowledgeBaseAnswer:
        """Return a validated, citation-bearing answer for an EMR4 query."""


class KnowledgeBaseAiProviderShim:
    """Adapts a knowledge-base provider to the generic Access AI provider seam."""

    def __init__(self, adapter: KnowledgeBaseAdapter) -> None:
        self._adapter = adapter

    def generate_json(self, contents: Any, temperature: float) -> dict:
        request = KnowledgeBaseQuery.model_validate(contents)
        answer = KnowledgeBaseAnswer.model_validate(self._adapter.retrieve(request))
        if request.requires_citations and not answer.citations:
            raise KnowledgeBasePolicyError("citations_required")
        return answer.model_dump(mode="json")


@dataclass(frozen=True)
class AccessAiKnowledgeBaseResult:
    allowed: bool
    answer: KnowledgeBaseAnswer | None
    denial_reason: str | None
    cost_envelope: AiCostEnvelope
    latency_ms: int | None
    audit_events: tuple[AccessAiAuditEvent, ...]


class AccessAiKnowledgeBaseService:
    """Access AI facade for licensed or provider-backed knowledge retrieval."""

    def __init__(self, adapter: KnowledgeBaseAdapter) -> None:
        self._adapter = adapter
        self._access_ai = AccessAiService(KnowledgeBaseAiProviderShim(adapter))

    async def query(
        self,
        *,
        actor: AiActorContext,
        request: KnowledgeBaseQuery,
        source_surface: AiAuditSourceSurface = AiAuditSourceSurface.API,
        target_resource_type: str | None = None,
        target_resource_id: UUID | str | None = None,
        correlation_id: UUID | None = None,
    ) -> AccessAiKnowledgeBaseResult:
        metadata = get_capability_metadata(AiCapability.CLINICAL_KNOWLEDGE_QUERY)
        shared_correlation_id = correlation_id or uuid4()
        safe_metadata = self._safe_audit_metadata(request)

        if request.contains_phi or not metadata.phi_allowed:
            if request.contains_phi:
                cost = estimate_ai_cost(metadata, request_contents=request.model_dump(mode="json"))
                blocked_event = build_access_ai_audit_event(
                    event_type=AiAuditEventType.KNOWLEDGE_QUERY_BLOCKED,
                    decision=AiAuditDecision.BLOCKED,
                    reason_code="phi_not_allowed",
                    actor_user_id=actor.user_id,
                    actor_roles=actor.roles,
                    practice_id=actor.practice_id,
                    capability=AiCapability.CLINICAL_KNOWLEDGE_QUERY,
                    method=AiMethod.INVOKE,
                    source_surface=source_surface,
                    target_resource_type=target_resource_type,
                    target_resource_id=target_resource_id,
                    correlation_id=shared_correlation_id,
                    metadata={
                        **safe_metadata,
                        **cost.audit_metadata(),
                        "risk_tier": metadata.risk_tier.value,
                    },
                )
                return AccessAiKnowledgeBaseResult(
                    allowed=False,
                    answer=None,
                    denial_reason="phi_not_allowed",
                    cost_envelope=cost,
                    latency_ms=None,
                    audit_events=(blocked_event,),
                )

        invocation = await self._access_ai.invoke(
            AccessAiRequest(
                actor=actor,
                capability=AiCapability.CLINICAL_KNOWLEDGE_QUERY,
                method=AiMethod.INVOKE,
                contents=request.model_dump(mode="json"),
                source_surface=source_surface,
                temperature=0.0,
                target_resource_type=target_resource_type,
                target_resource_id=target_resource_id,
                correlation_id=shared_correlation_id,
                metadata=safe_metadata,
            )
        )

        if not invocation.allowed or invocation.raw is None:
            return AccessAiKnowledgeBaseResult(
                allowed=False,
                answer=None,
                denial_reason=invocation.denial_reason,
                cost_envelope=invocation.cost_envelope,
                latency_ms=invocation.latency_ms,
                audit_events=invocation.audit_events,
            )

        answer = KnowledgeBaseAnswer.model_validate(invocation.raw)
        knowledge_event = build_access_ai_audit_event(
            event_type=AiAuditEventType.KNOWLEDGE_QUERY_ALLOWED,
            decision=AiAuditDecision.ALLOWED,
            actor_user_id=actor.user_id,
            actor_roles=actor.roles,
            practice_id=actor.practice_id,
            capability=AiCapability.CLINICAL_KNOWLEDGE_QUERY,
            method=AiMethod.INVOKE,
            source_surface=source_surface,
            target_resource_type=target_resource_type,
            target_resource_id=target_resource_id,
            correlation_id=shared_correlation_id,
            metadata={
                **safe_metadata,
                "citation_count": len(answer.citations),
                "citation_ids": ",".join(citation.citation_id for citation in answer.citations),
                "retrieved_text_stored": answer.retrieved_text_stored,
            },
        )
        return AccessAiKnowledgeBaseResult(
            allowed=True,
            answer=answer,
            denial_reason=None,
            cost_envelope=invocation.cost_envelope,
            latency_ms=invocation.latency_ms,
            audit_events=(*invocation.audit_events, knowledge_event),
        )

    def _safe_audit_metadata(
        self,
        request: KnowledgeBaseQuery,
    ) -> dict[str, str | int | float | bool | None]:
        return {
            "knowledge_base_id": request.knowledge_base_id,
            "source_collection": request.source_collection,
            "adapter_provider": self._adapter.provider_name,
            "requires_citations": request.requires_citations,
            "retrieval_text_storage": request.retrieval_text_storage,
        }
