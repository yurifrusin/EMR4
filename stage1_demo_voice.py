"""Bounded local WAV recognition bridge for the isolated Stage 1 demo.

This module contains no model import and makes no voice runtime available by
itself. A separately reviewed trusted harness must provide actual installation,
model and execution receipts before a VoiceRuntimeBinding can become ready.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import threading
from types import ModuleType
import wave


MAX_WAV_BYTES = 512 * 1024
MAX_FRAMES = 12 * 16_000
RECOGNIZER_SOURCE_SHA256 = "c936effb8b1180cbc8d68b9d59bdf19114c9a82799de60bfc1628de0af27940a"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
RUNTIME_ROOT = Path("C:/Users/there/EMR4-tools/stage1-offline-voice-runtime-v1")
PYTHON_PATH = RUNTIME_ROOT / "venv/Scripts/python.exe"
MODEL_ROOT = Path("C:/Users/there/EMR4-tools/stage1-offline-voice-model-v1/vosk-model-small-en-us-0.15")
PYTHON_SHA256 = "6285074735b3738a051bccbe944679268cf9b988832b4cfd1090752eb082f7e2"
PYVENV_CFG_SHA256 = "1af62a1b27a98ba36095ca9c2998d983eaf0c9abb735a9cd9123075e886a3581"
INSTALL_RESULT_SHA256 = "b2ad3b03931755d94fe832e719e1b5371bbb8c22b2cc00e549ebe6e881391854"
MODEL_RESULT_SHA256 = "a45b6e8ef1dbee94d5931be31895e436300538374892ead513c543f785faa31d"
# An independently accepted child-execution receipt is not available. A later
# reviewed source amendment must pin it explicitly before ready() can succeed.
EXECUTION_ACCEPTANCE_SHA256: str | None = None
# Native08 accepted one generated-silence child and its cleanup. Interactive
# clips still need their own reviewed source, execution and finite grant.
NATIVE08_EFFECT_REVIEW_SHA256 = "818f7069444cdbed12c5baf1608bb4ccfa44b936b5db7e33182fad7af1b3b1c2"
CONTAINED_RUNNER_PATH = Path("C:/Users/there/EMR4-migration/20260911-v1/current-control-repair-20260912-v1/demo-led-stage1-20261012-v2/stage1-voice-external-binding-source-v2/run_container_child_once.py")
CONTAINED_RUNNER_SHA256 = "9d389874d11223323f3ea9c31cc87e30ab1611f8b1f815820ca9d8aa44a264b5"
SELECTED_RECOGNIZER_PATH = Path("C:/Users/there/EMR4-migration/20260911-v1/current-control-repair-20260912-v1/demo-led-stage1-20261012-v2/stage1-offline-voice-preparation-v1/recognize_wav.py")
NATIVE_FILES = (
    ("vosk/libgcc_s_seh-1.dll", "201bf8a54ebb490f93ea4beb20740a483bf67036b90b5720f32d0c746a72d1e9"),
    ("vosk/libstdc++-6.dll", "a1d96a848a567d7657e152cfe92e2fd62da412968cc11ec8bdb04bf20ebc5747"),
    ("vosk/libvosk.dll", "9331c2f6a32cf77141af27c9750e79532718f51bbc2e3cea3c60f14ca4251e4e"),
    ("vosk/libwinpthread-1.dll", "92caeb8a4ea281c674003462a233f3b445b685b0a6f93eb11254feda2dda9cde"),
    ("_cffi_backend.cp312-win_amd64.pyd", "9af5e4f68a41f26b726f2e9424f9d58a4f5666189f6a48be95f406b257102aec"),
)
MODEL_FILES = (
    ("README", "c0cf286e4f7783306c5f6469b37db69228fb16803b03cae661edb2d7bba64ebb"),
    ("am/final.mdl", "75370a0137f9daf8f469dedd7daa4513ae7a621f03240c6e512e2b50b656a7b6"),
    ("conf/mfcc.conf", "1e2228006d01d805ad1c267fee9f79709ca87ac51bd82b0e3f5c69ba543f0fc4"),
    ("conf/model.conf", "8f14cb1eeb07c762c371db648c6be688d347236155ca0f64fb13b6567a8ce81f"),
    ("graph/Gr.fst", "023c8b7e30704a9e37765c635c252e608a02f361235bf94abdcf2a5225d85b20"),
    ("graph/HCLr.fst", "5caafba3081e1646545ac6bff0dd7a318e53dcbdc86f237909ce1d2ac1293d34"),
    ("graph/disambig_tid.int", "9ad87cc166d0998f08f758f47a6223a120dfffcbee805c4849c3aa5e6bb3c0fc"),
    ("graph/phones/word_boundary.int", "da199d9c991e0e84681ddbb34627b915b26302d50a8fdaa23c51e2bc3a50b5c3"),
    ("ivector/final.dubm", "8c5d7dd69d2122313baaf19f61f35dd3fa18b70c62ac0687e311e1c46e6daca7"),
    ("ivector/final.ie", "3f37faf90c375b9e4740b569398b5829ed9cc07d19be6d441f72c3b71d7efcc6"),
    ("ivector/final.mat", "ddd83586dc5f928cda8738b922c85ffe38fc789cb5f9151a712ca12f37265382"),
    ("ivector/global_cmvn.stats", "33be09afcc80059847a275c3d043b51f1ab954c7c2438ddbbf4745e8ba144ff9"),
    ("ivector/online_cmvn.conf", "a2f3571754b64297cb7efb2e7ca3df61995c5a45fcbb97188f90613552bb2dfe"),
    ("ivector/splice.conf", "9f0c5f7c82d18eaf25d8bce470efa9f7741f88411fe428774bc0a9bb69a24756"),
)


def _matches(path: Path, digest: str) -> bool:
    return path.is_file() and not path.is_symlink() and hashlib.sha256(path.read_bytes()).hexdigest() == digest


class VoiceInputRejected(ValueError):
    pass


class VoiceRecognitionUnavailable(RuntimeError):
    pass


class _OneClipClaim:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._used = False

    def available(self) -> bool:
        with self._lock:
            return not self._used

    def claim(self) -> bool:
        with self._lock:
            if self._used:
                return False
            self._used = True
            return True


@dataclass(frozen=True, repr=False)
class VoiceRuntimeBinding:
    python_executable: Path
    recognizer_script: Path
    model_root: Path
    temporary_root: Path
    installation_receipt_sha256: str
    model_receipt_sha256: str
    execution_acceptance_sha256: str

    def ready(self) -> bool:
        # Installed files are known, but child execution and voice activation
        # remain closed until a later independently reviewed source amendment.
        if (EXECUTION_ACCEPTANCE_SHA256 is None
                or self.installation_receipt_sha256 != INSTALL_RESULT_SHA256
                or self.model_receipt_sha256 != MODEL_RESULT_SHA256
                or self.execution_acceptance_sha256 != EXECUTION_ACCEPTANCE_SHA256):
            return False
        try:
            if (not all(isinstance(path, Path) for path in (
                    self.python_executable, self.recognizer_script,
                    self.model_root, self.temporary_root))
                    or not self.python_executable.is_file() or not self.recognizer_script.is_file()
                    or not self.model_root.is_dir() or not self.temporary_root.is_dir()
                    or self.model_root.is_symlink() or self.temporary_root.is_symlink()):
                return False
            if (self.python_executable.resolve() != PYTHON_PATH.resolve()
                    or self.recognizer_script.resolve() != SELECTED_RECOGNIZER_PATH.resolve()
                    or self.model_root.resolve() != MODEL_ROOT.resolve()
                    or not self.temporary_root.resolve().is_relative_to(RUNTIME_ROOT.resolve())
                    or self.temporary_root.resolve() == RUNTIME_ROOT.resolve()):
                return False
            site = RUNTIME_ROOT / "venv/Lib/site-packages"
            return (all(_matches(path, digest) for path, digest in (
                (PYTHON_PATH, PYTHON_SHA256),
                (RUNTIME_ROOT / "venv/pyvenv.cfg", PYVENV_CFG_SHA256),
                (SELECTED_RECOGNIZER_PATH, RECOGNIZER_SOURCE_SHA256),
            )) and all(_matches(site / name, digest) for name, digest in NATIVE_FILES)
                and all(_matches(MODEL_ROOT / name, digest) for name, digest in MODEL_FILES))
        except (OSError, ValueError):
            return False


_NATIVE_ISSUER = object()


class _TrustedNativeVoiceCapability:
    """Process-local capability installed only by the reviewed native entry.

    The callbacks must verify the live session and durably consume the named
    grant slot before returning a lower TrustedLaunchAuthority. This class
    cannot authenticate its own installer; it is never exposed to HTTP data.
    """

    __slots__ = ("scope_current", "consume_and_authorize", "_issuer")

    def __init__(self, scope_current, consume_and_authorize, issuer):
        if (issuer is not _NATIVE_ISSUER or not callable(scope_current)
                or not callable(consume_and_authorize)):
            raise VoiceRecognitionUnavailable("VOICE_RUNTIME_UNQUALIFIED")
        self.scope_current = scope_current
        self.consume_and_authorize = consume_and_authorize
        self._issuer = issuer


def _from_reviewed_native_entry(runner_module: ModuleType,
                                patient_child_binding: object,
                                staff_child_binding: object,
                                scope_current,
                                consume_and_authorize):
    """Native-only configuration seam; external review must authenticate caller.

    The caller validates exact upper/lower source, imported module and callable,
    independent reviews, finite grant, Native08, and durable two-slot checkpoint.
    No HTTP field or caller-constructed ExecutionBinding proves those facts.
    """
    capability = _TrustedNativeVoiceCapability(
        scope_current, consume_and_authorize, _NATIVE_ISSUER)
    return ContainedVoiceRuntimeBinding(
        runner_module, patient_child_binding, staff_child_binding, capability)


@dataclass(frozen=True, repr=False)
class ContainedVoiceRuntimeBinding:
    """Default-closed bridge to the exact reviewed V2 lower runner."""

    runner_module: ModuleType
    patient_child_binding: object
    staff_child_binding: object
    _native_capability: _TrustedNativeVoiceCapability | None = None
    _patient_claim: _OneClipClaim = field(default_factory=_OneClipClaim, init=False,
                                          repr=False, compare=False)
    _staff_claim: _OneClipClaim = field(default_factory=_OneClipClaim, init=False,
                                        repr=False, compare=False)

    def slot(self, persona: str) -> tuple[object, _OneClipClaim] | None:
        if persona == "patient":
            return self.patient_child_binding, self._patient_claim
        if persona == "staff":
            return self.staff_child_binding, self._staff_claim
        return None

    def ready(self, persona: str) -> bool:
        selected = self.slot(persona)
        capability = self._native_capability
        if (selected is None or not selected[1].available()
                or type(capability) is not _TrustedNativeVoiceCapability
                or capability._issuer is not _NATIVE_ISSUER):
            return False
        try:
            module = self.runner_module
            child = selected[0]
            return (type(module) is ModuleType and
                    Path(module.__file__) == CONTAINED_RUNNER_PATH and
                    _matches(CONTAINED_RUNNER_PATH, CONTAINED_RUNNER_SHA256) and
                    type(child) is module.ExecutionBinding and
                    child.mode == "interactive-voice" and
                    child.interactive_slot == persona and
                    child.child_effect_review_sha256 == NATIVE08_EFFECT_REVIEW_SHA256 and
                    module.CHILD_EFFECT_REVIEW_SHA256 == NATIVE08_EFFECT_REVIEW_SHA256 and
                    self.patient_child_binding.finite_grant_sha256 ==
                    self.staff_child_binding.finite_grant_sha256 and
                    callable(module.run_once) and
                    capability.scope_current(persona) is True)
        except (AttributeError, OSError, TypeError, ValueError, RuntimeError):
            return False


def target_for_persona(persona: str) -> str | None:
    return {"patient": "patient-words", "staff": "move-words"}.get(persona)


def validate_wav(raw: bytes) -> None:
    if (not isinstance(raw, bytes) or not 44 <= len(raw) <= MAX_WAV_BYTES
            or raw[:4] != b"RIFF" or raw[8:12] != b"WAVE"
            or int.from_bytes(raw[4:8], "little") + 8 != len(raw)):
        raise VoiceInputRejected("WAV_INVALID")
    try:
        with wave.open(io.BytesIO(raw), "rb") as audio:
            if (audio.getnchannels() != 1 or audio.getsampwidth() != 2
                    or audio.getframerate() != 16_000 or audio.getcomptype() != "NONE"
                    or not 1 <= audio.getnframes() <= MAX_FRAMES
                    or len(audio.readframes(MAX_FRAMES + 1)) != audio.getnframes() * 2):
                raise VoiceInputRejected("WAV_FORMAT_INVALID")
    except (wave.Error, EOFError) as exc:
        raise VoiceInputRejected("WAV_INVALID") from exc


def run_local_recognizer(raw: bytes,
                         binding: VoiceRuntimeBinding | ContainedVoiceRuntimeBinding,
                         persona: str | None = None) -> str:
    validate_wav(raw)
    if isinstance(binding, ContainedVoiceRuntimeBinding):
        selected = binding.slot(persona) if isinstance(persona, str) else None
        if selected is None or not binding.ready(persona) or not selected[1].claim():
            raise VoiceRecognitionUnavailable("VOICE_RUNTIME_UNQUALIFIED")
        try:
            # The native callback alone establishes the reviewed launch and
            # durable named-slot consumption before any lower child effect.
            capability = binding._native_capability
            if (type(capability) is not _TrustedNativeVoiceCapability
                    or capability.scope_current(persona) is not True):
                raise VoiceRecognitionUnavailable("VOICE_RUNTIME_UNQUALIFIED")
            authority = capability.consume_and_authorize(persona, selected[0])
            module = binding.runner_module
            if (type(authority) is not module.TrustedLaunchAuthority
                    or authority.durable_consumption_confirmed is not True
                    or authority.durable_consumption_slot != persona
                    or authority.durable_consumption_grant_sha256 !=
                       selected[0].finite_grant_sha256
                    or selected[0].ready(authority) is not True):
                raise VoiceRecognitionUnavailable("VOICE_RUNTIME_UNQUALIFIED")
            # run_once returns only after its owned child has exited and the
            # exact container cleanup is verified. Its text is advisory.
            transcript = module.run_once(
                raw, selected[0], launch_authority=authority)
        except (AttributeError, OSError, TypeError, ValueError, RuntimeError) as exc:
            raise VoiceRecognitionUnavailable("VOICE_RECOGNITION_UNAVAILABLE") from exc
        if not isinstance(transcript, str) or len(transcript) > 500:
            raise VoiceRecognitionUnavailable("VOICE_RESULT_UNAVAILABLE")
        return transcript.strip()
    if not isinstance(binding, VoiceRuntimeBinding):
        raise VoiceRecognitionUnavailable("VOICE_RUNTIME_UNQUALIFIED")
    if not binding.ready():
        raise VoiceRecognitionUnavailable("VOICE_RUNTIME_UNQUALIFIED")
    system_root = os.environ.get("SystemRoot")
    if not system_root:
        raise VoiceRecognitionUnavailable("VOICE_RUNTIME_UNAVAILABLE")
    with tempfile.TemporaryDirectory(prefix="stage1-voice-", dir=binding.temporary_root) as owned:
        wav_path = Path(owned) / "input.wav"
        output_path = Path(owned) / "result.json"
        wav_path.write_bytes(raw)
        env = {"SystemRoot": system_root, "PYTHONNOUSERSITE": "1", "PYTHONUTF8": "1",
               "TEMP": owned, "TMP": owned,
               "PATH": os.pathsep.join((str(binding.python_executable.parent),
                                       str(Path(system_root) / "System32")))}
        try:
            with output_path.open("wb") as output:
                result = subprocess.run(
                    [str(binding.python_executable), str(binding.recognizer_script),
                     "--model", str(binding.model_root), "--wav", str(wav_path)],
                    stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.DEVNULL,
                    env=env, timeout=25, check=False, shell=False,
                )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise VoiceRecognitionUnavailable("VOICE_RECOGNITION_UNAVAILABLE") from exc
        if result.returncode != 0 or output_path.stat().st_size > 4096:
            raise VoiceRecognitionUnavailable("VOICE_RECOGNITION_UNAVAILABLE")
        try:
            result_data = json.loads(output_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise VoiceRecognitionUnavailable("VOICE_RESULT_UNAVAILABLE") from exc
        transcript = result_data.get("text") if isinstance(result_data, dict) else None
        if not isinstance(transcript, str) or len(transcript) > 500:
            raise VoiceRecognitionUnavailable("VOICE_RESULT_UNAVAILABLE")
        return transcript.strip()
