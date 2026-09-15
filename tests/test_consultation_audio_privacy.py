"""Isolated source-component checks; no application/provider/database imports.

Execute only in a separately reviewed literal-file capsule. These checks do not
establish endpoint authentication, multipart retention, browser-host or G2 acceptance.
"""
import ast
import asyncio
import json
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
CONSULTATION = ROOT / "app/routers/consultation.py"
TASKPANE = ROOT / "EMR4 Sidebar/src/taskpane/taskpane.js"


def selected_function(name, namespace):
    tree = ast.parse(CONSULTATION.read_text(encoding="utf-8"))
    node = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name == name)
    node.decorator_list = []
    node.returns = None
    for argument in node.args.args:
        argument.annotation = None
    node.args.defaults = []
    module = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    exec(compile(module, str(CONSULTATION), "exec"), namespace)
    return namespace[name]


def fail_filesystem(*args, **kwargs):
    raise AssertionError("Audio component attempted filesystem access")


class NoFilesystem:
    def __getattr__(self, name):
        raise AssertionError("Audio component attempted filesystem access: " + name)


def response(*, content, status_code=200):
    return SimpleNamespace(content=content, status_code=status_code)


def test_static_mount_is_removed_and_taskpane_is_retained():
    tree = ast.parse((ROOT / "app/main.py").read_text(encoding="utf-8"))
    mounts = []
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            if isinstance(call.func, ast.Attribute) and call.func.attr == "mount":
                mounts.append(ast.literal_eval(call.args[0]))
    assert "/static" not in mounts
    assert "/taskpane" in mounts
    assert not any(isinstance(n, ast.Constant) and n.value == "static/audio" for n in ast.walk(tree))


def test_retained_router_annotations_have_their_imports():
    tree = ast.parse(CONSULTATION.read_text(encoding="utf-8"))
    # Selected-function tests erase annotations to isolate dependencies. Check
    # this retained module-level dependency separately so import cannot regress.
    if any(isinstance(n, ast.Name) and n.id == "uuid" for n in ast.walk(tree)):
        assert any(isinstance(n, ast.Import) and any(a.name == "uuid" for a in n.names) for n in tree.body)


def test_scribe_passes_bytes_without_persisting_or_returning_audio_url():
    captured = []

    async def read():
        return b"authored synthetic audio"

    async def scribe(*args):
        captured.append(args)
        return SimpleNamespace(audit_events=[], raw={"raw_transcript": "synthetic", "audio_url": "legacy"})

    namespace = dict(open=fail_filesystem, os=NoFilesystem(), uuid=NoFilesystem(),
                     _ai_service=SimpleNamespace(scribe_audio=scribe),
                     settings=SimpleNamespace(environment="test"),
                     actor_context_from_user=lambda *args, **kwargs: "synthetic-actor", JSONResponse=response)
    result = asyncio.run(selected_function("scribe_consultation", namespace)(
        SimpleNamespace(read=read, content_type="audio/webm"), SimpleNamespace(), SimpleNamespace()))
    assert captured[0][0:2] == (b"authored synthetic audio", "audio/webm")
    assert result["raw_transcript"] == "synthetic"
    assert "audio_url" not in result


def test_scribe_failure_is_not_a_success_response_or_persistent_file():
    async def read():
        return b"authored synthetic audio"

    async def fail(*args):
        raise RuntimeError("synthetic service failure")

    namespace = dict(open=fail_filesystem, os=NoFilesystem(), uuid=NoFilesystem(),
                     _ai_service=SimpleNamespace(scribe_audio=fail), settings=SimpleNamespace(environment="test"),
                     actor_context_from_user=lambda *args, **kwargs: "synthetic-actor", JSONResponse=response)
    result = asyncio.run(selected_function("scribe_consultation", namespace)(
        SimpleNamespace(read=read, content_type="audio/webm"), SimpleNamespace(), SimpleNamespace()))
    assert result.status_code >= 400
    assert "error" in result.content
    assert "audio_url" not in result.content


