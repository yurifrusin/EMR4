"use strict";
// Source-authored focused checks. Not executed by this author.
// VM-selected production functions + explicit substituted DOM/audio/fetch only.
// No browser, microphone, OS permission, backend, human semantic or M1 proof.
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),vm=require("node:vm");
const sourceRoot=path.resolve(__dirname,"../static/demo");
const pins={
  "stage1-interactive.html": "e14c725709ad9b06b99e69f336719ee095ba7aa1f3213cfc5f26d8295ccc4c80",
  "stage1-interactive.js": "98930fc6bfd1bccec823bfd343ee2913085cc22036952cb3aea9f6c5401c31e8",
  "stage1-local-voice.js": "9b499ec41afaa993a8dfedd860ff4129abda5ff1b6223d53311ca6c45378bbfb"
};
const texts={};
for(const [name,sha]of Object.entries(pins)){
  const raw=fs.readFileSync(path.join(sourceRoot,name));
  assert.equal(crypto.createHash("sha256").update(raw).digest("hex"),sha,"exact_source_pin");
  texts[name]=raw.toString("utf8");
}
function between(source,start,end){
  const a=source.indexOf(start),b=source.indexOf(end,a+start.length);
  assert(a>=0&&b>a,"exact_selected_definition_boundaries");return source.slice(a,b);
}
const voiceEnd=texts["stage1-local-voice.js"].indexOf("// A browser voice");
assert(voiceEnd>0,"exact_voice_boundary");
const voicePrefix=texts["stage1-local-voice.js"].slice(0,voiceEnd);
assert(voicePrefix.length>1000,"voice_prefix_boundary");
const definitions=voicePrefix.replace(/^export /gm,"");
const pureContext=vm.createContext({});
new vm.Script(definitions+";globalThis.factory=createManualIntentHandoff;globalThis.same=sameVoiceTarget;",
  {filename:"reviewed_voice_definitions"}).runInContext(pureContext);
