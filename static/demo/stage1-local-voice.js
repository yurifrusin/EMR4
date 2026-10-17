// Local-only, deliberately started dictation. It inserts editable text and
// never submits a request, proposes a booking, or confirms a command.
const MAX_SAMPLES = 12 * 16000;
const targetFor = persona => persona === "patient" ? "patient-words" :
  persona === "staff" ? "move-words" : null;
const scopeOf = session => session && `${session.persona}:${session.csrf}`;

// BEGIN MANUAL_INTENT_HANDOFF_V1: bounded UI state, not semantic verification.
function manualIntentKey(value) {
  const names=["kind","scope","request_id","request_version","appointment_ref","appointment_version","words","fields"];
  if (!value || typeof value!=="object" || Array.isArray(value) ||
      Object.keys(value).sort().join(",")!==names.sort().join(",") ||
      !["request","move"].includes(value.kind) ||
      typeof value.scope!=="string" || !value.scope || value.scope.length>4096 ||
      !value.scope.startsWith(value.kind==="request"?"patient:":"staff:") ||
      value.scope.length<=(value.kind==="request"?8:6) ||
      typeof value.request_id!=="string" || !value.request_id || value.request_id.length>200 ||
      !Number.isSafeInteger(value.request_version) || value.request_version<0 ||
      typeof value.words!=="string" || value.words.length>500 ||
      !value.fields || typeof value.fields!=="object" || Array.isArray(value.fields)) return null;
  const clock=v=>typeof v==="string" && v.length===5 && /^(?:[01]\d|2[0-3]):[0-5]\d$/.test(v);
  const date=v=>typeof v==="string" && v.length===10 && /^\d{4}-\d{2}-\d{2}$/.test(v);
  let fields;
  if (value.kind==="request") {
    if (value.appointment_ref!==null || value.appointment_version!==null ||
        Object.keys(value.fields).sort().join(",")!=="date,earliest_local,latest_local" ||
        !date(value.fields.date) || !clock(value.fields.earliest_local) || !clock(value.fields.latest_local) ||
        value.fields.earliest_local>=value.fields.latest_local) return null;
    fields=[value.fields.date,value.fields.earliest_local,value.fields.latest_local];
  } else {
    if (typeof value.appointment_ref!=="string" || !value.appointment_ref || value.appointment_ref.length>200 ||
        !Number.isSafeInteger(value.appointment_version) || value.appointment_version<0 ||
        Object.keys(value.fields).sort().join(",")!=="date,local_time" ||
        !date(value.fields.date) || !clock(value.fields.local_time)) return null;
    fields=[value.fields.date,value.fields.local_time];
  }
  return JSON.stringify([value.kind,value.scope,value.request_id,value.request_version,
    value.appointment_ref,value.appointment_version,value.words,...fields]);
}
export function createManualIntentHandoff() {
  let revision=0, current=null, acknowledged=null;
  const update=value=>{
    const key=manualIntentKey(value);
    if(key!==current){current=key;acknowledged=null;revision++;}
    return key;
  };
  const matched=value=>{
    const key=update(value);
    return key!==null && (!value.words.trim() || acknowledged===revision);
  };
  return Object.freeze({
    revision:()=>revision,
    invalidate:()=>{acknowledged=null;revision++;},
    inspect:value=>{const key=update(value);return {
      supported:key!==null,required:typeof value?.words==="string"&&Boolean(value.words.trim()),
      acknowledged:key!==null&&acknowledged===revision,revision};},
    acknowledge:value=>{
      if(update(value)===null || !value.words.trim())throw new Error("MAPPING_UNSUPPORTED");
      acknowledged=revision;return revision;
    },
    review:value=>{
      if(!matched(value))throw new Error("MAPPING_REQUIRED");
      return Object.freeze({revision,key:current});
    },
    isReviewCurrent:(value,review)=>matched(value)&&Boolean(review)&&
      review.revision===revision&&review.key===current,
  });
}
function sameVoiceTarget(expected, actual) {
  return typeof expected==="string" && expected.length>0 && expected.length<=4096 &&
    typeof actual==="string" && expected===actual;
}
// END MANUAL_INTENT_HANDOFF_V1