def test_legacy_finalize_audio_url_is_accepted_but_never_read_or_deleted():
    tree = ast.parse(CONSULTATION.read_text(encoding="utf-8"))
    payload_class = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "FinalizePayload")
    assert any(isinstance(n, ast.AnnAssign) and n.target.id == "audio_url" for n in payload_class.body)

    class Payload:
        patient_id = "00000000-0000-4000-8000-000000000001"
        document_id = "synthetic-document"
        text_delta = "synthetic notes"
        clinician_overrides = SimpleNamespace(consultation_type="test", mbs_items=[], diagnoses=[], medications=[])

        @property
        def audio_url(self):
            raise AssertionError("Legacy audio URL must not convey filesystem authority")

    patient = SimpleNamespace(id=Payload.patient_id, practice_id="synthetic-practice")
    query = SimpleNamespace(filter=lambda *args: SimpleNamespace(first=lambda: patient))
    namespace = dict(open=fail_filesystem, os=NoFilesystem(), _safe_audio_cleanup=fail_filesystem,
                     Patient=SimpleNamespace(id="id", practice_id="practice_id"),
                     _save_encounter=lambda *args: SimpleNamespace(id="synthetic-encounter"), JSONResponse=response)
    result = asyncio.run(selected_function("finalize_consultation", namespace)(
        Payload(), SimpleNamespace(query=lambda model: query, rollback=fail_filesystem),
        SimpleNamespace(practice_id="synthetic-practice")))
    assert result.content["_saved"] is True