const factory=pureContext.factory;
let cases=0,currentCase="source_setup";
async function check(name,fn){currentCase=name;await fn();cases++;}
function request(words="Authored fictional follow-up note"){
  return {kind:"request",scope:"patient:fixture-session",request_id:"request-A",request_version:1,
    appointment_ref:null,appointment_version:null,words,
    fields:{date:"2026-10-22",earliest_local:"14:15",latest_local:"17:00"}};
}
function move(words="Authored fictional move note"){
  return {kind:"move",scope:"staff:fixture-session",request_id:"request-A",request_version:1,
    appointment_ref:"appointment-A",appointment_version:2,words,
    fields:{date:"2026-10-22",local_time:"15:00"}};
}
function copy(value){return JSON.parse(JSON.stringify(value));}
function element(value=""){
  const handlers=new Map();return {value,checked:false,disabled:false,hidden:false,textContent:"",maxLength:500,
    focus(){},addEventListener(type,fn){const list=handlers.get(type)||[];list.push(fn);handlers.set(type,list);},
    dispatchEvent(event){for(const fn of handlers.get(event.type)||[])fn(event);},
    querySelector(){return {focus(){}};},
    click(){this.dispatchEvent({type:"click"});}};
}
function uiFixture(kind="request"){
  const fields={};for(const id of ["patient-words","move-words","request-date","request-earliest","request-latest",
    "move-date","move-time","request-mapping-ack","move-mapping-ack","request-mapping","move-mapping",
    "request-mapping-status","move-mapping-status","request-review-box","request-summary","request-submit",
    "move-review","move-summary","move-confirm","create-review","create-cancel","staff-offers","reconcile","request-suggest","move-suggest"])fields[id]=element();
  Object.assign(fields["patient-words"],{value:"Authored fictional follow-up note"});
  fields["move-words"].value="Authored fictional move note";
  fields["request-date"].value=fields["move-date"].value="2026-10-22";
  fields["request-earliest"].value="14:15";fields["request-latest"].value="17:00";fields["move-time"].value="15:00";
  const appointment={ref:"appointment-A",state_version:2,date:"2026-10-22",start_local:"10:00",zone:"Australia/Brisbane",
    patient_label:"Fictional patient",practitioner_label:"Fictional clinician",type_label:"Follow-up",duration_minutes:20,location_label:"Synthetic room"};
  const state={session:{persona:kind==="request"?"patient":"staff",csrf:"fixture-session",zone:"Australia/Brisbane"},
    request:{request_id:"request-A",request_version:1,state:"draft"},appointment,create:null,move:null,offer:null,
    requestReview:null,moveReview:null,pendingKey:null,busy:false};
  const calls=[],messages=[],interpretations=[];
  const interpretedNotes={request:null,move:null},interpretationGeneration={request:0,move:0};let localVoice=null;
  const context=vm.createContext({createManualIntentHandoff:factory,state,interpretedNotes,interpretationGeneration,localVoice,$:id=>{assert(fields[id],"known_DOM_id");return fields[id];},
    text:(id,value)=>{fields[id].textContent=value;},show:(id,value)=>{fields[id].hidden=!value;},
    spoken:{stop(){},offer(){}},status:value=>messages.push(value),uuid:()=>"authored-fixture-key",
    dateTime:(date,clock,zone)=>date+" at "+clock+" "+zone,
    facts(){},fetch:async(url,options)=>{
      assert.equal(url,"/demo/stage1/interpret");
      const input=JSON.parse(options.body);assert.equal(input.words,fields[input.kind==="request"?"patient-words":"move-words"].value);
      interpretations.push({url,kind:input.kind,words:input.words});
      return {ok:true,json:async()=>({schema:"emr4.stage1_word_interpretation.v1",status:state.session.interpretedStatus||"PROPOSED",kind:input.kind,
        method:"DETERMINISTIC_LOCAL",fields:input.kind==="request"?
          {date:state.session.interpreted.date,earliest_local:state.session.interpreted.earliest_local,latest_local:state.session.interpreted.latest_local}:
          {target_date:state.session.interpreted.date,target_start_local:state.session.interpreted.local_time},missing:[],message:"DETAILS_PROPOSED"})};
    },api:async(method,action,body,key)=>{
      calls.push({method,action,body:copy(body),key});
      if(action==="propose_move")return {safe:true,proposal_ref:"authored-proposal"};
      if(action==="confirm_move")return {outcome:"committed",appointment:{ref:"appointment-A",date:"2026-10-22",start_local:"15:00"}};
      return {request:state.request};
    },displayRequest(){},refresh:async()=>({appointment:{...appointment,start_local:"15:00"}})});
  const ui=texts["stage1-interactive.js"];
  const body=between(ui,"const intentHandoffs=","async function api(")+
    between(ui,"function clearPending()","function displayRequest(")+
    between(ui,"function requestFields()","async function reviewCreate(")+
    between(ui,"async function reviewMove()",'$("request-review").addEventListener');
  const cancel=between(ui,'$("create-cancel").addEventListener','$("move-propose").addEventListener');
  const apiActual=between(ui,"async function api(","\nfunction facts(").replace("async function api(","async function apiActual(");
  new vm.Script(apiActual,{filename:"reviewed_production_api"}).runInContext(context);
  new vm.Script(body+cancel+";globalThis.testUI={reviewRequest,submitRequest,reviewMove,confirmMove,acceptMapping,invalidateIntent,intentSnapshot,intentHandoffs,suggestFromWords,hasCurrentInterpretation,showWriteFailure};globalThis.setPending=value=>{localVoice={isIdle:()=>!value,invalidateTarget(){}};};",
    {filename:"reviewed_UI_mapping_and_command_functions"}).runInContext(context);
  state.session.interpreted={date:"2026-10-22",earliest_local:"14:15",latest_local:"17:00",local_time:"15:00"};
  return {context,fields,state,calls,messages,interpretations,ui:context.testUI};
}
async function settle(){for(let i=0;i<32;i++)await Promise.resolve();}
function voiceFixture({selection="appointment-A:v2",deferSession=false,deferVoice=false}={}){
  const fields={};for(const id of ["voice-toggle","voice-cancel","voice-note","voice-availability","move-words","patient-words"])fields[id]=element();
  const session={persona:"staff",csrf:"fixture-csrf",voice_available:true,voice_nonce:"fixture-nonce"};
  const calls=[],timers=new Map();let nextTimer=0,mediaCalls=0,stops=0,invalidations=0,sessionResolve,voiceResolve,processor=null;
  const track={stop(){stops++;},addEventListener(){}};
  const stream={getTracks:()=>[track]};
  const node=()=>({connect(){},disconnect(){}});
  class AudioContextStub{
    constructor(){this.sampleRate=16000;}
    async resume(){} async close(){}
    createMediaStreamSource(){return node();}
    createScriptProcessor(){processor={...node(),onaudioprocess:null};return processor;}
    createGain(){return {...node(),gain:{value:1}};}
    get destination(){return {};}
  }
  const response=value=>({ok:true,json:async()=>value});
  const context=vm.createContext({document:{hidden:false,getElementById:id=>fields[id],addEventListener(){}},
    window:{AudioContext:AudioContextStub,addEventListener(){}},AudioContext:AudioContextStub,
    navigator:{mediaDevices:{getUserMedia:async()=>{mediaCalls++;return stream;}}},
    Blob,AbortController,Event:class{constructor(type){this.type=type;}},
    setTimeout:fn=>{const id=++nextTimer;timers.set(id,fn);return id;},clearTimeout:id=>timers.delete(id),
    fetch:async(url,options={})=>{
      calls.push({url,options});
      if(url==="/demo/stage1/voice"){
        if(deferVoice)return new Promise(resolve=>{voiceResolve=resolve;});
        return response({target:"move-words",text:"Authored fictional transcript"});
      }
      assert.equal(url,"/demo/stage1/session","only_authored_fixture_routes");
      if(deferSession){deferSession=false;return new Promise(resolve=>{sessionResolve=resolve;});}
      return response({...session});
    }});
  new vm.Script(definitions+";globalThis.testInit=initLocalVoice;",{filename:"reviewed_voice_definitions"}).runInContext(context);
  const controller=context.testInit(()=>session,()=>{},()=>selection,()=>{invalidations++;},()=>{});
  return {fields,calls,session,controller,get mediaCalls(){return mediaCalls;},get stops(){return stops;},
    get invalidations(){return invalidations;},setSelection:value=>{selection=value;},
    resolveSession:()=>sessionResolve(response({...session})),
    resolveVoice:()=>voiceResolve(response({target:"move-words",text:"Authored fictional transcript"})),
    feed(){assert(processor&&processor.onaudioprocess,"synthetic_processor_ready");processor.onaudioprocess({inputBuffer:{getChannelData:()=>new Float32Array([0.25,-0.25])}});}};
}
async function main(){

  await check("progress_renderer_distinguishes_both_delivered_classes_and_reuse",()=>{
    const made=[],paragraphs=[];
    const root={append(){}};
    const context=vm.createContext({document:{createElement:tag=>{const n={tag,textContent:"",append(){}};made.push(n);return n;}},
      labParagraph:(_,value)=>paragraphs.push(value),facts(){}});
    const source=texts["stage1-interactive.js"],start=source.indexOf("function displayLabProgress("),end=source.indexOf("\nfunction ",start+1);
    assert(start>=0&&end>start,"selected_actual_progress_renderer");
    new vm.Script(source.slice(start,end)+";globalThis.render=displayLabProgress;").runInContext(context);
    const example=(case_id,evidence_kind)=>({case_id,evidence_kind,authored_request:"Authored synthetic words",authored_expected_proposal:"Authored time",
      proposal_observation:"UNKNOWN",actual_validation:"UNKNOWN",before_after:{before:"UNKNOWN",after:"UNKNOWN"},readback:"UNKNOWN",command_audit:"UNKNOWN",outcome:"UNKNOWN"});
    context.render(root,{schema:"emr4.stage1_reliability_progress_view.v2",evidence_through:"NATIVE09_REVIEWED_DELIVERED",catalog_cases:16,catalog_families:11,
      baseline_dispositions:{current_controls:2,qualified_reused_boundaries:4,not_run:10},attempts:[],worked_examples:[
        example("create-valid-01","NATIVE04_DELIVERED_CONTROL"),example("move-valid-timeonly-01","CURRENT_DELIVERED_CONTROL"),example("move-source-cancelled-08","QUALIFIED_REUSED_BOUNDARY")],
      whole_journey_grade:"UNKNOWN",display:"NOT_OBSERVED",disclosure:"NOT_OBSERVED",actual_model:"NOT_RUN",m1_model_binding:"OPEN",generated_silence_voice:"NOT_RUN",genuine_ptt_voice:"NOT_RUN"});
    const titles=made.filter(n=>n.tag==="h4").map(n=>n.textContent);
    assert.equal(titles.filter(x=>x.endsWith("delivered control")).length,2);
    assert.equal(titles.filter(x=>x.endsWith("reused boundary")).length,1);
    assert(paragraphs[0].includes("NATIVE09_REVIEWED_DELIVERED"));
    assert(!paragraphs[0].includes("through Native08"));
  });

  await check("structured_only_fallback",()=>{for(const value of [request(""),move("")]){const m=factory();assert(m.isReviewCurrent(value,m.review(value)));}});
  await check("unacknowledged_note_rejected",()=>{assert.throws(()=>factory().review(request()),/MAPPING_REQUIRED/);});
  await check("explicit_current_ack_positive",()=>{const m=factory(),v=request();m.acknowledge(v);assert(m.isReviewCurrent(v,m.review(v)));});
  await check("replaced_words_rejected",()=>{const m=factory(),v=request();m.acknowledge(v);const r=m.review(v);assert.equal(m.isReviewCurrent({...v,words:"Different authored note"},r),false);});
  await check("edit_and_revert_does_not_restore_ack",()=>{const m=factory(),v=request();m.acknowledge(v);const r=m.review(v),n=m.revision();m.invalidate();assert(m.revision()>n);assert.equal(m.isReviewCurrent(v,r),false);assert.throws(()=>m.review(v),/MAPPING_REQUIRED/);});
  await check("structured_detail_changes_rejected",()=>{for(const [kind,field,value]of [["request","date","2026-10-23"],["request","earliest_local","14:30"],["request","latest_local","16:30"],["move","date","2026-10-23"],["move","local_time","15:30"]]){const m=factory(),v=kind==="request"?request():move();m.acknowledge(v);const r=m.review(v),changed=copy(v);changed.fields[field]=value;assert.equal(m.isReviewCurrent(changed,r),false);}});
  await check("target_session_version_changes_rejected",()=>{for(const [field,value]of [["scope","other-persona:other-session"],["request_id","request-B"],["request_version",2],["appointment_ref","appointment-B"],["appointment_version",3]]){const m=factory(),v=move();m.acknowledge(v);const r=m.review(v);assert.equal(m.isReviewCurrent({...v,[field]:value},r),false);}});
  await check("unsupported_and_extra_shapes_rejected",()=>{for(const v of [{...request(),kind:"unknown"},{...request(),extra:true},{...request(),words:"x".repeat(501)},{...move(),appointment_ref:null},{...request(),request_version:-1},{...request(),fields:{...request().fields,earliest_local:"17:30"}},{...move(),fields:{date:"2026-10-22",local_time:"15:00:00"}}]){assert.throws(()=>factory().acknowledge(v),/MAPPING_UNSUPPORTED/);}});
  await check("ack_never_mutates_or_translates_note",()=>{const v=request("A deliberately ambiguous authored note"),before=JSON.stringify(v),m=factory();m.acknowledge(v);m.review(v);assert.equal(JSON.stringify(v),before);});
  await check("clearing_note_requires_fresh_review",()=>{const v=request(),m=factory();m.acknowledge(v);const old=m.review(v),blank={...v,words:""};assert.equal(m.isReviewCurrent(blank,old),false);assert(m.isReviewCurrent(blank,m.review(blank)));});
  await check("UI_unacknowledged_review_and_write_blocked",async()=>{const f=uiFixture();f.ui.reviewRequest();assert.equal(f.state.requestReview,null);await f.ui.submitRequest();assert.equal(f.calls.length,0);});
  await check("UI_revoked_staff_access_denial_is_definitive_without_retry",async()=>{for(const statusCode of [401,403]){const f=uiFixture("move");f.state.pendingKey="authored-pending-key";let calls=0;f.context.fetch=async()=>{calls++;return {ok:false,status:statusCode};};let caught;try{await f.context.apiActual("write","confirm_move",{proposal_ref:"authored-proposal"},"authored-key");}catch(error){caught=error;}assert(caught);f.ui.showWriteFailure(caught,"Move");assert.equal(calls,1);assert.equal(f.state.session,null);assert.equal(f.state.pendingKey,null);assert.equal(f.fields.reconcile.hidden,true);assert(f.messages.at(-1).includes("cannot perform that action"));assert(!f.messages.at(-1).includes("outcome uncertain"));assert(!f.messages.at(-1).includes("confirmed"));}});
  await check("UI_conflict_write_remains_uncertain",()=>{const f=uiFixture("move");f.state.pendingKey="authored-pending-key";f.ui.showWriteFailure({status:409,message:"Current facts changed. Refresh and review again."},"Move");assert.equal(f.fields.reconcile.hidden,false);assert.equal(f.state.pendingKey,"authored-pending-key");assert(f.messages.at(-1).includes("outcome uncertain"));});
  await check("UI_manual_ack_preserves_closed_request_body",async()=>{const f=uiFixture();await f.ui.suggestFromWords("request");f.fields["request-mapping-ack"].checked=true;f.ui.acceptMapping("request");f.ui.reviewRequest();await f.ui.submitRequest();assert.equal(f.calls.length,1);assert.equal(f.calls[0].action,"submit_request");assert.deepEqual(Object.keys(f.calls[0].body).sort(),["date","earliest_local","latest_local","reason_code","request_version"].sort());assert.equal(f.calls[0].body.reason_code,"follow_up");assert.equal(f.fields["patient-words"].value,"Authored fictional follow-up note");});
  await check("UI_manual_ack_alone_cannot_allow_nonblank_note",async()=>{const f=uiFixture();f.fields["request-mapping-ack"].checked=true;f.ui.acceptMapping("request");f.ui.reviewRequest();await f.ui.submitRequest();assert.equal(f.calls.length,0);assert.equal(f.state.requestReview,null);});
  await check("UI_suggestion_prefills_without_command_until_human_review",async()=>{const f=uiFixture();await f.ui.suggestFromWords("request");assert.equal(f.interpretations.length,1);assert.equal(f.interpretations[0].kind,"request");assert.equal(f.interpretations[0].words,"Authored fictional follow-up note");assert.deepEqual([f.fields["request-date"].value,f.fields["request-earliest"].value,f.fields["request-latest"].value],["2026-10-22","14:15","17:00"]);assert.equal(f.calls.length,0);assert.equal(f.state.requestReview,null);});
  await check("UI_move_suggestion_uses_closed_interpretation_kind_and_waits_for_review",async()=>{const f=uiFixture("move");await f.ui.suggestFromWords("move");assert.deepEqual(f.interpretations,[{url:"/demo/stage1/interpret",kind:"move",words:"Authored fictional move note"}]);assert.deepEqual([f.fields["move-date"].value,f.fields["move-time"].value],["2026-10-22","15:00"]);assert.equal(f.calls.length,0);f.fields["move-mapping-ack"].checked=true;f.ui.acceptMapping("move");await f.ui.reviewMove();assert.equal(f.calls.length,1);assert.equal(f.calls[0].action,"propose_move");});
  await check("UI_clarification_does_not_adopt_or_act",async()=>{const f=uiFixture();f.state.session.interpretedStatus="CLARIFICATION";f.fields["request-date"].value="2026-10-24";await f.ui.suggestFromWords("request");assert.equal(f.fields["request-date"].value,"2026-10-24");assert.equal(f.ui.hasCurrentInterpretation("request"),false);assert.equal(f.state.requestReview,null);assert.equal(f.calls.length,0);});
  await check("UI_late_interpretation_after_current_context_edit_is_refused",async()=>{for(const change of ["words","target","session","version"]){const f=uiFixture();let resolve;f.context.fetch=async()=>new Promise(r=>{resolve=r;});const pending=f.ui.suggestFromWords("request");if(change==="words")f.fields["patient-words"].value+=" edited";if(change==="target")f.fields["request-date"].value="2026-10-23";if(change==="session")f.state.session.csrf="changed-fixture-session";if(change==="version")f.state.request={...f.state.request,request_version:2};if(change!=="session" && change!=="version")f.ui.invalidateIntent("request");resolve({ok:true,json:async()=>({schema:"emr4.stage1_word_interpretation.v1",status:"PROPOSED",kind:"request",method:"DETERMINISTIC_LOCAL",fields:{date:"2026-10-22",earliest_local:"14:15",latest_local:"17:00"},missing:[],message:"DETAILS_PROPOSED"})});await pending;assert.equal(f.ui.hasCurrentInterpretation("request"),false);assert.equal(f.calls.length,0);assert.equal(f.state.requestReview,null);}});
  await check("UI_create_cancel_preserves_move_handoff_acknowledgement",async()=>{const f=uiFixture("move");await f.ui.suggestFromWords("move");f.fields["move-mapping-ack"].checked=true;f.ui.acceptMapping("move");const revision=f.ui.intentHandoffs.move.revision();f.state.move="authored-proposal";f.fields["create-cancel"].click();assert.equal(f.ui.intentHandoffs.move.revision(),revision);assert.equal(f.ui.intentHandoffs.move.inspect(f.ui.intentSnapshot("move")).acknowledged,true);});
  await check("UI_changed_detail_blocks_old_submit",async()=>{const f=uiFixture();await f.ui.suggestFromWords("request");f.fields["request-mapping-ack"].checked=true;f.ui.acceptMapping("request");f.ui.reviewRequest();f.fields["request-earliest"].value="14:30";await f.ui.submitRequest();assert.equal(f.calls.length,0);});
  await check("UI_pending_capture_blocks_ack_and_review",async()=>{const f=uiFixture();await f.ui.suggestFromWords("request");f.context.setPending(true);f.fields["request-mapping-ack"].checked=true;f.ui.acceptMapping("request");f.ui.reviewRequest();assert.equal(f.state.requestReview,null);assert.equal(f.fields["request-mapping-ack"].checked,false);});
  await check("UI_stale_async_move_proposal_not_adopted",async()=>{const f=uiFixture("move");await f.ui.suggestFromWords("move");let resolve;f.context.api=async()=>new Promise(r=>{resolve=r;});f.fields["move-mapping-ack"].checked=true;f.ui.acceptMapping("move");const pending=f.ui.reviewMove();f.fields["move-time"].value="15:30";f.ui.invalidateIntent("move");resolve({safe:true,proposal_ref:"stale-proposal"});await pending;assert.equal(f.state.move,null);assert.equal(f.state.moveReview,null);});
  await check("UI_current_move_positive_and_changed_target_blocks_confirm",async()=>{const f=uiFixture("move");await f.ui.suggestFromWords("move");f.fields["move-mapping-ack"].checked=true;f.ui.acceptMapping("move");await f.ui.reviewMove();assert.equal(f.state.move,"authored-proposal");assert.equal(f.calls[0].action,"propose_move");assert.deepEqual(Object.keys(f.calls[0].body).sort(),["appointment_ref","source_state_version","target_date","target_start_local"].sort());f.state.appointment={...f.state.appointment,ref:"appointment-B"};await f.ui.confirmMove();assert.equal(f.calls.length,1);assert.equal(f.state.move,null);});
  await check("UI_structured_only_path_stays_usable",async()=>{const f=uiFixture();f.fields["patient-words"].value="";f.ui.reviewRequest();await f.ui.submitRequest();assert.equal(f.calls.length,1);});
  await check("voice_target_key_refuses_unknown_or_stale",()=>{assert.equal(pureContext.same("target-A","target-A"),true);for(const v of [null,undefined,"","target-B","x".repeat(4097)])assert.equal(pureContext.same("target-A",v),false);});
  await check("substituted_voice_current_target_insertion",async()=>{const f=voiceFixture();f.fields["voice-toggle"].click();await settle();assert.equal(f.mediaCalls,1);f.feed();f.fields["voice-toggle"].click();await settle();assert.equal(f.fields["move-words"].value,"Authored fictional transcript");assert.equal(f.calls.filter(r=>r.url==="/demo/stage1/voice").length,1);assert.equal(f.controller.isIdle(),true);assert(f.stops>=1);});
  await check("substituted_target_change_before_permission_blocks_capture",async()=>{const f=voiceFixture({deferSession:true});f.fields["voice-toggle"].click();await settle();f.setSelection("appointment-B:v1");f.controller.invalidateTarget();f.resolveSession();await settle();assert.equal(f.mediaCalls,0);assert.equal(f.fields["move-words"].value,"");assert.equal(f.controller.isIdle(),true);});
  await check("substituted_active_target_change_closes_capture",async()=>{const f=voiceFixture();f.fields["voice-toggle"].click();await settle();f.setSelection("appointment-B:v1");f.controller.invalidateTarget();await settle();assert(f.stops>=1);assert.equal(f.calls.filter(r=>r.url==="/demo/stage1/voice").length,0);assert.equal(f.controller.isIdle(),true);});
  await check("substituted_cancelled_transcription_late_result_rejected",async()=>{const f=voiceFixture({deferVoice:true});f.fields["voice-toggle"].click();await settle();f.feed();f.fields["voice-toggle"].click();await settle();f.setSelection("appointment-B:v1");f.controller.invalidateTarget();f.resolveVoice();await settle();assert.equal(f.fields["move-words"].value,"");assert(f.invalidations>=1);assert.equal(f.controller.isIdle(),true);});
  await check("substituted_changed_session_late_result_rejected",async()=>{const f=voiceFixture({deferVoice:true});f.fields["voice-toggle"].click();await settle();f.feed();f.fields["voice-toggle"].click();await settle();f.session.csrf="changed-authored-session";f.resolveVoice();await settle();assert.equal(f.fields["move-words"].value,"");assert(f.invalidations>=1);});
  await check("substituted_unsupported_target_is_disabled",async()=>{const f=voiceFixture({selection:null});assert.equal(f.fields["voice-toggle"].disabled,true);f.fields["voice-toggle"].click();await settle();assert.equal(f.mediaCalls,0);assert.equal(f.calls.length,0);});
  await check("UI_current_move_confirm_keeps_closed_proposal_body",async()=>{const f=uiFixture("move");await f.ui.suggestFromWords("move");f.fields["move-mapping-ack"].checked=true;f.ui.acceptMapping("move");await f.ui.reviewMove();await f.ui.confirmMove();assert.equal(f.calls.length,2);assert.equal(f.calls[1].action,"confirm_move");assert.deepEqual(f.calls[1].body,{proposal_ref:"authored-proposal"});});
  await check("substituted_explicit_cancel_before_permission",async()=>{const f=voiceFixture({deferSession:true});f.fields["voice-toggle"].click();await settle();f.fields["voice-cancel"].click();f.resolveSession();await settle();assert.equal(f.mediaCalls,0);assert.equal(f.controller.isIdle(),true);assert(f.invalidations>=1);});
  process.stdout.write(JSON.stringify({schema:"emr4.stage1_voice_intent_handoff_pure_tests.v1",status:"PASS_FOCUSED_SUBSTITUTED_UI_BOUNDARIES",cases,
    browser_microphone_backend_human_semantics_proven:false})+"\n");
}
main().catch(error=>{const rawType=error&&typeof error.name==="string"?error.name:"Error";const error_type=["AssertionError","TypeError","ReferenceError","RangeError","SyntaxError","Error"].includes(rawType)?rawType:"Error";const rawCode=error&&typeof error.code==="string"?error.code:"";const error_code=/^[A-Z0-9_]{1,80}$/.test(rawCode)?rawCode:null;const assertion_diagnostic="Authored focused case failed; failure detail intentionally limited to allowlisted type/code.";process.stderr.write(JSON.stringify({schema:"emr4.stage1_voice_intent_handoff_pure_tests.v1",status:"NONPASS",failed_case:currentCase,passed_cases:cases,error_type,error_code,assertion_diagnostic})+"\n");process.exitCode=1;});
