// Pure source-bound confirmation check: no browser, server, DB, audio or writes.
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");

const source=fs.readFileSync(path.join(__dirname,"../static/demo/stage1-interactive.js"),"utf8");
const start=source.indexOf("function canConfirmPrepared(");
const end=source.indexOf("\nfunction showWriteFailure(",start);
assert(start>=0 && end>start,"exact controller confirmation functions required");

function fixture(words="Move this appointment Thursday at three pm.") {
  let snapshot={kind:"move",scope:"staff:synthetic-csrf",request_id:"request-1",
    request_version:2,appointment_ref:"appointment-1",appointment_version:3,
    words,fields:{date:"2026-10-29",local_time:"15:00"}};
  let generation=7,busy=false,uncertain=false,idle=true,ack=0,review=0;
  const handoff={
    acknowledge(value){assert.deepEqual(JSON.parse(JSON.stringify(value)),snapshot);ack++;return 1;},
    review(value){assert.deepEqual(JSON.parse(JSON.stringify(value)),snapshot);review++;return {revision:1,key:"exact"};},
    isReviewCurrent(value,receipt){return value===snapshot && receipt.key==="exact";}
  };
  const context={JSON,Error,intentSnapshot:()=>snapshot,
    interpretationGeneration:{move:generation},state:{busy},
    localVoice:{isIdle:()=>idle},hasCurrentInterpretation:()=>true,
    intentHandoffs:{move:handoff}};
  vm.createContext(context);
  vm.runInContext(source.slice(start,end),context,{timeout:1000});
  return {
    context,prepared:()=>({snapshot:JSON.stringify(snapshot),generation}),
    setSnapshot(value){snapshot=value;},setGeneration(value){generation=value;context.interpretationGeneration.move=value;},
    setBusy(value){busy=value;context.state.busy=value;},setIdle(value){idle=value;},
    counts:()=>({ack,review}),confirm(prepared){return context.finalHumanReview("move",prepared,uncertain);},
    setUncertain(value){uncertain=value;}
  };
}

{
  const case1=fixture(),prepared=case1.prepared();
  assert.equal(case1.counts().ack,0,"preparation is not acknowledgement");
  assert.equal(case1.confirm(prepared).key,"exact");
  assert.deepEqual(case1.counts(),{ack:1,review:1});
}
for(const change of [
  s=>({...s,words:"Different instruction"}),
  s=>({...s,fields:{...s.fields,local_time:"16:00"}}),
  s=>({...s,appointment_version:4}),
  s=>({...s,appointment_ref:"appointment-2"}),
]){
  const trial=fixture(),prepared=trial.prepared();
  trial.setSnapshot(change(trial.context.intentSnapshot()));
  assert.throws(()=>trial.confirm(prepared),/prepared details changed/);
  assert.deepEqual(trial.counts(),{ack:0,review:0});
}
for(const alter of [
  trial=>trial.setGeneration(8),
  trial=>trial.setBusy(true),
  trial=>trial.setIdle(false),
  trial=>trial.setUncertain(true),
]){
  const trial=fixture(),prepared=trial.prepared();alter(trial);
  assert.throws(()=>trial.confirm(prepared),/prepared details changed/);
  assert.deepEqual(trial.counts(),{ack:0,review:0});
}
{
  const trial=fixture(""),prepared=trial.prepared();
  assert.equal(trial.confirm(prepared).key,"exact");
  assert.deepEqual(trial.counts(),{ack:0,review:1},"blank note uses structured review");
}
process.stdout.write("INTENT_CONFIRMATION_PURE_PASS\n");
