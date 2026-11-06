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
    hour:"2-digit",minute:"2-digit",second:"2-digit",hourCycle:"h23"
  }).formatToParts(new Date(value)).map(part=>[part.type,part.value]));
  return {date:result.year+"-"+result.month+"-"+result.day,
    clock:result.hour+":"+result.minute+(result.second==="00"?"":":"+result.second),hour:Number(result.hour)};
}
export function validatedDiary(raw, now=Date.now(), zone, selectedContext=null) {
  try {
    if (!raw || raw.schema_version !== "staff_diary_read.v1" || raw.state !== "complete" ||
        raw.read_only !== true || raw.availability_authority !== false ||
        !Array.isArray(raw.items) || raw.items.length > 32 || !raw.window ||
        raw.qualification !== "appointments_only_no_availability" ||
        (selectedContext === null ? raw.window.practice_timezone !== "Australia/Brisbane"
          : !["Australia/Brisbane","Australia/Sydney"].includes(raw.window.practice_timezone)) ||
        (zone && raw.window.practice_timezone !== zone)) return null;
    const first=day(raw.window.date_from), end=day(raw.window.date_to);
    if (selectedContext !== null && (!uuid(selectedContext.practice_id)
        || raw.window.date_from !== selectedContext.date || end-first !== 7*86400000)) return null;
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
      if (tenant !== item.practice_id || selectedContext !== null
          && item.practice_id !== selectedContext.practice_id) return null;
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
  const hourPixels=70, minimumTileMinutes=30;
  const minute=clock=>Number(clock.slice(0,2))*60+Number(clock.slice(3,5));
  const offsetAt=value=>{
    const local=localParts(value,model.zone);
    return (Date.parse(local.date+"T"+local.clock+(local.clock.length===5?":00":"")+"Z")-value)/60000;
  };
  // The frozen model has no per-row instant/offset. Nearby clock changes use details.
  const stableDates=new Map(model.days.map(date=>{
    const at=Date.parse(date+"T00:00:00Z");
    return [date,new Set([-86400000,0,86400000].map(delta=>offsetAt(at+delta))).size===1];
  }));
  const entries=model.rows.map(row=>{
    const start=minute(row.start), end=minute(row.end);
    let reason=null;
    if (row.start.length!==5 || row.end.length!==5)
      reason="Appointment includes seconds: use full details or List view.";
    else if (row.endDate!==row.date) reason="Cross-date appointment: use full details or List view.";
    else if (!stableDates.get(row.date) || end-start!==row.duration)
      reason="Clock timing cannot be positioned unambiguously: use full details or List view.";
    else if (row.duration<minimumTileMinutes)
      reason="Short appointment: use full details or List view.";
    return {row,start,end,reason,lane:0};
  });
  const layouts=new Map(model.days.map(date=>{
    const positions=entries.filter(entry=>entry.row.date===date && entry.reason===null)
      .sort((a,b)=>a.start-b.start || a.end-b.end || (a.row.id<b.row.id?-1:a.row.id>b.row.id?1:0));
    const ends=[];
    for (const entry of positions) {
      let lane=ends.findIndex(end=>end<=entry.start);
      if (lane===-1) lane=ends.length;
      ends[lane]=entry.end;entry.lane=lane;
    }
    return [date,{positions,lanes:Math.max(1,ends.length)}];
  }));
  const positions=entries.filter(entry=>entry.reason===null);
  const from=Math.min(8,...positions.map(entry=>Math.floor(entry.start/60)));
  const to=Math.max(18,...positions.map(entry=>Math.ceil(entry.end/60)));
  const height=(to-from)*hourPixels;
  grid.style.gridTemplateColumns=["60px",...model.days.map(date=>"minmax("+(layouts.get(date).lanes*132)+"px,1fr)")].join(" ");
  grid.append(element("div","Time","grid-corner"));
  for (const date of model.days) {
    const heading=element("div",undefined,"grid-day-heading");
    const parsed=new Date(date+"T12:00:00Z");
    heading.append(element("span",new Intl.DateTimeFormat("en-AU",{weekday:"short",timeZone:"UTC"}).format(parsed)),
      element("strong",new Intl.DateTimeFormat("en-AU",{day:"numeric",month:"short",timeZone:"UTC"}).format(parsed)));
    grid.append(heading);
  }
  const axis=element("div",undefined,"grid-time-axis");
  axis.style.height=height+"px";
  for (let hour=from;hour<to;hour++)
    axis.append(element("div",String(hour).padStart(2,"0")+":00","grid-time"));
  grid.append(axis);

  const panel=element("section",undefined,"grid-event-panel");
  panel.hidden=true;panel.setAttribute("aria-labelledby","diary-event-details-heading");
  const panelHeading=element("div",undefined,"grid-event-panel-heading");
  const title=element("h3","Appointment details");title.id="diary-event-details-heading";
  const close=element("button","Close appointment details","quiet");
  close.type="button";close.id="diary-event-details-close";
  panelHeading.append(title,close);panel.append(panelHeading);
  let activeControl=null;
  for (const entry of entries) {
    const row=entry.row, card=element("article",undefined,"grid-event");
    card.id="diary-appointment-"+row.id;card.tabIndex=-1;card.hidden=true;
    card.setAttribute("aria-label",person(row)+", "+row.date+", "+timeRange(row)+", "+row.status);
    card.append(element("strong",person(row)),element("span",timeRange(row)),
      element("span",row.practitioner),element("span",type(row)),
      element("span",row.duration+" minutes · "+row.status),sourceDetails(row));
    if (entry.reason) card.append(element("p",entry.reason,"grid-placement-note"));
    entry.card=card;panel.append(card);
  }
  const openDetails=(entry,control)=>{
    for (const item of entries) item.card.hidden=item!==entry;
    if (activeControl) activeControl.setAttribute("aria-expanded","false");
    activeControl=control;control.setAttribute("aria-expanded","true");
    panel.hidden=false;entry.card.focus();
  };
  close.addEventListener("click",()=>{
    panel.hidden=true;
    for (const entry of entries) entry.card.hidden=true;
    const previous=activeControl;activeControl=null;
    if (previous) {
      previous.setAttribute("aria-expanded","false");
      const fallback=previous.closest("details.grid-fallback");
      if (fallback) fallback.open=true;
      previous.focus();
    }
  });
  const controlFor=(entry,className)=>{
    const control=element("button",undefined,className);
    control.type="button";control.dataset.appointmentId=entry.row.id;
    control.setAttribute("aria-label",person(entry.row)+", "+entry.row.date+", "+timeRange(entry.row)+", "+entry.row.status+". Appointment details.");
    control.setAttribute("aria-controls",entry.card.id);control.setAttribute("aria-expanded","false");
    control.addEventListener("click",()=>openDetails(entry,control));
    return control;
  };
  for (const date of model.days) {
    const column=element("div",undefined,"grid-day-column"), layout=layouts.get(date);
    column.style.height=height+"px";
    for (const entry of layout.positions) {
      const tile=controlFor(entry,"grid-slot");
      tile.style.top=((entry.start-from*60)*hourPixels/60)+"px";
      tile.style.height=(entry.row.duration*hourPixels/60)+"px";
      tile.style.left="calc("+(entry.lane*100/layout.lanes)+"% + 5px)";
      tile.style.width="calc("+(100/layout.lanes)+"% - 10px)";
      tile.append(element("span",timeRange(entry.row)),element("strong",person(entry.row)));
      column.append(tile);
    }
    grid.append(column);
  }
  root.replaceChildren();
  root.append(element("p","Choose an appointment for its full details and Source. Time positions show appointments only.","grid-help"),grid);
  const unpositioned=entries.filter(entry=>entry.reason!==null);
  if (unpositioned.length) {
    const fallback=element("details",undefined,"grid-fallback");
    fallback.append(element("summary",unpositioned.length+" appointment(s) shown in details only"));
    fallback.append(element("p","These appointments are not positioned on the time grid. List view includes every appointment.","grid-help"));
    const list=element("ul");
    for (const entry of unpositioned) {
      const item=element("li"), control=controlFor(entry,"quiet grid-fallback-entry");
      control.append(element("strong",entry.row.date+" · "+timeRange(entry.row)),
        element("span",person(entry.row)),element("span",entry.reason));
      item.append(control);list.append(item);
    }
    fallback.append(list);root.append(fallback);
  }
  root.append(panel);
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
export function initDiaryView({load,selectedContext=null,taskVisibility=null}) {
  const required=["view-switch","focus-view","grid-view","focus-workspace","diary-workspace",
    "diary-refresh","diary-grid","diary-list","diary-list-toggle","diary-status","diary-window",
    "view-prompt","view-prompt-form","view-prompt-words","view-prompt-status"];
  if (typeof load !== "function" || required.some(id=>!byId(id))) throw Error("Diary view contract incomplete");
  if ((selectedContext !== null && typeof selectedContext !== "function")
      || (taskVisibility !== null && typeof taskVisibility !== "function")
      || (selectedContext === null) !== (taskVisibility === null)) throw Error("Diary selected context incomplete");
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
    const ticket=++generation, context=selectedContext ? selectedContext() : null;
    if (selectedContext && context === null) {clear("Diary unavailable. Check your current sign-in.");return;}
    const contextKey=JSON.stringify(context);
    inFlight=true;clear("Reading the current diary…");
    try {
      const raw=await load();
      if (ticket !== generation || selectedContext
          && JSON.stringify(selectedContext()) !== contextKey) return;
      const safe=validatedDiary(raw,Date.now(),undefined,context);
      if (!safe) {clear("Diary unavailable. No appointment details are shown. Your current task is still here.");return;}
      model=safe;renderGrid(safe);renderList(safe);showRepresentation();
      byId("diary-window").textContent=(selectedContext ? "Appointments starting " : "")
        +safe.days[0]+" to "+safe.days.at(-1)+" · "+safe.zone;
      byId("diary-status").textContent=safe.rows.length+" appointment(s) · Captured at "+
        new Intl.DateTimeFormat("en-AU",{timeZone:safe.zone,hour:"2-digit",minute:"2-digit"}).format(new Date(safe.captured))+". Appointments only · Read-only.";
      expiry=setTimeout(()=>{generation++;clear("This diary read has expired. Refresh it for current facts.");},
        Math.max(0,safe.expires-Date.now()+1));
    } catch (_) {if (ticket===generation) clear("Diary unavailable. No appointment details are shown. Your current task is still here.");}
    finally {if (ticket===generation) inFlight=false;}
  }
  async function open() {
    if (selectedContext && selectedContext() === null) return;
    visible=true;
    if (taskVisibility) taskVisibility(false);
    else byId("focus-workspace").hidden=true;
    byId("diary-workspace").hidden=false;
    byId("focus-view").setAttribute("aria-pressed","false");byId("grid-view").setAttribute("aria-pressed","true");
    if ((!model || Date.now()>model.expires) && !inFlight) await read();
    byId("diary-heading").tabIndex=-1;byId("diary-heading").focus();
  }
  function task() {
    visible=false;
    if (taskVisibility) taskVisibility(true);
    else byId("focus-workspace").hidden=false;
    byId("diary-workspace").hidden=true;
    byId("focus-view").setAttribute("aria-pressed","true");byId("grid-view").setAttribute("aria-pressed","false");
    if (!taskVisibility) byId("focus-view").focus();
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
  document.addEventListener(selectedContext ? "raisa:selected-staff-facts" : "raisa:staff-facts",()=>{
    generation++;inFlight=false;clear("Appointment facts changed. Refresh the diary for a current read.");
    if(visible)void read();
  });
  window.addEventListener("pagehide",()=>{generation++;clearTimeout(expiry);});
  return Object.freeze({open,task,invalidate:()=>{generation++;inFlight=false;clear("Refresh the diary for current facts.");},
    deactivate:()=>{generation++;inFlight=false;visible=false;clear("Diary unavailable. Check your current sign-in.");
      byId("diary-workspace").hidden=true;if(taskVisibility)taskVisibility(true,false);}});
}