function wavFromPcm(chunks, samples) {
  if (!samples || samples > MAX_SAMPLES) throw new Error("No bounded recording was captured.");
  const bytes = 44 + samples * 2;
  if (bytes > 512 * 1024) throw new Error("The recording is too large.");
  const buffer = new ArrayBuffer(bytes), view = new DataView(buffer);
  const ascii = (offset, value) => [...value].forEach((letter, index) =>
    view.setUint8(offset + index, letter.charCodeAt(0)));
  ascii(0, "RIFF"); view.setUint32(4, bytes - 8, true); ascii(8, "WAVE");
  ascii(12, "fmt "); view.setUint32(16, 16, true); view.setUint16(20, 1, true);
  view.setUint16(22, 1, true); view.setUint32(24, 16000, true);
  view.setUint32(28, 32000, true); view.setUint16(32, 2, true);
  view.setUint16(34, 16, true); ascii(36, "data");
  view.setUint32(40, samples * 2, true);
  let offset = 44;
  for (const chunk of chunks) for (const sample of chunk) {
    view.setInt16(offset, sample, true); offset += 2;
  }
  return new Blob([buffer], { type: "audio/wav" });
}

async function readSession({ signal } = {}) {
  const response = await fetch("/demo/stage1/session",
    { credentials: "same-origin", cache: "no-store", redirect: "error", signal });
  if (!response.ok) throw new Error("The local session changed.");
  return response.json();
}

