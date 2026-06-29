"""Static Access AI capability registry.

Sprint 79 keeps this deliberately config/static and fail-closed. Later sprints
can attach product entitlements, audit storage, and runtime invocation to these
metadata contracts.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.services.ai.contracts import (
    AiCapability,
    AiMethod,
    AiModality,
    AiProviderClass,
    AiRiskTier,
)


@dataclass(frozen=True)
class AiCapabilityMetadata:
    capability: AiCapability
    modality: AiModality
    allowed_methods: tuple[AiMethod, ...]
    allowed_environments: tuple[str, ...]
    provider_class: AiProviderClass
    default_provider: str
    default_project: str
    default_location: str
    model_name: str | None
    risk_tier: AiRiskTier
    phi_allowed: bool
    raw_prompt_logging_allowed: bool
    human_confirmation_required: bool
    max_estimated_cost_usd: float | None
    audit_policy: str


def _metadata(
    *,
    capability: AiCapability,
    modality: AiModality,
    allowed_methods: tuple[AiMethod, ...],
    provider_class: AiProviderClass,
    default_provider: str = "gemini_vertex",
    default_project: str = "emr4-copilot-dev",
    default_location: str = "australia-southeast1",
    model_name: str | None = "gemini-2.5-flash",
    risk_tier: AiRiskTier,
    phi_allowed: bool,
    raw_prompt_logging_allowed: bool = False,
    human_confirmation_required: bool = False,
    allowed_environments: tuple[str, ...] = ("dev",),
    max_estimated_cost_usd: float | None = None,
    audit_policy: str = "metadata_only",
) -> AiCapabilityMetadata:
    return AiCapabilityMetadata(
        capability=capability,
        modality=modality,
        allowed_methods=allowed_methods,
        allowed_environments=allowed_environments,
        provider_class=provider_class,
        default_provider=default_provider,
        default_project=default_project,
        default_location=default_location,
        model_name=model_name,
        risk_tier=risk_tier,
        phi_allowed=phi_allowed,
        raw_prompt_logging_allowed=raw_prompt_logging_allowed,
        human_confirmation_required=human_confirmation_required,
        max_estimated_cost_usd=max_estimated_cost_usd,
        audit_policy=audit_policy,
    )


CAPABILITY_REGISTRY: dict[AiCapability, AiCapabilityMetadata] = {
    AiCapability.CLINICAL_EXTRACTION: _metadata(
        capability=AiCapability.CLINICAL_EXTRACTION,
        modality=AiModality.TEXT,
        allowed_methods=(AiMethod.INVOKE, AiMethod.DRY_RUN, AiMethod.EVALUATE_FIXTURE),
        provider_class=AiProviderClass.MODEL_GENERATION,
        risk_tier=AiRiskTier.CLINICAL_READ,
        phi_allowed=True,
    ),
    AiCapability.AUDIO_SCRIBE: _metadata(
        capability=AiCapability.AUDIO_SCRIBE,
        modality=AiModality.AUDIO,
        allowed_methods=(AiMethod.INVOKE, AiMethod.DRY_RUN, AiMethod.EVALUATE_FIXTURE),
        provider_class=AiProviderClass.MODEL_GENERATION,
        risk_tier=AiRiskTier.CLINICAL_DRAFT,
        phi_allowed=True,
    ),
    AiCapability.LETTER_DRAFTING: _metadata(
        capability=AiCapability.LETTER_DRAFTING,
        modality=AiModality.TEXT,
        allowed_methods=(AiMethod.INVOKE, AiMethod.DRY_RUN, AiMethod.EVALUATE_FIXTURE),
        provider_class=AiProviderClass.MODEL_GENERATION,
        risk_tier=AiRiskTier.CLINICAL_DRAFT,
        phi_allowed=True,
    ),
    AiCapability.CLINICAL_KNOWLEDGE_QUERY: _metadata(
        capability=AiCapability.CLINICAL_KNOWLEDGE_QUERY,
        modality=AiModality.DOCUMENT,
        allowed_methods=(AiMethod.INVOKE, AiMethod.DRY_RUN, AiMethod.EVALUATE_FIXTURE),
        provider_class=AiProviderClass.RETRIEVAL_GENERATION,
        default_provider="licensed_clinical_kb",
        default_project="emr4-copilot-dev",
        default_location="multi-region",
        model_name=None,
        risk_tier=AiRiskTier.CLINICAL_READ,
        phi_allowed=False,
    ),
    AiCapability.BERNIE_BOOKING_INTERPRET: _metadata(
        capability=AiCapability.BERNIE_BOOKING_INTERPRET,
        modality=AiModality.TOOL_INTENT,
        allowed_methods=(AiMethod.INVOKE, AiMethod.DRY_RUN, AiMethod.EVALUATE_FIXTURE),
        provider_class=AiProviderClass.TOOL_INTENT,
        default_project="emr4-bernie-dev",
        risk_tier=AiRiskTier.ADMIN_PROPOSAL,
        phi_allowed=False,
    ),
    AiCapability.BERNIE_BOOKING_SUGGEST_SLOTS: _metadata(
        capability=AiCapability.BERNIE_BOOKING_SUGGEST_SLOTS,
        modality=AiModality.TOOL_INTENT,
        allowed_methods=(AiMethod.INVOKE, AiMethod.DRY_RUN),
        provider_class=AiProviderClass.TOOL_INTENT,
        default_provider="local_deterministic",
        default_project="emr4-bernie-dev",
        model_name=None,
        risk_tier=AiRiskTier.ADMIN_PROPOSAL,
        phi_allowed=False,
    ),
    AiCapability.BERNIE_BOOKING_PREPARE_PROPOSAL: _metadata(
        capability=AiCapability.BERNIE_BOOKING_PREPARE_PROPOSAL,
        modality=AiModality.TOOL_INTENT,
        allowed_methods=(AiMethod.INVOKE, AiMethod.DRY_RUN),
        provider_class=AiProviderClass.TOOL_INTENT,
        default_provider="local_deterministic",
        default_project="emr4-bernie-dev",
        model_name=None,
        risk_tier=AiRiskTier.HUMAN_CONFIRMED_WRITE,
        phi_allowed=False,
        human_confirmation_required=True,
    ),
    AiCapability.PROVIDER_LIVE_SMOKE: _metadata(
        capability=AiCapability.PROVIDER_LIVE_SMOKE,
        modality=AiModality.TEXT,
        allowed_methods=(AiMethod.LIVE_SMOKE,),
        provider_class=AiProviderClass.MODEL_GENERATION,
        default_project="emr4-bernie-dev",
        risk_tier=AiRiskTier.LOW_READ_ONLY,
        phi_allowed=False,
        allowed_environments=("dev",),
        max_estimated_cost_usd=1.0,
    ),
}


class UnknownAiCapabilityError(KeyError):
    """Raised when capability metadata is missing or malformed."""


def get_capability_metadata(
    capability: AiCapability | str,
) -> AiCapabilityMetadata:
    try:
        normalized = capability if isinstance(capability, AiCapability) else AiCapability(capability)
    except ValueError as exc:
        raise UnknownAiCapabilityError(str(capability)) from exc

    try:
        metadata = CAPABILITY_REGISTRY[normalized]
    except KeyError as exc:
        raise UnknownAiCapabilityError(normalized.value) from exc

    _validate_metadata(metadata)
    return metadata


def list_capabilities() -> tuple[AiCapabilityMetadata, ...]:
    return tuple(_validate_metadata(item) for item in CAPABILITY_REGISTRY.values())


def is_method_allowed(
    capability: AiCapability | str,
    method: AiMethod | str,
) -> bool:
    metadata = get_capability_metadata(capability)
    normalized = method if isinstance(method, AiMethod) else AiMethod(method)
    return normalized in metadata.allowed_methods


def _validate_metadata(metadata: AiCapabilityMetadata) -> AiCapabilityMetadata:
    required_strings = (
        metadata.default_provider,
        metadata.default_project,
        metadata.default_location,
        metadata.audit_policy,
    )
    if any(not value for value in required_strings):
        raise UnknownAiCapabilityError(metadata.capability.value)
    if not metadata.allowed_methods or not metadata.allowed_environments:
        raise UnknownAiCapabilityError(metadata.capability.value)
    if metadata.risk_tier is AiRiskTier.BLOCKED:
        raise UnknownAiCapabilityError(metadata.capability.value)
    return metadata
