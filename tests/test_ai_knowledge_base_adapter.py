import uuid

import pytest

from app.services.ai.audit_events import AiAuditEventType, AiAuditSourceSurface
from app.services.ai.entitlements import AiAccessRole, AiActorContext
from app.services.ai.knowledge_base import (
    AccessAiKnowledgeBaseService,
    KnowledgeBaseAnswer,
    KnowledgeBaseCitation,
    KnowledgeBasePolicyError,
    KnowledgeBaseQuery,
)


class FakeKnowledgeBaseAdapter:
    provider_name = "fake_licensed_kb"

    def __init__(self, answer: KnowledgeBaseAnswer | None = None):
        self.answer = answer or KnowledgeBaseAnswer(
            answer_text="Use the current evidence summary as clinician decision support.",
            provider=self.provider_name,
            knowledge_base_id="licensed-clinical-kb",
            citations=(
                KnowledgeBaseCitation(
                    citation_id="kb-001",
                    title="Evidence summary fixture",
                    provider=self.provider_name,
                    source_uri="https://example.test/evidence/kb-001",
                    licence_scope="dev-fixture",
                ),
            ),
            confidence="fixture",
        )
        self.calls = 0
        self.last_request = None

    def retrieve(self, request: KnowledgeBaseQuery) -> KnowledgeBaseAnswer:
        self.calls += 1
        self.last_request = request
        return self.answer


def actor(*roles: str) -> AiActorContext:
    return AiActorContext(
        user_id=uuid.uuid4(),
        practice_id=uuid.uuid4(),
        roles=roles,
        environment="dev",
    )


def query(**kwargs) -> KnowledgeBaseQuery:
    return KnowledgeBaseQuery(
        knowledge_base_id="licensed-clinical-kb",
        query_text="non-PHI evidence question",
        source_collection="dev-fixture",
        **kwargs,
    )


@pytest.mark.asyncio
async def test_knowledge_base_query_routes_through_access_ai_with_citation_audit():
    adapter = FakeKnowledgeBaseAdapter()
    service = AccessAiKnowledgeBaseService(adapter)
    correlation_id = uuid.uuid4()

    result = await service.query(
        actor=actor(AiAccessRole.CLINICAL_USER),
        request=query(),
        source_surface=AiAuditSourceSurface.COMMAND_CENTRE,
        correlation_id=correlation_id,
    )

    assert result.allowed is True
    assert result.answer is not None
    assert result.answer.citations[0].citation_id == "kb-001"
    assert adapter.calls == 1
    assert adapter.last_request.knowledge_base_id == "licensed-clinical-kb"
    assert [event.event_type for event in result.audit_events] == [
        AiAuditEventType.INVOCATION_ALLOWED,
        AiAuditEventType.KNOWLEDGE_QUERY_ALLOWED,
    ]
    assert all(event.correlation_id == correlation_id for event in result.audit_events)
    invocation_metadata = result.audit_events[0].metadata
    knowledge_metadata = result.audit_events[1].metadata
    assert invocation_metadata["knowledge_base_id"] == "licensed-clinical-kb"
    assert "query_text" not in invocation_metadata
    assert knowledge_metadata["citation_count"] == 1
    assert knowledge_metadata["citation_ids"] == "kb-001"
    assert knowledge_metadata["retrieved_text_stored"] is False


@pytest.mark.asyncio
async def test_knowledge_base_query_refuses_phi_before_adapter_call():
    adapter = FakeKnowledgeBaseAdapter()
    service = AccessAiKnowledgeBaseService(adapter)

    result = await service.query(
        actor=actor(AiAccessRole.CLINICAL_USER),
        request=query(contains_phi=True),
    )

    assert result.allowed is False
    assert result.answer is None
    assert result.denial_reason == "phi_not_allowed"
    assert adapter.calls == 0
    assert result.audit_events[0].event_type == AiAuditEventType.KNOWLEDGE_QUERY_BLOCKED
    assert result.audit_events[0].reason_code == "phi_not_allowed"
    assert "query_text" not in result.audit_events[0].metadata


@pytest.mark.asyncio
async def test_knowledge_base_query_denies_reception_role_before_adapter_call():
    adapter = FakeKnowledgeBaseAdapter()
    service = AccessAiKnowledgeBaseService(adapter)

    result = await service.query(
        actor=actor(AiAccessRole.RECEPTION_USER),
        request=query(),
    )

    assert result.allowed is False
    assert result.denial_reason == "role_not_allowed"
    assert adapter.calls == 0
    assert result.audit_events[0].event_type == AiAuditEventType.INVOCATION_BLOCKED


@pytest.mark.asyncio
async def test_required_citations_fail_closed_after_provider_response():
    adapter = FakeKnowledgeBaseAdapter(
        KnowledgeBaseAnswer(
            answer_text="Answer without citations should fail when citations are required.",
            provider="fake_licensed_kb",
            knowledge_base_id="licensed-clinical-kb",
            citations=(),
        )
    )
    service = AccessAiKnowledgeBaseService(adapter)

    result = await service.query(
        actor=actor(AiAccessRole.CLINICAL_USER),
        request=query(),
    )

    assert result.allowed is False
    assert result.answer is None
    assert result.denial_reason == "KnowledgeBasePolicyError"
    assert adapter.calls == 1
    assert [event.event_type for event in result.audit_events] == [
        AiAuditEventType.INVOCATION_ALLOWED,
        AiAuditEventType.INVOCATION_FAILED,
    ]


def test_retrieved_text_storage_is_transient_only():
    with pytest.raises(ValueError, match="retrieved_text_must_be_transient"):
        query(retrieval_text_storage="cache_provider_passages")

    with pytest.raises(ValueError, match="retrieved_text_storage_not_allowed"):
        KnowledgeBaseAnswer(
            answer_text="unsafe storage",
            provider="fake_licensed_kb",
            knowledge_base_id="licensed-clinical-kb",
            citations=(
                KnowledgeBaseCitation(
                    citation_id="kb-001",
                    title="Evidence summary fixture",
                    provider="fake_licensed_kb",
                ),
            ),
            retrieved_text_stored=True,
        )
