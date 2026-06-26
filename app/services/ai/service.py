"""
AiService — EMR4 AI facade.

Routes each clinical AI capability through the provider protocol so routers
never import a provider SDK directly. The provider is injected at construction
time to allow fake providers in tests (no network required).

asyncio.to_thread wraps every blocking provider call to preserve the
event-loop-freeze fix established in consultation.py and letters.py.
"""
import asyncio
from typing import Optional

from app.services.ai.contracts import (
    AiProvider,
    AiResult,
    AudioScribeData,
    ClinicalExtractionData,
    LetterDraftingData,
)

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

    async def analyze_consultation_text(self, prompt: str) -> AiResult:
        raw = await asyncio.to_thread(self._provider.generate_json, prompt, 0.1)
        return AiResult(raw=raw, data=ClinicalExtractionData.model_validate(raw))

    async def scribe_audio(
        self, audio_bytes: bytes, mime_type: str, prompt_text: str
    ) -> AiResult:
        contents = {
            "audio_bytes": audio_bytes,
            "mime_type": mime_type,
            "prompt": prompt_text,
        }
        raw = await asyncio.to_thread(self._provider.generate_json, contents, 0.1)
        return AiResult(raw=raw, data=AudioScribeData.model_validate(raw))

    async def draft_letter(self, prompt: str) -> AiResult:
        raw = await asyncio.to_thread(self._provider.generate_json, prompt, 0.3)
        return AiResult(raw=raw, data=LetterDraftingData.model_validate(raw))
