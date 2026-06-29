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
    CLINICAL_EXTRACTION = "clinical.note.extract"
    AUDIO_SCRIBE = "clinical.scribe.transcribe"
    LETTER_DRAFTING = "clinical.letter.draft"
    BERNIE_BOOKING_INTERPRET = "admin.booking.interpret"
    BERNIE_BOOKING_SUGGEST_SLOTS = "admin.booking.suggest_slots"
    BERNIE_BOOKING_PREPARE_PROPOSAL = "admin.booking.prepare_proposal"
    PROVIDER_LIVE_SMOKE = "ai.provider.live_smoke"


class AiModality(str, Enum):
    TEXT = "text"
    AUDIO = "audio"
    DOCUMENT = "document"
    IMAGE = "image"
    TOOL_INTENT = "tool_intent"
    MULTIMODAL = "multimodal"


class AiMethod(str, Enum):
    INVOKE = "invoke"
    DRY_RUN = "dry_run"
    EVALUATE_FIXTURE = "evaluate_fixture"
    LIVE_SMOKE = "live_smoke"
    ESTIMATE_COST = "estimate_cost"


class AiRiskTier(str, Enum):
    LOW_READ_ONLY = "low_read_only"
    CLINICAL_READ = "clinical_read"
    CLINICAL_DRAFT = "clinical_draft"
    ADMIN_PROPOSAL = "admin_proposal"
    HUMAN_CONFIRMED_WRITE = "human_confirmed_write"
    BLOCKED = "blocked"


class AiProviderClass(str, Enum):
    MODEL_GENERATION = "model_generation"
    RETRIEVAL_GENERATION = "retrieval_generation"
    EMBEDDING_RETRIEVAL = "embedding_retrieval"
    TOOL_INTENT = "tool_intent"
    LOCAL_OR_TEST = "local_or_test"


class AiResult:
    __slots__ = ("raw", "data", "audit_events", "cost_envelope", "latency_ms")

    def __init__(
        self,
        raw: dict,
        data: Any,
        *,
        audit_events: tuple = (),
        cost_envelope: Any = None,
        latency_ms: int | None = None,
    ) -> None:
        self.raw = raw
        self.data = data
        self.audit_events = audit_events
        self.cost_envelope = cost_envelope
        self.latency_ms = latency_ms


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
    def generate_json(self, contents: Any, temperature: float) -> dict:
        pass
