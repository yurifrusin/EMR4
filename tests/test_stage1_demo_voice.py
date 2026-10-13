"""Authored mock-only local voice seam tests; no model, microphone or browser run."""

from dataclasses import replace
import base64
import io
from pathlib import Path
import shutil
import subprocess
import wave

import httpx
import pytest

import stage1_demo_http
from stage1_demo_http import create_stage1_demo_app
import stage1_demo_voice
from stage1_demo_voice import (VoiceInputRejected, VoiceRecognitionUnavailable,
                               VoiceRuntimeBinding, run_local_recognizer, validate_wav)
from test_stage1_demo_http import REQ_A, REQ_B, bridge_case


def _wav(*, channels=1, rate=16000, frames=160) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as writer:
        writer.setnchannels(channels)
        writer.setsampwidth(2)
        writer.setframerate(rate)
        writer.writeframes(b"\0\0" * frames * channels)
    return buffer.getvalue()


def _binding() -> VoiceRuntimeBinding:
    return VoiceRuntimeBinding(
        python_executable=Path("uninstalled/python.exe"),
        recognizer_script=Path("uninstalled/recognize_wav.py"),
        model_root=Path("uninstalled/model"),
        temporary_root=Path("uninstalled/temp"),
        installation_receipt_sha256="", model_receipt_sha256="",
        execution_acceptance_sha256="",
    )


def test_voice_binding_closed_without_actual_runtime_receipts():
    assert _binding().ready() is False


def test_accepted_install_and_model_pins_still_cannot_activate_voice():
    """Source-only default closure; this does not execute the installed child."""
    assert len(stage1_demo_voice.NATIVE_FILES) == 5
    assert len(stage1_demo_voice.MODEL_FILES) == 14
    assert stage1_demo_voice.EXECUTION_ACCEPTANCE_SHA256 is None
    binding = replace(_binding(),
        python_executable=stage1_demo_voice.PYTHON_PATH,
        recognizer_script=stage1_demo_voice.SELECTED_RECOGNIZER_PATH,
        model_root=stage1_demo_voice.MODEL_ROOT,
        installation_receipt_sha256=stage1_demo_voice.INSTALL_RESULT_SHA256,
        model_receipt_sha256=stage1_demo_voice.MODEL_RESULT_SHA256,
        execution_acceptance_sha256="0" * 64)
    assert binding.ready() is False


@pytest.mark.parametrize("raw", [
    b"", b"not a wav", _wav(channels=2), _wav(rate=8000),
    _wav(frames=12 * 16000 + 1), b"x" * (512 * 1024 + 1),
])
def test_voice_rejects_unbounded_or_wrong_pcm(raw):
    with pytest.raises(VoiceInputRejected):
        validate_wav(raw)


@pytest.mark.parametrize("child_timeout", [False, True])
def test_mock_child_cleans_owned_audio_and_transcript(tmp_path, monkeypatch, child_timeout):
    binding = replace(_binding(), temporary_root=tmp_path)
    monkeypatch.setattr(VoiceRuntimeBinding, "ready", lambda self: True)
    monkeypatch.setenv("SystemRoot", str(tmp_path))

    def fake_child(argv, **kwargs):
        assert argv[1].endswith("recognize_wav.py")
        assert Path(argv[-1]).is_file()
        if child_timeout:
            raise subprocess.TimeoutExpired(argv, 25)
        kwargs["stdout"].write(b'{"text":"follow up"}')
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(stage1_demo_voice.subprocess, "run", fake_child)
    if child_timeout:
        with pytest.raises(VoiceRecognitionUnavailable):
            run_local_recognizer(_wav(), binding)
    else:
        assert run_local_recognizer(_wav(), binding) == "follow up"
    assert list(tmp_path.iterdir()) == []


