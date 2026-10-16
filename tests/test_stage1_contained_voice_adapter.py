"""Pure synthetic checks for the trusted-native voice entry seam; NOT_EXECUTED.

These tests use fake upper callbacks, a synthetic WAV, and the actual lower
module API only in a qualification-mode negative. They do not establish real
native containment, source authentication, durable storage, process cleanup,
microphone behavior, or runtime acceptance.
"""

import io
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
import wave

import pytest

import stage1_demo_voice as voice
import run_container_child_once as lower


def synthetic_wav():
    stream = io.BytesIO()
    with wave.open(stream, "wb") as target:
        target.setnchannels(1)
        target.setsampwidth(2)
        target.setframerate(16_000)
        target.writeframes(b"\0\0" * 160)
    return stream.getvalue()


def fixture(monkeypatch, *, native=True):
    consumed = []
    calls = []
    current = {"patient": True, "staff": True}

    @dataclass(frozen=True)
    class Authority:
        durable_consumption_confirmed: bool
        durable_consumption_grant_sha256: str
        durable_consumption_slot: str

    class ChildBinding:
        mode = "interactive-voice"
        child_effect_review_sha256 = voice.NATIVE08_EFFECT_REVIEW_SHA256
        finite_grant_sha256 = "a" * 64

        def __init__(self, slot):
            self.interactive_slot = slot

        def ready(self, authority=None):
            return (type(authority) is Authority
                    and authority.durable_consumption_confirmed is True
                    and authority.durable_consumption_grant_sha256 ==
                    self.finite_grant_sha256
                    and authority.durable_consumption_slot ==
                    self.interactive_slot)

    module = ModuleType("synthetic_lower_runner")
    module.__file__ = str(voice.CONTAINED_RUNNER_PATH)
    module.ExecutionBinding = ChildBinding
    module.TrustedLaunchAuthority = Authority
    module.CHILD_EFFECT_REVIEW_SHA256 = voice.NATIVE08_EFFECT_REVIEW_SHA256

    def run_once(raw, child, *, launch_authority=None):
        assert child.ready(launch_authority)
        calls.append((raw, child.interactive_slot))
        return "  editable advisory text  "

    module.run_once = run_once
    monkeypatch.setattr(voice, "_matches", lambda path, digest:
                        path == voice.CONTAINED_RUNNER_PATH
                        and digest == voice.CONTAINED_RUNNER_SHA256)
    patient, staff = ChildBinding("patient"), ChildBinding("staff")

    def scope_current(persona):
        return current.get(persona) is True

    def consume_and_authorize(persona, child):
        if not scope_current(persona) or child.interactive_slot != persona:
            raise RuntimeError("synthetic scope or slot mismatch")
        consumed.append(persona)
        return Authority(True, child.finite_grant_sha256, persona)

    binding = (voice._from_reviewed_native_entry(
        module, patient, staff, scope_current, consume_and_authorize)
        if native else voice.ContainedVoiceRuntimeBinding(module, patient, staff))
    return binding, module, current, consumed, calls


def test_native08_alone_does_not_enable_either_persona(monkeypatch):
    binding, _, _, consumed, calls = fixture(monkeypatch, native=False)
    for persona in ("patient", "staff"):
        assert binding.ready(persona) is False
        with pytest.raises(voice.VoiceRecognitionUnavailable):
            voice.run_local_recognizer(synthetic_wav(), binding, persona)
    assert consumed == calls == []


def test_two_persona_slots_are_distinct_and_each_one_use(monkeypatch):
    binding, _, _, consumed, calls = fixture(monkeypatch)
    clip = synthetic_wav()
    for persona in ("patient", "staff"):
        assert binding.ready(persona) is True
        assert voice.run_local_recognizer(clip, binding, persona) == (
            "editable advisory text")
        assert binding.ready(persona) is False
        with pytest.raises(voice.VoiceRecognitionUnavailable):
            voice.run_local_recognizer(clip, binding, persona)
    assert consumed == ["patient", "staff"]
    assert calls == [(clip, "patient"), (clip, "staff")]
    assert binding.ready("unknown") is False


