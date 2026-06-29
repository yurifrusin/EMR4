"""
AiService — EMR4 AI facade.

Routes each clinical AI capability through the provider protocol so routers
never import a provider SDK directly. The provider is injected at construction
time to allow fake providers in tests (no network required).

asyncio.to_thread wraps every blocking provider call to preserve the
event-loop-freeze fix established in consultation.py and letters.py.
"""
from typing import Optional

from app.services.ai.contracts import (
    AiCapability,
    AiMethod,
    AiProvider,
    AiResult,
    AudioScribeData,
    ClinicalExtractionData,
    LetterDraftingData,
)
from app.services.ai.access_service import AccessAiRequest, AccessAiService
from app.services.ai.audit_events import AiAuditSourceSurface
from app.services.ai.entitlements import AiAccessRole, AiActorContext

_default_provider: Optional["AiProvider"] = None


def _get_default_provider() -> "AiProvider":
    global _default_provider
    if _default_provider is None:
        from app.services.ai.providers.gemini import GeminiProvider
        _default_provider = GeminiProvider()
    return _default_provider


class AiService:
    def __init__(self, provider: Optional["AiProvider"] = None) -> None:
        self._provider: AiProvider = provider or _get_default_provider()

    async def analyze_consultation_text(
        self,
        prompt: str,
        actor_context: AiActorContext | None = None,
    ) -> AiResult:
        result = await AccessAiService(self._provider).invoke(
            AccessAiRequest(
                actor=actor_context or _fallback_clinical_actor_context(),
                capability=AiCapability.CLINICAL_EXTRACTION,
                method=AiMethod.INVOKE,
                contents=prompt,
                source_surface=AiAuditSourceSurface.TASKPANE,
                temperature=0.1,
                metadata={"clinical_surface": "analyze_consultation"},
            )
        )
        if not result.allowed or result.raw is None:
            raise RuntimeError(result.denial_reason or "access_ai_clinical_extraction_blocked")
        return AiResult(
            raw=result.raw,
            data=ClinicalExtractionData.model_validate(result.raw),
            audit_events=result.audit_events,
            cost_envelope=result.cost_envelope,
            latency_ms=result.latency_ms,
        )

    async def scribe_audio(
        self,
        audio_bytes: bytes,
        mime_type: str,
        prompt_text: str,
        actor_context: AiActorContext | None = None,
    ) -> AiResult:
        contents = {
            "audio_bytes": audio_bytes,
            "mime_type": mime_type,
            "prompt": prompt_text,
        }
        result = await AccessAiService(self._provider).invoke(
            AccessAiRequest(
                actor=actor_context or _fallback_clinical_actor_context(),
                capability=AiCapability.AUDIO_SCRIBE,
                method=AiMethod.INVOKE,
                contents=contents,
                source_surface=AiAuditSourceSurface.COMMAND_CENTRE,
                temperature=0.1,
                metadata={"clinical_surface": "scribe_consultation"},
            )
        )
        if not result.allowed or result.raw is None:
            raise RuntimeError(result.denial_reason or "access_ai_audio_scribe_blocked")
        return AiResult(
            raw=result.raw,
            data=AudioScribeData.model_validate(result.raw),
            audit_events=result.audit_events,
            cost_envelope=result.cost_envelope,
            latency_ms=result.latency_ms,
        )

    async def draft_letter(
        self,
        prompt: str,
        actor_context: AiActorContext | None = None,
    ) -> AiResult:
        result = await AccessAiService(self._provider).invoke(
            AccessAiRequest(
                actor=actor_context or _fallback_clinical_actor_context(),
                capability=AiCapability.LETTER_DRAFTING,
                method=AiMethod.INVOKE,
                contents=prompt,
                source_surface=AiAuditSourceSurface.TASKPANE,
                temperature=0.3,
                metadata={"clinical_surface": "draft_letter"},
            )
        )
        if not result.allowed or result.raw is None:
            raise RuntimeError(result.denial_reason or "access_ai_letter_drafting_blocked")
        return AiResult(
            raw=result.raw,
            data=LetterDraftingData.model_validate(result.raw),
            audit_events=result.audit_events,
            cost_envelope=result.cost_envelope,
            latency_ms=result.latency_ms,
        )


def _fallback_clinical_actor_context() -> AiActorContext:
    return AiActorContext(
        user_id=None,
        practice_id=None,
        roles=(AiAccessRole.CLINICAL_USER,),
        environment="dev",
    )
