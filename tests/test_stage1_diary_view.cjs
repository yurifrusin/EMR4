// Actual module with synthetic parser and simulated-DOM checks; no app/DB/browser.
const assert=require("node:assert/strict"), fs=require("node:fs"), path=require("node:path");
(async()=>{
 const source=fs.readFileSync(path.join(__dirname,"../static/demo/stage1-diary-view.js"),"utf8");
 const {parseViewIntent,validatedDiary,initDiaryView}=await import("data:text/javascript;base64,"+Buffer.from(source).toString("base64"));
 const captured="2026-10-24T05:00:00Z", now=Date.parse(captured)+1000;
 const base={schema_version:"staff_diary_read.v1",state:"complete",
  qualification:"appointments_only_no_availability",
  window:{date_from:"2026-10-24",date_to:"2026-10-31",practice_timezone:"Australia/Brisbane"},
  captured_at:captured,source:{id:"00000000-0000-4000-8000-000000000001",revision:1,kind:"immutable_capture",total_count:1},
  read_only:true,availability_authority:false,items:[{
   id:"00000000-0000-4000-8000-000000000002",practice_id:"00000000-0000-4000-8000-000000000003",source_version:7,
   practitioner_id:"00000000-0000-4000-8000-000000000004",practitioner_name:"Sam Example",
   patient_id:"00000000-0000-4000-8000-000000000005",patient_name:"Ada Example",
   appointment_type_id:"00000000-0000-4000-8000-000000000006",appointment_type_name:"Follow-up",
   start_time:"2026-10-25T06:00:00Z",end_time:"2026-10-25T06:30:00Z",duration_minutes:30,status:"Booked"}]};
 const copy=()=>JSON.parse(JSON.stringify(base));
 let checks=0;
 const valid=validatedDiary(base,now,"Australia/Brisbane"); assert(valid);checks++;
 assert.deepEqual([valid.rows[0].date,valid.rows[0].start,valid.rows[0].end],["2026-10-25","16:00","16:30"]);checks++;
 assert.equal(valid.rows[0].source_version,7);assert.equal(valid.source.revision,1);checks++;
 assert.equal(valid.days.length,7);checks++;
 for(const words of ["Show me the full diary","Open the diary","show the week!"]) {assert.equal(parseViewIntent(words),"diary");checks++;}
 for(const words of ["Back to my task","show my task"]) {assert.equal(parseViewIntent(words),"task");checks++;}
 for(const words of ["cancel the appointment and show the diary","book 4 pm","show the diary then move it",null]) {
  assert.equal(parseViewIntent(words),null);checks++;
 }
 const mutations=[
  x=>x.state="unavailable",x=>x.availability_authority=true,x=>x.read_only=false,
  x=>x.source.kind="diary_aggregate",x=>x.source.revision=7,x=>x.source.total_count=2,
  x=>x.window.date_to="2026-11-01",x=>x.window.date_from="2026-02-30",
  x=>x.items.push({...x.items[0]}),
  x=>x.items[0].source_version=0,x=>x.items[0].duration_minutes=45,
  x=>x.items[0].patient_name="<bad>\nprivate",x=>x.items[0].start_time="2026-11-02T06:00:00Z",
  x=>x.items[0].status="Available",x=>x.captured_at="2026-10-24T04:54:59Z",
  x=>x.captured_at="2026-10-24T05:01:00Z",
  x=>{x.items=Array.from({length:33},()=>({...x.items[0]}));x.source.total_count=33;}
 ];
 for(const mutate of mutations){const input=copy();mutate(input);assert.equal(validatedDiary(input,now),null);checks++;}
 const mixed=copy();mixed.items.push({...mixed.items[0],id:"00000000-0000-4000-8000-000000000009",
   practice_id:"00000000-0000-4000-8000-000000000099"});mixed.source.total_count=2;
 assert.equal(validatedDiary(mixed,now),null);checks++;
 const extra=copy();extra.private_rejected_note="must never render";extra.items[0].raw_note="must never render";
 const safe=validatedDiary(extra,now);assert(safe);assert(!JSON.stringify(safe).includes("must never render"));checks++;
 const empty=copy();empty.items=[];empty.source.total_count=0;
 assert.equal(validatedDiary(empty,now).rows.length,0);checks++;
 assert.equal(validatedDiary(base,now,"Australia/Sydney"),null);checks++;
 // The changed user-visible scope must survive opening, fallback and returning.
 class Element {
  constructor(){this.children=[];this.attributes={};this.handlers={};this.value="";this._text="";}
  set textContent(value){this._text=String(value);this.children=[];}
  get textContent(){return this._text+this.children.map(x=>x.textContent||"").join("");}
  append(...nodes){this.children.push(...nodes);}
  replaceChildren(...nodes){this.children=[...nodes];this._text="";}
  setAttribute(key,value){this.attributes[key]=value;}
  addEventListener(name,fn){this.handlers[name]=fn;}
  focus(){document.activeElement=this;}
 }
 const ids=["view-switch","focus-view","grid-view","focus-workspace","diary-workspace",
  "diary-refresh","diary-grid","diary-list","diary-list-toggle","diary-status","diary-window",
  "view-prompt","view-prompt-form","view-prompt-words","view-prompt-status","diary-heading"];
 const elements=Object.fromEntries(ids.map(id=>[id,new Element()]));
 global.document={getElementById:id=>elements[id],createElement:()=>new Element(),addEventListener(){}};
 global.window={addEventListener(){}};
 const originalNow=Date.now;
 let response=copy(), reads=0, view;
 Date.now=()=>now;
 try {
  view=initDiaryView({load:async()=>{reads++;return response;}});
  await view.open();
  assert.equal(reads,1);assert.equal(elements["diary-workspace"].hidden,false);
  assert.match(elements["diary-status"].textContent,/Captured at .*Appointments only.*Read-only/);checks++;
  assert(elements["diary-grid"].textContent.includes("Ada Example"));
  elements["diary-list-toggle"].handlers.click();
  assert(elements["diary-list"].textContent.includes("Ada Example"));checks++;
  elements["view-prompt-words"].value="Show me the full diary";
  elements["view-prompt-form"].handlers.submit({preventDefault(){}});
  assert.equal(elements["view-prompt-status"].textContent,
   "Opening weekly appointments. Your appointment task is preserved.");checks++;
  view.task();assert.equal(elements["diary-workspace"].hidden,true);
  assert.equal(document.activeElement,elements["focus-view"]);checks++;
  view.invalidate();response={...copy(),state:"unavailable",items:[]};
  await view.open();
  assert.equal(elements["diary-grid"].textContent,"");
  assert.equal(elements["diary-list"].textContent,"");
  assert.match(elements["diary-window"].textContent,/selected dates/);
  assert.match(elements["diary-status"].textContent,/Diary unavailable/);checks++;
 } finally {if(view)view.invalidate();Date.now=originalNow;delete global.document;delete global.window;}
 const html=fs.readFileSync(path.join(__dirname,"../static/demo/stage1-interactive.html"),"utf8");
 assert.match(html,/id="diary-heading">Weekly appointments<\/h2>/);
 assert.match(html,/Rosters and breaks are not included/);
 assert(!html.includes("Your full diary"));checks++;
 process.stdout.write(JSON.stringify({status:"PASS",assertion_groups:checks,
  scope:"actual view parser/validator and simulated DOM; not rendered browser, backend, DB, microphone, provider or writes"})+"\n");
})().catch(error=>{process.stderr.write(error.stack+"\n");process.exitCode=1;});