NODE_CHECKS = r'''
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(process.argv[1], 'utf8');
const cases = [];
const deferred = () => { let resolve; const promise = new Promise(r => resolve = r); return {promise, resolve}; };
const tick = () => new Promise(r => setImmediate(r));
function fixture() {
  const elements = new Map(), handlers = {}, revoked = [], created = [], tracks = [], requests = [], updates = [], notes = [];
  const element = id => {
    if (!elements.has(id)) {
      const classes = new Set(['hidden']);
      elements.set(id, {value:'', textContent:'', disabled:false, src:'',
        classList:{add(n){classes.add(n);},remove(n){classes.delete(n);},
          toggle(n,force){if(force === undefined ? !classes.has(n) : force)classes.add(n);else classes.delete(n);},
          contains(n){return classes.has(n);}}, pause(){},load(){},
        removeAttribute(name){delete this[name];},addEventListener(){}});
    }
    return elements.get(id);
  };
  let nextFetch = async () => ({ok:true,json:async()=>({})});
  let nextMedia = async () => { const t={readyState:'live',stop(){this.readyState='ended';}}; tracks.push(t); return {getTracks:()=>[t]}; };
  class Recorder {
    constructor(stream) { this.stream=stream; this.state='inactive'; }
    start(){this.state='recording';}
    stop(){this.state='inactive'; if(this.ondataavailable)this.ondataavailable({data:new Blob(['synthetic'])}); if(this.onstop)this.onstop();}
  }
  const context=vm.createContext({console, Blob, AbortController, MediaRecorder:Recorder,
    FormData:class {append(){}}, URL:{createObjectURL(blob){assert(blob instanceof Blob);const u='blob:synthetic-'+created.length;created.push(u);return u;},revokeObjectURL(u){revoked.push(u);}},
    crypto:{randomUUID:()=> '00000000-0000-4000-8000-000000000001'},
    window:{location:{port:'',origin:'https://synthetic.invalid',protocol:'https:',hostname:'synthetic.invalid'},addEventListener(n,f){handlers[n]=f;}},
    document:{getElementById:element,addEventListener(){}},
    localStorage:{getItem(){return null;},removeItem(){},setItem(){}},
    Office:{onReady(){}}, Word:{InsertLocation:{end:'end'},run:async fn=>fn({document:{body:{insertParagraph(text){notes.push(text);}}},sync:async()=>{}})},
    navigator:{mediaDevices:{getUserMedia:()=>nextMedia()}},
    fetch:(url,options)=>{requests.push({url,options});return nextFetch(url,options);},
    alert(){},setTimeout(){},clearTimeout(){},clearInterval(){},URLSearchParams,
  });
  vm.runInContext(source,context,{timeout:1000});
  context.updates=updates;
  vm.runInContext(`setStatus = text => globalThis.lastStatus=text; updateFormFields = data => updates.push(data);
    updateLockUI=()=>{}; updateStartConsultButton=()=>{}; updateOpenFileButton=()=>{}; updatePatientEditButton=()=>{};
    showView=()=>{}; getCurrentConsultText=async()=> 'synthetic'; currentPatient={id:'A'}; token='synthetic';`,context);
  const run=s=>vm.runInContext(s,context,{timeout:1000});
  return {run,context,handlers,revoked,created,tracks,requests,updates,notes,element,
    fetch:fn=>nextFetch=fn,media:fn=>nextMedia=fn,async start(){await run('toggleRecording()');},
    async stop(){await run('toggleRecording()');await tick();await tick();}};
}
async function check(name,fn){await fn();cases.push(name);}
function showTranscript(f,text){
  f.element('raw-transcript').value=text;
  f.element('transcript-row').classList.remove('hidden');
  assert.equal(f.element('transcript-row').classList.contains('hidden'),false);
}
(async()=>{
  await check('local playback, replacement and pagehide revocation',async()=>{
    const f=fixture(); await f.start(); await f.stop(); assert.equal(f.created.length,1);
    assert.equal(f.element('audio-playback').src,f.created[0]); assert(f.tracks.every(t=>t.readyState==='ended'));
    showTranscript(f,'prior transcript');
    await f.start();assert(f.revoked.includes(f.created[0]));assert.equal(f.element('raw-transcript').value,'');
    await f.stop();showTranscript(f,'new transcript');f.handlers.pagehide();
    assert(f.created.every(u=>f.revoked.includes(u)));assert.equal(f.run('currentAudioUrl'),null);
    assert.equal(f.element('raw-transcript').value,'');assert(f.element('transcript-row').classList.contains('hidden'));
  });
  for(const result of [{ok:false,json:async()=>({})},{ok:true,json:async()=>({error:'synthetic'})},{ok:true,json:async()=>{throw Error('invalid JSON');}}]) {
    await check('scribe error cannot report success',async()=>{const f=fixture();f.fetch(async()=>result);await f.start();await f.stop();
      assert.equal(f.updates.length,0);assert.equal(f.notes.length,0);assert.equal(f.run('isLocked'),false);
      assert.equal(f.created.length,1);assert.equal(f.revoked.length,0);assert.match(f.context.lastStatus,/failed/);});
  }
  for(const transition of ['clearAudioSession(); currentPatient={id:"B"}', 'logout()', 'toggleRecording()']) {
    await check('late scribe response is inert: '+transition,async()=>{const f=fixture(),d=deferred();f.fetch(()=>d.promise);
      await f.start();await f.stop();await f.run(transition);d.resolve({ok:true,json:async()=>({generated_clinical_note:'synthetic'})});
      await tick();await tick();assert.equal(f.updates.length,0);assert.equal(f.notes.length,0);f.handlers.pagehide();});
  }
  await check('late JSON response is inert',async()=>{const f=fixture(),d=deferred();f.fetch(async()=>({ok:true,json:()=>d.promise}));
    await f.start();await f.stop();f.run('clearAudioSession();currentPatient={id:"B"}');d.resolve({generated_clinical_note:'synthetic'});
    await tick();assert.equal(f.updates.length,0);assert.equal(f.notes.length,0);});
  await check('late microphone permission releases captured stream',async()=>{const f=fixture(),d=deferred();f.media(()=>d.promise);
    const pending=f.start(); f.run('logout()');const track={readyState:'live',stop(){this.readyState='ended';}};
    d.resolve({getTracks:()=>[track]});await pending;assert.equal(track.readyState,'ended');assert.equal(f.requests.length,0);});
  for(const transition of ['audioContext.recorder.onerror()', 'clearAudioSession();currentPatient={id:"B"}', 'logout()']) {
    await check('abandoned recording cannot upload: '+transition,async()=>{const f=fixture();await f.start();f.run(transition);await tick();
      assert(f.tracks.every(t=>t.readyState==='ended'));assert.equal(f.requests.length,0);assert.equal(f.run('isRecording'),false);});
  }
  await check('pagehide stops recording without upload',async()=>{const f=fixture();await f.start();f.handlers.pagehide();await tick();
    assert(f.tracks.every(t=>t.readyState==='ended'));assert.equal(f.requests.length,0);});
  await check('finalize never sends audio URL and clears successful playback',async()=>{const f=fixture();await f.start();await f.stop();
    showTranscript(f,'synthetic transcript');
    f.fetch(async()=>({ok:true,json:async()=>({_saved:true})}));await f.run('approveAndFinalize()');
    assert(!('audio_url' in JSON.parse(f.requests.at(-1).options.body)));assert(f.created.every(u=>f.revoked.includes(u)));
    assert.equal(f.element('raw-transcript').value,'');assert(f.element('transcript-row').classList.contains('hidden'));});
  for(const patient of ['null', '{id:""}']) {
    await check('finalize requires explicit patient: '+patient,async()=>{
      const f=fixture();f.run('currentPatient='+patient+';getCurrentConsultText=async()=>{throw Error("must not read Word");}');
      await f.run('approveAndFinalize()');assert.equal(f.requests.length,0);assert.equal(f.notes.length,0);
      assert.match(f.context.lastStatus,/Select a patient/);assert.equal(f.run('isLocked'),false);
    });
  }
  await check('finalize failure preserves playback',async()=>{const f=fixture();await f.start();await f.stop();
    showTranscript(f,'synthetic transcript');
    f.fetch(async()=>({ok:true,json:async()=>({_saved:false})}));await f.run('approveAndFinalize()');assert.equal(f.revoked.length,0);
    assert.equal(f.element('raw-transcript').value,'synthetic transcript');
    assert.equal(f.element('transcript-row').classList.contains('hidden'),false);});
  for(const kind of ['scribe','finalize']) {
    await check('actual patient-selection entry invalidates pending '+kind,async()=>{
      const f=fixture(),pending=deferred(),summary=deferred();
      if(kind==='scribe')f.fetch(()=>pending.promise);
      await f.start();await f.stop();let finalizing;
      if(kind==='finalize'){f.fetch(()=>pending.promise);finalizing=f.run('approveAndFinalize()');await tick();}
      showTranscript(f,'patient A transcript');
      const updatesBefore=f.updates.length,notesBefore=f.notes.length;
      f.context.summary=summary.promise;f.run('apiFetch=()=>summary');
      const selecting=f.run('loadPatient("B")');
      assert(f.tracks.every(t=>t.readyState==='ended'));assert(f.created.every(u=>f.revoked.includes(u)));
      assert.equal(f.element('raw-transcript').value,'');assert(f.element('transcript-row').classList.contains('hidden'));
      pending.resolve({ok:true,json:async()=>({_saved:true,generated_clinical_note:'stale synthetic'})});
      await tick();await tick();if(finalizing)await finalizing;
      assert.equal(f.updates.length,updatesBefore);assert.equal(f.notes.length,notesBefore);
      assert(!String(f.context.lastStatus).includes('complete'));assert(!String(f.context.lastStatus).includes('finalised'));
      summary.resolve(null);await selecting;
    });
  }
  await check('recorder construction failure stops tracks and preserves prior review',async()=>{
    const f=fixture();await f.start();await f.stop();showTranscript(f,'prior transcript');
    const oldUrl=f.run('currentAudioUrl'),requestCount=f.requests.length;
    f.context.MediaRecorder=class {constructor(){throw Error('synthetic constructor failure');}};
    await f.start();assert(f.tracks.every(t=>t.readyState==='ended'));assert.equal(f.requests.length,requestCount);
    assert.equal(f.run('isRecording'),false);assert.equal(f.run('audioStartPending'),false);
    assert.equal(f.run('currentAudioUrl'),oldUrl);assert(!f.revoked.includes(oldUrl));
    assert.equal(f.element('raw-transcript').value,'prior transcript');
    assert.equal(f.element('transcript-row').classList.contains('hidden'),false);f.handlers.pagehide();
  });
  console.log(JSON.stringify({passed:true,cases}));
})().catch(error=>{console.error(error);process.exitCode=1;});
'''


def test_browser_audio_components_with_authored_adapters():
    node = shutil.which("node")
    assert node, "The reviewed Node runtime is required; do not skip browser component checks"
    result = subprocess.run([node, "-e", NODE_CHECKS, str(TASKPANE)], text=True,
                            capture_output=True, timeout=30, check=False)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["passed"] is True
    assert len(report["cases"]) == 20
