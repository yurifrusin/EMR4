"""Source-prepared synthetic two-persona adapter checks; not executed."""

import io
from pathlib import Path
from types import ModuleType
import wave

import pytest

import stage1_demo_voice as voice
import run_container_child_once as lower


def synthetic_wav() -> bytes:
    stream = io.BytesIO()
    with wave.open(stream, "wb") as target:
        target.setnchannels(1)
        target.setsampwidth(2)
        target.setframerate(16_000)
        target.writeframes(b"\0\0" * 160)
    return stream.getvalue()


def fake_binding(monkeypatch):
    calls = []

    class ChildBinding:
        child_effect_review_sha256 = voice.NATIVE08_EFFECT_REVIEW_SHA256
        finite_grant_sha256 = "g" * 64
        mode = "interactive-voice"

        def __init__(self, slot):
            self.interactive_slot = slot

        def ready(self):
            return True

    module = ModuleType("reviewed_contained_voice_test_double")
    module.__file__ = str(voice.CONTAINED_RUNNER_PATH)
    module.ExecutionBinding = ChildBinding
    module.CHILD_EFFECT_REVIEW_SHA256 = voice.NATIVE08_EFFECT_REVIEW_SHA256

    def run_once(raw, child):
        calls.append((raw, child.interactive_slot))
        return "  review this text  "

    module.run_once = run_once
    monkeypatch.setattr(voice, "_matches", lambda path, digest:
                        path == voice.CONTAINED_RUNNER_PATH and
                        digest == voice.CONTAINED_RUNNER_SHA256)
    binding = voice.ContainedVoiceRuntimeBinding(
        module, ChildBinding("patient"), ChildBinding("staff"), "a" * 64)
    return binding, calls


def test_native08_alone_does_not_enable_either_persona(monkeypatch):
    binding, calls = fake_binding(monkeypatch)
    assert voice.INTERACTIVE_EXECUTION_ACCEPTANCE_SHA256 is None
    for persona in ("patient", "staff"):
        assert binding.ready(persona) is False
        with pytest.raises(voice.VoiceRecognitionUnavailable):
            voice.run_local_recognizer(synthetic_wav(), binding, persona)
    assert calls == []


def test_two_persona_slots_are_distinct_and_each_one_use(monkeypatch):
    binding, calls = fake_binding(monkeypatch)
    monkeypatch.setattr(voice, "INTERACTIVE_EXECUTION_ACCEPTANCE_SHA256", "a" * 64)
    clip = synthetic_wav()
    for persona in ("patient", "staff"):
        assert binding.ready(persona) is True
        assert voice.run_local_recognizer(clip, binding, persona) == "review this text"
        assert binding.ready(persona) is False
        with pytest.raises(voice.VoiceRecognitionUnavailable):
            voice.run_local_recognizer(clip, binding, persona)
    assert calls == [(clip, "patient"), (clip, "staff")]
    assert binding.ready("unknown") is False


def test_wrong_slot_or_unready_lower_binding_fails_closed(monkeypatch):
    binding, calls = fake_binding(monkeypatch)
    monkeypatch.setattr(voice, "INTERACTIVE_EXECUTION_ACCEPTANCE_SHA256", "a" * 64)
    binding.patient_child_binding.interactive_slot = "staff"
    assert binding.ready("patient") is False
    with pytest.raises(voice.VoiceRecognitionUnavailable):
        voice.run_local_recognizer(synthetic_wav(), binding, "patient")
    binding.staff_child_binding.ready = lambda: False
    assert binding.ready("staff") is False
    assert calls == []


def test_qualification_mode_cannot_use_interactive_slot(monkeypatch):
    binding, calls = fake_binding(monkeypatch)
    monkeypatch.setattr(voice, "INTERACTIVE_EXECUTION_ACCEPTANCE_SHA256", "a" * 64)
    binding.patient_child_binding.mode = "child-qualification"
    assert binding.ready("patient") is False
    with pytest.raises(voice.VoiceRecognitionUnavailable):
        voice.run_local_recognizer(synthetic_wav(), binding, "patient")
    assert calls == []


def test_lower_successor_rejects_qualification_mode_before_any_effect():
    binding = lower.ExecutionBinding(
        docker_executable=Path("not-opened"),
        docker_sha256="a" * 64,
        capsule_root=Path("not-opened"),
        owned_output_root=Path("not-opened"),
        stage1_profile_sha256="a" * 64,
        source_review_sha256="a" * 64,
        execution_review_sha256="a" * 64,
        finite_grant_sha256="a" * 64,
        mode="child-qualification",
        child_effect_review_sha256=voice.NATIVE08_EFFECT_REVIEW_SHA256,
        interactive_slot="patient",
    )
    assert binding.ready() is False
    with pytest.raises(lower.ChildUnavailable):
        lower.run_once(synthetic_wav(), binding)


def test_lower_failure_consumes_only_selected_slot(monkeypatch):
    binding, calls = fake_binding(monkeypatch)
    monkeypatch.setattr(voice, "INTERACTIVE_EXECUTION_ACCEPTANCE_SHA256", "a" * 64)

    def unavailable(raw, child):
        raise RuntimeError("synthetic child cleanup unresolved")

    binding.runner_module.run_once = unavailable
    with pytest.raises(voice.VoiceRecognitionUnavailable):
        voice.run_local_recognizer(synthetic_wav(), binding, "patient")
    assert binding.ready("patient") is False
    assert binding.ready("staff") is True
    assert calls == []
