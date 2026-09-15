"""Isolated source-component checks; no application/provider/database imports.

Execute only in a separately reviewed literal-file capsule. These checks do not
establish endpoint authentication, multipart retention, browser-host or G2 acceptance.
"""
import ast
import asyncio
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace
import uuid


ROOT = Path(__file__).resolve().parents[1]
CONSULTATION = ROOT / "app/routers/consultation.py"
TASKPANE = ROOT / "EMR4 Sidebar/src/taskpane/taskpane.js"


def selected_function(name, namespace):
    tree = ast.parse(CONSULTATION.read_text(encoding="utf-8"))
    node = next(n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)
    node.decorator_list = []
    node.returns = None
    for argument in node.args.args + node.args.kwonlyargs:
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

    class Overrides:
        def model_dump(self, *, mode):
            assert mode == "json"
            return dict(consultation_type="test", mbs_items=[], diagnoses=[], medications=[])

    class Payload:
        patient_id = uuid.UUID("00000000-0000-4000-8000-000000000001")
        document_id = uuid.UUID("00000000-0000-4000-8000-000000000002")
        document_context = "https://synthetic.invalid/word/audio-check"
        text_delta = "synthetic notes"
        clinician_attested = True
        clinician_overrides = Overrides()

        @property
        def audio_url(self):
            raise AssertionError("Legacy audio URL must not convey filesystem authority")

    # Authored command-session adapters isolate the audio guarantee. They do not
    # establish real HTTP/role/transaction acceptance; the reviewed runtime does.
    class Field:
        def __init__(self, name):
            self.name = name

        def __eq__(self, value):
            return self.name, value

    class AuthError(Exception):
        def __init__(self, *, status_code, detail):
            super().__init__(detail)
            self.status_code = status_code

    class AuthoredIntegrityError(Exception):
        pass

    gp_role = SimpleNamespace(value="GP")
    patient = SimpleNamespace(
        id=Payload.patient_id,
        practice_id=uuid.UUID("00000000-0000-4000-8000-000000000003"),
        document_url=Payload.document_context,
    )
    practitioner = SimpleNamespace(
        id=uuid.UUID("00000000-0000-4000-8000-000000000004"),
        practice_id=patient.practice_id,
        is_active=True,
    )
    actor = SimpleNamespace(
        id=uuid.UUID("00000000-0000-4000-8000-000000000005"),
        practice_id=patient.practice_id,
        practitioner_id=practitioner.id, role=gp_role, is_active=True,
    )
    models = [
        SimpleNamespace(id=Field("id"), practice_id=Field("practice_id"))
        for _ in range(3)
    ]
    models.append(SimpleNamespace(
        event_id=Field("event_id"), practice_id=Field("practice_id"),
        event_type=Field("event_type"),
    ))
    rows = [actor, practitioner, patient, None]
    queried, saved, audited, actions = [], [], [], []

    class Query:
        def __init__(self, index):
            self.index = index
            self.row = rows[index]

        def filter(self, *conditions):
            if self.row is not None:
                assert all(getattr(self.row, name) == value for name, value in conditions)
            else:
                assert dict(conditions) == {
                    "event_id": namespace["_clinical_finalization_event_id"](
                        patient.practice_id, Payload.document_id
                    ),
                    "practice_id": patient.practice_id,
                    "event_type": "clinical.consultation.attested",
                }
            return self

        def with_for_update(self):
            return self

        def first(self):
            return self.row

    class CommandDatabase:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def begin(self):
            return self

        def execute(self, statement, params):
            assert params == {"practice_id": str(patient.practice_id)}

        def query(self, model):
            index = next(i for i, candidate in enumerate(models) if candidate is model)
            queried.append(index)
            return Query(index)

        add = commit = rollback = fail_filesystem

    def save(*args):
        actions.append("clinical_save")
        saved.append(args)
        return args[3]

    def persist(db, events):
        actions.append("audit_receipt")
        audited.extend(events)

    namespace = dict(
        open=fail_filesystem, os=NoFilesystem(), _safe_audio_cleanup=fail_filesystem,
        User=models[0], Practitioner=models[1], Patient=models[2], AccessAiAuditLog=models[3],
        UserRole=SimpleNamespace(GP=gp_role), _save_encounter=save,
        HTTPException=AuthError, IntegrityError=AuthoredIntegrityError,
        status=SimpleNamespace(HTTP_403_FORBIDDEN=403, HTTP_409_CONFLICT=409),
        text=lambda value: value, json=json, hashlib=hashlib, uuid=uuid,
        AiAuditEventType=SimpleNamespace(
            CLINICAL_CONSULTATION_ATTESTED=SimpleNamespace(value="clinical.consultation.attested")
        ),
        AiAuditSourceSurface=SimpleNamespace(API="api"),
        AiAuditDecision=SimpleNamespace(RECORDED="recorded"),
        build_access_ai_audit_event=lambda **kwargs: kwargs,
        persist_access_ai_audit_events=persist,
        JSONResponse=response,
    )
    constants = [
        node for node in tree.body
        if isinstance(node, ast.Assign)
        and all(isinstance(target, ast.Name) and target.id.startswith(
            ("CLINICAL_FINALIZATION_", "_FINALIZATION_")
        ) for target in node.targets)
    ]
    exec(compile(ast.fix_missing_locations(ast.Module(
        body=constants, type_ignores=[]
    )), str(CONSULTATION), "exec"), namespace)
    # Exercise real command-ID/normalization/hash/response helpers as well as the
    # route: an indirect legacy URL read must not slip through a route-only check.
    for helper in (
        "_clinical_finalization_event_id", "_effective_finalization_projection",
        "_reviewed_content_sha256", "_finalization_response",
    ):
        selected_function(helper, namespace)
    result = asyncio.run(selected_function("finalize_consultation", namespace)(
        Payload(), CommandDatabase, actor))
    assert result.content["_saved"] is True
    assert queried == [0, 1, 2, 3]
    assert actions == ["audit_receipt", "clinical_save"]
    assert len(saved) == len(audited) == 1
    assert saved[0][1] is patient and saved[0][2] == practitioner.id
    assert isinstance(saved[0][3], uuid.UUID)
    assert saved[0][4] == str(Payload.document_id)
    assert result.content["encounter_id"] == str(saved[0][3])
    assert audited[0]["metadata"]["attested"] is True


