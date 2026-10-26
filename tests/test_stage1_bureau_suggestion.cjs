// Actual suggestion controller in a pure VM: no browser, services or command writes.
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const source=fs.readFileSync(path.join(__dirname,"../static/demo/stage1-interactive.js"),"utf8");
function section(begin,end){
  const a=source.indexOf(begin),b=source.indexOf(end,a);
  assert(a>=0&&b>a,"source boundary missing");return source.slice(a,b);
}
const functions=section("function intentSnapshot(","function selectedVoiceTarget(")+"\n"+
  section("async function suggestFromWords(","function renderMapping(");
function fixture(kind="move",alter=null){
  const elements=Object.fromEntries(["patient-words","move-words","request-date","request-earliest",
    "request-latest","move-date","move-time"].map(id=>[id,{value:""}]));
  elements[kind==="move"?"move-words":"patient-words"].value=kind==="move"
    ?"Move this appointment to Wednesday at two pm.":"Please book Sunday between four pm and five pm.";
  const state={session:{persona:kind==="move"?"staff":"patient",csrf:"synthetic-csrf"},
    request:{request_id:"synthetic-request",request_version:2},
    appointment:{ref:"synthetic-appointment",state_version:4}};
  const sent=[],messages=[];let previews=0;
  const reply={schema:"emr4.stage1_word_interpretation.v1",kind,
    method:kind==="move"?"BUREAU_DETERMINISTIC":"DETERMINISTIC_LOCAL",status:"PROPOSED",missing:[],
    fields:kind==="move"?{target_date:"2026-10-28",target_start_local:"14:00"}:
      {date:"2026-10-25",earliest_local:"16:00",latest_local:"17:00"},
    selection:{appointment_ref:"synthetic-appointment",source_state_version:4}};
  const context={JSON,Error,Number,Boolean,state,$:id=>elements[id],
    intentKind:()=>kind,localVoice:{isIdle:()=>true},
    interpretationGeneration:{move:0,request:0},interpretedNotes:{move:null,request:null},
    status:message=>messages.push(message),renderMapping:()=>{},
    invalidateIntent:which=>{context.interpretationGeneration[which]++;},
    reviewMove:async()=>{previews++;},reviewRequest:()=>{previews++;},
    fetch:async(url,options)=>{sent.push({url,body:JSON.parse(options.body)});
      if(alter)alter({state,reply,elements,context});
      return {ok:true,json:async()=>reply};}};
  vm.createContext(context);vm.runInContext(functions,context,{timeout:1000});
  return {context,state,reply,elements,sent,messages,previews:()=>previews,
    run:()=>context.suggestFromWords(kind)};
}
(async()=>{
  const normal=fixture();await normal.run();
  assert.deepEqual(normal.sent[0].body,{kind:"move",words:"Move this appointment to Wednesday at two pm.",
    appointment_ref:"synthetic-appointment",source_state_version:4});
  assert.equal(normal.elements["move-time"].value,"14:00");assert.equal(normal.previews(),1);
  for(const alter of [
    ({state})=>{state.appointment.ref="different-appointment";},
    ({state})=>{state.appointment.state_version=5;},
    ({elements})=>{elements["move-words"].value="Changed words";},
    ({reply})=>{reply.selection.source_state_version=5;},
    ({reply})=>{reply.method="DETERMINISTIC_LOCAL";},
    ({reply})=>{reply.status="CLARIFICATION";reply.fields={};reply.missing=["target_date"];},
  ]){
    const rejected=fixture("move",alter);await rejected.run();
    assert.equal(rejected.elements["move-time"].value,"");assert.equal(rejected.previews(),0);
  }
  const noSelection=fixture();noSelection.state.appointment=null;await noSelection.run();
  assert.equal(noSelection.sent.length,0);
  const patient=fixture("request");await patient.run();
  assert.deepEqual(Object.keys(patient.sent[0].body).sort(),["kind","words"]);
  assert.equal(patient.elements["request-earliest"].value,"16:00");assert.equal(patient.previews(),1);
  process.stdout.write("BUREAU_SUGGESTION_SOURCE_BOUND_PASS\n");
})().catch(error=>{process.stderr.write(String(error.stack||error));process.exitCode=1;});
