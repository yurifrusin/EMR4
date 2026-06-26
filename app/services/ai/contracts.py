"""
EMR4 AI capability contracts.

Defines the AiProvider protocol that all provider adapters must satisfy,
the AiResult wrapper, and permissive Pydantic models for each capability.

Routers read AiResult.raw (the raw dict returned by the provider) so that
HTTP response shapes are byte-for-byte unchanged. AiResult.data holds a
validated contract model used in tests and future structured-output paths;
permissive config (extra="allow", all fields Optional) ensures live Gemini
output never triggers a validation rejection.
"""
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict
from typing import Protocol, runtime_checkable


class AiCapability(str, Enum):
    CLINICAL_EXTRACTION = "clinical_extraction"
    AUDIO_SCRIBE = "audio_scribe"
    LETTER_DRAFTING = "letter_drafting"


class AiResult:
    __slots__ = ("raw", "data")

    def __init__(self, raw: dict, data: Any) -> None:
        self.raw = raw
        self.data = data


class ClinicalExtractionData(BaseModel):
    model_config = ConfigDict(extra="allow")
    encounter_metadata: Optional[dict] = None
    clinical_diagnoses: Optional[list] = None
    medications_and_prescriptions: Optional[list] = None


class AudioScribeData(BaseModel):
    model_config = ConfigDict(extra="allow")
    raw_transcript: Optional[str] = None
    generated_clinical_note: Optional[str] = None
    encounter_metadata: Optional[dict] = None
    clinical_diagnoses: Optional[list] = None
    medications_and_prescriptions: Optional[list] = None


class LetterDraftingData(BaseModel):
    model_config = ConfigDict(extra="allow")
    subject_line: Optional[str] = None
    letter_text: Optional[str] = None


@runtime_checkable
class AiProvider(Protocol):
    """Sync callable: build provider request, return json.loads result."""
    def generate_json(self, contents: Any, temperature: float) -> dict: ...