NODE_CHECKS = r'''
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(process.argv[1], 'utf8');
const cases = [];
const deferred = () => { let resolve; const promise = new Promise(r => resolve = r); return {promise, resolve}; };
const tick = () => new Promise(r => setImmediate(r));
async function fixture({started=true}={}) {
  const elements = new Map(), handlers = {}, revoked = [], created = [], tracks = [], requests = [], updates = [], notes = [], affirmations = [];
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
  let nextConfirm = () => true, nextWordSync = async () => {}, syncCalls = 0, uuidCounter = 0, bookmark = null;
  const paragraphs = [];
  function paragraph(text,style='Normal') {
    const item={text,styleBuiltIn:style,font:{},
      insertText(value){this.text+=value;return {font:{}};},
      insertParagraph(value){const added=paragraph(value);paragraphs.splice(paragraphs.indexOf(this)+1,0,added);return added;},
      getRange(){return {insertBookmark(){bookmark=item;},select(){}};}};
    return item;
  }
  const collection={items:paragraphs,load(){}};
  const contentControls={items:[],load(){},getByTag(){return {items:[],load(){}};}};
  const body={paragraphs:collection,insertParagraph(text){notes.push(text);const added=paragraph(text);paragraphs.push(added);return added;}};
  const wordDocument={body,contentControls,getBookmarkRangeOrNullObject(){
    return {isNullObject:!bookmark,insertParagraph(text){notes.push(text);return bookmark.insertParagraph(text);}};
  }};
  paragraphs.push(paragraph('Contemporaneous Notes','Heading1'));
  let nextMedia = async () => { const t={readyState:'live',stop(){this.readyState='ended';}}; tracks.push(t); return {getTracks:()=>[t]}; };
  class Recorder {
    constructor(stream) { this.stream=stream; this.state='inactive'; }
    start(){this.state='recording';}
    stop(){this.state='inactive'; if(this.ondataavailable)this.ondataavailable({data:new Blob(['synthetic'])}); if(this.onstop)this.onstop();}
  }
  const context=vm.createContext({console, Blob, AbortController, MediaRecorder:Recorder,
    FormData:class {append(){}}, URL:{createObjectURL(blob){assert(blob instanceof Blob);const u='blob:synthetic-'+created.length;created.push(u);return u;},revokeObjectURL(u){revoked.push(u);}},
    crypto:{randomUUID:()=> '00000000-0000-4000-8000-'+String(++uuidCounter).padStart(12,'0')},
    window:{location:{port:'',origin:'https://synthetic.invalid',protocol:'https:',hostname:'synthetic.invalid'},addEventListener(n,f){handlers[n]=f;},
      confirm(message){affirmations.push(message);return nextConfirm(message);}},
    document:{getElementById:element,addEventListener(){}},
    localStorage:{getItem(){return null;},removeItem(){},setItem(){}},
    Office:{onReady(){},context:{document:{url:'https://synthetic.invalid/word/A'}}},
    Word:{InsertLocation:{end:'end',after:'after'},RangeLocation:{end:'end'},BuiltInStyleName:{heading1:'Heading1',normal:'Normal'},
      run:async fn=>fn({document:wordDocument,sync:()=>nextWordSync(++syncCalls)})},
    navigator:{mediaDevices:{getUserMedia:()=>nextMedia()}},
    fetch:(url,options)=>{requests.push({url,options});return nextFetch(url,options);},
    alert(){},setTimeout(){},clearTimeout(){},clearInterval(){},URLSearchParams,
  });
  vm.runInContext(source,context,{timeout:1000});
  context.updates=updates;
  vm.runInContext(`setStatus = text => globalThis.lastStatus=text; updateFormFields = data => updates.push(data);
    updateLockUI=()=>{}; updateOpenFileButton=()=>{}; updatePatientEditButton=()=>{}; setBanner=()=>{};
    showView=()=>{}; currentPatient={id:'A',document_url:'https://synthetic.invalid/word/A',
      first_name:'Synthetic',last_name:'Patient A',date_of_birth:'1990-01-01'}; token='synthetic';`,context);
  const run=s=>vm.runInContext(s,context,{timeout:1000});
  let note = null;
  if(started) {
    await run('window.startConsultation()');
    assert.equal(run('consultStarted'),true);
    note = paragraphs[1].insertParagraph('synthetic');
    updates.length=0;
  }
  return {run,context,handlers,revoked,created,tracks,requests,updates,notes,element,affirmations,paragraphs,paragraph,note,
    wordSync:fn=>nextWordSync=fn,confirm:fn=>nextConfirm=fn,
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
    const f=await fixture(); await f.start(); await f.stop(); assert.equal(f.created.length,1);
    assert.equal(f.element('audio-playback').src,f.created[0]); assert(f.tracks.every(t=>t.readyState==='ended'));
    showTranscript(f,'prior transcript');
    await f.start();assert(f.revoked.includes(f.created[0]));assert.equal(f.element('raw-transcript').value,'');
    await f.stop();showTranscript(f,'new transcript');f.handlers.pagehide();
    assert(f.created.every(u=>f.revoked.includes(u)));assert.equal(f.run('currentAudioUrl'),null);
    assert.equal(f.element('raw-transcript').value,'');assert(f.element('transcript-row').classList.contains('hidden'));
  });
  for(const result of [{ok:false,json:async()=>({})},{ok:true,json:async()=>({error:'synthetic'})},{ok:true,json:async()=>{throw Error('invalid JSON');}}]) {
    await check('scribe error cannot report success',async()=>{const f=await fixture();f.fetch(async()=>result);await f.start();await f.stop();
      assert.equal(f.updates.length,0);assert.equal(f.notes.length,0);assert.equal(f.run('isLocked'),false);
      assert.equal(f.created.length,1);assert.equal(f.revoked.length,0);assert.match(f.context.lastStatus,/failed/);});
  }
  for(const transition of ['clearAudioSession(); currentPatient={id:"B"}', 'logout()', 'toggleRecording()']) {
    await check('late scribe response is inert: '+transition,async()=>{const f=await fixture(),d=deferred();f.fetch(()=>d.promise);
      await f.start();await f.stop();await f.run(transition);d.resolve({ok:true,json:async()=>({generated_clinical_note:'synthetic'})});
      await tick();await tick();assert.equal(f.updates.length,0);assert.equal(f.notes.length,0);f.handlers.pagehide();});
  }
  await check('late JSON response is inert',async()=>{const f=await fixture(),d=deferred();f.fetch(async()=>({ok:true,json:()=>d.promise}));
    await f.start();await f.stop();f.run('clearAudioSession();currentPatient={id:"B"}');d.resolve({generated_clinical_note:'synthetic'});
    await tick();assert.equal(f.updates.length,0);assert.equal(f.notes.length,0);});
  await check('late microphone permission releases captured stream',async()=>{const f=await fixture(),d=deferred();f.media(()=>d.promise);
    const pending=f.start(); f.run('logout()');const track={readyState:'live',stop(){this.readyState='ended';}};
    d.resolve({getTracks:()=>[track]});await pending;assert.equal(track.readyState,'ended');assert.equal(f.requests.length,0);});
  for(const transition of ['audioContext.recorder.onerror()', 'clearAudioSession();currentPatient={id:"B"}', 'logout()']) {
    await check('abandoned recording cannot upload: '+transition,async()=>{const f=await fixture();await f.start();f.run(transition);await tick();
      assert(f.tracks.every(t=>t.readyState==='ended'));assert.equal(f.requests.length,0);assert.equal(f.run('isRecording'),false);});
  }
  await check('pagehide stops recording without upload',async()=>{const f=await fixture();await f.start();f.handlers.pagehide();await tick();
    assert(f.tracks.every(t=>t.readyState==='ended'));assert.equal(f.requests.length,0);});
  await check('finalize never sends audio URL and clears successful playback',async()=>{const f=await fixture();await f.start();await f.stop();
    showTranscript(f,'synthetic transcript');
    f.fetch(async()=>({ok:true,json:async()=>({_saved:true,encounter_id:'00000000-0000-4000-8000-000000000101'})}));await f.run('approveAndFinalize()');
    assert(!('audio_url' in JSON.parse(f.requests.at(-1).options.body)));assert(f.created.every(u=>f.revoked.includes(u)));
    assert.equal(f.element('raw-transcript').value,'');assert(f.element('transcript-row').classList.contains('hidden'));});
  for(const patient of ['null', '{id:""}']) {
    await check('finalize requires explicit patient: '+patient,async()=>{
      const f=await fixture();f.run('currentPatient='+patient+';getCurrentConsultText=async()=>{throw Error("must not read Word");}');
      await f.run('approveAndFinalize()');assert.equal(f.requests.length,0);assert.equal(f.notes.length,0);
      assert.match(f.context.lastStatus,/Select a patient/);assert.equal(f.run('isLocked'),false);
    });
  }
  await check('finalize failure preserves playback',async()=>{const f=await fixture();await f.start();await f.stop();
    showTranscript(f,'synthetic transcript');
    f.fetch(async()=>({ok:true,json:async()=>({_saved:false})}));await f.run('approveAndFinalize()');assert.equal(f.revoked.length,0);
    assert.equal(f.element('raw-transcript').value,'synthetic transcript');
    assert.equal(f.element('transcript-row').classList.contains('hidden'),false);});
  for(const kind of ['scribe','finalize']) {
    await check('actual patient-selection entry invalidates pending '+kind,async()=>{
      const f=await fixture(),pending=deferred(),summary=deferred();
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
    const f=await fixture();await f.start();await f.stop();showTranscript(f,'prior transcript');
    const oldUrl=f.run('currentAudioUrl'),requestCount=f.requests.length;
    f.context.MediaRecorder=class {constructor(){throw Error('synthetic constructor failure');}};
    await f.start();assert(f.tracks.every(t=>t.readyState==='ended'));assert.equal(f.requests.length,requestCount);
    assert.equal(f.run('isRecording'),false);assert.equal(f.run('audioStartPending'),false);
    assert.equal(f.run('currentAudioUrl'),oldUrl);assert(!f.revoked.includes(oldUrl));
    assert.equal(f.element('raw-transcript').value,'prior transcript');
    assert.equal(f.element('transcript-row').classList.contains('hidden'),false);f.handlers.pagehide();
  });
  await check('declined attestation sends nothing and preserves review',async()=>{
    const f=await fixture();await f.start();await f.stop();showTranscript(f,'reviewed synthetic transcript');
    const before=f.requests.length,lockBefore=f.run('isLocked'),submissionBefore=f.run('finalizationSubmission');
    assert.equal(lockBefore,true);assert.equal(submissionBefore,null);
    f.confirm(()=>false);await f.run('approveAndFinalize()');
    assert.equal(f.requests.length,before);assert.equal(f.affirmations.length,1);assert.equal(f.revoked.length,0);
    assert.equal(f.element('raw-transcript').value,'reviewed synthetic transcript');assert.equal(f.run('isLocked'),lockBefore);
    assert.equal(f.run('finalizationSubmission'),submissionBefore);
    assert.match(f.context.lastStatus,/Explicit clinician attestation/);
  });
  await check('missing confirmation host fails closed',async()=>{
    const f=await fixture();f.run('delete window.confirm');await f.run('approveAndFinalize()');
    assert.equal(f.requests.length,0);assert.equal(f.run('isLocked'),false);assert.match(f.context.lastStatus,/Not saved/);
  });
  await check('Word resolves before exact form snapshot and affirmation',async()=>{
    const f=await fixture(),d=deferred();let reads=0;f.wordSync(()=>++reads===1?d.promise:Promise.resolve());
    f.run('rxRowCount=1');f.element('rx-name-0').value='old synthetic drug';
    const pending=f.run('approveAndFinalize()');
    assert.equal(f.affirmations.length,0);f.element('rx-name-0').value='reviewed synthetic drug';
    f.element('rx-dose-0').value='synthetic dose';f.note.text='reviewed synthetic Word text';
    f.confirm(message=>{assert.match(message,/personally reviewed/);assert.match(message,/AI suggestions do not authorise/);return true;});
    d.resolve();await pending;assert.equal(reads,2);assert.equal(f.requests.length,1);
    const body=JSON.parse(f.requests[0].options.body);assert.equal(body.text_delta,'reviewed synthetic Word text');
    assert.equal(body.clinician_overrides.medications[0].drug_name,'reviewed synthetic drug');
    assert.equal(body.clinician_attested,true);assert.equal(body.patient_id,'A');
    assert.equal(body.document_context,'https://synthetic.invalid/word/A');
    assert.match(body.document_id,/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-8[0-9a-f]{3}-[0-9a-f]{12}$/);
    assert.deepEqual(Object.keys(body).sort(),['clinician_attested','clinician_overrides','document_context','document_id','patient_id','text_delta']);
  });
  await check('patient change during Word read cancels before attestation',async()=>{
    const f=await fixture(),d=deferred();f.wordSync(()=>d.promise);
    const pending=f.run('approveAndFinalize()');f.run('clearAudioSession();currentPatient={id:"B"}');
    d.resolve();await pending;assert.equal(f.affirmations.length,0);assert.equal(f.requests.length,0);
  });
  await check('identity change during Word read cancels before attestation',async()=>{
    const f=await fixture(),d=deferred();f.wordSync(()=>d.promise);
    const pending=f.run('approveAndFinalize()');f.run('token="different-synthetic-session"');
    d.resolve();await pending;assert.equal(f.affirmations.length,0);assert.equal(f.requests.length,0);
  });
  await check('patient change in confirmation cannot send stale snapshot',async()=>{
    const f=await fixture();f.confirm(()=>{f.run('clearAudioSession();currentPatient={id:"B"}');return true;});
    await f.run('approveAndFinalize()');assert.equal(f.affirmations.length,1);assert.equal(f.requests.length,0);
  });
  await check('each changed-content or newly started patient attempt requires fresh attestation',async()=>{
    const f=await fixture();f.confirm(()=>false);
    await f.run('approveAndFinalize()');assert.equal(f.requests.length,0);assert.equal(f.affirmations.length,1);
    f.note.text='edited synthetic text';
    await f.run('approveAndFinalize()');assert.equal(f.requests.length,0);assert.equal(f.affirmations.length,2);
    f.run('invalidateConsultationBinding();currentPatient={id:"B",document_url:"https://synthetic.invalid/word/B",first_name:"Synthetic",last_name:"Patient B",date_of_birth:"1990-01-01"};Office.context.document.url=currentPatient.document_url');
    await f.run('window.startConsultation()');
    const header=f.paragraphs.find(p=>p.text.startsWith(f.run('lastConsultHeader')));
    header.insertParagraph('patient B synthetic notes');
    await f.run('approveAndFinalize()');
    assert.equal(f.requests.length,0);assert.equal(f.affirmations.length,3);
  });
  await check('unsigned-in finalize cannot read Word or attest',async()=>{
    const f=await fixture();f.run('token=null');f.wordSync(()=>{throw Error("must not read Word");});
    await f.run('approveAndFinalize()');assert.equal(f.requests.length,0);assert.equal(f.affirmations.length,0);
    assert.match(f.context.lastStatus,/Sign in/);
  });
  await check('real getter reads only the uniquely started consultation',async()=>{
    const f=await fixture();
    f.paragraphs.push(f.paragraph('14-09-2026  Synthetic Older Patient  9 AM  36 years old.'));
    f.paragraphs.push(f.paragraph('older consultation must not escape'));
    f.paragraphs.push(f.paragraph('Medical History','Heading1'));
    f.paragraphs.push(f.paragraph('other section must not escape'));
    assert.equal(await f.run('getCurrentConsultText()'),'synthetic');
    assert(f.run('lastConsultHeader').includes(f.run('consultationBinding.commandId')));
  });
  await check('no started consultation means no Word read or affirmation',async()=>{
    const f=await fixture({started:false});f.wordSync(()=>{throw Error("must not read Word");});
    await f.run('approveAndFinalize()');assert.equal(f.requests.length,0);assert.equal(f.affirmations.length,0);
    assert.match(f.context.lastStatus,/Start a consultation/);
  });
  for(const mutation of [
    'Office.context.document.url=""',
    'Office.context.document.url="https://synthetic.invalid/word/B"',
    'currentPatient.document_url=""',
    'currentPatient.document_url="https://synthetic.invalid/word/B"',
  ]) {
    await check('document association fails closed: '+mutation,async()=>{
      const f=await fixture();f.run(mutation);
      await assert.rejects(f.run('getCurrentConsultText()'),/binding/);
      await f.run('approveAndFinalize()');assert.equal(f.requests.length,0);assert.equal(f.affirmations.length,0);
      const fresh=await fixture({started:false});fresh.run(mutation);const count=fresh.paragraphs.length;
      await fresh.run('window.startConsultation()');
      assert.equal(fresh.run('consultStarted'),false);assert.equal(fresh.paragraphs.length,count);
    });
  }
  for(const damage of ['missing header','old header','missing section','duplicate marker','duplicate inline marker','edited header','header in another section']) {
    await check('real getter rejects '+damage+' without fallback',async()=>{
      const f=await fixture(),header=f.paragraphs[1];
      if(damage==='missing header')f.paragraphs.splice(1,1);
      if(damage==='old header')header.text='14-09-2026  Synthetic Old Patient  9 AM  36 years old.';
      if(damage==='missing section')f.paragraphs.splice(0,1);
      if(damage==='duplicate marker')f.paragraphs.push(f.paragraph(header.text));
      if(damage==='duplicate inline marker')header.text+=' '+f.run('consultationBinding.marker');
      if(damage==='edited header')header.text='Changed '+header.text;
      if(damage==='header in another section')f.paragraphs.splice(1,0,f.paragraph('Medical History','Heading1'));
      await assert.rejects(f.run('getCurrentConsultText()'));
      await f.run('approveAndFinalize()');assert.equal(f.requests.length,0);assert.equal(f.affirmations.length,0);
    });
  }
  await check('failed Word insertion cannot publish a consultation binding',async()=>{
    const f=await fixture({started:false});let syncs=0;
    f.wordSync(async()=>{if(++syncs===2)throw Error('authored Word commit failure');});
    await f.run('window.startConsultation()');
    assert.equal(f.run('consultStarted'),false);assert.equal(f.run('consultationBinding'),null);
    assert.equal(f.run('lastConsultHeader'),'');assert.equal(f.element('btn-finalize').disabled,true);
    await f.run('approveAndFinalize()');assert.equal(f.requests.length,0);
  });
  await check('patient selection during header insertion cannot publish the old binding',async()=>{
    const f=await fixture({started:false}),d=deferred();f.wordSync(()=>d.promise);
    const starting=f.run('window.startConsultation()');f.run('apiFetch=async()=>null');
    await f.run('loadPatient("B")');assert.equal(f.element('btn-finalize').disabled,true);
    d.resolve();await starting;
    assert.equal(f.run('consultationBinding'),null);assert.equal(f.run('lastConsultHeader'),'');
    assert.equal(f.paragraphs.length,1);
  });
  await check('completed patient change and out-of-order summaries cannot reuse A notes',async()=>{
    const f=await fixture(),b=deferred(),c=deferred();f.context.b=b.promise;f.context.c=c.promise;
    f.run('apiFetch=path=>path.includes("/B/")?b:c');
    const selectingB=f.run('loadPatient("B")');
    assert.equal(f.element('btn-finalize').disabled,true);assert.equal(f.run('consultationBinding'),null);
    const selectingC=f.run('loadPatient("C")');
    c.resolve({ok:true,json:async()=>({patient:{id:'C',document_url:'https://synthetic.invalid/word/C'},allergies:[]})});
    await selectingC;
    b.resolve({ok:true,json:async()=>({patient:{id:'B',document_url:'https://synthetic.invalid/word/B'},allergies:[]})});
    await selectingB;assert.equal(f.run('audioPatientId()'),'C');
    await f.run('approveAndFinalize()');assert.equal(f.requests.length,0);assert.equal(f.affirmations.length,0);
    assert.equal(f.element('btn-finalize').disabled,true);
  });
  for(const edit of ['form','Word']) {
    await check('post-confirmation reread rejects changed '+edit,async()=>{
      const f=await fixture();f.run('rxRowCount=1');f.element('rx-name-0').value='reviewed synthetic drug';
      f.confirm(()=>{
        if(edit==='form')f.element('rx-name-0').value='later synthetic edit';
        else f.note.text='later synthetic notes';
        return true;
      });
      await f.run('approveAndFinalize()');assert.equal(f.affirmations.length,1);assert.equal(f.requests.length,0);
      assert.match(f.context.lastStatus,/changed during confirmation/);
    });
  }
  await check('patient change during the second Word read cancels the confirmed snapshot',async()=>{
    const f=await fixture(),d=deferred();let reads=0;f.wordSync(()=>++reads===2?d.promise:Promise.resolve());
    const pending=f.run('approveAndFinalize()');await tick();assert.equal(f.affirmations.length,1);
    f.run('apiFetch=async()=>null');await f.run('loadPatient("B")');d.resolve();await pending;
    assert.equal(f.requests.length,0);
  });
  await check('overlapping finalization clicks issue one request and one affirmation',async()=>{
    const f=await fixture(),d=deferred();f.fetch(()=>d.promise);
    const first=f.run('approveAndFinalize()');await tick();
    await f.run('approveAndFinalize()');assert.equal(f.requests.length,1);assert.equal(f.affirmations.length,1);
    d.resolve({ok:true,json:async()=>({_saved:true,encounter_id:'00000000-0000-4000-8000-000000000101'})});
    await first;await f.run('approveAndFinalize()');
    assert.equal(f.requests.length,1);assert.equal(f.run('consultationBinding'),null);
  });
  await check('ambiguous retry preserves exact command payload and requires new affirmation',async()=>{
    const f=await fixture();f.fetch(async()=>{throw Error('authored lost response');});
    await f.run('approveAndFinalize()');const first=f.requests[0].options.body;
    f.fetch(async()=>({ok:true,json:async()=>({_saved:true,encounter_id:'00000000-0000-4000-8000-000000000101'})}));
    await f.run('approveAndFinalize()');
    assert.equal(f.requests.length,2);assert.equal(f.affirmations.length,2);
    assert.equal(f.requests[1].options.body,first);assert.equal(f.run('consultationBinding'),null);
  });
  await check('ambiguous save cannot be retried with changed content',async()=>{
    const f=await fixture();f.fetch(async()=>{throw Error('authored lost response');});
    await f.run('approveAndFinalize()');f.note.text='changed synthetic notes';
    await f.run('approveAndFinalize()');assert.equal(f.requests.length,1);assert.equal(f.affirmations.length,1);
    assert.match(f.context.lastStatus,/Previous save may have completed/);
  });
  for(const result of [{},{_saved:true},{_saved:true,encounter_id:''},{_saved:true,encounter_id:'not-a-uuid'},{_saved:true,encounter_id:'A0000000-0000-4000-8000-000000000001'}]) {
    await check('incomplete success response cannot report a finalized record: '+JSON.stringify(result),async()=>{
      const f=await fixture();f.fetch(async()=>({ok:true,json:async()=>result}));
      await f.run('approveAndFinalize()');assert.equal(f.run('isLocked'),false);
      assert.equal(f.run('consultStarted'),true);assert.match(f.context.lastStatus,/Save not confirmed/);
    });
  }
  await check('late finalized JSON after patient selection is inert',async()=>{
    const f=await fixture(),d=deferred();f.fetch(async()=>({ok:true,json:()=>d.promise}));
    const pending=f.run('approveAndFinalize()');await tick();
    f.run('apiFetch=async()=>null');await f.run('loadPatient("B")');
    d.resolve({_saved:true,encounter_id:'00000000-0000-4000-8000-000000000101'});await pending;
    assert.equal(f.run('isLocked'),false);assert.equal(f.run('consultationBinding'),null);
    assert.notEqual(f.context.lastStatus,'Record finalised and saved.');
  });
  await check('a subsequent successfully started consult gets a fresh full command UUID',async()=>{
    const f=await fixture(),first=f.run('consultationBinding.commandId');
    f.fetch(async()=>({ok:true,json:async()=>({_saved:true,encounter_id:'00000000-0000-4000-8000-000000000101'})}));
    await f.run('approveAndFinalize()');await f.run('window.startConsultation()');
    assert.notEqual(f.run('consultationBinding.commandId'),first);
    assert.equal(await f.run('getCurrentConsultText()'),'');
  });
  await check('date and age bearing prose never truncates the exact consultation',async()=>{
    const f=await fixture();
    const dated=f.note.insertParagraph('15-09-2026 reviewed today; patient is 36 years old');
    dated.insertParagraph('important later synthetic note');
    assert.equal(await f.run('getCurrentConsultText()'),'synthetic\n15-09-2026 reviewed today; patient is 36 years old\nimportant later synthetic note');
    await f.run('approveAndFinalize()');
    assert.equal(JSON.parse(f.requests[0].options.body).text_delta,'synthetic\n15-09-2026 reviewed today; patient is 36 years old\nimportant later synthetic note');
  });
  for(const damage of ['missing','duplicate','edited','before start','crossing section']) {
    await check('exact consultation END boundary fails closed: '+damage,async()=>{
      const f=await fixture(),end=f.run('consultationBinding.endMarker');
      const index=f.paragraphs.findIndex(p=>p.text===end),closing=f.paragraphs[index];
      if(damage==='missing')f.paragraphs.splice(index,1);
      if(damage==='duplicate')f.paragraphs.push(f.paragraph(end));
      if(damage==='edited')closing.text+=' edited';
      if(damage==='before start'){f.paragraphs.splice(index,1);f.paragraphs.splice(1,0,closing);}
      if(damage==='crossing section')f.paragraphs.splice(index,0,f.paragraph('Medical History','Heading1'));
      await assert.rejects(f.run('getCurrentConsultText()'));
      await f.run('approveAndFinalize()');assert.equal(f.requests.length,0);assert.equal(f.affirmations.length,0);
    });
  }
  for(const state of ['starting','saving','ambiguous']) {
    await check('Command Centre cannot overlap taskpane '+state,async()=>{
      const f=await fixture({started:state!=='starting'}),d=deferred();let pending,opened=0;
      f.context.Office.context.ui={displayDialogAsync(){opened++;}};
      if(state==='starting'){
        f.wordSync(()=>d.promise);pending=f.run('window.startConsultation()');
      } else {
        f.fetch(state==='saving'?()=>d.promise:async()=>{throw Error('authored ambiguous save');});
        pending=f.run('approveAndFinalize()');await tick();
        if(state==='ambiguous')await pending;
      }
      f.run('openCommandCentre()');assert.equal(opened,0);assert.equal(f.run('commandCentreOpen'),false);
      assert.match(f.context.lastStatus,/Resolve the current consultation/);
      if(state==='starting'){d.resolve();await pending;}
      if(state==='saving'){d.resolve({ok:false,status:503});await pending;}
    });
  }
  await check('taskpane cannot finalize while Command Centre owns editing',async()=>{
    const f=await fixture();f.run('commandCentreOpen=true');
    f.wordSync(()=>{throw Error('must not read Word');});
    await f.run('approveAndFinalize()');assert.equal(f.requests.length,0);assert.equal(f.affirmations.length,0);
    assert.match(f.context.lastStatus,/Close Command Centre/);
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
    assert len(report["cases"]) == 67