def test_wrong_slot_or_unready_lower_binding_fails_closed(monkeypatch):
    binding, _, _, consumed, calls = fixture(monkeypatch)
    binding.patient_child_binding.interactive_slot = "staff"
    assert binding.ready("patient") is False
    with pytest.raises(voice.VoiceRecognitionUnavailable):
        voice.run_local_recognizer(synthetic_wav(), binding, "patient")
    assert consumed == calls == []

    # Upper readiness does not call child.ready() before an authority exists.
    # The trusted route durably consumes staff, then rejects the unready child
    # before runner invocation. The finite grant is therefore burned safely.
    binding.staff_child_binding.ready = lambda authority=None: False
    assert binding.ready("staff") is True
    with pytest.raises(voice.VoiceRecognitionUnavailable):
        voice.run_local_recognizer(synthetic_wav(), binding, "staff")
    assert consumed == ["staff"]
    assert calls == []


def test_qualification_mode_cannot_use_interactive_slot(monkeypatch):
    binding, _, _, consumed, calls = fixture(monkeypatch)
    binding.patient_child_binding.mode = "child-qualification"
    assert binding.ready("patient") is False
    with pytest.raises(voice.VoiceRecognitionUnavailable):
        voice.run_local_recognizer(synthetic_wav(), binding, "patient")
    assert consumed == calls == []


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
    binding, _, _, consumed, calls = fixture(monkeypatch)

    def failed_lower(*args, **kwargs):
        raise RuntimeError("synthetic lower failure")

    binding.runner_module.run_once = failed_lower
    with pytest.raises(voice.VoiceRecognitionUnavailable):
        voice.run_local_recognizer(synthetic_wav(), binding, "patient")
    assert binding.ready("patient") is False
    assert binding.ready("staff") is True
    assert consumed == ["patient"]
    assert calls == []


def test_default_closed_and_client_forgery_rejected(monkeypatch):
    binding, module, _, consumed, calls = fixture(monkeypatch, native=False)
    forged = module.TrustedLaunchAuthority(True, "a" * 64, "patient")
    assert binding.patient_child_binding.ready(forged) is True
    for persona in ("patient", "staff"):
        with pytest.raises(voice.VoiceRecognitionUnavailable):
            voice.run_local_recognizer(synthetic_wav(), binding, persona)
    assert consumed == calls == []


def test_wrong_persona_and_stale_session_refuse_before_grant(monkeypatch):
    binding, _, current, consumed, calls = fixture(monkeypatch)
    assert binding.ready("unknown") is False
    with pytest.raises(voice.VoiceRecognitionUnavailable):
        voice.run_local_recognizer(synthetic_wav(), binding, "unknown")
    current["patient"] = False
    assert binding.ready("patient") is False
    with pytest.raises(voice.VoiceRecognitionUnavailable):
        voice.run_local_recognizer(synthetic_wav(), binding, "patient")
    assert consumed == calls == []


def test_scope_rechecked_after_claim_before_durable_consumption(monkeypatch):
    binding, _, current, consumed, calls = fixture(monkeypatch)
    original_claim = binding._patient_claim.claim

    def stale_after_claim():
        result = original_claim()
        current["patient"] = False
        return result

    monkeypatch.setattr(binding._patient_claim, "claim", stale_after_claim)
    with pytest.raises(voice.VoiceRecognitionUnavailable):
        voice.run_local_recognizer(synthetic_wav(), binding, "patient")
    assert consumed == calls == []
    assert binding.ready("patient") is False


def test_changed_lower_provenance_or_wrong_slot_refuses(monkeypatch):
    binding, module, _, consumed, calls = fixture(monkeypatch)
    monkeypatch.setattr(voice, "_matches", lambda path, digest: False)
    assert binding.ready("patient") is False
    with pytest.raises(voice.VoiceRecognitionUnavailable):
        voice.run_local_recognizer(synthetic_wav(), binding, "patient")
    assert consumed == calls == []
    monkeypatch.setattr(voice, "_matches", lambda path, digest: True)
    module.__file__ = "changed-lower.py"
    assert binding.ready("patient") is False
    module.__file__ = str(voice.CONTAINED_RUNNER_PATH)
    binding.patient_child_binding.interactive_slot = "staff"
    assert binding.ready("patient") is False


def test_lower_authority_mismatch_fails_without_child_call(monkeypatch):
    binding, module, _, consumed, calls = fixture(monkeypatch)
    capability = binding._native_capability
    capability.consume_and_authorize = lambda persona, child: (
        module.TrustedLaunchAuthority(True, "b" * 64, persona))
    with pytest.raises(voice.VoiceRecognitionUnavailable):
        voice.run_local_recognizer(synthetic_wav(), binding, "patient")
    assert consumed == calls == []
    assert binding.ready("patient") is False