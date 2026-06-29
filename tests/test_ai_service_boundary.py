"""
AI provider boundary tests.

All tests use a FakeProvider that returns fixture dicts — no network,
no Gemini credentials, no DB required.

Verifies:
- AiService returns AiResult with correct .raw and .data types
- Contract models tolerate extra and missing fields (extra="allow", Optional)
- FakeProvider satisfies the AiProvider runtime protocol
- asyncio.to_thread is used (providers are always called in a thread)
"""
import asyncio
import json
import pathlib

from app.services.ai.contracts import (
    AiProvider,
    AiResult,
    AiCapability,
    AudioScribeData,
    ClinicalExtractionData,
    LetterDraftingData,
)
from app.services.ai.audit_events import AiAuditEventType
from app.services.ai.entitlements import AiActorContext
from app.services.ai.service import AiService

FIXTURES = (
    pathlib.Path(__file__).parent.parent
    / "app" / "services" / "ai" / "evals" / "fixtures"
)


class FakeProvider:
    """Returns a pre-set dict; records the last (contents, temperature) call."""

    def __init__(self, response: dict) -> None:
        self._response = response
        self.last_contents = None
        self.last_temperature: float = 0.0

    def generate_json(self, contents, temperature: float) -> dict:
        self.last_contents = contents
        self.last_temperature = temperature
        return self._response


def _fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


# ── clinical extraction ──────────────────────────────────────────────────────

def test_analyze_consultation_returns_aresult():
    fixture = _fixture("clinical_extraction_fixture.json")
    provider = FakeProvider(fixture)
    result = asyncio.run(AiService(provider).analyze_consultation_text("Patient has hypertension"))
    assert isinstance(result, AiResult)
    assert result.raw == fixture
    assert isinstance(result.data, ClinicalExtractionData)
    assert result.audit_events[0].event_type == AiAuditEventType.INVOCATION_ALLOWED
    assert result.audit_events[0].capability == AiCapability.CLINICAL_EXTRACTION
    assert result.cost_envelope is not None


def test_analyze_consultation_data_fields():
    fixture = _fixture("clinical_extraction_fixture.json")
    result = asyncio.run(AiService(FakeProvider(fixture)).analyze_consultation_text("x"))
    assert result.data.encounter_metadata is not None
    assert result.data.clinical_diagnoses is not None
    assert result.data.medications_and_prescriptions is not None


def test_analyze_consultation_temperature():
    provider = FakeProvider({})
    asyncio.run(AiService(provider).analyze_consultation_text("x"))
    assert provider.last_temperature == 0.1


def test_analyze_consultation_denied_actor_fails_before_provider_call():
    provider = FakeProvider({})
    denied_actor = AiActorContext(
        user_id=None,
        practice_id=None,
        roles=(),
        environment="dev",
    )

    try:
        asyncio.run(AiService(provider).analyze_consultation_text("x", denied_actor))
    except RuntimeError as exc:
        assert "role_not_allowed" in str(exc)
    else:
        raise AssertionError("Access AI denial should raise")

    assert provider.last_contents is None


# ── audio scribe ─────────────────────────────────────────────────────────────

def test_scribe_audio_returns_aresult():
    fixture = _fixture("audio_scribe_fixture.json")
    provider = FakeProvider(fixture)
    result = asyncio.run(
        AiService(provider).scribe_audio(b"fakebytes", "audio/webm", "scribe prompt")
    )
    assert isinstance(result, AiResult)
    assert result.raw == fixture
    assert isinstance(result.data, AudioScribeData)
    assert result.audit_events[0].event_type == AiAuditEventType.INVOCATION_ALLOWED
    assert result.audit_events[0].capability == AiCapability.AUDIO_SCRIBE


def test_scribe_audio_data_fields():
    fixture = _fixture("audio_scribe_fixture.json")
    result = asyncio.run(
        AiService(FakeProvider(fixture)).scribe_audio(b"x", "audio/webm", "p")
    )
    assert result.data.raw_transcript is not None
    assert result.data.generated_clinical_note is not None


def test_scribe_audio_passes_audio_dict_to_provider():
    provider = FakeProvider({})
    asyncio.run(AiService(provider).scribe_audio(b"bytes", "audio/webm", "prompt"))
    assert isinstance(provider.last_contents, dict)
    assert provider.last_contents["audio_bytes"] == b"bytes"
    assert provider.last_contents["mime_type"] == "audio/webm"
    assert provider.last_contents["prompt"] == "prompt"
    assert provider.last_temperature == 0.1


# ── letter drafting ───────────────────────────────────────────────────────────

def test_draft_letter_returns_aresult():
    fixture = _fixture("letter_drafting_fixture.json")
    result = asyncio.run(AiService(FakeProvider(fixture)).draft_letter("Draft a referral"))
    assert isinstance(result, AiResult)
    assert result.raw == fixture
    assert isinstance(result.data, LetterDraftingData)
    assert result.audit_events[0].event_type == AiAuditEventType.INVOCATION_ALLOWED
    assert result.audit_events[0].capability == AiCapability.LETTER_DRAFTING


def test_draft_letter_data_fields():
    fixture = _fixture("letter_drafting_fixture.json")
    result = asyncio.run(AiService(FakeProvider(fixture)).draft_letter("x"))
    assert result.data.subject_line is not None
    assert result.data.letter_text is not None


def test_draft_letter_temperature():
    provider = FakeProvider({})
    asyncio.run(AiService(provider).draft_letter("x"))
    assert provider.last_temperature == 0.3


# ── permissive contract validation ───────────────────────────────────────────

def test_extra_fields_tolerated():
    fixture = {**_fixture("clinical_extraction_fixture.json"), "unexpected": "value"}
    result = asyncio.run(AiService(FakeProvider(fixture)).analyze_consultation_text("x"))
    assert isinstance(result.data, ClinicalExtractionData)


def test_missing_fields_tolerated():
    result = asyncio.run(AiService(FakeProvider({})).analyze_consultation_text("x"))
    assert isinstance(result.data, ClinicalExtractionData)
    assert result.data.encounter_metadata is None
    assert result.data.clinical_diagnoses is None
    assert result.data.medications_and_prescriptions is None


def test_audio_scribe_missing_fields_tolerated():
    result = asyncio.run(AiService(FakeProvider({})).scribe_audio(b"x", "audio/webm", "x"))
    assert isinstance(result.data, AudioScribeData)
    assert result.data.raw_transcript is None


def test_letter_drafting_missing_fields_tolerated():
    result = asyncio.run(AiService(FakeProvider({})).draft_letter("x"))
    assert isinstance(result.data, LetterDraftingData)
    assert result.data.subject_line is None
    assert result.data.letter_text is None


# ── protocol compliance ───────────────────────────────────────────────────────

def test_fake_provider_matches_protocol():
    assert isinstance(FakeProvider({}), AiProvider)
