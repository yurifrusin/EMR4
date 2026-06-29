import pytest

from app.services.ai.contracts import (
    AiCapability,
    AiMethod,
    AiProviderClass,
    AiRiskTier,
)
from app.services.ai.registry import (
    UnknownAiCapabilityError,
    get_capability_metadata,
    is_method_allowed,
    list_capabilities,
)


def test_registry_contains_expected_initial_capabilities():
    capabilities = {metadata.capability for metadata in list_capabilities()}
    assert AiCapability.CLINICAL_EXTRACTION in capabilities
    assert AiCapability.AUDIO_SCRIBE in capabilities
    assert AiCapability.LETTER_DRAFTING in capabilities
    assert AiCapability.CLINICAL_KNOWLEDGE_QUERY in capabilities
    assert AiCapability.BERNIE_BOOKING_INTERPRET in capabilities
    assert AiCapability.PROVIDER_LIVE_SMOKE in capabilities


def test_clinical_scribe_metadata_allows_phi_and_uses_copilot_project():
    metadata = get_capability_metadata(AiCapability.AUDIO_SCRIBE)
    assert metadata.phi_allowed is True
    assert metadata.default_project == "emr4-copilot-dev"
    assert metadata.provider_class is AiProviderClass.MODEL_GENERATION
    assert metadata.risk_tier is AiRiskTier.CLINICAL_DRAFT


def test_bernie_interpret_metadata_is_admin_proposal_and_non_phi():
    metadata = get_capability_metadata("admin.booking.interpret")
    assert metadata.phi_allowed is False
    assert metadata.default_project == "emr4-bernie-dev"
    assert metadata.provider_class is AiProviderClass.TOOL_INTENT
    assert metadata.risk_tier is AiRiskTier.ADMIN_PROPOSAL


def test_prepare_proposal_requires_human_confirmation():
    metadata = get_capability_metadata(AiCapability.BERNIE_BOOKING_PREPARE_PROPOSAL)
    assert metadata.human_confirmation_required is True
    assert metadata.risk_tier is AiRiskTier.HUMAN_CONFIRMED_WRITE


def test_clinical_knowledge_query_is_retrieval_generation_and_non_phi():
    metadata = get_capability_metadata(AiCapability.CLINICAL_KNOWLEDGE_QUERY)
    assert metadata.phi_allowed is False
    assert metadata.provider_class is AiProviderClass.RETRIEVAL_GENERATION
    assert metadata.default_provider == "licensed_clinical_kb"
    assert metadata.default_project == "emr4-copilot-dev"
    assert metadata.risk_tier is AiRiskTier.CLINICAL_READ


def test_live_smoke_is_dev_only_low_cost_and_non_phi():
    metadata = get_capability_metadata(AiCapability.PROVIDER_LIVE_SMOKE)
    assert metadata.allowed_environments == ("dev",)
    assert metadata.phi_allowed is False
    assert metadata.max_estimated_cost_usd == 1.0
    assert metadata.allowed_methods == (AiMethod.LIVE_SMOKE,)


def test_unknown_capability_fails_closed():
    with pytest.raises(UnknownAiCapabilityError):
        get_capability_metadata("unknown.capability")


def test_method_allowlist_is_explicit():
    assert is_method_allowed(AiCapability.CLINICAL_EXTRACTION, AiMethod.INVOKE)
    assert not is_method_allowed(AiCapability.CLINICAL_EXTRACTION, AiMethod.LIVE_SMOKE)