export function initLocalVoice(getSession, onStart = () => {}, getTarget = () => null, onInvalidate = () => {}, onPhaseChange = () => {}) {
  const button = document.getElementById("voice-toggle");
  const cancelButton = document.getElementById("voice-cancel");
  const note = document.getElementById("voice-note");
  const label = document.getElementById("voice-availability");
  const voiceStatus = message => { note.textContent = message; };
  const voice = { epoch: 0, phase: "idle", capture: null, abort: null };
  const initial = getSession();
  const originScope = scopeOf(initial);
  const target = targetFor(initial?.persona);
  const readTarget=()=>{const value=getTarget();return sameVoiceTarget(value,value)?value:null;};
  const supported = Boolean(navigator.mediaDevices?.getUserMedia && window.AudioContext);
  const available = Boolean(initial?.voice_available && initial?.voice_nonce && target && supported);

  function paint() {
    button.disabled = !available || !readTarget();
    button.textContent = voice.phase === "recording" ? "Stop talking" :
      voice.phase === "requesting" ? "Cancel microphone request" :
      voice.phase === "transcribing" ? "Cancel transcription" : "Start talking";
    cancelButton.hidden = voice.phase === "idle";
    label.textContent = available && readTarget() ? "Local voice bound" : "Voice unavailable · type instead";
    onPhaseChange();
  }
  async function closeCapture(capture) {
    if (!capture) return;
    clearTimeout(capture.timer);
    capture.processor.onaudioprocess = null;
    capture.stream.getTracks().forEach(track => track.stop());
    capture.source.disconnect(); capture.processor.disconnect(); capture.silent.disconnect();
    try { await capture.context.close(); } catch (_) { /* already closed */ }
  }
  function cancel() {
    ++voice.epoch;
    const capture = voice.capture; voice.capture = null;
    voice.abort?.abort(); voice.abort = null;
    voice.phase = "idle";
    void closeCapture(capture);
    onInvalidate();paint();
    voiceStatus("Dictation cancelled. You can type instead.");
  }
  async function finish() {
    if (voice.phase !== "recording" || !voice.capture) return;
    const capture = voice.capture, ticket = capture.ticket;
    voice.capture = null; voice.phase = "transcribing"; paint();
    await closeCapture(capture);
    if (ticket !== voice.epoch || document.hidden || !sameVoiceTarget(capture.selection,readTarget())) {
      if (ticket === voice.epoch) cancel();
      return;
    }
    try {
      const wav = wavFromPcm(capture.chunks, capture.samples);
      const controller = new AbortController(); voice.abort = controller;
      const response = await fetch("/demo/stage1/voice", {
        method: "POST", credentials: "same-origin", cache: "no-store", redirect: "error",
        headers: { "Content-Type": "audio/wav",
          "X-CSRF-Token": capture.csrf, "X-Voice-Nonce": capture.nonce,
          "X-Voice-Target": capture.target },
        body: wav, signal: controller.signal,
      });
      if (!response.ok) throw new Error("Local recognition was unavailable.");
      const result = await response.json();
      const current = await readSession();
      if (ticket !== voice.epoch || document.hidden ||
          scopeOf(current) !== capture.scope ||
          scopeOf(getSession()) !== capture.scope || !sameVoiceTarget(capture.selection,readTarget()) ||
          result.target !== capture.target || typeof result.text !== "string" || result.text.length > 500) {
        if(ticket===voice.epoch)cancel();
        return;
      }
      const field = document.getElementById(capture.target);
      if (!field || field.disabled) return;
      const transcript = result.text.trim();
      if (transcript) {
        field.value = [field.value.trim(), transcript].filter(Boolean).join(" ").slice(0, field.maxLength);
        field.dispatchEvent(new Event("input", { bubbles: true }));
        field.focus();
        voiceStatus("Local transcript added as editable text. Review it before using any action.");
      } else voiceStatus("No words were recognised. Type or try again.");
    } catch (_) {
      if (ticket === voice.epoch && !document.hidden)
        voiceStatus("Local recognition unavailable. Type your request or instruction.");
    } finally {
      if (ticket === voice.epoch) {
        voice.abort = null; voice.phase = "idle"; paint();
      }
    }
  }
  async function start() {
    if (!available || voice.phase !== "idle" || document.hidden) return;
    onStart(); // New input supersedes the old mapped review and spoken reply.
    const selection=readTarget();
    if(!selection)return;
    const ticket = ++voice.epoch;
    voice.phase = "requesting"; paint();
    voiceStatus("Checking local session before asking for microphone permission…");
    let stream, context;
    try {
      const fresh = await readSession();
      if (ticket !== voice.epoch || document.hidden ||
          scopeOf(fresh) !== originScope ||
          scopeOf(getSession()) !== originScope || !sameVoiceTarget(selection,readTarget()) ||
          !fresh.voice_available || !fresh.voice_nonce)
        throw new Error("Local session changed.");
      // This is reached only from a deliberate button action.
      stream = await navigator.mediaDevices.getUserMedia({
        audio: { channelCount: 1, sampleRate: 16000, echoCancellation: true }, video: false,
      });
      if (ticket !== voice.epoch || document.hidden || !sameVoiceTarget(selection,readTarget())) {
        stream.getTracks().forEach(track => track.stop());
        if (ticket === voice.epoch) cancel();
        return;
      }
      context = new AudioContext({ sampleRate: 16000 });
      if (context.sampleRate !== 16000) throw new Error("16 kHz capture is unavailable.");
      await context.resume();
      if (ticket !== voice.epoch || document.hidden || !sameVoiceTarget(selection,readTarget()))
        throw new Error("Dictation was cancelled.");
      const source = context.createMediaStreamSource(stream);
      const processor = context.createScriptProcessor(4096, 1, 1);
      const silent = context.createGain(); silent.gain.value = 0;
      const capture = { ticket, stream, context, source, processor, silent,
        chunks: [], samples: 0, nonce: fresh.voice_nonce, csrf: fresh.csrf,
        scope: originScope, target, selection, timer: null };
      processor.onaudioprocess = event => {
        if (ticket !== voice.epoch || voice.phase !== "recording") return;
        if (document.hidden || !sameVoiceTarget(capture.selection,readTarget())) { cancel(); return; }
        const input = event.inputBuffer.getChannelData(0);
        const take = Math.min(input.length, MAX_SAMPLES - capture.samples);
        const chunk = new Int16Array(take);
        for (let i = 0; i < take; i++) {
          const value = Math.max(-1, Math.min(1, input[i]));
          chunk[i] = value < 0 ? Math.round(value * 32768) : Math.round(value * 32767);
        }
        capture.chunks.push(chunk); capture.samples += take;
        if (capture.samples >= MAX_SAMPLES) void finish();
      };
      source.connect(processor); processor.connect(silent); silent.connect(context.destination);
      voice.capture = capture; voice.phase = "recording"; paint();
      capture.timer = setTimeout(() => void finish(), 12000);
      stream.getTracks().forEach(track => track.addEventListener("ended", () => {
        if (voice.capture === capture) cancel();
      }));
      voiceStatus("Recording locally. Press Stop talking; capture ends after 12 seconds.");
    } catch (_) {
      if (stream) stream.getTracks().forEach(track => track.stop());
      if (context) try { await context.close(); } catch (_) { /* already closed */ }
      if (ticket === voice.epoch) {
        voice.phase = "idle"; paint();
        voiceStatus("Microphone or local capture unavailable. Type instead.");
      }
    }
  }

  button.addEventListener("click", () => {
    if (voice.phase === "idle") void start();
    else if (voice.phase === "recording") void finish();
    else cancel();
  });
  cancelButton.addEventListener("click", cancel);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden && voice.phase !== "idle") cancel();
  });
  window.addEventListener("pagehide", cancel);
  paint();
  if (available) voiceStatus("Start talking requests microphone permission. Transcript stays editable; nothing is submitted automatically.");
  return Object.freeze({isIdle:()=>voice.phase==="idle",invalidateTarget:()=>{
    if(voice.phase!=="idle")cancel();else paint();
  }});
}

// A browser voice is not qualified by being installed, marked default, or
// bearing a familiar name. A separate browser/profile/offline review must pin
// this exact identity before a source successor can enable output.
const QUALIFIED_LOCAL_SPEECH_VOICE = null;
const SPEECH_CHECK_MS = 1000;
const SPEECH_CHECK_TIMEOUT_MS = 750;
const SPEECH_MAX_MS = 15000;
const SPEECH_MAX_CHECKS = 15;

