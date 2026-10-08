"use strict";

// Complete taskpane source, synthetic in-memory collaborators, no browser,
// network, Office, device, application/database imports, or real storage.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const sourcePath = path.resolve(process.argv[2] || "");
if (!process.argv[2]) throw new Error("Pass the exact taskpane source path");
const source = fs.readFileSync(sourcePath, "utf8");
const authority = [
  "provider_authority", "backend_authority", "credential_authority",
  "microphone_authority", "command_authority", "document_write_authority",
  "production_authority",
];
function policy(mode = "public_https_development", origin = "https://fixture.a.run.app") {
  return Object.assign({
    contract_version: "raisa.public-hosting-policy.v1", mode,
    data_class: mode === "disabled" ? "none" : "authored_synthetic",
    expected_origin: mode === "disabled" ? "" : origin,
  }, Object.fromEntries(authority.map(key => [key, false])));
}
function createHarness(options = {}) {
  const location = new URL(options.origin || "https://fixture.a.run.app");
  location.search = options.search || "";
  const observed = {
    fetch: 0, microphone: 0, recorders: 0, recorderStarts: 0, trackStops: 0,
    documentWrites: 0, documentReads: 0, storageReads: 0, storageWrites: 0,
    storageRemovals: 0, credentialReads: 0, logs: 0, confirmations: 0,
  };
  const elements = new Map();
  function element(id) {
    if (elements.has(id)) return elements.get(id);
    const classes = new Set();
    const node = {
      dataset: {}, style: {}, disabled: false, checked: false, textContent: "",
      innerHTML: "", src: "", value: "synthetic-query",
      classList: {
        add: (...values) => values.forEach(v => classes.add(v)),
        remove: (...values) => values.forEach(v => classes.delete(v)),
        contains: v => classes.has(v),
        toggle: (v, enabled) => {
          const add = enabled === undefined ? !classes.has(v) : enabled;
          if (add) classes.add(v); else classes.delete(v);
        },
      },
      addEventListener() {}, removeEventListener() {}, appendChild() {},
      setAttribute() {}, removeAttribute() {}, pause() {}, load() {},
      querySelectorAll: () => [], querySelector: () => null, closest: () => null,
    };
    if (id === "login-email" || id === "login-password") {
      Object.defineProperty(node, "value", {
        get() { observed.credentialReads++; return "synthetic-fixture"; },
      });
    }
    elements.set(id, node);
    return node;
  }
  const timers = new Map();
  let nextTimer = 1;
  const track = { readyState: "live", stop() { this.readyState = "ended"; observed.trackStops++; } };
  const stream = { getTracks: () => [track] };
  let mediaHook = async () => stream;
  let fetchHook = async () => ({ ok: true, status: 200, json: async () => ({ access_token: "synthetic-only" }) });
  class FakeMediaRecorder {
    constructor() { observed.recorders++; this.state = "inactive"; }
    start() { observed.recorderStarts++; this.state = "recording"; }
    stop() { this.state = "inactive"; if (this.onstop) this.onstop(); }
  }
  FakeMediaRecorder.isTypeSupported = () => true;
  const sandbox = {
    URL, URLSearchParams, AbortController, Blob, FormData, TextEncoder, TextDecoder,
    crypto: { randomUUID: () => "00000000-0000-4000-8000-000000000001" },
    location,
    document: {
      readyState: "loading", body: element("body"),
      getElementById: element, querySelectorAll: () => [],
      querySelector: selector => options.marker && selector === 'meta[name="raisa-static-synthetic-only"]' ? {} : null,
      addEventListener() {}, createElement: () => element("created"),
    },
    localStorage: {
      getItem() { observed.storageReads++; return "legacy-synthetic-token"; },
      setItem() { observed.storageWrites++; },
      removeItem() { observed.storageRemovals++; },
    },
    navigator: { mediaDevices: { getUserMedia: async () => { observed.microphone++; return mediaHook(); } } },
    MediaRecorder: FakeMediaRecorder,
    fetch: async (...args) => { observed.fetch++; return fetchHook(...args); },
    Word: {
      InsertLocation: { end: "end" },
      run: async callback => callback({
        document: { body: { insertParagraph() { observed.documentWrites++; } } },
        sync: async () => {},
      }),
    },
    Office: { onReady(callback) { sandbox.ready = callback; }, HostType: { Word: "Word" } },
    setTimeout(callback) { const id = nextTimer++; timers.set(id, callback); return id; },
    clearTimeout: id => timers.delete(id),
    setInterval() { return 0; }, clearInterval() {},
    addEventListener() {}, removeEventListener() {},
    alert() {}, confirm() { observed.confirmations++; return true; },
    console: { log() { observed.logs++; }, warn() { observed.logs++; }, error() { observed.logs++; } },
  };
  sandbox.window = sandbox;
  sandbox.self = sandbox;
  const context = vm.createContext(sandbox);
  if (options.policy !== "absent") {
    sandbox.RAISA_PUBLIC_HOSTING_POLICY = options.policy || policy();
  }
  vm.runInContext(source, context, { filename: sourcePath, timeout: 3000 });
  return {
    observed, sandbox, context, stream, track, elements,
    evaluate: expression => vm.runInContext(expression, context, { timeout: 3000 }),
    setPolicy: value => { sandbox.RAISA_PUBLIC_HOSTING_POLICY = value; },
    mediaHook: callback => { mediaHook = callback; },
    fetchHook: callback => { fetchHook = callback; },
    async flushTimers() {
      const pending = Array.from(timers.values()); timers.clear();
      for (const callback of pending) await callback();
    },
    seedFinalization() {
      sandbox.Office.context = { document: { url: "https://synthetic.invalid/document" } };
      sandbox.fixtureRead = async () => { observed.documentReads++; return "authored synthetic note"; };
      vm.runInContext(`
        token = "synthetic-token";
        currentPatient = { id: "synthetic-patient", document_url: "https://synthetic.invalid/document" };
        consultStarted = true; lastConsultHeader = "synthetic header"; consultationGeneration = 8;
        consultationBinding = { token, generation: 8, patientId: "synthetic-patient",
          documentContext: currentPatient.document_url, header: lastConsultHeader,
          commandId: "00000000-0000-4000-8000-000000000002" };
        getCurrentConsultText = fixtureRead;
      `, context);
      assert.equal(vm.runInContext("consultationIsCurrent(consultationBinding)", context), true);
    },
    seedAudio() {
      return vm.runInContext(
        'currentPatient = {id:"synthetic-patient"}; token = "synthetic-token"; ' +
        'audioGeneration = 7; ({generation:7,patientId:"synthetic-patient",chunks:[]})', context);
    },
  };
}
const cases = [];
function check(name, run) { cases.push({ name, run }); }
check("exact hosted policy enables only synthetic mode", () => {
  const h = createHarness();
  assert.equal(h.evaluate("isHostedSyntheticOnlyModeEnabled()"), true);
  assert.equal(h.evaluate("isBackendTransportRestricted()"), true);
});
check("ordinary disabled sentinel permits one synthetic fetch positive control", async () => {
  const h = createHarness({ origin: "https://ordinary.invalid", policy: policy("disabled") });
  assert.equal(h.evaluate("isBackendTransportRestricted()"), false);
  await h.evaluate('apiFetch("/synthetic-positive-control")');
  assert.equal(h.observed.fetch, 1);
});
for (const key of authority) {
  check("reject authority field " + key, async () => {
    const h = createHarness({ policy: { ...policy(), [key]: true }, marker: true });
    assert.equal(h.evaluate("isHostedSyntheticOnlyModeEnabled()"), false);
    await assert.rejects(h.evaluate('apiFetch("/synthetic-denied")'), /unavailable/);
    assert.equal(h.observed.fetch, 0);
  });
}
for (const [key, value] of [
  ["contract_version", "wrong"], ["mode", "wrong"], ["data_class", "real"],
  ["expected_origin", "https://different.invalid"],
]) {
  check("reject mismatched policy " + key, () => {
    const h = createHarness({ policy: { ...policy(), [key]: value }, marker: true });
    assert.equal(h.evaluate("isHostedSyntheticOnlyModeEnabled()"), false);
    assert.equal(h.evaluate("isBackendTransportRestricted()"), true);
  });
}
check("reject extra-field hosted policy", () => {
  const h = createHarness({ policy: { ...policy(), extra: false } });
  assert.equal(h.evaluate("isHostedSyntheticOnlyModeEnabled()"), false);
});
check("reject inherited hosted policy fields", () => {
  const h = createHarness({ policy: Object.create(policy()) });
  assert.equal(h.evaluate("isHostedSyntheticOnlyModeEnabled()"), false);
});
check("reject array-shaped hosted policy", () => {
  const h = createHarness({ policy: Object.assign([], policy()) });
  assert.equal(h.evaluate("isHostedSyntheticOnlyModeEnabled()"), false);
});
check("reject accessor-shaped hosted policy without consuming getter", () => {
  let reads = 0;
  const p = policy();
  Object.defineProperty(p, "mode", { enumerable: true, get() { reads++; return "public_https_development"; } });
  const h = createHarness({ policy: p, marker: true });
  assert.equal(h.evaluate("isHostedSyntheticOnlyModeEnabled()"), false);
  assert.equal(reads, 0);
});
check("marked static page stays restricted with missing policy", async () => {
  const h = createHarness({ policy: "absent", marker: true });
  await assert.rejects(h.evaluate('apiFetch("/synthetic-denied")'), /unavailable/);
  assert.equal(h.observed.fetch, 0);
});
check("restriction latches across policy downgrade", () => {
  const h = createHarness({ origin: "https://ordinary.invalid", policy: policy("disabled") });
  assert.equal(h.evaluate("isBackendTransportRestricted()"), false);
  h.setPolicy(policy("public_https_development", "https://ordinary.invalid"));
  assert.equal(h.evaluate("isBackendTransportRestricted()"), true);
  h.setPolicy(policy("disabled"));
  assert.equal(h.evaluate("isBackendTransportRestricted()"), true);
});
check("restricted login reads no credentials and issues no request", async () => {
  const h = createHarness();
  await h.evaluate("login()");
  assert.equal(h.observed.credentialReads, 0);
  assert.equal(h.observed.fetch, 0);
  assert.equal(h.evaluate("token"), null);
});
check("restricted patient apiFetch issues no request", async () => {
  const h = createHarness();
  await assert.rejects(h.evaluate('apiFetch("/patients/search?q=synthetic")'), /unavailable/);
  assert.equal(h.observed.fetch, 0);
});
check("restricted analysis reads no document and issues no request", async () => {
  const h = createHarness();
  h.sandbox.fixtureRead = async () => { h.observed.documentReads++; return "synthetic note"; };
  h.evaluate("consultStarted = true; getCurrentConsultText = fixtureRead;");
  await h.evaluate("runBackgroundSync()");
  assert.equal(h.observed.fetch, 0);
  assert.equal(h.observed.documentReads, 0);
});
check("restricted transcription issues no request or document write", async () => {
  const h = createHarness();
  h.sandbox.fixtureAudio = h.seedAudio();
  await h.evaluate("processAudio(fixtureAudio)");
  assert.equal(h.observed.fetch, 0);
  assert.equal(h.observed.documentWrites, 0);
});
check("restricted typeahead issues no request", async () => {
  const h = createHarness();
  await h.evaluate('handleKeystroke("mbs", 1)');
  await h.flushTimers();
  assert.equal(h.observed.fetch, 0);
});
check("restricted finalisation reads no document and issues no request", async () => {
  const h = createHarness();
  h.seedFinalization();
  await h.evaluate("approveAndFinalize()");
  assert.equal(h.observed.fetch, 0);
  assert.equal(h.observed.documentReads, 0);
  assert.equal(h.observed.confirmations, 0);
});
check("ordinary finalisation reaches synthetic attestation and fetch positive control", async () => {
  const h = createHarness({ origin: "https://ordinary.invalid", policy: policy("disabled") });
  h.seedFinalization();
  await h.evaluate("approveAndFinalize()");
  assert.equal(h.observed.documentReads, 2);
  assert.equal(h.observed.confirmations, 1);
  assert.equal(h.observed.fetch, 1);
});
check("ordinary recording starts synthetic recorder positive control", async () => {
  const h = createHarness({ origin: "https://ordinary.invalid", policy: policy("disabled") });
  await h.evaluate("toggleRecording()");
  assert.equal(h.observed.microphone, 1);
  assert.equal(h.observed.recorderStarts, 1);
  h.evaluate("clearAudioSession()");
  assert.equal(h.track.readyState, "ended");
  assert.equal(h.observed.fetch, 0);
});
check("restriction during recorded chunk stops microphone and discards audio", async () => {
  const h = createHarness({ origin: "https://ordinary.invalid", policy: policy("disabled") });
  await h.evaluate("toggleRecording()");
  assert.equal(h.observed.recorderStarts, 1);
  h.setPolicy(policy("public_https_development", "https://ordinary.invalid"));
  h.evaluate("audioContext.recorder.ondataavailable({data:new Blob(['synthetic-audio'])})");
  assert.equal(h.track.readyState, "ended");
  assert.equal(h.evaluate("audioContext"), null);
  assert.equal(h.observed.fetch, 0);
});
check("disabled policy accessor cannot grant ordinary transport or consume getter", () => {
  let reads = 0;
  const p = policy("disabled");
  Object.defineProperty(p, "mode", { enumerable: true, get() { reads++; return "disabled"; } });
  const h = createHarness({ origin: "https://ordinary.invalid", policy: p });
  assert.equal(h.evaluate("isBackendTransportRestricted()"), true);
  assert.equal(reads, 0);
});
check("restricted recording requests no microphone", async () => {
  const h = createHarness();
  await h.evaluate("toggleRecording()");
  assert.equal(h.observed.microphone, 0);
  assert.equal(h.observed.recorders, 0);
});
check("policy restriction during microphone permission stops returned stream", async () => {
  const h = createHarness({ origin: "https://ordinary.invalid", policy: policy("disabled") });
  let resolveMedia;
  h.mediaHook(() => new Promise(resolve => { resolveMedia = resolve; }));
  const pending = h.evaluate("toggleRecording()");
  assert.equal(h.observed.microphone, 1);
  h.setPolicy(policy("public_https_development", "https://ordinary.invalid"));
  resolveMedia(h.stream);
  await pending;
  assert.equal(h.observed.recorders, 0);
  assert.equal(h.track.readyState, "ended");
});
check("policy restriction before transcription response prevents document write", async () => {
  const h = createHarness({ origin: "https://ordinary.invalid", policy: policy("disabled") });
  h.sandbox.fixtureAudio = h.seedAudio();
  h.sandbox.URL = class extends URL {};
  h.sandbox.URL.createObjectURL = () => "blob:synthetic-fixture";
  h.sandbox.URL.revokeObjectURL = () => {};
  let resolveFetch;
  h.fetchHook(() => new Promise(resolve => { resolveFetch = resolve; }));
  const pending = h.evaluate("processAudio(fixtureAudio)");
  assert.equal(h.observed.fetch, 1);
  h.setPolicy(policy("public_https_development", "https://ordinary.invalid"));
  resolveFetch({
    ok: true, status: 200,
    json: async () => ({ generated_clinical_note: "synthetic-only", raw_transcript: "synthetic-only" }),
  });
  await pending;
  assert.equal(h.observed.documentWrites, 0);
  assert.notEqual(h.elements.get("raw-transcript")?.value, "synthetic-only");
});
for (const boundary of ["JSON decoding", "Word callback"]) {
  check("restriction during " + boundary + " prevents late transcription write", async () => {
    const h = createHarness({ origin: "https://ordinary.invalid", policy: policy("disabled") });
    h.sandbox.fixtureAudio = h.seedAudio();
    h.sandbox.URL = class extends URL {};
    h.sandbox.URL.createObjectURL = () => "blob:synthetic-fixture";
    h.sandbox.URL.revokeObjectURL = () => {};
    const data = { generated_clinical_note: "synthetic-only", raw_transcript: "synthetic-only" };
    let entered;
    const reached = new Promise(resolve => { entered = resolve; });
    let release;
    if (boundary === "JSON decoding") {
      h.fetchHook(async () => ({ ok: true, status: 200, json: () => {
        entered(); return new Promise(resolve => { release = () => resolve(data); });
      } }));
    } else {
      h.fetchHook(async () => ({ ok: true, status: 200, json: async () => data }));
      h.sandbox.Word.run = callback => {
        entered(); return new Promise((resolve, reject) => { release = () =>
          Promise.resolve(callback({ document: { body: { insertParagraph() {
            h.observed.documentWrites++;
          } } }, sync: async () => {} })).then(resolve, reject);
        });
      };
    }
    const pending = h.evaluate("processAudio(fixtureAudio)");
    await reached;
    assert.equal(h.observed.fetch, 1);
    h.setPolicy(policy("public_https_development", "https://ordinary.invalid"));
    release();
    await pending;
    assert.equal(h.observed.documentWrites, 0);
    assert.notEqual(h.elements.get("raw-transcript")?.value, "synthetic-only");
  });
}
check("legacy bearer storage is removed and never read or written", () => {
  const h = createHarness();
  assert.equal(h.observed.storageReads, 0);
  assert.equal(h.observed.storageWrites, 0);
  assert.equal(h.observed.storageRemovals, 1);
});
(async () => {
  const results = [];
  for (const item of cases) {
    try { await item.run(); results.push({ name: item.name, status: "passed" }); }
    catch (error) {
      results.push({ name: item.name, status: "failed", error: String(error.message).slice(0, 240) });
    }
  }
  const passed = results.filter(r => r.status === "passed").length;
  const output = {
    scope: "Complete source in VM with authored in-memory transport/device/Office/storage collaborators; not observed browser traffic or product integration.",
    source_sha256: require("node:crypto").createHash("sha256").update(source).digest("hex"),
    node: process.version, total: results.length, passed, failed: results.length - passed, results,
  };
  console.log(JSON.stringify(output, null, 2));
  process.exitCode = passed === results.length ? 0 : 1;
})();