@pytest.mark.anyio
async def test_voice_endpoint_session_nonce_role_and_wav_are_bounded(bridge_case, monkeypatch):
    _, _, config, *_ = bridge_case
    calls = []
    # Mock only the future qualified runtime and recognizer. This is not a
    # source claim that installation, model inference or voice is accepted.
    monkeypatch.setattr(VoiceRuntimeBinding, "ready", lambda self: True)
    monkeypatch.setattr(stage1_demo_http, "run_local_recognizer",
                        lambda raw, binding: calls.append(raw) or "next Thursday")
    app, issuer = create_stage1_demo_app(replace(config, voice_runtime=_binding()))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53200)), base_url="http://127.0.0.1:8765") as client:
        patient_cookie = dict([issuer.cookie_for("patient", REQ_B)])
        other_cookie = dict([issuer.cookie_for("patient", REQ_A)])
        staff_cookie = dict([issuer.cookie_for("staff", REQ_A)])
        session = (await client.get("/demo/stage1/session", cookies=patient_cookie)).json()
        assert session["voice_available"] is True
        headers = {"Origin": "http://127.0.0.1:8765", "Content-Type": "audio/wav",
                   "X-CSRF-Token": session["csrf"], "X-Voice-Nonce": session["voice_nonce"],
                   "X-Voice-Target": "patient-words"}
        wrong_scope = await client.post("/demo/stage1/voice", cookies=other_cookie,
                                        headers=headers, content=_wav())
        assert wrong_scope.status_code == 403 and calls == []
        wrong_origin = await client.post("/demo/stage1/voice", cookies=patient_cookie,
            headers={**headers, "Origin": "http://wrong.example"}, content=_wav())
        assert wrong_origin.status_code == 403 and calls == []
        bad_audio = await client.post("/demo/stage1/voice", cookies=patient_cookie,
                                      headers=headers, content=_wav(rate=8000))
        assert bad_audio.status_code == 400 and calls == []
        fresh = (await client.get("/demo/stage1/session", cookies=patient_cookie)).json()
        headers["X-Voice-Nonce"] = fresh["voice_nonce"]
        accepted = await client.post("/demo/stage1/voice", cookies=patient_cookie,
                                     headers=headers, content=_wav())
        assert accepted.status_code == 200 and accepted.json() == {
            "text": "next Thursday", "target": "patient-words"}
        assert calls == [_wav()]
        replay = await client.post("/demo/stage1/voice", cookies=patient_cookie,
                                   headers=headers, content=_wav())
        assert replay.status_code == 403 and len(calls) == 1
        staff_session = (await client.get("/demo/stage1/session", cookies=staff_cookie)).json()
        staff_headers = {"Origin": "http://127.0.0.1:8765", "Content-Type": "audio/wav",
                         "X-CSRF-Token": staff_session["csrf"],
                         "X-Voice-Nonce": staff_session["voice_nonce"],
                         "X-Voice-Target": "patient-words"}
        wrong_role = await client.post("/demo/stage1/voice", cookies=staff_cookie,
                                       headers=staff_headers, content=_wav())
        assert wrong_role.status_code == 403 and len(calls) == 1


@pytest.mark.anyio
async def test_voice_disabled_default_never_calls_recognizer(bridge_case, monkeypatch):
    app, issuer, *_ = bridge_case
    monkeypatch.setattr(stage1_demo_http, "run_local_recognizer",
                        lambda raw, binding: pytest.fail("recognizer was called"))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,
            client=("127.0.0.1", 53201)), base_url="http://127.0.0.1:8765") as client:
        cookie = dict([issuer.cookie_for("patient", REQ_B)])
        session = (await client.get("/demo/stage1/session", cookies=cookie)).json()
        assert session["voice_available"] is False and session["voice_nonce"] is None
        response = await client.post("/demo/stage1/voice", cookies=cookie,
            headers={"Origin": "http://127.0.0.1:8765", "Content-Type": "audio/wav"},
            content=_wav())
        assert response.status_code == 503