export function initSpokenReply(getSession) {
  const button = document.getElementById("spoken-reply");
  const note = document.getElementById("spoken-availability");
  const synth = window.speechSynthesis;
  let epoch = 0, offered = null, current = null, watch = null;
  const originalScope = scopeOf(getSession());
  const identity = QUALIFIED_LOCAL_SPEECH_VOICE;
  const selectedVoice = () => {
    if (!identity || !synth || typeof SpeechSynthesisUtterance !== "function") return null;
    if (!identity.voiceURI || !identity.name || !identity.lang) return null;
    try {
      const matches = synth.getVoices().filter(voice =>
        voice.localService === true && voice.voiceURI === identity.voiceURI &&
        voice.name === identity.name && voice.lang === identity.lang);
      return matches.length === 1 ? matches[0] : null;
    } catch (_) { return null; }
  };
  function paint() {
    button.disabled = !offered || !selectedVoice() || document.hidden ||
      scopeOf(getSession()) !== originalScope;
    note.textContent = selectedVoice() ?
      "Spoken replies available. Choose Speak verified reply to hear this result." :
      "Spoken replies unavailable. Read the reply here.";
  }
  function disposeWatch() {
    const old = watch; watch = null;
    if (!old) return;
    clearInterval(old.interval); clearTimeout(old.deadline);
    clearTimeout(old.timeout); old.abort?.abort();
  }
  function stop() {
    ++epoch; offered = null;
    disposeWatch();
    if (synth && current) synth.cancel();
    current = null; paint();
  }
  function offer(message) {
    stop();
    if (typeof message !== "string" || !message || message.length > 240 ||
        scopeOf(getSession()) !== originalScope || document.hidden) return;
    offered = { message, scope: originalScope }; paint();
  }
  async function checkActive(ticket, requested) {
    if (ticket !== epoch || !current || !watch) return;
    if (document.hidden || scopeOf(getSession()) !== requested.scope ||
        document.getElementById("status").textContent !== requested.message) {
      stop(); return;
    }
    if (watch.pending) return;
    if (++watch.checks > SPEECH_MAX_CHECKS) { stop(); return; }
    const owner = watch, controller = new AbortController();
    owner.pending = true; owner.abort = controller;
    owner.timeout = setTimeout(() => controller.abort(), SPEECH_CHECK_TIMEOUT_MS);
    try {
      const session = await readSession({ signal: controller.signal });
      if (ticket !== epoch || watch !== owner) return;
      if (document.hidden || scopeOf(session) !== requested.scope ||
          scopeOf(getSession()) !== requested.scope ||
          document.getElementById("status").textContent !== requested.message)
        stop();
    } catch (_) {
      if (ticket === epoch && watch === owner) stop();
    } finally {
      clearTimeout(owner.timeout);
      if (ticket === epoch && watch === owner) {
        owner.timeout = null; owner.abort = null; owner.pending = false;
      }
    }
  }
  async function speak() {
    if (button.disabled || current) return;
    if (!offered || document.hidden || scopeOf(getSession()) !== originalScope) {
      stop(); return;
    }
    const ticket = ++epoch, requested = offered;
    button.disabled = true;
    try {
      const session = await readSession();
      if (ticket !== epoch || document.hidden ||
          scopeOf(session) !== requested.scope ||
          scopeOf(getSession()) !== requested.scope ||
          document.getElementById("status").textContent !== requested.message) {
        stop(); return;
      }
      const voice = selectedVoice();
      if (!voice) { stop(); return; }
      const utterance = new SpeechSynthesisUtterance(requested.message);
      utterance.voice = voice; utterance.lang = voice.lang;
      utterance.onend = utterance.onerror = () => {
        if (ticket === epoch && current === utterance) {
          ++epoch; disposeWatch(); current = null; paint();
        }
      };
      if (ticket !== epoch || document.hidden ||
          document.getElementById("status").textContent !== requested.message) {
        stop(); return;
      }
      current = utterance; synth.speak(utterance);
      if (ticket !== epoch || current !== utterance) return;
      watch = { interval: null, deadline: null, timeout: null,
        abort: null, pending: false, checks: 0 };
      watch.interval = setInterval(() => { void checkActive(ticket, requested); }, SPEECH_CHECK_MS);
      watch.deadline = setTimeout(() => { if (ticket === epoch) stop(); }, SPEECH_MAX_MS);
    } catch (_) { if (ticket === epoch) stop(); }
  }
  button.addEventListener("click", () => { void speak(); });
  document.addEventListener("visibilitychange", () => { if (document.hidden) stop(); else paint(); });
  window.addEventListener("pagehide", stop);
  document.addEventListener("input", stop);
  if (synth) synth.addEventListener?.("voiceschanged", paint);
  paint();
  return { offer, stop };
}
