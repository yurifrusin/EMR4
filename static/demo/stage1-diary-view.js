// Read-only view over one validated server capture. No command or microphone API.
export function parseViewIntent(words) {
  if (typeof words !== "string" || words.length > 80) return null;
  const value = words.trim().toLowerCase().replace(/[.!?]$/, "").replace(/\s+/g, " ");
  if (/^(?:show|open)(?: me)?(?: the)?(?: full)? diary$/.test(value) ||
      /^(?:show|open)(?: me)?(?: the)? week$/.test(value)) return "diary";
  if (/^(?:back|return) to (?:my|the|current) task$/.test(value) ||
      /^(?:show|open)(?: me)? (?:my|the|current) task$/.test(value)) return "task";
  return null;
}
const uuid = value => typeof value === "string" &&
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(value);
const textValue = value => typeof value === "string" && value.length > 0 &&
  value.length <= 241 && value.trim() === value && !/[\u0000-\u001f\u007f]/.test(value);
const statuses = new Set(["Booked","Confirmed","Arrived","InConsult","Completed","Cancelled","NoShow","DNA"]);
function day(value) {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) throw Error("date");
  const result = Date.parse(value + "T00:00:00Z");
  if (!Number.isFinite(result) || new Date(result).toISOString().slice(0,10) !== value) throw Error("date");
  return result;
}
function instant(value) {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(value)) throw Error("time");
  const result = Date.parse(value);
  if (!Number.isFinite(result) || new Date(result).toISOString() !== value.slice(0,-1)+".000Z") throw Error("time");
  return result;
}
function localParts(value, zone) {
  const result = Object.fromEntries(new Intl.DateTimeFormat("en-GB",{
    timeZone:zone,year:"numeric",month:"2-digit",day:"2-digit",
    hour:"2-digit",minute:"2-digit",hourCycle:"h23"
  }).formatToParts(new Date(value)).map(part=>[part.type,part.value]));
  return {date:result.year+"-"+result.month+"-"+result.day,
    clock:result.hour+":"+result.minute,hour:Number(result.hour)};
}
export function validatedDiary(raw, now=Date.now(), zone) {
  try {
    if (!raw || raw.schema_version !== "staff_diary_read.v1" || raw.state !== "complete" ||
        raw.read_only !== true || raw.availability_authority !== false ||
        !Array.isArray(raw.items) || raw.items.length > 32 || !raw.window ||
        raw.qualification !== "appointments_only_no_availability" ||
        raw.window.practice_timezone !== "Australia/Brisbane" ||
        (zone && raw.window.practice_timezone !== zone)) return null;
    const first=day(raw.window.date_from), end=day(raw.window.date_to);
    const count=(end-first)/86400000, captured=instant(raw.captured_at);
    if (!Number.isInteger(count) || count < 1 || count > 7 ||
        !Number.isFinite(now) || now < captured || now-captured > 300000 ||
        !raw.source || !uuid(raw.source.id) || raw.source.kind !== "immutable_capture" ||
        raw.source.revision !== 1 || raw.source.total_count !== raw.items.length) return null;
    const seen=new Set(), rows=[];
    let tenant=null, previous="";
    for (const item of raw.items) {
      if (!item || !uuid(item.id) || seen.has(item.id) || !uuid(item.practice_id) ||
          !Number.isSafeInteger(item.source_version) || item.source_version < 1 ||
          !uuid(item.practitioner_id) || !textValue(item.practitioner_name) ||
          !statuses.has(item.status) ||
          (item.patient_id !== null && !uuid(item.patient_id)) ||
          (item.patient_name !== null && !textValue(item.patient_name)) ||
          (item.patient_id !== null && item.patient_name === null) ||
          (item.appointment_type_id !== null && !uuid(item.appointment_type_id)) ||
          (item.appointment_type_name !== null && !textValue(item.appointment_type_name)) ||
          ((item.appointment_type_id === null) !== (item.appointment_type_name === null))) return null;
      tenant=tenant || item.practice_id;
      if (tenant !== item.practice_id) return null;
      const begin=instant(item.start_time), finish=instant(item.end_time);
      if (!Number.isSafeInteger(item.duration_minutes) || item.duration_minutes < 1 ||
          item.duration_minutes > 480 || finish-begin !== item.duration_minutes*60000) return null;
      const start=localParts(begin,raw.window.practice_timezone);
      const stop=localParts(finish,raw.window.practice_timezone);
      if (start.date < raw.window.date_from || start.date >= raw.window.date_to) return null;
      const order=item.start_time+"|"+item.id;
      if (previous && order < previous) return null;
      previous=order; seen.add(item.id);
      // Explicit allowlist: raw or rejected fields never enter the DOM model.
      rows.push(Object.freeze({id:item.id,source_version:item.source_version,
        patient:item.patient_name,practitioner:item.practitioner_name,
        type:item.appointment_type_name,duration:item.duration_minutes,status:item.status,
        date:start.date,start:start.clock,end:stop.clock,endDate:stop.date,hour:start.hour}));
    }
    const days=Array.from({length:count},(_,index)=>new Date(first+index*86400000).toISOString().slice(0,10));
    return Object.freeze({days:Object.freeze(days),zone:raw.window.practice_timezone,
      captured:raw.captured_at,expires:captured+300000,
      source:Object.freeze({id:raw.source.id,revision:1}),
      rows:Object.freeze(rows)});
  } catch (_) { return null; }
}
const byId=id=>document.getElementById(id);
function element(tag, value, className) {
  const result=document.createElement(tag);
  if (value !== undefined) result.textContent=value;
  if (className) result.className=className;
  return result;
}
function timeRange(row) {
  return row.start+"–"+(row.endDate === row.date ? "" : row.endDate+" ")+row.end;
}
function person(row) { return row.patient === null ? "No patient name supplied" : row.patient; }
function type(row) { return row.type === null ? "No appointment type supplied" : row.type; }
function sourceDetails(row) {
  const details=element("details"), summary=element("summary","Source");
  details.append(summary,element("span","Appointment "+row.id+" · state version "+row.source_version));
  return details;
}
function renderGrid(model) {
  const root=byId("diary-grid"), grid=element("div",undefined,"week-grid");
  root.replaceChildren(); grid.append(element("div","Time","grid-corner"));
  for (const date of model.days) {
    const heading=element("div",undefined,"grid-day-heading");
    const parsed=new Date(date+"T12:00:00Z");
    heading.append(element("span",new Intl.DateTimeFormat("en-AU",{weekday:"short",timeZone:"UTC"}).format(parsed)),
      element("strong",new Intl.DateTimeFormat("en-AU",{day:"numeric",month:"short",timeZone:"UTC"}).format(parsed)));
    grid.append(heading);
  }
  const from=Math.min(8,...model.rows.map(row=>row.hour)), to=Math.max(17,...model.rows.map(row=>row.hour));
  for (let hour=from;hour<=to;hour++) {
    grid.append(element("div",String(hour).padStart(2,"0")+":00","grid-time"));
    for (const date of model.days) {
      const cell=element("div",undefined,"grid-cell");
      for (const row of model.rows.filter(item=>item.date===date && item.hour===hour)) {
        const card=element("article",undefined,"grid-event");
        card.setAttribute("aria-label",person(row)+", "+date+", "+timeRange(row)+", "+row.status);
        card.append(element("strong",person(row)),element("span",timeRange(row)),
          element("span",row.practitioner),element("span",type(row)),
          element("span",row.duration+" minutes · "+row.status),sourceDetails(row));
        cell.append(card);
      }
      grid.append(cell);
    }
  }
  root.append(grid);
}
function renderList(model) {
  const table=element("table"), caption=element("caption","The same appointments and source versions as the weekly grid. Times in "+model.zone+".");
  table.append(caption);
  const head=element("thead"), titles=element("tr");
  for (const title of ["Date and time","Patient","Practitioner","Appointment","Status","Source"]) {
    const cell=element("th",title); cell.scope="col"; titles.append(cell);
  }
  head.append(titles); table.append(head);
  const body=element("tbody");
  for (const row of model.rows) {
    const line=element("tr"), date=element("th",row.date+" · "+timeRange(row));date.scope="row";line.append(date);
    line.append(element("td",person(row)),element("td",row.practitioner),
      element("td",type(row)+" · "+row.duration+" minutes"),element("td",row.status),
      element("td","Appointment "+row.id+" · state version "+row.source_version));
    body.append(line);
  }
  table.append(body);byId("diary-list").replaceChildren(table);
}
function moveVoiceControls(persona) {
  const destination=byId(persona==="patient"?"patient-voice-slot":"staff-voice-slot");
  if (destination) destination.append(byId("voice-controls"));
}
if (typeof document !== "undefined") document.addEventListener("raisa:session-ready",event=>{
  if (["patient","staff"].includes(event.detail?.persona)) moveVoiceControls(event.detail.persona);
});
export function initDiaryView({load}) {
  const required=["view-switch","focus-view","grid-view","focus-workspace","diary-workspace",
    "diary-refresh","diary-grid","diary-list","diary-list-toggle","diary-status","diary-window",
    "view-prompt","view-prompt-form","view-prompt-words","view-prompt-status"];
  if (typeof load !== "function" || required.some(id=>!byId(id))) throw Error("Diary view contract incomplete");
  let model=null, generation=0, inFlight=false, list=false, visible=false, expiry=null;
  // Staff bootstrap calls this function; patient bootstrap never admits a diary loader.
  byId("view-switch").hidden=false;byId("view-prompt").hidden=false;
  function clear(message) {
    clearTimeout(expiry);model=null;
    byId("diary-grid").replaceChildren();byId("diary-list").replaceChildren();
    byId("diary-window").textContent="A complete current read for the selected dates is required.";
    byId("diary-status").textContent=message;
  }
  function showRepresentation() {
    byId("diary-grid").hidden=list;byId("diary-list").hidden=!list;
    byId("diary-list-toggle").setAttribute("aria-pressed",String(list));
    byId("diary-list-toggle").textContent=list?"Weekly grid":"List view";
  }
  async function read() {
    const ticket=++generation;inFlight=true;clear("Reading the current diary…");
    try {
      const raw=await load();
      if (ticket !== generation) return;
      const safe=validatedDiary(raw);
      if (!safe) {clear("Diary unavailable. No appointment details are shown. Your current task is still here.");return;}
      model=safe;renderGrid(safe);renderList(safe);showRepresentation();
      byId("diary-window").textContent=safe.days[0]+" to "+safe.days.at(-1)+" · "+safe.zone;
      byId("diary-status").textContent=safe.rows.length+" appointment(s) · Captured at "+
        new Intl.DateTimeFormat("en-AU",{timeZone:safe.zone,hour:"2-digit",minute:"2-digit"}).format(new Date(safe.captured))+". Appointments only · Read-only.";
      expiry=setTimeout(()=>{generation++;clear("This diary read has expired. Refresh it for current facts.");},
        Math.max(0,safe.expires-Date.now()+1));
    } catch (_) {if (ticket===generation) clear("Diary unavailable. No appointment details are shown. Your current task is still here.");}
    finally {if (ticket===generation) inFlight=false;}
  }
  async function open() {
    visible=true;byId("focus-workspace").hidden=true;byId("diary-workspace").hidden=false;
    byId("focus-view").setAttribute("aria-pressed","false");byId("grid-view").setAttribute("aria-pressed","true");
    if ((!model || Date.now()>model.expires) && !inFlight) await read();
    byId("diary-heading").tabIndex=-1;byId("diary-heading").focus();
  }
  function task() {
    visible=false;byId("focus-workspace").hidden=false;byId("diary-workspace").hidden=true;
    byId("focus-view").setAttribute("aria-pressed","true");byId("grid-view").setAttribute("aria-pressed","false");
    byId("focus-view").focus();
  }
  byId("grid-view").addEventListener("click",()=>{void open();});
  byId("focus-view").addEventListener("click",task);
  byId("diary-refresh").addEventListener("click",()=>{if(!inFlight)void read();});
  byId("diary-list-toggle").addEventListener("click",()=>{list=!list;showRepresentation();});
  byId("view-prompt-form").addEventListener("submit",event=>{
    event.preventDefault();
    const intent=parseViewIntent(byId("view-prompt-words").value);
    if(intent==="diary"){void open();byId("view-prompt-status").textContent="Opening weekly appointments. Your appointment task is preserved.";}
    else if(intent==="task"){task();byId("view-prompt-status").textContent="Your current appointment task is here, unchanged.";}
    else byId("view-prompt-status").textContent="Try “Show me the diary” or “Back to my task”. No appointment action was taken.";
  });
  document.addEventListener("raisa:staff-facts",()=>{
    generation++;inFlight=false;clear("Appointment facts changed. Refresh the diary for a current read.");
    if(visible)void read();
  });
  window.addEventListener("pagehide",()=>{generation++;clearTimeout(expiry);});
  return Object.freeze({open,task,invalidate:()=>{generation++;inFlight=false;clear("Refresh the diary for current facts.");}});
}