def test_mock_browser_hidden_lifecycle_discards_audio_and_late_text():
    """Authored Node DOM/media mock; no real browser, mic, model or voice proof."""
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for the future mock lifecycle source test")
    source = (Path(__file__).resolve().parents[1] / "static" / "demo" /
              "stage1-local-voice.js").read_bytes()
    module_url = "data:text/javascript;base64," + base64.b64encode(source).decode("ascii")
    mock = r"""
import assert from "node:assert/strict";
const {initLocalVoice} = await import(process.argv[1]);
const tick = () => new Promise(resolve => setImmediate(resolve));
const defer = () => {
  let resolve;
  const promise = new Promise(done => { resolve = done; });
  return {promise, resolve};
};
function harness() {
  const permission = defer(), recognition = defer(), events = {};
  const track = {stops: 0, stop() {this.stops++;}, addEventListener() {}};
  const stream = {getTracks: () => [track]};
  const elements = Object.fromEntries(
    ["voice-toggle", "voice-cancel", "voice-note", "voice-availability", "patient-words"]
      .map(id => [id, {id, hidden:false, disabled:false, textContent:"", value:"",
        maxLength:500, events:0, listeners:{},
        addEventListener(name, handler) {this.listeners[name] = handler;},
        dispatchEvent() {this.events++;}, focus() {}}]));
  const contexts = [];
  class Context {
    constructor() { this.sampleRate = 16000; this.destination = {}; this.closed = false;
      this.processor = null; contexts.push(this); }
    async resume() {}
    async close() {this.closed = true;}
    createMediaStreamSource() {return {connect(){}, disconnect(){}};}
    createScriptProcessor() {this.processor = {onaudioprocess:null, connect(){}, disconnect(){}};
      return this.processor;}
    createGain() {return {gain:{value:0}, connect(){}, disconnect(){}};}
  }
  const session = {persona:"patient", csrf:"scope-a", voice_available:true, voice_nonce:"nonce-a"};
  const calls = {mic:0, voice:0, other:0};
  globalThis.document = {hidden:false, getElementById:id=>elements[id],
    addEventListener:(name,handler)=>{events[name]=handler;}};
  globalThis.window = {AudioContext:Context, addEventListener:(name,handler)=>{events[name]=handler;}};
  globalThis.AudioContext = Context;
  Object.defineProperty(globalThis, "navigator", {configurable:true,
    value:{mediaDevices:{getUserMedia:()=>{calls.mic++;return permission.promise;}}}});
  globalThis.fetch = async url => {
    if (url === "/demo/stage1/session") return {ok:true, json:async()=>session};
    if (url === "/demo/stage1/voice") {calls.voice++; return recognition.promise;}
    calls.other++; throw Error("Unexpected command request");
  };
  globalThis.Event = class {};
  initLocalVoice(() => session);
  return {permission, recognition, events, elements, track, stream, contexts, calls,
    click:()=>elements["voice-toggle"].listeners.click(),
    hide:()=>{document.hidden=true;events.visibilitychange();},
    show:()=>{document.hidden=false;events.visibilitychange();}};
}

// Switching tabs during capture immediately stops the track and processor;
// returning to the tab does not start another recording.
{
  const h=harness(); h.click(); await tick();
  h.permission.resolve(h.stream); await tick(); await tick();
  assert.equal(h.calls.mic, 1);
  assert.ok(h.contexts[0].processor.onaudioprocess);
  h.hide(); await tick();
  assert.ok(h.track.stops >= 1);
  assert.equal(h.contexts[0].processor.onaudioprocess, null);
  assert.equal(h.contexts[0].closed, true);
  h.show(); await tick();
  assert.equal(h.calls.mic, 1); assert.equal(h.calls.voice, 0);
}

// Permission may resolve only after the tab is hidden. Its late stream is
// stopped without creating a context or starting capture.
{
  const h=harness(); h.click(); await tick();
  h.hide(); h.permission.resolve(h.stream); await tick(); await tick();
  assert.ok(h.track.stops >= 1);
  assert.equal(h.contexts.length, 0);
  assert.equal(h.calls.voice, 0);
  h.show(); await tick(); assert.equal(h.calls.mic, 1);
}

// A recognition reply that arrives after hiding cannot insert text or trigger
// an appointment command, even if the mock ignores request abort.
{
  const h=harness(); h.click(); await tick();
  h.permission.resolve(h.stream); await tick(); await tick();
  h.contexts[0].processor.onaudioprocess(
    {inputBuffer:{getChannelData:()=>new Float32Array(160)}});
  h.click(); await tick(); await tick();
  assert.equal(h.calls.voice, 1);
  h.hide();
  h.recognition.resolve({ok:true, json:async()=>({text:"private late words", target:"patient-words"})});
  await tick(); await tick();
  assert.equal(h.elements["patient-words"].value, "");
  assert.equal(h.elements["patient-words"].events, 0);
  assert.ok(h.track.stops >= 1);
  assert.equal(h.calls.other, 0);
}
"""
    subprocess.run([node, "--input-type=module", "-e", mock, module_url],
                   check=True, capture_output=True, text=True, timeout=15)
