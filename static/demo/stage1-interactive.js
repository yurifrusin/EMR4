// Source-only UI. The same-origin adapter contract is specified beside this file.
// No demo identity, capability, signed proposal, or staff credential is kept by the browser.
import { initLocalVoice, initSpokenReply, createManualIntentHandoff } from "./stage1-local-voice.js";
import { initDiaryView } from "./stage1-diary-view.js";
const $ = id => document.getElementById(id);
const state = { session: null, request: null, appointment: null, offer: null,
  bookingPrepared: null, bookingReview: null,
  create: null, move: null, pendingKey: null, requestUncertain: false, generation: 0,
  proposalGeneration: 0, busy: false, staffUncertain: false, requestReview: null, moveReview: null };
const text = (id, value) => { $(id).textContent = value == null ? "" : String(value); };
const show = (id, visible) => {
  $(id).hidden = !visible;
  // Keep exact fields in the DOM for snapshot checks while the proposal takes
  // visual focus. Hiding an editor neither acknowledges it nor alters state.
  if(id==="request-review-box")$("request-entry").hidden=visible ||
    Boolean(state.request && state.request.state!=="draft");
  if(id==="move-review"){
    $("move-entry").hidden=visible;$("diary").hidden=visible;
    $("staff-request").hidden=visible || state.request?.state==="booked";
  }
  if(id==="create-review"){
    $("staff-offers").hidden=visible;$("staff-request").hidden=visible || state.request?.state==="booked";
  }
};
let spoken = null;
const status = message => { spoken?.stop(); text("status", message); };
const dateTime = (date, clock, zone) => `${date} at ${clock} ${zone}`;
const uuid = () => crypto.randomUUID();

const intentHandoffs={request:createManualIntentHandoff(),move:createManualIntentHandoff()};
const interpretedNotes={request:null,move:null};
const interpretationGeneration={request:0,move:0};
let localVoice=null;
let diaryView=null;
let authPromptTimer=null;
function armAuthPrompt() {
  clearTimeout(authPromptTimer);
  if(state.session?.persona!=="staff")return;
  const tokenEnd=Date.parse(state.session.mock_token_expires_at||"");
  const windowEnd=Date.parse(state.session.human_window_ends_at||"");
  if(!Number.isFinite(tokenEnd)||!Number.isFinite(windowEnd))return;
  const check=()=>{
    if(Date.now()>=windowEnd){show("continue-demo",false);status("The recording window has ended. Your editable words remain on this page.");return;}
    if(Date.now()>=tokenEnd){show("continue-demo",true);status("Mock organisation access expired. Your words remain editable. Select Continue demo before another staff action.");return;}
    authPromptTimer=setTimeout(check,Math.max(1000,Math.min(tokenEnd-Date.now(),60000)));
  };
  check();
}
const intentKind=()=>state.session?.persona==="patient"?"request":"move";
function intentSnapshot(kind) {
  return {kind,scope:state.session?state.session.persona+":"+state.session.csrf:"",
    request_id:state.request?.request_id,request_version:state.request?.request_version,
    appointment_ref:kind==="move"?state.appointment?.ref:null,
    appointment_version:kind==="move"?state.appointment?.state_version:null,
    words:$(kind==="request"?"patient-words":"move-words").value,
    fields:kind==="request"?{date:$("request-date").value,
      earliest_local:$("request-earliest").value,latest_local:$("request-latest").value}:
      {date:$("move-date").value,local_time:$("move-time").value}};
}
function selectedVoiceTarget() {
  const value=intentSnapshot(intentKind());
  if(!["patient","staff"].includes(state.session?.persona) || typeof value.request_id!=="string" || !value.request_id ||
      !Number.isSafeInteger(value.request_version) ||
      (value.kind==="move" && (typeof value.appointment_ref!=="string" || !value.appointment_ref ||
        !Number.isSafeInteger(value.appointment_version))))return null;
  return JSON.stringify([value.kind,value.scope,value.request_id,value.request_version,
    value.appointment_ref,value.appointment_version]);
}
function currentVoiceTarget() {
  const selected=selectedVoiceTarget();
  return selected?selected+":"+intentHandoffs[intentKind()].revision():null;
}

function hasCurrentInterpretation(kind) {
  const snapshot=intentSnapshot(kind);
  return !snapshot.words.trim() || interpretedNotes[kind]===JSON.stringify(snapshot);
}
async function suggestFromWords(kind) {
  if(!state.session || kind!==intentKind() || (localVoice && !localVoice.isIdle())) {
    status("Finish or cancel dictation in the current session before suggesting details.");return;
  }
  const selected=intentSnapshot(kind),words=selected.words;
  if(!words.trim()){
    if(kind==="request")reviewRequest();else await reviewMove();
    return;
  }
  if(kind==="move" && (typeof selected.appointment_ref!=="string" || !selected.appointment_ref ||
      !Number.isSafeInteger(selected.appointment_version) || selected.appointment_version<1)){
    status("Choose the current appointment before preparing a change.");return;
  }
  invalidateIntent(kind,false);
  const generation=interpretationGeneration[kind],before=JSON.stringify(intentSnapshot(kind));
  status(kind==="move"?"Raisa is preparing the selected appointment change for review…":
    "Interpreting your words locally. No request or appointment is being changed…");
  try {
    const response=await fetch("/demo/stage1/interpret",{method:"POST",credentials:"same-origin",cache:"no-store",redirect:"error",
      headers:{"Content-Type":"application/json","X-CSRF-Token":state.session.csrf},body:JSON.stringify(kind==="move"
        ?{kind,words,appointment_ref:selected.appointment_ref,source_state_version:selected.appointment_version}:{kind,words})});
    if(!response.ok)throw new Error("The note could not be interpreted in this session. Refresh or use structured details.");
    const result=await response.json();
    if(generation!==interpretationGeneration[kind] || before!==JSON.stringify(intentSnapshot(kind)) ||
        (localVoice && !localVoice.isIdle()))return;
    if(!result || result.schema!=="emr4.stage1_word_interpretation.v1" || result.kind!==kind ||
        result.method!==(kind==="move"?"BUREAU_SYNTHETIC_MODEL_REPLY":"DETERMINISTIC_LOCAL") ||
        !["PROPOSED","CLARIFICATION"].includes(result.status) ||
        !Array.isArray(result.missing) || !result.fields || typeof result.fields!=="object" || Array.isArray(result.fields))
      throw new Error("The suggested details could not be verified. Clarify the note or use structured details.");
    if(kind==="move" && (!result.selection || result.selection.appointment_ref!==selected.appointment_ref ||
        result.selection.source_state_version!==selected.appointment_version))
      throw new Error("The selected appointment changed. Refresh and prepare the change again.");
    if(result.status!=="PROPOSED"){
      status(result.message==="DATE_NOT_CURRENTLY_OFFERED"
        ?"That date is not currently offered. Check the offered dates, clarify your words, and suggest again. No details were adopted."
        :"Please clarify the note with one date and an exact time or a bounded preferred window. No details were adopted.");return;
    }
    if(kind==="move"){
      const carrier=result.synthetic_carrier;
      if(!carrier || carrier.producer!=="authored_synthetic_model_shaped_reply" ||
          carrier.provider_calls!==0 ||
          typeof carrier.raw_response_sha256!=="string" || !/^[a-f0-9]{64}$/.test(carrier.raw_response_sha256) ||
          typeof carrier.compiled_plan_sha256!=="string" || !/^[a-f0-9]{64}$/.test(carrier.compiled_plan_sha256) ||
          carrier.raw_response_sha256===carrier.compiled_plan_sha256 ||
          carrier.planner_source_sha256!=="45a28b40611508910fd338f775644ff4863fd0ff84609040cb697d157a09b2d8" ||
          !Number.isSafeInteger(carrier.context_revision) || carrier.context_revision<1 ||
          !Number.isSafeInteger(carrier.source_state_version) || carrier.source_state_version!==selected.appointment_version ||
          !Number.isSafeInteger(carrier.duration_minutes) || carrier.duration_minutes!==state.appointment?.duration_minutes)
        throw new Error("The synthetic proposal provenance changed. Refresh and prepare the change again.");
    }
    const keys=kind==="request"?["date","earliest_local","latest_local"]:["target_date","target_start_local"];
    const fields=result.fields,date=fields[kind==="request"?"date":"target_date"];
    const clocks=kind==="request"?[fields.earliest_local,fields.latest_local]:[fields.target_start_local];
    if(Object.keys(fields).sort().join("|")!==keys.sort().join("|") || result.missing.length ||
        typeof date!=="string" || !/^\d{4}-\d{2}-\d{2}$/.test(date) ||
        clocks.some(value=>typeof value!=="string" || !/^(?:[01]\d|2[0-3]):[0-5]\d$/.test(value)) ||
        (kind==="request" && fields.earliest_local>=fields.latest_local))
      throw new Error("The suggested date or time is incomplete. Clarify the note before review.");
    if(kind==="request"){
      $("request-date").value=date;$("request-earliest").value=fields.earliest_local;$("request-latest").value=fields.latest_local;
    }else{$("move-date").value=date;$("move-time").value=fields.target_start_local;}
    invalidateIntent(kind,false);
    interpretedNotes[kind]=JSON.stringify(intentSnapshot(kind));
    renderMapping(kind);
    // Interpretation changes only editable fields. The following step prepares
    // an exact visible review; it never writes or acknowledges the mapping.
    if(kind==="request")reviewRequest();else await reviewMove();
  }catch(error){if(generation===interpretationGeneration[kind])status(error.message);}
}

function renderMapping(kind) {
  const info=intentHandoffs[kind].inspect(intentSnapshot(kind));
  text(kind+"-mapping-status",info.required && !hasCurrentInterpretation(kind)
    ?"Prepare a suggestion from your words, or enter the date and time below.":"");
}
function invalidateIntent(kind, cancelCapture=true) {
  interpretedNotes[kind]=null;interpretationGeneration[kind]++;
  intentHandoffs[kind].invalidate();
  if(kind==="request"){state.requestReview=null;show("request-review-box",false);}
  else clearPending();
  renderMapping(kind);
  if(cancelCapture)localVoice?.invalidateTarget();
}
function canConfirmPrepared(prepared, snapshot, generation, busy, uncertain, voiceIdle) {
  return Boolean(prepared) && !busy && !uncertain && voiceIdle &&
    prepared.snapshot===JSON.stringify(snapshot) && prepared.generation===generation;
}
function finalHumanReview(kind, prepared, uncertain=false) {
  const snapshot=intentSnapshot(kind);
  if(!canConfirmPrepared(prepared,snapshot,interpretationGeneration[kind],state.busy,
      uncertain,!localVoice || localVoice.isIdle()) || !hasCurrentInterpretation(kind))
    throw new Error("The prepared details changed. Prepare and check them again before confirming.");
  const handoff=intentHandoffs[kind];
  try {
    // This exact final button click is the human acknowledgement for a note.
    // Blank notes use the existing structured-only review path.
    if(snapshot.words.trim())handoff.acknowledge(snapshot);
    const review=handoff.review(snapshot);
    if(!handoff.isReviewCurrent(snapshot,review))throw new Error("stale");
    return review;
  } catch (_) {
    throw new Error("The current words, target and details need a fresh review.");
  }
}


function showWriteFailure(error,subject) {
  if(error?.reauth){show("continue-demo",true);status("Mock organisation access expired. Continue demo, then review and choose the action again. Your words and original command key remain here.");return;}
  const definitive=error?.status===400 || error?.status===401 || error?.status===403 || error?.status===422;
  if(definitive){
    state.pendingKey=null;
    if(state.session?.persona==="staff")state.staffUncertain=false;
    if(subject==="Submission"){
      state.requestUncertain=false;
      show("request-review-box",false);
      text("patient-outcome",`Request was rejected: ${error.message}`);
    }
    show("reconcile",false);status(error.message);
  }
  else {
    if(state.session?.persona==="staff")state.staffUncertain=true;
    if(subject==="Submission"){
      state.requestUncertain=true;
      show("request-review-box",false);
      text("patient-outcome","Submission outcome unverified. Check the original action before another confirmation. The current request state is not verified.");
    }
    show("reconcile",true);status(subject+" outcome uncertain. Check the original action before another confirmation.");
  }
}

async function api(method, action, body, key) {
  if (!state.session) throw new Error("No verified demo session.");
  const response = await fetch("/demo/stage1/action", {
    method: "POST", credentials: "same-origin", cache: "no-store", redirect: "error",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": state.session.csrf },
    body: JSON.stringify({ method, action, body, idempotency_key: key || null }),
  });
  if (!response.ok) {
    const detail=(await response.json().catch(()=>null))?.detail;
    if(detail==="MOCK_STAFF_SESSION_EXPIRED")show("continue-demo",true);
    if(detail==="DEMO_HUMAN_WINDOW_ENDED")show("continue-demo",false);
    const message=response.status===400 || response.status===422
      ? "Check the date, time and required details. The submitted details were not accepted."
      : response.status===409 ? "Current facts changed. Refresh and review again."
      : response.status===404 ? "This request or appointment is unavailable in the current session."
      : detail==="MOCK_STAFF_SESSION_EXPIRED" ? "Mock organisation access expired. Continue demo; your editable words remain here."
      : detail==="DEMO_HUMAN_WINDOW_ENDED" ? "The recording window has ended. Your editable words remain on this page."
      : response.status===401 || response.status===403 ? "This session cannot perform that action."
      : "The action could not be verified. Check the original action before another confirmation.";
    const error=new Error(message);error.status=response.status;
    error.reauth=detail==="MOCK_STAFF_SESSION_EXPIRED";throw error;
  }
  return response.json();
}

function facts(root, rows) {
  root.replaceChildren();
  const dl = document.createElement("dl");
  for (const [label, value] of rows) {
    const dt = document.createElement("dt"); dt.textContent = label;
    const dd = document.createElement("dd"); dd.textContent = value ?? "Unknown";
    dl.append(dt, dd);
  }
  root.append(dl);
}
let labLoaded = false;
function labParagraph(root, value) {
  const p = document.createElement("p"); p.textContent = value; root.append(p);
}
function labCounts(part) {
  if (!part || part.status === "NOT_APPLICABLE") return "Not applicable to this group";
  return `${part.denominator} eligible episode(s): ${part.counts.CONTAINED} contained, ${part.counts.RECOVERED_BY_OBSERVED_HUMAN} recovered by observed human action, ${part.counts.NOT_CONTAINED} not contained, ${part.counts.UNRESOLVED} unresolved, ${part.counts.OUTCOME_CORRECT_CAUSE_UNRESOLVED} correct outcome with cause unresolved`;
}
function displayNative04(root, native) {
  if (!native || native.schema !== "emr4.stage1_reliability_native04_view.v1" ||
      native.qualification !== "EXTERNALLY_REVIEWED_RESULT_DELIVERY_ONLY") return;
  const heading = document.createElement("h3");
  heading.textContent = "Two observed synthetic controls"; root.append(heading);
  labParagraph(root, `Native04 delivered two bounded projections with an independent effect review (${native.effect_review_sha256}). Internal source origin: ${native.source_origin}; internal runtime binding: ${native.internal_runtime_binding}; internal grade: ${native.internal_grade}. This does not establish a whole-journey grade.`);
  labParagraph(root, `Catalog dispositions: ${native.current_controls} current controls, ${native.qualified_reused_boundaries} qualified reused boundaries, ${native.not_run_catalog_cases} NOT_RUN. Reused boundaries are not new episodes. New unique case coverage from this delivery: ${native.new_unique_case_coverage}. The two controls had ${native.phase_reports_for_two_controls} setup/call/teardown reports.`);
  const appointment = value => value ? `${value.date} ${value.start_local} · ${value.status}` : "None observed";
  for (const control of native.controls) {
    const card = document.createElement("div"); card.className = "fact-card";
    const title = document.createElement("h4");
    title.textContent = `${control.case_id} · ${control.journey} valid control`; card.append(title);
    const body = document.createElement("div");
    facts(body, [
      ["Before", `${control.before.appointment_count} appointment(s); request ${control.before.request_state ?? "not reported"}; selected appointment ${appointment(control.before.appointment)}`],
      ["After", `${control.after.appointment_count} appointment(s); request ${control.after.request_state ?? "not reported"}; selected appointment ${appointment(control.after.appointment)}`],
      ["Observed command and audit", `${control.new_command_count} command, ${control.new_audit_count} audit record`],
      ["Readback", `current ${control.current_readback}; patient ${control.patient_readback}; source ${control.source_readback}`],
      ["Qualification", `grade ${control.grade}; display ${control.display}`],
      ["Request, proposal and validation detail", "Absent from the delivered projection; catalog expectations are not observed results."],
    ]);
    card.append(body); root.append(card);
  }
  labParagraph(root, `Actual model: ${native.actual_model}; voice: ${native.voice}. No inference or episode runs when this view opens.`);
}
function displayLabProgress(root, progress) {
  if (!progress || progress.schema !== "emr4.stage1_reliability_progress_view.v2") return;
  const heading = document.createElement("h3");
  heading.textContent = "What the bounded evidence covers"; root.append(heading);
  const dispositions = progress.baseline_dispositions;
  labParagraph(root, `Bound evidence marker: ${progress.evidence_through}. The authored catalog has ${progress.catalog_cases} distinct cases in ${progress.catalog_families} families. Its prior evidence review classified ${dispositions.current_controls} current controls, ${dispositions.qualified_reused_boundaries} reused boundaries and ${dispositions.not_run} NOT_RUN cases. Test attempts, phase reports and delivered records below are separate counts; they do not increase catalog coverage.`);
  for (const attempt of progress.attempts) {
    const card = document.createElement("div"); card.className = "fact-card";
    const title = document.createElement("h4"); title.textContent = attempt.name; card.append(title);
    const body = document.createElement("div");
    facts(body, [
      ["Reviewed status", attempt.status.replaceAll("_", " ")],
      ["Selected test instances", attempt.selected_test_instances],
      ["Setup, call and teardown reports", attempt.phase_reports],
      ["Delivered selected records", attempt.delivered_selected_records],
      ["Selected cases and call phases", attempt.cases.length ?
        attempt.cases.map(item => `${item.case_id}: ${item.call_phase}`).join("; ") :
        "No selected test began"],
    ]);
    card.append(body); root.append(card);
  }
  labParagraph(root, "Native05 and Native07 each attempted the two lost-response selected tests. In each batch CREATE's call failed and MOVE's call passed, but neither batch delivered an accepted selected episode record; the failed CREATE grade-reason set was not retained. A passing test phase is not a whole-journey grade. Native06 and Native08 stopped before Docker and before any test. None of these runs supplies a graded disturbance episode.");
  const labels = {
    "create-valid-01": "Valid create control",
    "move-valid-timeonly-01": "Valid time-only move control",
    "move-attempted-identity-change-05": "Attempted identity change",
    "move-stale-expired-authority-06": "Stale or expired authority",
    "move-source-cancelled-08": "Cancelled source",
    "move-duplicate-lost-response-10": "Completed replay without response loss",
  };
  for (const example of progress.worked_examples) {
    const card = document.createElement("div"); card.className = "fact-card";
    const title = document.createElement("h4");
    title.textContent = `${labels[example.case_id] ?? example.case_id} · ${["NATIVE04_DELIVERED_CONTROL", "CURRENT_DELIVERED_CONTROL"].includes(example.evidence_kind) ? "delivered control" : "reused boundary"}`; card.append(title);
    const body = document.createElement("div");
    facts(body, [
      ["Authored request", example.authored_request],
      ["Authored proposal expectation", example.authored_expected_proposal],
      ["Observed proposal", example.proposal_observation.replaceAll("_", " ")],
      ["Observed validation", example.actual_validation.replaceAll("_", " ")],
      ["Before", example.before_after.before.replaceAll("_", " ")],
      ["After", example.before_after.after.replaceAll("_", " ")],
      ["Readback", example.readback.replaceAll("_", " ")],
      ["Command and audit", example.command_audit.replaceAll("_", " ")],
      ["Outcome", example.outcome.replaceAll("_", " ")],
    ]);
    card.append(body); root.append(card);
  }
  labParagraph(root, `Whole-journey grade: ${progress.whole_journey_grade}. Display and disclosure: ${progress.display}, ${progress.disclosure}. Actual model: ${progress.actual_model}; M1 model binding: ${progress.m1_model_binding}; generated-silence voice: ${progress.generated_silence_voice}; genuine push-to-talk voice: ${progress.genuine_ptt_voice}. No inference or evaluation runs when this view opens.`);
}
function displayLab(view) {
  const root = $("reliability-lab-content"); root.replaceChildren();
  if (!view || !["emr4.stage1_reliability_lab_view.v1",
                  "emr4.stage1_reliability_lab_view.v2",
                  "emr4.stage1_reliability_lab_view.v3"].includes(view.schema)) {
    labParagraph(root, "Report unavailable. No evaluation result is shown."); return;
  }
  if (view.status === "NOT_RUN") {
    labParagraph(root, "NOT_RUN · No aggregate outcome report is bound to this demo session.");
    labParagraph(root, view.native04 ?
      "The aggregate grader is NOT_RUN here. Two separately reviewed control projections are shown below; they do not supply a whole-journey grade." :
      "Catalog: 16 authored cases across 11 families. None are counted as executed episodes here.");
    if (view.native04) displayNative04(root, view.native04);
    if (view.progress) displayLabProgress(root, view.progress);
    return;
  }
  labParagraph(root, `Source: ${view.source_schema} · ${view.origin}. Catalog: ${view.catalog_sha256}. External runtime qualification: ${view.external_runtime_qualification}. Actual model: ${view.actual_model}. Voice: ${view.voice}.`);
  labParagraph(root, `Catalog: ${view.catalog_cases} authored cases across ${view.catalog_families} families. Selected records: ${view.records}; unrun: ${view.unrun}; supplied-record grades: ${view.groups.reduce((count, group) => count + group.episodes, 0)}.`);
  labParagraph(root, `Canonical linkage nonpass: ${view.canonical_link_nonpass}. Patient readback unresolved: ${view.unresolved_patient_readback}. Singleton readback unresolved: ${view.unresolved_singleton_readback}. These counts are not pooled into a risk rate.`);
  if (view.status === "BOUND_UNGRADED") labParagraph(root, "A versioned report is bound, but no episode has an eligible supplied-record grade. Reported nonpass and unresolved records remain visible above; outcome and measurement grades are NOT_RUN / not measured.");
  for (const group of view.groups) {
    const card = document.createElement("div"); card.className = "fact-card";
    const title = document.createElement("h3"); title.textContent = `${group.set_kind} · ${group.journey} · ${group.channel}`; card.append(title);
    const body = document.createElement("div");
    facts(body, [
      ["Evidence", `${group.evidence_class}; ${group.boundaries.length ? group.boundaries.join(", ") : "no boundary mode"}`],
      ["Unique cases", group.unique_cases], ["Unique families", group.unique_families],
      ["Episodes", group.episodes], ["Repeat trials", group.repeat_trials],
      ["Final outcomes", `${group.final_outcomes.CORRECT} correct, ${group.final_outcomes.INCORRECT} incorrect, ${group.final_outcomes.UNKNOWN} unknown`],
      ["Known observations", `${group.counts.eligible_attempts} eligible attempts, ${group.counts.actual_commits} actual commits, ${group.counts.model_error_episodes} model error episodes`],
      ["Missing observations", `${group.missing_count_observations.eligible_attempts} eligible-attempt, ${group.missing_count_observations.actual_commits} commit, ${group.missing_count_observations.model_error_episodes} model-error counts missing`],
      ["Natural error containment", labCounts(group.natural_error_containment)],
      ["Deliberate challenge containment", labCounts(group.deliberate_challenge_containment)],
      ["Latency", group.latency], ["Cost", group.cost],
    ]);
    card.append(body);
    root.append(card);
  }
  labParagraph(root, "Worked appointment examples: not available in the bound summary. No raw request, proposal, confirmation token, audit record or recording is exposed here.");
  if (view.native04) displayNative04(root, view.native04);
  if (view.progress) displayLabProgress(root, view.progress);
}
$("reliability-lab").addEventListener("toggle", async () => {
  if (!$("reliability-lab").open || labLoaded || state.session?.persona !== "staff") return;
  labLoaded = true;
  text("reliability-lab-content", "Reading the bound local report…");
  try {
    const response = await fetch("/demo/stage1/reliability", {
      method: "GET", credentials: "same-origin", cache: "no-store", redirect: "error" });
    if (!response.ok) throw new Error("unavailable");
    displayLab(await response.json());
  } catch (_) { text("reliability-lab-content", "Report unavailable. No evaluation was started."); }
});
function clearPending() {
  state.bookingReview=null;
  spoken?.stop();
  state.proposalGeneration++;
  state.create = state.move = state.offer = state.moveReview = null;
  show("create-review", false); show("move-review", false);
}
function displayRequest(request, original, options = [], uncertain = false) {
  const previousTarget=selectedVoiceTarget();
  state.request = request;
  if (uncertain === true) state.requestUncertain = true;
  else if (uncertain === false) state.requestUncertain = false;
  if(previousTarget!==selectedVoiceTarget())invalidateIntent("request");
  if (!request) { text("patient-outcome", "Request unavailable."); return; }
  if (request.state === "draft" && Array.isArray(options) && options.length) {
    const dates = [...new Set(options.map(option => option.date))].sort();
    $("request-date").min = dates[0]; $("request-date").max = dates.at(-1);
    if (!dates.includes($("request-date").value)) $("request-date").value = dates[0];
    if (!$("request-earliest").value) $("request-earliest").value = "14:00";
    if (!$("request-latest").value) $("request-latest").value = "17:00";
    text("request-options-note", `Request dates currently offered: ${dates.join(", ")}. These are request choices, not reserved appointments.`);
  }
  const booked = request.state === "booked" && request.booked_appointment_id && request.booked_start_time;
  const message = state.requestUncertain
    ? "Submission outcome unverified. Check the original action before another confirmation. The current request state is not verified."
    : booked
    ? `This request led to a booking. ${original?.source === "completed_create_command_result" ?
      `Original booking result: ${dateTime(original.date, original.start_local, original.zone)}. ` :
      "The original booking command result is unavailable in this demo session. "}Current appointment time from readback: ${request.booked_start_time}. Current status: ${request.booked_status}.`
    : request.state === "submitted"
      ? "Request received. Reception One has not confirmed a booking. No time is reserved."
      : request.state === "draft" ? "Draft request. Review and send when ready." : `Request state: ${request.state}.`;
  text("patient-outcome", message);
  $("request-entry").hidden=request.state!=="draft" || !$("request-review-box").hidden;
  if (state.requestUncertain) show("request-review-box", false);
  renderMapping("request");
}
function checkedPreparedBooking(value,request) {
  const exact=(v,keys)=>v && typeof v==="object" && !Array.isArray(v) &&
    Object.keys(v).sort().join("|")===keys.slice().sort().join("|");
  if(!exact(value,["schema","prepared_options_ref","request_version","intent","result",
      "requires_human_choice","requires_confirmation","write_performed","options"]) ||
      value.schema!=="emr4.request_booking_prepared_options.v1" ||
      typeof value.prepared_options_ref!=="string" || !/^[A-Za-z0-9_-]{32}$/.test(value.prepared_options_ref) ||
      value.intent!=="request_booking" || !["proposal_ready","clarification_required"].includes(value.result) ||
      value.requires_human_choice!==true || value.requires_confirmation!==true || value.write_performed!==false ||
      !Number.isSafeInteger(value.request_version) || value.request_version!==request.request_version ||
      request.state!=="submitted" || !Array.isArray(value.options) || value.options.length>7 ||
      value.result==="proposal_ready" && value.options.length===0)
    throw new Error("Prepared request options unavailable. Refresh current facts.");
  const seen=new Set();
  for(const o of value.options) {
    if(!exact(o,["date","local_time","zone"]) || !/^\d{4}-\d{2}-\d{2}$/.test(o.date) ||
        !/^(?:[01]\d|2[0-3]):[0-5]\d$/.test(o.local_time) ||
        typeof o.zone!=="string" || !o.zone || seen.has(JSON.stringify(o)))
      throw new Error("Prepared request options unavailable.");
    seen.add(JSON.stringify(o));
  }
  return value;
}
function displayStaff(data) {
  if (!data || !data.request) { text("staff-request", "Request unavailable."); return; }
  const requestKeys=new Set(["request_id","patient_id","state","request_version","preference_date",
    "earliest_local","latest_local","practice_timezone","booked_appointment_id","booked_start_time",
    "booked_status","historical_request_result"]);
  if(Object.keys(data.request).some(k=>!requestKeys.has(k)))
    throw new Error("Private request data refused.");
  state.request = data.request;
  state.appointment = data.appointment || null;
  if(Object.hasOwn(data,"prepared_request_booking")) {
    state.bookingPrepared=data.prepared_request_booking==null ? null :
      checkedPreparedBooking(data.prepared_request_booking,data.request);
    if(state.bookingPrepared && JSON.stringify(data.options)!==JSON.stringify(state.bookingPrepared.options))
      throw new Error("Prepared options changed.");
  } else state.bookingPrepared=null;
  if(data.uncertain===true || data.request.state!=="submitted")state.bookingPrepared=null;

  if(data.uncertain===true)state.staffUncertain=true;
  else if(data.uncertain===false)state.staffUncertain=false;
  invalidateIntent("move");
  const r = data.request;
  const clarificationNeeded = !state.staffUncertain && state.bookingPrepared?.result === "clarification_required";
  $("staff-request").hidden=r.state==="booked";
  facts($("staff-request"), [
    ["Request", r.state],
    ["Preference", r.preference_date && r.earliest_local && r.latest_local
      ? `${r.preference_date}, ${r.earliest_local}–${r.latest_local} ${r.practice_timezone}` : "Not submitted"],
    ...(clarificationNeeded ? [["Next step", "Clarification is required. No booking is prepared."]] : [])]);
  facts($("staff-request-details"), [
    ["Source", "Synthetic patient web text"],
    ["Identity", "Fictional demo session; no real patient identity"],
    ["Request version", r.request_version],
    ...(state.bookingPrepared ? [["Prepared intent","Book this existing request"],
      ["Next step",state.bookingPrepared.options.length ? "Choose a time, then confirm separately." :
        "Clarification is required. No booking is prepared."]] : []),
    ["Original booking result", data.original_booking?.source === "completed_create_command_result"
      ? dateTime(data.original_booking.date, data.original_booking.start_local, data.original_booking.zone)
      : "Unavailable in this demo session"],
  ]);
  const appt = data.appointment;
  show("move-area", Boolean(appt));
  if (appt) {
    facts($("diary"), [["Current appointment", dateTime(appt.date, appt.start_local, appt.zone)],
      ["Patient", appt.patient_label], ["Practitioner", appt.practitioner_label],
      ["Type", appt.type_label], ["Duration", `${appt.duration_minutes} minutes`]]);
    facts($("diary-details"), [["Status", appt.status], ["Location", appt.location_label],
      ["Appointment version", appt.state_version], ["Appointment reference", appt.ref]]);
  } else {$("diary").replaceChildren();$("diary-details").replaceChildren();}
  const offers = $("staff-offers"); offers.replaceChildren();
  if (Array.isArray(data.options)) for (const option of data.options) {
    const row = document.createElement("div"); row.className = "offer";
    const label = document.createElement("span"); label.textContent = dateTime(option.date, option.local_time, option.zone);
    const button = document.createElement("button"); button.type = "button"; button.textContent = "Review this time";
    button.addEventListener("click", () => reviewCreate(option)); row.append(label, button); offers.append(row);
  }
  const noOptionMessage = "No current option is available. Offer an alternative through the reviewed backend flow.";
  const clarificationMessage = "Clarification is required. No booking is prepared.";
  if ([noOptionMessage, clarificationMessage].includes($("staff-outcome").textContent))
    text("staff-outcome", "");
  if (!state.staffUncertain && !data.options?.length && r.state === "submitted")
    text("staff-outcome", clarificationNeeded ? clarificationMessage : noOptionMessage);
  document.dispatchEvent(new CustomEvent("raisa:staff-facts", {detail:{
    request_state:r.state,appointment_ref:appt?.ref||null,
    appointment_version:appt?.state_version??null}}));
}
function consumePreparedMove(value) {
  const exact=(v,keys)=>v && typeof v==="object" && !Array.isArray(v) &&
    Object.keys(v).sort().join("|")===keys.slice().sort().join("|");
  const hash=v=>typeof v==="string" && /^[a-f0-9]{64}$/.test(v);
  if(!exact(value,["schema","prepared_review_ref","review","provenance"]) ||
      value.schema!=="emr4.current_point_v3_prepared_move_review.v1" ||
      typeof value.prepared_review_ref!=="string" || !/^[A-Za-z0-9_-]{32}$/.test(value.prepared_review_ref))
    throw new Error("Prepared move unavailable. Refresh current facts.");
  const r=value.review,p=value.provenance,a=state.appointment;
  if(!exact(r,["appointment_ref","source_state_version","source_date","source_start_local","target_date",
      "target_start_local","duration_minutes","requires_confirmation","autonomy_tier","warnings","blocks"]) ||
      !exact(p,["method","request_id","context_revision","frame_sha256","raw_sha256","compiled_plan_sha256",
      "planner_source_sha256","schema_sha256"]) || !a || a.status!=="Booked" ||
      r.appointment_ref!==a.ref || !Number.isSafeInteger(r.source_state_version) || r.source_state_version!==a.state_version ||
      r.source_date!==a.date || r.source_start_local!==a.start_local ||
      !Number.isSafeInteger(r.duration_minutes) || r.duration_minutes!==a.duration_minutes ||
      r.requires_confirmation!==true || r.autonomy_tier!=="proposal" || !Array.isArray(r.blocks) || r.blocks.length ||
      !Array.isArray(r.warnings) || !r.warnings.includes("staff_confirmation_required") ||
      r.warnings.some(w=>!["staff_confirmation_required","no_reservation"].includes(w)) ||
      new Set(r.warnings).size!==r.warnings.length || !/^\d{4}-\d{2}-\d{2}$/.test(r.target_date) ||
      !/^(?:[01]\d|2[0-3]):[0-5]\d$/.test(r.target_start_local) ||
      p.method!=="BUREAU_SYNTHETIC_MODEL_REPLY" || typeof p.request_id!=="string" || !p.request_id ||
      !Number.isSafeInteger(p.context_revision) || p.context_revision<1 ||
      ![p.frame_sha256,p.raw_sha256,p.compiled_plan_sha256].every(hash) || p.raw_sha256===p.compiled_plan_sha256 ||
      p.planner_source_sha256!=="45a28b40611508910fd338f775644ff4863fd0ff84609040cb697d157a09b2d8" ||
      p.schema_sha256!=="05f324de7c7c01254e666c754b44631652e794ff9a3a45c87d5106478725d5a0")
    throw new Error("Prepared move provenance or appointment changed. Refresh current facts.");
  // Adopt the existing checked review; no interpretation or proposal request.
  $("move-words").value="";
  $("move-date").value=r.target_date;$("move-time").value=r.target_start_local;
  interpretedNotes.move=JSON.stringify(intentSnapshot("move"));
  state.move=value.prepared_review_ref;
  state.moveReview={snapshot:JSON.stringify(intentSnapshot("move")),generation:interpretationGeneration.move,
    proposalGeneration:state.proposalGeneration};
  facts($("move-summary"),[["Instruction","Prepared synthetic point move"],
    ["Before",dateTime(a.date,a.start_local,a.zone)],["After",dateTime(r.target_date,r.target_start_local,a.zone)]]);
  const unchanged=document.createElement("p");unchanged.className="helper";
  unchanged.textContent=`Unchanged: ${a.patient_label} · ${a.practitioner_label} · ${a.type_label} · ${a.duration_minutes} minutes · ${a.location_label}. Review this time before choosing Confirm move. The proposed time is not held.`;
  $("move-summary").append(unchanged);show("move-review",true);
}

async function refresh() {
  if (state.session?.persona === "patient" && state.busy) {
    status("Wait for the current submission result before refreshing.");
    return null;
  }
  invalidateIntent("request");invalidateIntent("move");
  clearPending(); const generation = ++state.generation;
  status("Refreshing current facts…");
  try {
    const result = await api("read", "refresh", null);
    if (generation !== state.generation) return;
    if (state.session.persona === "patient") displayRequest(result.request, result.original_booking, result.options, result.uncertain);
    else {
      displayStaff(result);
      if(result.prepared_move_review!=null && !state.staffUncertain && !state.busy)
        consumePreparedMove(result.prepared_move_review);
    }
    // A staff confirmation keeps its original key until this caller verifies
    // the matching appointment readback below. Other definitive reads clear it.
    if (result.uncertain === false && !(state.session.persona==="staff" && state.busy))
      state.pendingKey = null;
    const uncertain=state.session.persona==="staff"?state.staffUncertain:state.requestUncertain;
    show("reconcile", uncertain);
    status(uncertain ? "An earlier action is still uncertain. Check that original action before any new confirmation." :
      "Current facts loaded. Check the practice date and time before acting.");
    return result;
  } catch (error) { status(error.message); return null; }
}
function requestFields() {
  const date = $("request-date").value, earliest_local = $("request-earliest").value,
    latest_local = $("request-latest").value;
  if (!date || !earliest_local || !latest_local || earliest_local >= latest_local)
    throw new Error("Choose a date and a valid start and end of your preferred window.");
  return { date, earliest_local, latest_local };
}
function reviewRequest() {
  state.requestReview=null;show("request-review-box",false);
  try {
    if (state.requestUncertain) throw new Error("Check the original action before reviewing or sending another request.");
    const value = requestFields();
    if (!state.request || state.request.state !== "draft") throw new Error("Refresh the draft request before submitting.");
    const snapshot=intentSnapshot("request");
    if(!intentHandoffs.request.inspect(snapshot).supported || !hasCurrentInterpretation("request") ||
        (localVoice && !localVoice.isIdle()))
      throw new Error("Check the current suggested or structured details before preparing the request.");
    state.requestReview={snapshot:JSON.stringify(snapshot),generation:interpretationGeneration.request};
    text("request-summary", `Follow-up · ${value.date} · ${value.earliest_local}–${value.latest_local} ${state.session.zone}`);
    text("request-words-review",snapshot.words.trim());
    $("request-words-review").hidden=!snapshot.words.trim();
    show("request-review-box", true); $("request-submit").focus();
    status("Your request is ready to review. Nothing has been sent.");
  } catch (error) { $("request-structured").open=true;status(error.message); }
}
async function submitRequest() {
  if(state.requestUncertain){
    show("request-review-box",false);
    status("Check the original action before sending another request.");
    return;
  }
  let value;
  try { finalHumanReview("request",state.requestReview,state.requestUncertain);value=requestFields(); }
  catch(error){show("request-review-box",false);status(error.message);return;}
  try {
    if (state.busy) return;
    state.requestReview=null;
    const key = state.pendingKey || uuid(); state.pendingKey = key; state.busy = true;
    status("Sending request…");
    text("patient-outcome", "Sending request… No booking is being made yet.");
    const result = await api("write", "submit_request", { ...value, request_version: state.request.request_version,
      reason_code: "follow_up" }, key);
    state.pendingKey = null; show("request-review-box", false); displayRequest(result.request, result.original_booking, result.options);
    status("Request result read back from the server.");
  } catch (error) {
    if (error?.status !== 400 && error?.status !== 401 && error?.status !== 403 && error?.status !== 422) {
      show("request-review-box", false);
      text("patient-outcome", "Submission outcome unverified. Check the original action before another confirmation. The current request state is not verified.");
    }
    showWriteFailure(error,"Submission");
  }
  finally { state.busy = false; }
}
async function reviewCreate(option) {
  if(state.staffUncertain || state.busy){status("Check the original action before preparing another booking.");return;}
  const prepared=state.bookingPrepared;
  if(prepared && !prepared.options.some(o=>JSON.stringify(o)===JSON.stringify(option))) {
    status("This prepared option changed. Refresh current facts.");return;
  }
  clearPending(); status("Checking this time against current request and availability…");
  const proposalGeneration=state.proposalGeneration,requestVersion=state.request?.request_version;
  try {
    const result = await api("read", "propose_create", { request_version: state.request.request_version, selected: option });
    if(proposalGeneration!==state.proposalGeneration || state.request?.request_version!==requestVersion)return;
    if (!result.safe || !result.proposal_ref) throw new Error("This option is unavailable. Refresh current facts.");
    state.create = result.proposal_ref;
    state.bookingReview=prepared ? {optionsRef:prepared.prepared_options_ref,
      requestVersion:prepared.request_version,option:{...option},proposalRef:result.proposal_ref,
      generation:state.generation,proposalGeneration:state.proposalGeneration} : null;
    text("create-summary", `Create a follow-up for ${result.patient_label} with ${result.practitioner_label} on ${dateTime(option.date, option.local_time, option.zone)}. This is a fresh proposal, not a booking.`);
    show("create-review", true); $("create-confirm").focus(); status("Review the proposed booking before confirmation.");
  } catch (error) { status(error.message); }
}
async function confirmCreate() {
  if (!state.create || state.busy) return;
  const bookingReview=state.bookingReview;
  if(bookingReview && (!state.bookingPrepared ||
      state.bookingPrepared.prepared_options_ref!==bookingReview.optionsRef ||
      state.bookingPrepared.request_version!==bookingReview.requestVersion ||
      state.request?.request_version!==bookingReview.requestVersion ||
      state.create!==bookingReview.proposalRef || state.generation!==bookingReview.generation ||
      state.proposalGeneration!==bookingReview.proposalGeneration)) {
    clearPending();status("The prepared request changed. Refresh before confirming.");return;
  }
  if(state.staffUncertain){status("Check the original action before confirming another booking.");return;}
  state.busy = true; const key = state.pendingKey || uuid(); state.pendingKey = key;
  status("Confirming booking and checking committed readback…");
  try {
    const result = await api("write", "confirm_create", { proposal_ref: state.create }, key);
    clearPending();
    if (result.outcome !== "committed" || !result.appointment) throw new Error("No verified booking readback.");
    if(bookingReview) {
      const r=result.command_receipt;
      if(!r || Object.keys(r).sort().join("|")!==["schema","request_version","appointment_ref",
          "appointment_state_version","database_readback_verified"].sort().join("|") ||
          r.schema!=="emr4.request_booking_verified_outcome.v1" ||
          r.request_version!==bookingReview.requestVersion+1 ||
          r.appointment_ref!==result.appointment.ref || r.database_readback_verified!==true ||
          r.appointment_state_version!==result.appointment.state_version)
        throw new Error("Original request booking outcome is unverified.");
    }
    const current = await refresh();
    if (!current?.appointment || !current.appointment.zone ||
        current.appointment.ref !== result.appointment.ref ||
        current.appointment.date !== result.appointment.date ||
        current.appointment.start_local !== result.appointment.start_local)
      throw new Error("Booking readback did not match the command result.");
    if(bookingReview && (current.request?.state!=="booked" ||
        current.request.request_version!==bookingReview.requestVersion+1 ||
        current.request.booked_appointment_id!==result.appointment.ref ||
        current.appointment.state_version!==result.command_receipt.appointment_state_version ||
        current.appointment.date!==bookingReview.option.date ||
        current.appointment.start_local!==bookingReview.option.local_time))
      throw new Error("Request version or new appointment readback did not match.");
    state.pendingKey = null;
    const message = `Booking confirmed for ${dateTime(current.appointment.date, current.appointment.start_local, current.appointment.zone)}. You can still view the original request.`;
    status(message); spoken?.offer(message);
  } catch (error) { if(!error?.reauth)clearPending();showWriteFailure(error,"Booking"); }
  finally { state.busy = false; }
}
async function reviewMove() {
  if(state.staffUncertain || state.busy){status("Check the original action before preparing another move.");return;}
  clearPending();
  const appointment = state.appointment, date = $("move-date").value, local_time = $("move-time").value;
  if (!appointment || !date || !local_time) { $("move-structured").open=true;status("Select a current appointment, new date and time."); return; }
  const snapshot=intentSnapshot("move"),generation=interpretationGeneration.move,
    proposalGeneration=state.proposalGeneration;
  if(!intentHandoffs.move.inspect(snapshot).supported || !hasCurrentInterpretation("move") ||
      (localVoice && !localVoice.isIdle())){
    status("Check the current suggested or structured move details before preparing the proposal.");return;
  }
  status("Checking the exact appointment and proposed time…");
  try {
    const result = await api("read", "propose_move", { appointment_ref: appointment.ref,
      source_state_version: appointment.state_version, target_date: date, target_start_local: local_time });
    if(proposalGeneration!==state.proposalGeneration || generation!==interpretationGeneration.move ||
        JSON.stringify(intentSnapshot("move"))!==JSON.stringify(snapshot) ||
        state.appointment?.ref!==appointment.ref ||
        state.appointment?.state_version!==appointment.state_version ||
        (localVoice && !localVoice.isIdle()))return;
    if (!result.safe || !result.proposal_ref) throw new Error("Move unavailable. Refresh the appointment.");
    state.moveReview={snapshot:JSON.stringify(snapshot),generation,proposalGeneration};
    state.move = result.proposal_ref;
    facts($("move-summary"), [["Instruction", snapshot.words.trim()||"No note; structured details only"],
      ["Before", dateTime(appointment.date, appointment.start_local, appointment.zone)],
      ["After", dateTime(date, local_time, appointment.zone)]]);
    const unchanged=document.createElement("p");unchanged.className="helper";
    unchanged.textContent=`Unchanged: ${appointment.patient_label} · ${appointment.practitioner_label} · ${appointment.type_label} · ${appointment.duration_minutes} minutes · ${appointment.location_label}. Review this time before choosing Confirm move. The proposed time is not held.`;
    $("move-summary").append(unchanged);
    show("move-review", true); $("move-confirm").focus(); status("Your proposed move is ready. The appointment has not changed yet.");
  } catch (error) { status(error.message); }
}
async function confirmMove() {
  if (!state.move || state.busy) return;
  if(state.staffUncertain){status("Check the original action before confirming another move.");return;}
  try {
    if(state.moveReview?.proposalGeneration!==state.proposalGeneration)throw new Error("stale");
    finalHumanReview("move",state.moveReview,state.staffUncertain);
  } catch (_) {clearPending();status("The prepared move changed. Check a fresh proposal before confirming.");return;}
  const before = state.appointment;
  state.moveReview=null;
  state.busy = true; const key = state.pendingKey || uuid(); state.pendingKey = key;
  status("Confirming move and checking the same appointment…");
  try {
    const result = await api("write", "confirm_move", { proposal_ref: state.move }, key);
    clearPending();
    if (result.outcome !== "committed" || !result.appointment) throw new Error("No verified move readback.");
    const current = await refresh();
    if (!current?.appointment || !current.appointment.zone ||
        current.appointment.ref !== result.appointment.ref ||
        current.appointment.date !== result.appointment.date ||
        current.appointment.start_local !== result.appointment.start_local)
      throw new Error("Move readback did not match the command result.");
    if (!before || current.appointment.ref !== before.ref ||
        current.appointment.zone !== before.zone ||
        ["patient_label", "practitioner_label", "type_label", "duration_minutes", "location_label"]
          .some(field => current.appointment[field] !== before[field]))
      throw new Error("The same appointment and unchanged details were not verified.");
    state.pendingKey = null;
    const message = `The same appointment was moved to ${dateTime(current.appointment.date, current.appointment.start_local, current.appointment.zone)}.`;
    status(message); spoken?.offer(message);
  } catch (error) { if(!error?.reauth)clearPending();showWriteFailure(error,"Move"); }
  finally { state.busy = false; }
}

$("request-suggest").addEventListener("click",()=>suggestFromWords("request"));
$("move-suggest").addEventListener("click",()=>suggestFromWords("move"));
$("request-review").addEventListener("click", reviewRequest);
$("request-edit").addEventListener("click", () => { invalidateIntent("request"); spoken?.stop(); show("request-review-box", false); $("request-structured").open=true; $("request-date").focus(); });
$("request-submit").addEventListener("click", submitRequest);
$("patient-refresh").addEventListener("click", refresh);
$("staff-refresh").addEventListener("click", refresh);
$("create-confirm").addEventListener("click", confirmCreate);
$("create-cancel").addEventListener("click", () => { clearPending(); $("staff-offers").querySelector("button")?.focus(); });
$("move-propose").addEventListener("click", reviewMove);
$("move-confirm").addEventListener("click", confirmMove);
$("move-cancel").addEventListener("click", () => { invalidateIntent("move"); clearPending(); $("move-structured").open=true; $("move-date").focus(); });
$("reconcile").addEventListener("click", async () => {
  if (state.busy) {
    status("Wait for the current action result before checking the original action.");
    return;
  }
  invalidateIntent("request");invalidateIntent("move");
  status("Checking the original action with its existing command key…");
  try {
    const result = await api("read", "reconcile", null);
    if (state.session.persona === "patient") displayRequest(result.request, result.original_booking, result.options, result.uncertain); else displayStaff(result);
    if (result.uncertain === false) state.pendingKey = null;
    const uncertain=state.session.persona==="staff"?state.staffUncertain:state.requestUncertain;
    show("reconcile", uncertain);
    status(uncertain ? "Outcome remains uncertain; no new action was started." : "Original action reconciled; current facts refreshed.");
  } catch (_) {
    if(state.session?.persona==="staff")state.staffUncertain=true;
    else state.requestUncertain=true;
    show("request-review-box",false);
    show("reconcile", true);
    if(state.session?.persona==="patient")text("patient-outcome","Submission outcome unverified. Check the original action before another confirmation. The current request state is not verified.");
    status("Original action remains uncertain. No new action was started.");
  }
});
$("continue-demo").addEventListener("click", async () => {
  if(state.session?.persona!=="staff" || state.busy)return;
  $("continue-demo").disabled=true;
  status("Checking current synthetic organisation access for this same staff session…");
  try {
    const response=await fetch("/demo/stage1/continue",{method:"POST",credentials:"same-origin",
      cache:"no-store",redirect:"error",headers:{"Content-Type":"application/json",
        "X-CSRF-Token":state.session.csrf},body:"{}"});
    if(!response.ok)throw new Error(response.status===403?
      "Current mock organisation access or the recording window is unavailable. Your words remain editable.":
      "This session could not continue. Your words remain editable.");
    const result=await response.json();
    if(result?.continued!==true || typeof result.mock_token_expires_at!=="string" ||
        result.human_window_ends_at!==state.session.human_window_ends_at)
      throw new Error("Continuation response could not be verified. Your words remain editable.");
    state.session.mock_token_expires_at=result.mock_token_expires_at;
    show("continue-demo",false);
    armAuthPrompt();
    status("Mock organisation access checked for the same staff session. Review your words and current facts before choosing an action. No command was repeated.");
  }catch(error){status(error.message);}
  finally{$("continue-demo").disabled=false;}
});
for (const id of ["request-date", "request-earliest", "request-latest", "patient-words"]) $(id).addEventListener("input", () => invalidateIntent("request"));
for (const id of ["move-date", "move-time", "move-words"]) $(id).addEventListener("input", () => invalidateIntent("move"));

async function startWorkspace() {
 try {
  const response = await fetch("/demo/stage1/session", { credentials: "same-origin", cache: "no-store", redirect: "error" });
  if (!response.ok) throw new Error("The local demo session is unavailable.");
  const session = await response.json();
  if (!session || !["patient", "staff"].includes(session.persona) || !session.csrf || !session.zone || !session.demo_clock)
    throw new Error("The local demo session is incomplete.");
  state.session = session;
  if (session.persona === "staff") {
    const identity = session.mock_identity;
    if (!identity || identity.mode !== "synthetic_mock" || identity.mock !== true ||
        identity.status !== "active" || typeof identity.user_label !== "string" ||
        !identity.user_label || identity.user_label.length > 80)
      throw new Error("Current mock organisation access could not be verified. No appointment action is available.");
    text("mock-identity", `${identity.user_label} · Synthetic organisation access checked. Backend permissions and your confirmation are still required. This is not a real PRODA sign-in.`);
    show("mock-identity", true);
    armAuthPrompt();
  }
  text("role", session.persona === "patient" ? "Alex · patient request" :
    accountIdentity ? `${accountIdentity.practice_name} · ${accountIdentity.role}` : "Reception One · staff");
  text("title", session.persona === "patient" ? "When would you like to come in?" : "How can I help with your appointments?");
  text("intro", session.persona === "patient" ? "Tell Reception One when you prefer to come. A request does not reserve a time." : "Review the current request and appointment, then choose what you want to do.");
  text("clock", `Practice clock when this page loaded: ${session.demo_clock} · Practice timezone: ${session.zone}`);
  document.querySelectorAll(".zone").forEach(node => { node.textContent = session.zone; });
  show("patient", session.persona === "patient"); show("staff", session.persona === "staff");
  if(session.persona==="staff")diaryView=initDiaryView({load:()=>api("read","diary",null)});
  document.dispatchEvent(new CustomEvent("raisa:session-ready", {detail:{persona:session.persona,zone:session.zone}}));
  spoken = initSpokenReply(() => state.session);
  localVoice=initLocalVoice(() => state.session, () => {
    spoken?.stop();invalidateIntent(intentKind(),false);
  }, currentVoiceTarget, () => invalidateIntent(intentKind(),false), () => {
    renderMapping("request");renderMapping("move");
  });
  renderMapping("request");renderMapping("move");
  await refresh();
 } catch (error) { status(error.message); }
}

// Account tokens and passwords never become UI state or browser storage.
let accountCsrf = null;
let accountIdentity = null; // Display only; never used to authorise an action.
let accountBusy = false;
let restorePractitionerAfterAccountBusy = null;
let accountStarted = false;
const patientRecords = initPatientRecords();
let selectedDiaryView=null, selectedDiaryContext=null, selectedDiarySignature=null;
let selectedDiaryEpoch=0, selectedTaskFocus=null, selectedDiaryOpen=false;
document.addEventListener("focusin",event=>{
  if($("patient-records").contains(event.target))selectedTaskFocus=event.target;
});
// Presentation only: these snapshots never authorise an account or practice action.
const ownerPresentation = (() => {
  const details=$("owner-details"), summary=$("owner-details-summary");
  let account=null, complete=false, busy=false, accountPending=false, attention=null, ownerStatus="";
  let compactHandled=false;
  function canCompact() { return complete && account!==null && !busy && !accountPending && attention===null; }
  function render() {
    const context=$("owner-current-practice");
    context.hidden=account===null;
    context.textContent=account ? `${account.practice_name} · ${account.role}` : "";
    summary.textContent=complete && account ? "Practice setup details" : "Practice setup";
    if(attention!==null){
      $("owner-onboarding").hidden=false;
      $("owner-status").textContent=attention;
    }else if(ownerStatus){$("owner-status").textContent=ownerStatus;}
    if(!canCompact()){
      details.open=true;
    }else if(!compactHandled && !details.contains(document.activeElement)){
      compactHandled=true;
      details.open=false;
    }
  }
  summary.addEventListener("click",event=>{
    if(!canCompact()){event.preventDefault();details.open=true;}
    else compactHandled=true;
  });
  details.addEventListener("focusout",()=>queueMicrotask(render));
  return {
    account(value) {
      const identity=value?.identity;
      const selected=value?.enabled===true && value.phase==="selected"
        && identity?.role==="Receptionist" && typeof identity.email==="string"
        && typeof identity.practice_name==="string"
        && value.invitation?.phase!=="review";
      const next=selected ? {key:JSON.stringify([identity.email,identity.practice_name,
        value.staff_booking_context?.practice_id ?? null]),
        practice_name:identity.practice_name,role:identity.role} : null;
      if(next?.key!==account?.key)compactHandled=false;
      account=next;
      render();
    },
    owner(value) {
      complete=value.phase==="verified" && value.invitation?.issued===true
        && value.invitation.can_issue===false;
      ownerStatus=$("owner-status").textContent;
      render();
    },
    busy(value) { busy=value;render(); },
    accountBusy(value) { accountPending=value;render(); },
    attention(message, actionUncertain=false) {
      if(attention===null || actionUncertain)attention=message;
      render();
    },
    confirmed() { attention=null;render(); }
  };
})();

function configureSelectedDiary(value) {
  ownerPresentation.account(value);
  const meta=value?.staff_booking_context, identity=value?.identity;
  const available=value?.selected_diary_available===true && value.phase==="selected"
    && identity?.role==="Receptionist" && typeof value.csrf==="string"
    && typeof meta?.practice_id==="string" && typeof meta.date==="string";
  const signature=available ? JSON.stringify([value.csrf,identity.email,identity.practice_name,
    meta.practice_id,meta.date,meta.duration_minutes]) : null;
  if(signature!==selectedDiarySignature){
    selectedDiaryEpoch++;selectedDiaryView?.deactivate();selectedDiarySignature=signature;
    selectedTaskFocus=null;
  }
  selectedDiaryContext=available ? Object.freeze({generation:selectedDiaryEpoch,
    practice_id:meta.practice_id,date:meta.date}) : null;
  if(!available){
    if(selectedDiaryView){show("view-switch",false);show("view-prompt",false);
      document.querySelector(".workspace-heading").hidden=true;}
    return;
  }
  if(!selectedDiaryView)selectedDiaryView=initDiaryView({
    selectedContext:()=>selectedDiaryContext,
    taskVisibility:(visible,restoreFocus=true)=>{
      selectedDiaryOpen=!visible;patientRecords.setWorkspace(!visible);
      if(visible && restoreFocus){
        const target=selectedTaskFocus;
        if(target?.isConnected && !target.disabled && !$("patient-records").hidden)target.focus();
        else $("focus-view").focus();
      }
    },
    load:async()=>{
      const epoch=selectedDiaryEpoch, token=accountCsrf;
      const current=()=>selectedDiaryContext!==null && selectedDiaryEpoch===epoch && accountCsrf===token;
      if(!current() || !token)throw Error("Diary unavailable");
      const response=await fetch("/demo/stage1/selected-account-diary/read",{
        method:"POST",credentials:"same-origin",cache:"no-store",redirect:"error",
        headers:{"Content-Type":"application/json","X-CSRF-Token":token},body:"{}"});
      if(!current() || !response.ok || !response.body)throw Error("Diary unavailable");
      const reader=response.body.getReader(),chunks=[];let size=0;
      while(true){
        const part=await reader.read();
        if(!current()){await reader.cancel();throw Error("Diary unavailable");}
        if(part.done)break;
        size+=part.value.byteLength;
        if(size>262144){await reader.cancel();throw Error("Diary unavailable");}
        chunks.push(part.value);
      }
      const bytes=new Uint8Array(size);let offset=0;
      for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.byteLength;}
      if(!current())throw Error("Diary unavailable");
      return JSON.parse(new TextDecoder("utf-8",{fatal:true}).decode(bytes));
    }});
  document.querySelector(".workspace-heading").hidden=false;
  patientRecords.setWorkspace(selectedDiaryOpen);
  $("focus-workspace").hidden=true;
  show("view-switch",true);show("view-prompt",true);
  text("title","Your appointments");
  text("intro","Keep your current task, or read appointments starting in the next seven days.");
  text("grid-view","Next seven days");
  text("diary-heading","Appointments starting in the next seven days");
}

function accountBusyState(busy) {
  accountBusy = busy;
  ownerPresentation.accountBusy(busy);
  $("account-panel").querySelectorAll("button,input,select").forEach(node => {
    if (!node.closest("#owner-practitioner-box,#owner-location-box")) node.disabled = busy;
  });
  $("account-logout").disabled=busy;
  if (restorePractitionerAfterAccountBusy) restorePractitionerAfterAccountBusy();
}
function accountWorkspace(visible) {
  patientRecords.setWorkspace(visible);
  show("account-panel", !visible);
  $("focus-workspace").hidden = !visible;
  document.querySelector(".workspace-heading").hidden = !visible;
  document.querySelector(".feedback").hidden = !visible;
  if(!visible){show("view-switch",false);show("view-prompt",false);}
}
function presentAccount(value) {
  if(!value || value.enabled!==true || typeof value.csrf!=="string" ||
      !["login","choose","selected"].includes(value.phase))throw new Error("Sign-in is unavailable. Please reload this page.");
  show("account-invitation-refresh",value.phase==="selected" && Object.hasOwn(value,"invitation"));
  const invitation=value.invitation;
  show("account-invitation",invitation?.phase==="review" && invitation.can_accept===true);
  $("account-invitation-confirm").checked=false;
  if(invitation?.phase==="review")text("account-invitation-review",`${invitation.practice_name} · Receptionist · Existing synthetic receptionist`);
  patientRecords.setAccount(value);
  accountCsrf=value.csrf;
  accountIdentity=value.phase==="selected" ? value.identity : null;
  accountWorkspace(false);
  show("account-login",value.phase==="login");
  show("account-selection",value.phase==="choose");
  show("account-identity",value.phase==="selected");
  show("account-logout",value.phase!=="login");
  show("account-continue",value.phase==="selected" && value.bureau_available===true);
  $("account-password").value="";
  $("account-username").value="";
  const choices=$("account-membership");
  choices.replaceChildren(new Option("Choose a practice", ""));
  if(value.phase==="choose"){
    if(!Array.isArray(value.memberships) || !value.memberships.length)throw new Error("No practice is available. Please sign in again.");
    for(const row of value.memberships){
      if(typeof row.membership_id!=="string" || typeof row.practice_name!=="string" || typeof row.role!=="string")throw new Error("Practice choices are unavailable.");
      choices.append(new Option(`${row.practice_name} · ${row.role}`,row.membership_id));
    }
    text("account-status","Choose your practice, then confirm it.");
    choices.focus();
  }else if(value.phase==="selected"){
    const identity=value.identity;
    if(!identity || typeof identity.email!=="string" || typeof identity.role!=="string" || typeof identity.practice_name!=="string")throw new Error("Your current practice could not be checked.");
    text("account-identity",`${identity.email} · ${identity.practice_name} · ${identity.role}`);
    text("role",`${identity.practice_name} · ${identity.role}`);
    text("account-status",value.bureau_available===true ? "Your practice is ready. Continue when you’re ready." : "You’re signed in. Your practice identity is shown below.");
  }else{
    text("account-identity","");text("role","Sign in");
    text("account-status","Sign in to your fictional practice.");
  }
  configureSelectedDiary(value);
}
async function accountRequest(action, body) {
  if(accountBusy)return;
  accountBusyState(true);
  try{
    patientRecords.setAccount(null);configureSelectedDiary(null);
    const response=await fetch(`/demo/stage1/account/${action}`,{
      method:"POST",credentials:"same-origin",cache:"no-store",redirect:"error",
      headers:{"Content-Type":"application/json","X-CSRF-Token":accountCsrf||""},body:JSON.stringify(body)});
    if(!response.ok)throw new Error("Sign-in could not be completed. Please sign in again.");
    const value=await response.json();
    presentAccount(value);
  }catch(_){
    accountCsrf=null;
    accountIdentity=null;configureSelectedDiary(null);
    text("account-status","Sign-in could not be completed. Reload this page to sign in again.");
    show("account-login",false);show("account-selection",false);
    show("account-identity",false);show("account-continue",false);show("account-logout",false);
    text("account-identity","");
  }finally{
    if(body && Object.hasOwn(body,"password"))body.password="";
    $("account-password").value="";
    accountBusyState(false);
  }
}
$("account-login").addEventListener("submit",async event=>{
  event.preventDefault();
  if(accountBusy)return;
  const username=$("account-username").value,password=$("account-password").value;
  $("account-password").value="";
  await accountRequest("login",{username,password});
});
$("account-selection").addEventListener("submit",async event=>{
  event.preventDefault();
  const membership_id=$("account-membership").value;
  if(membership_id)await accountRequest("select",{membership_id});
});
$("account-invitation-refresh").addEventListener("click",async()=>{
  if(accountBusy)return;
  accountBusyState(true);
  try{const r=await fetch("/demo/stage1/account/state",{credentials:"same-origin",cache:"no-store",redirect:"error"});
    if(!r.ok)throw new Error();presentAccount(await r.json());}
  catch(_){patientRecords.setAccount(null);configureSelectedDiary(null);text("account-status","The invitation could not be checked. Sign in again.");}
  finally{accountBusyState(false);}
});
$("account-invitation-form").addEventListener("submit",async event=>{
  event.preventDefault();if($("account-invitation-confirm").checked)await accountRequest("accept-invitation",{confirmed:true});
});
$("account-logout").addEventListener("click",async()=>{
  if(accountBusy || state.busy)return;
  await accountRequest("logout",{});
  // Drop all appointment projections and pending UI work with this page.
  window.location.reload();
});
$("account-continue").addEventListener("click",async()=>{
  if(accountBusy || accountStarted)return;
  accountStarted=true;accountBusyState(true);
  accountWorkspace(true);
  await startWorkspace();
  accountBusyState(false);
});
try{
  const response=await fetch("/demo/stage1/account/state",{credentials:"same-origin",cache:"no-store",redirect:"error"});
  if(!response.ok)throw new Error("Sign-in is unavailable. Reload this page to try again.");
  const value=await response.json();
  if(value?.enabled===false)await startWorkspace();
  else presentAccount(value);
}catch(_){status("The local session is unavailable. Reload this page to try again.");}

// Optional local owner setup; tokens remain server-side and no Bureau session is issued.
(async () => {
  let csrf = null, busy = false;
  const el = id => document.getElementById(id);
  // STOPPED SOURCE ONLY. Removing either client/server barrier requires later
  // exact reviewed source adoption and finite bindings, never a DOM toggle.
  let ownerViewEpoch = 0;
  let practiceLocation = null;
  const practitioner = (() => {
    const stopped = false;
    const p = name => el("owner-practitioner-" + name);
    const uuid = v => typeof v === "string" && /^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/.test(v);
    const closed = (v, keys) => v !== null && typeof v === "object" && !Array.isArray(v)
      && Object.keys(v).length === keys.length && keys.every(k => Object.hasOwn(v,k));
    const decimal = (v, zero=false) => typeof v === "string"
      && (zero && v==="0" || /^[1-9][0-9]{0,18}$/.test(v))
      && (v.length<19 || v.length===19 && v<="9223372036854775807");
    const digest = v => typeof v==="string" && /^[0-9a-f]{64}$/.test(v);
    const scalarText = (v, minimum=0) => {
      if(typeof v!=="string")return false;
      let count=0;
      for(const char of v){const cp=char.codePointAt(0);if(cp>=0xD800 && cp<=0xDFFF)return false;count++;}
      return count>=minimum && count<=100;
    };
    // Exact W1 only for input advice. Send original text; review normalized
    // server-returned fields. No browser digest or authority is manufactured.
    const w1 = new Set(Array.from("\u0009\u000a\u000b\u000c\u000d\u001c\u001d\u001e\u001f\u0020\u0085\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000"));
    function advice(v, optional=false){
      const chars=Array.from(v);while(chars.length && w1.has(chars[0]))chars.shift();
      while(chars.length && w1.has(chars[chars.length-1]))chars.pop();
      const text=chars.join("");
      return optional && text==="" || scalarText(text,1) && !/[\u0000-\u001f\u007f]/.test(text);
    }
    const bodyShape = v => closed(v,["first_name","last_name","specialty","distinct_resource"])
      && scalarText(v.first_name,1) && scalarText(v.last_name,1)
      && (v.specialty===null || scalarText(v.specialty,1)) && typeof v.distinct_resource==="boolean";
    const scopeShape = v => closed(v,["practice_id"]) && uuid(v.practice_id);
    let scope=null, identity=null, known=false, epoch=0, pending=false;
    let draft=null, predecessor=null, unresolved=null, requestPrepare=null, refusedPredecessor=null;
    let expiresTimer=null;
    function status(message){p("status").textContent=message;}
    function clearReview(){
      draft=null;p("review").hidden=true;p("matches").replaceChildren();
      p("confirm").disabled=true;clearTimeout(expiresTimer);expiresTimer=null;
    }
    function invalidateOwner(dropRefusedPredecessor=false){
      if(dropRefusedPredecessor)refusedPredecessor=null;
      epoch++;scope=null;identity=null;predecessor=null;clearReview();
      // Preserve only original unresolved key/fingerprint and namespace for
      // recovery, not a confirmable draft or a token. Nothing enters storage.
      restore();
    }
    function edit(){
      epoch++;clearReview();
      status(unresolved ? "A previous result is uncertain. Check its creation reference before starting another creation."
        : "Details changed. Check details again before creating.");
      restore();
    }
    function restore(){
      const visible=!stopped && known;
      p("box").hidden=!visible;
      const available=visible && scope!==null && !busy && !accountBusy && !pending && !practiceLocation?.blocked();
      p("form").querySelectorAll("input,button").forEach(n=>n.disabled=!available || unresolved!==null);
      if(available && unresolved?.kind==="prepare" && requestPrepare
          && unresolved.practice===scope && unresolved.email===identity?.email)p("prepare").disabled=false;
      p("prepare").textContent=unresolved?.kind==="prepare" ? "Check prepared details" : "Check details";
      p("confirm").disabled=!available || unresolved!==null || !draft || !draft.can_confirm
        || !(Date.now()<Date.parse(draft.expires_at));
      p("refresh").disabled=!visible || busy || accountBusy || pending || practiceLocation?.blocked();
      p("reference").disabled=!available;
      p("recover").disabled=!available || !uuid(p("reference").value);
      if(pending || unresolved)p("box").open=true;
    }
    function presentOwner(value){
      clearReview();predecessor=null;epoch++;
      known=!stopped && Object.hasOwn(value,"practitioner_create_scope");
      scope=null;identity=null;
      const v=value.practitioner_create_scope;
      if(known && value.phase==="verified" && scopeShape(v) && typeof value.identity?.email==="string"
          && typeof value.identity.practice_name==="string" && value.identity.role==="PracticeOwner"){
        scope=v.practice_id;
        identity=Object.freeze({email:value.identity.email,practice_name:value.identity.practice_name});
        p("practice").textContent=identity.practice_name;
      }else{
        p("practice").textContent="";
        if(known && v!==null && v!==undefined && !scopeShape(v))throw Error("unavailable");
      }
      // A typed known-uncommitted result may retain only a nonconfirmable
      // predecessor. Restore it only after fresh owner state matches the exact
      // CSRF/scope/display-identity tag; the server still requires its private
      // native predecessor and fresh authority. No evidence is carried here.
      if(refusedPredecessor && scope===refusedPredecessor.practice && csrf===refusedPredecessor.csrf
          && identity?.email===refusedPredecessor.email && identity.practice_name===refusedPredecessor.practice_name){
        predecessor=refusedPredecessor.value;
      }
      refusedPredecessor=null;
      if(unresolved){
        p("reference").value=unresolved.key;
        p("recovery").open=true;
        status("The earlier creation still needs its result checked under the same owner account and practice.");
      }
      restore();
    }
    function snapshot(){
      if(stopped || scope===null || !identity || !csrf)throw Error("unavailable");
      const e=epoch, token=csrf, practice=scope, owner=identity;
      return {practice,owner,token,current:()=>epoch===e && csrf===token && scope===practice && identity===owner};
    }
    async function decode(response,current){
      if(!current() || !response.body || response.headers.get("Content-Type")?.split(";")[0]!=="application/json")throw Error("unavailable");
      const reader=response.body.getReader(), chunks=[];let size=0;
      while(true){
        const part=await reader.read();
        if(!current()){await reader.cancel();throw Error("stale");}
        if(part.done)break;
        size+=part.value.byteLength;
        if(size>32768){await reader.cancel();throw Error("unavailable");}
        chunks.push(part.value);
      }
      if(!current())throw Error("stale");
      const bytes=new Uint8Array(size);let offset=0;
      for(const part of chunks){bytes.set(part,offset);offset+=part.byteLength;}
      const value=JSON.parse(new TextDecoder("utf-8",{fatal:true}).decode(bytes));
      if(!current())throw Error("stale");
      return value;
    }
    function draftShape(d,key){
      if(!closed(d,["command_key","command_id","create_intent_id","draft_revision","body","body_digest",
          "matching_context_digest","expires_at","sample_count","sample_label","requires_distinct_resource_decision",
          "match_total","advisory_matches","can_confirm"]) || d.command_key!==key
          || !uuid(d.command_id) || !uuid(d.create_intent_id) || !decimal(d.draft_revision)
          || !bodyShape(d.body) || !digest(d.body_digest) || !digest(d.matching_context_digest)
          || !decimal(d.match_total,true) || !Number.isInteger(d.sample_count)
          || d.sample_count<0 || d.sample_count>10 || !Array.isArray(d.advisory_matches)
          || d.advisory_matches.length!==d.sample_count
          || d.sample_label!=="Showing "+d.sample_count+" of "+d.match_total
          || typeof d.requires_distinct_resource_decision!=="boolean" || typeof d.can_confirm!=="boolean"
          || typeof d.expires_at!=="string" || !/^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$/.test(d.expires_at)
          || !Number.isFinite(Date.parse(d.expires_at)))return false;
      const moreThanTen=d.match_total.length>2 || d.match_total.length===2 && d.match_total>"10";
      if(moreThanTen ? d.sample_count!==10 : String(d.sample_count)!==d.match_total)return false;
      if(d.requires_distinct_resource_decision!==(d.match_total!=="0" && !d.body.distinct_resource)
          || d.requires_distinct_resource_decision && d.can_confirm)return false;
      return d.advisory_matches.every(row=>closed(row,["first_name","last_name","specialty","is_active"])
        && scalarText(row.first_name) && scalarText(row.last_name)
        && (row.specialty===null || scalarText(row.specialty)) && (row.is_active===null || typeof row.is_active==="boolean"));
    }
    function receiptShape(r,key){
      return closed(r,["command_key","command_id","create_intent_id","draft_revision","body_digest","matching_context_digest","committed_at"])
        && r.command_key===key && uuid(r.command_id) && uuid(r.create_intent_id) && decimal(r.draft_revision)
        && digest(r.body_digest) && digest(r.matching_context_digest) && typeof r.committed_at==="string"
        && r.committed_at.length<=64 && /(?:Z|\+00:00)$/.test(r.committed_at) && Number.isFinite(Date.parse(r.committed_at));
    }
    function factsShape(f){
      return closed(f,["first_name","last_name","specialty","is_active","aggregate_version"])
        && scalarText(f.first_name) && scalarText(f.last_name) && (f.specialty===null || scalarText(f.specialty))
        && (f.is_active===null || typeof f.is_active==="boolean")
        && typeof f.aggregate_version==="string" && /^-?(?:0|[1-9][0-9]{0,18})$/.test(f.aggregate_version);
    }
    function renderDraft(d){
      draft=Object.freeze(d);
      predecessor=Object.freeze({command_id:d.command_id,create_intent_id:d.create_intent_id,draft_revision:d.draft_revision});
      p("summary").textContent=identity.practice_name+" · "+d.body.first_name+" "+d.body.last_name
        +(d.body.specialty===null ? "" : " · "+d.body.specialty);
      p("count").textContent=d.sample_label+". Name matches may include inactive resources; the sample may omit further matches.";
      p("matches").replaceChildren();
      for(const row of d.advisory_matches){
        const li=document.createElement("li");
        li.textContent=row.first_name+" "+row.last_name+(row.specialty===null ? "" : " · "+row.specialty)
          +" · "+(row.is_active===null ? "Active status unavailable" : row.is_active ? "Active" : "Inactive");
        p("matches").append(li);
      }
      p("distinct-label").hidden=d.match_total==="0";
      p("expiry").textContent="Review expires at "+d.expires_at+" (UTC).";
      p("review").hidden=false;p("box").open=true;
      status(d.requires_distinct_resource_decision
        ? "Review the name matches. To add a separate scheduling resource, acknowledge them and check details again."
        : "Check the exact practice and details, then choose Create practitioner.");
      clearTimeout(expiresTimer);
      expiresTimer=setTimeout(()=>{if(draft===d || draft?.command_key===d.command_key)restore();},
        Math.max(0,Math.min(2147483647,Date.parse(d.expires_at)-Date.now()+1)));
      p("review-title").focus();
    }
    function committed(value,key){
      if(!receiptShape(value.receipt,key) || !Object.hasOwn(value,"readback"))throw Error("unavailable");
      const rb=value.readback;
      if(rb!==null && (!closed(rb,["status","expected","current"]) || !factsShape(rb.expected)
          || !["matches_created","diverged","missing"].includes(rb.status)
          || (rb.status==="missing" ? rb.current!==null : !factsShape(rb.current))))throw Error("unavailable");
      unresolved=null;requestPrepare=null;predecessor=null;clearReview();
      p("reference").value=key;p("recovery").open=true;
      const copy=rb===null ? "Created. Check creation result to read its current details."
        : rb.status==="matches_created" ? "Created, and the current details match the saved creation."
        : rb.status==="diverged" ? "Created. Its current details have changed; this is still a completed creation."
        : "Created. The resource is now missing from current truth; do not create a replacement to resolve this result.";
      status(copy);
      if(rb){
        const facts=rb.current || rb.expected;
        p("summary").textContent=identity.practice_name+" · "+facts.first_name+" "+facts.last_name
          +(facts.specialty===null ? "" : " · "+facts.specialty);
        p("review").hidden=false;
      }
    }
    async function request(action,body,context){
      const r=await fetch("/demo/stage1/owner/practitioners/"+action,{
        method:"POST",credentials:"same-origin",cache:"no-store",redirect:"error",
        headers:{"Content-Type":"application/json","X-CSRF-Token":context.token},body:JSON.stringify(body)});
      if(!context.current())throw Error("stale");
      const value=await decode(r,context.current);
      if(!context.current())throw Error("stale");
      if(!r.ok){
        const codes=["PRACTITIONER_CREATE_INVALID","PRACTITIONER_COMMAND_KEY_INVALID","PRACTITIONER_CONFIRMATION_INVALID",
          "PRACTITIONER_AUTHENTICATION_REQUIRED","PRACTITIONER_CREATE_DENIED","PRACTITIONER_CREATE_CONFLICT"];
        if(action!=="receipt" && closed(value,["state","code","detail"]) && value.state==="refused" && codes.includes(value.code)){
          const retained=predecessor;
          unresolved=null;requestPrepare=null;invalidateOwner(true);
          if(retained)refusedPredecessor=Object.freeze({value:retained,practice:context.practice,
            csrf:context.token,email:context.owner.email,practice_name:context.owner.practice_name});
          ownerPresentation.attention("Creation was refused. Check the owner account, then explicitly review fresh details.");
          return null;
        }
        throw Error("uncertain");
      }
      if(!scopeShape(value.practitioner_create_scope) || value.practitioner_create_scope.practice_id!==context.practice)throw Error("unavailable");
      return value;
    }
    async function perform(action,body){
      if(busy || accountBusy || pending || practiceLocation?.blocked())return;
      const context=snapshot();
      pending=true;restore();practiceLocation?.restore();ownerPresentation.busy(true);
      try{
        const value=await request(action,body,context);
        if(value===null)return;
        if(!context.current())throw Error("stale");
        if(action==="prepare" && value.state==="prepared"){
          if(!closed(value,["state","draft","practitioner_create_scope"]) || !draftShape(value.draft,body.command_key))throw Error("unavailable");
          unresolved=null;requestPrepare=null;renderDraft(value.draft);
        }else if(value.state==="committed" && closed(value,["state","receipt","readback","practitioner_create_scope"])){
          committed(value,body.command_key);
        }else throw Error("unavailable");
      }catch(_){
        const wasCurrent=context.current();
        clearReview();
        // Even an error before a reply may follow a committed dispatch. Do not
        // allocate a replacement key, resend a write, or erase the original key.
        if(wasCurrent){
          invalidateOwner(true); // An ambiguous outcome retains only its recovery key.
          status("The result is uncertain. Check the owner account, then check this same creation reference; do not submit another creation.");
          p("reference").value=body.command_key;p("recovery").open=true;
        }
      }finally{
        pending=false;ownerPresentation.busy(false);restore();practiceLocation?.restore();
      }
    }
    p("form").addEventListener("submit",async event=>{
      event.preventDefault();
      if(stopped || busy || accountBusy || pending || practiceLocation?.blocked() || scope===null)return;
      if(unresolved){
        if(unresolved.kind==="prepare" && requestPrepare && unresolved.practice===scope && unresolved.email===identity?.email)
          await perform("prepare",requestPrepare); // Explicit identical-key prepare check only; never confirm retry.
        return;
      }
      const body={first_name:p("first").value,last_name:p("last").value,
        specialty:p("specialty").value,distinct_resource:p("distinct").checked};
      if(!advice(body.first_name) || !advice(body.last_name) || !advice(body.specialty,true)){
        status("Use names and an optional specialty of at most 100 Unicode characters, without control characters.");return;
      }
      // Explicit form submit prepares only. Each edited revision gets one key;
      // exact predecessor decimal text is echoed unchanged, never Number().
      const key=crypto.randomUUID(), prior=predecessor;
      requestPrepare={command_key:key,body,new_intent:prior===null,
        create_intent_id:prior?.create_intent_id ?? null,supersedes_command_id:prior?.command_id ?? null,
        supersedes_revision:prior?.draft_revision ?? null};
      const context=snapshot();
      unresolved={key,practice:context.practice,email:context.owner.email,kind:"prepare"};
      clearReview();
      await perform("prepare",requestPrepare);
    });
    p("confirm").addEventListener("click",async()=>{
      if(stopped || busy || accountBusy || pending || practiceLocation?.blocked() || !draft || p("confirm").disabled || unresolved)return;
      const d=draft, context=snapshot();
      const body={command_key:d.command_key,command_id:d.command_id,create_intent_id:d.create_intent_id,
        draft_revision:d.draft_revision,body_digest:d.body_digest,matching_context_digest:d.matching_context_digest,confirmed:true};
      unresolved={key:d.command_key,practice:context.practice,email:context.owner.email,kind:"confirm"};
      clearReview(); // One explicit click consumes the local confirmable view.
      await perform("confirm",body);
    });
    p("recovery-form").addEventListener("submit",async event=>{
      event.preventDefault();
      if(stopped || busy || accountBusy || pending || practiceLocation?.blocked() || scope===null || !uuid(p("reference").value))return;
      const key=p("reference").value,context=snapshot();
      if(unresolved && (unresolved.key!==key || unresolved.practice!==context.practice || unresolved.email!==context.owner.email)){
        status("Use the original creation reference and the same owner account and practice.");return;
      }
      unresolved=unresolved || {key,practice:context.practice,email:context.owner.email,kind:"receipt"};
      clearReview();await perform("receipt",{command_key:key});
    });
    p("refresh").addEventListener("click",async()=>{if(!busy && !accountBusy && !pending && !practiceLocation?.blocked())try{await state();}catch(_){invalidateOwner();}});
    p("reference").addEventListener("input",restore);
    for(const id of ["first","last","specialty","distinct"])p(id).addEventListener("input",edit);
    p("box").addEventListener("toggle",()=>{if(!p("box").open && (pending || unresolved))p("box").open=true;});
    restore();
    return {invalidateOwner,presentOwner,restore,decode,blocked:()=>pending};
  })();
  practiceLocation = (() => {
    const p = name => el("owner-location-" + name);
    const uuid = v => typeof v === "string" && /^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/.test(v);
    const closed = (v, keys) => v !== null && typeof v === "object" && !Array.isArray(v)
      && Object.keys(v).length === keys.length && keys.every(k => Object.hasOwn(v,k));
    const decimal = v => typeof v === "string" && /^[1-9][0-9]{0,18}$/.test(v)
      && (v.length<19 || v.length===19 && v<="9223372036854775807");
    const digest = v => typeof v === "string" && /^[0-9a-f]{64}$/.test(v);
    const scalarText = (v, minimum=0) => {
      if(typeof v!=="string")return false;
      let count=0;
      for(const char of v){const cp=char.codePointAt(0);if(cp>=0xD800 && cp<=0xDFFF)return false;count++;}
      return count>=minimum && count<=255;
    };
    const w1 = new Set(Array.from("\u0009\u000a\u000b\u000c\u000d\u001c\u001d\u001e\u001f\u0020\u0085\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000"));
    function advice(value){
      if(typeof value!=="string")return false;
      const chars=Array.from(value);while(chars.length && w1.has(chars[0]))chars.shift();
      while(chars.length && w1.has(chars[chars.length-1]))chars.pop();
      const trimmed=chars.join("");
      return scalarText(trimmed,1) && !/[\u0000-\u001f\u007f]/.test(trimmed);
    }
    const nameShape = v => scalarText(v,1) && advice(v)
      && !w1.has(Array.from(v)[0]) && !w1.has(Array.from(v).at(-1));
    const bodyShape = v => closed(v,["name"]) && nameShape(v.name);
    const scopeShape = v => closed(v,["practice_id"]) && uuid(v.practice_id);
    const instant = v => typeof v==="string"
      && /^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$/.test(v)
      && Number.isFinite(Date.parse(v));
    let scope=null, identity=null, known=false, epoch=0, pending=false;
    let draft=null, predecessor=null, unresolved=null, requestPrepare=null, refusedPredecessor=null;
    let expiresTimer=null;
    function status(message){p("status").textContent=message;}
    function clearReview(){
      draft=null;p("review").hidden=true;p("confirm").disabled=true;
      clearTimeout(expiresTimer);expiresTimer=null;
    }
    function invalidateOwner(dropRefusedPredecessor=false){
      if(dropRefusedPredecessor)refusedPredecessor=null;
      epoch++;scope=null;identity=null;predecessor=null;clearReview();
      p("created").hidden=true;p("created").textContent="";
      // Preserve only the unresolved key and original namespace, never evidence.
      restore();
    }
    function edit(){
      epoch++;clearReview();p("created").hidden=true;
      status(unresolved ? "A previous result is uncertain. Check its creation reference before starting another creation."
        : "Details changed. Check details again before creating.");
      restore();
    }
    function restore(){
      const visible=known;
      p("box").hidden=!visible;
      const available=visible && scope!==null && !busy && !accountBusy && !pending && !practitioner.blocked();
      p("form").querySelectorAll("input,button").forEach(n=>n.disabled=!available || unresolved!==null);
      if(available && unresolved?.kind==="prepare" && requestPrepare
          && unresolved.practice===scope && unresolved.email===identity?.email)p("prepare").disabled=false;
      p("prepare").textContent=unresolved?.kind==="prepare" ? "Check prepared details" : "Check details";
      p("confirm").disabled=!available || unresolved!==null || !draft || !draft.can_confirm
        || !(Date.now()<Date.parse(draft.expires_at));
      p("refresh").disabled=!visible || busy || accountBusy || pending || practitioner.blocked();
      p("reference").disabled=!available;
      p("recover").disabled=!available || !uuid(p("reference").value);
      if(pending || unresolved)p("box").open=true;
    }
    function presentOwner(value){
      clearReview();predecessor=null;epoch++;
      p("created").hidden=true;p("created").textContent="";
      known=Object.hasOwn(value,"practice_location_create_scope");
      scope=null;identity=null;
      const projected=value.practice_location_create_scope;
      if(known && value.phase==="verified" && scopeShape(projected) && typeof value.identity?.email==="string"
          && typeof value.identity.practice_name==="string" && value.identity.role==="PracticeOwner"){
        scope=projected.practice_id;
        identity=Object.freeze({email:value.identity.email,practice_name:value.identity.practice_name});
        p("practice").textContent=identity.practice_name;
      }else{
        p("practice").textContent="";
        if(known && projected!==null && projected!==undefined && !scopeShape(projected))throw Error("unavailable");
      }
      if(refusedPredecessor && scope===refusedPredecessor.practice && csrf===refusedPredecessor.csrf
          && identity?.email===refusedPredecessor.email && identity.practice_name===refusedPredecessor.practice_name){
        predecessor=refusedPredecessor.value;
      }
      refusedPredecessor=null;
      if(unresolved){
        p("reference").value=unresolved.key;p("recovery").open=true;
        status("The earlier creation needs its result checked under the same owner account and practice.");
      }
      restore();
    }
    function snapshot(){
      if(scope===null || !identity || !csrf)throw Error("unavailable");
      const e=epoch, token=csrf, practice=scope, owner=identity;
      return {practice,owner,token,current:()=>epoch===e && csrf===token && scope===practice && identity===owner};
    }
    async function decode(response,current){
      if(!current() || !response.body || response.headers.get("Content-Type")?.split(";")[0]!=="application/json")throw Error("unavailable");
      const reader=response.body.getReader(),chunks=[];let size=0;
      while(true){
        const part=await reader.read();
        if(!current()){await reader.cancel();throw Error("stale");}
        if(part.done)break;
        size+=part.value.byteLength;
        if(size>32768){await reader.cancel();throw Error("unavailable");}
        chunks.push(part.value);
      }
      if(!current())throw Error("stale");
      const bytes=new Uint8Array(size);let offset=0;
      for(const part of chunks){bytes.set(part,offset);offset+=part.byteLength;}
      const value=JSON.parse(new TextDecoder("utf-8",{fatal:true}).decode(bytes));
      if(!current())throw Error("stale");
      return value;
    }
    function draftShape(value,key){
      return closed(value,["command_key","command_id","create_intent_id","body","body_digest","expires_at","draft_revision","can_confirm"])
        && value.command_key===key && uuid(value.command_id) && uuid(value.create_intent_id)
        && decimal(value.draft_revision) && bodyShape(value.body) && digest(value.body_digest)
        && instant(value.expires_at) && typeof value.can_confirm==="boolean";
    }
    function receiptShape(value,key,practice){
      return closed(value,["command_key","command_id","create_intent_id","draft_revision","practice_id","location_id","body_digest","committed_at"])
        && value.command_key===key && uuid(value.command_id) && uuid(value.create_intent_id)
        && decimal(value.draft_revision) && value.practice_id===practice && uuid(value.practice_id)
        && uuid(value.location_id) && digest(value.body_digest) && instant(value.committed_at);
    }
    function readbackShape(value,receipt){
      if(!closed(value,["status","expected","current"]) || !["matches_created","diverged","missing"].includes(value.status)
          || !closed(value.expected,["name","is_active"]) || !nameShape(value.expected.name)
          || value.expected.is_active!==true)return false;
      if(value.status==="missing")return value.current===null;
      const current=value.current;
      if(!closed(current,["id","practice_id","name","is_active"]) || current.id!==receipt.location_id
          || current.practice_id!==receipt.practice_id || !scalarText(current.name)
          || !(current.is_active===null || typeof current.is_active==="boolean"))return false;
      const matches=current.name===value.expected.name && current.is_active===true;
      return value.status==="matches_created" ? matches : !matches;
    }
    function renderDraft(value){
      draft=Object.freeze(value);
      predecessor=Object.freeze({command_id:value.command_id,create_intent_id:value.create_intent_id,draft_revision:value.draft_revision});
      p("summary").textContent=identity.practice_name+" · "+value.body.name;
      p("expiry").textContent="Review expires at "+value.expires_at+" (UTC).";
      p("review").hidden=false;p("box").open=true;
      p("reference").value=value.command_key;p("recovery").open=true;
      status("Check the exact practice and location name, then choose Create location.");
      clearTimeout(expiresTimer);
      expiresTimer=setTimeout(()=>{if(draft?.command_key===value.command_key)restore();},
        Math.max(0,Math.min(2147483647,Date.parse(value.expires_at)-Date.now()+1)));
      p("review-title").focus();
    }
    function committed(value,key,context){
      if(!receiptShape(value.receipt,key,context.practice) || !Object.hasOwn(value,"readback")
          || value.readback!==null && !readbackShape(value.readback,value.receipt))throw Error("unavailable");
      unresolved=null;requestPrepare=null;predecessor=null;clearReview();
      p("reference").value=key;p("recovery").open=true;
      p("created").textContent="Location reference: "+value.receipt.location_id+" · Practice: "+value.receipt.practice_id;
      p("created").hidden=false;
      const current=value.readback;
      status(current===null ? "Location created. Check creation result to read its current details."
        : current.status==="matches_created" ? "Location created, and the current details match the saved creation."
        : current.status==="diverged" ? "Location created. Its current details have changed; the original creation is complete."
        : "Location created. It is now missing from current truth; do not create a replacement to resolve this result.");
      if(current){
        p("summary").textContent=identity.practice_name+" · "+(current.current || current.expected).name;
        p("expiry").textContent="";p("review").hidden=false;
      }
    }
    async function request(action,body,context){
      const response=await fetch("/demo/stage1/owner/locations/"+action,{
        method:"POST",credentials:"same-origin",cache:"no-store",redirect:"error",
        headers:{"Content-Type":"application/json","X-CSRF-Token":context.token},body:JSON.stringify(body)});
      if(!context.current())throw Error("stale");
      const value=await decode(response,context.current);
      if(!context.current())throw Error("stale");
      if(!response.ok){
        const codes=["PRACTICE_LOCATION_CREATE_INVALID","PRACTICE_LOCATION_COMMAND_KEY_INVALID","PRACTICE_LOCATION_CONFIRMATION_INVALID",
          "PRACTICE_LOCATION_AUTHENTICATION_REQUIRED","PRACTICE_LOCATION_CREATE_DENIED","PRACTICE_LOCATION_CREATE_CONFLICT"];
        if(action!=="receipt" && closed(value,["state","code","detail"]) && value.state==="refused" && codes.includes(value.code)){
          const retained=predecessor;
          unresolved=null;requestPrepare=null;invalidateOwner(true);
          if(retained)refusedPredecessor=Object.freeze({value:retained,practice:context.practice,
            csrf:context.token,email:context.owner.email,practice_name:context.owner.practice_name});
          ownerPresentation.attention("Location creation was refused. Check the owner account, then explicitly review fresh details.");
          return null;
        }
        // Any denied, malformed or uncertain response leaves the original key
        // unresolved; there is no automatic confirm or replacement-key retry.
        throw Error("uncertain");
      }
      if(!scopeShape(value.practice_location_create_scope) || value.practice_location_create_scope.practice_id!==context.practice)throw Error("unavailable");
      return value;
    }
    async function perform(action,body){
      if(busy || accountBusy || pending || practitioner.blocked())return;
      const context=snapshot();
      pending=true;accountBusyState(true);practitioner.restore();restore();ownerPresentation.busy(true);
      try{
        const value=await request(action,body,context);
        if(value===null)return;
        if(!context.current())throw Error("stale");
        if(action==="prepare" && value.state==="prepared"){
          if(!closed(value,["state","draft","practice_location_create_scope"]) || !draftShape(value.draft,body.command_key))throw Error("unavailable");
          unresolved=null;requestPrepare=null;renderDraft(value.draft);
        }else if(value.state==="committed" && closed(value,["state","receipt","readback","practice_location_create_scope"])){
          committed(value,body.command_key,context);
        }else throw Error("unavailable");
      }catch(_){
        const wasCurrent=context.current();clearReview();
        if(wasCurrent){
          invalidateOwner(true);
          status("The result is uncertain. Check the owner account, then check this same creation reference; do not submit another creation.");
          p("reference").value=body.command_key;p("recovery").open=true;
        }
      }finally{
        pending=false;ownerPresentation.busy(false);accountBusyState(false);practitioner.restore();restore();
      }
    }
    p("form").addEventListener("submit",async event=>{
      event.preventDefault();
      if(busy || accountBusy || pending || practitioner.blocked() || scope===null)return;
      if(unresolved){
        if(unresolved.kind==="prepare" && requestPrepare && unresolved.practice===scope && unresolved.email===identity?.email)
          await perform("prepare",requestPrepare); // Explicit same-key prepared-details check only.
        return;
      }
      const body={name:p("name").value};
      if(!advice(body.name)){status("Use a location name of up to 255 characters, without control characters.");return;}
      const key=crypto.randomUUID(),prior=predecessor;
      requestPrepare={command_key:key,body,new_intent:prior===null,
        create_intent_id:prior?.create_intent_id ?? null,supersedes_command_id:prior?.command_id ?? null,
        supersedes_revision:prior?.draft_revision ?? null};
      const context=snapshot();
      unresolved={key,practice:context.practice,email:context.owner.email,kind:"prepare"};
      p("created").hidden=true;clearReview();await perform("prepare",requestPrepare);
    });
    p("confirm").addEventListener("click",async()=>{
      if(busy || accountBusy || pending || practitioner.blocked() || !draft || p("confirm").disabled || unresolved)return;
      const value=draft,context=snapshot();
      const body={command_key:value.command_key,command_id:value.command_id,create_intent_id:value.create_intent_id,
        draft_revision:value.draft_revision,body_digest:value.body_digest,confirmed:true};
      unresolved={key:value.command_key,practice:context.practice,email:context.owner.email,kind:"confirm"};
      clearReview();await perform("confirm",body); // Explicit click consumes the only confirmable view.
    });
    p("recovery-form").addEventListener("submit",async event=>{
      event.preventDefault();
      if(busy || accountBusy || pending || practitioner.blocked() || scope===null || !uuid(p("reference").value))return;
      const key=p("reference").value,context=snapshot();
      if(unresolved && (unresolved.key!==key || unresolved.practice!==context.practice || unresolved.email!==context.owner.email)){
        status("Use the original creation reference and the same owner account and practice.");return;
      }
      unresolved=unresolved || {key,practice:context.practice,email:context.owner.email,kind:"receipt"};
      clearReview();await perform("receipt",{command_key:key});
    });
    p("refresh").addEventListener("click",async()=>{if(!busy && !accountBusy && !pending && !practitioner.blocked())try{await state();}catch(_){invalidateOwner();}});
    p("reference").addEventListener("input",restore);
    p("name").addEventListener("input",edit);
    p("box").addEventListener("toggle",()=>{if(!p("box").open && (pending || unresolved))p("box").open=true;});
    restore();
    return {invalidateOwner,presentOwner,restore,blocked:()=>pending};
  })();
  restorePractitionerAfterAccountBusy = () => {practitioner.restore();practiceLocation.restore();};
  function showOwner(value) {
    if (!value || value.enabled !== true || typeof value.csrf !== "string" ||
        !["credentials", "pending", "inspect", "verified"].includes(value.phase)) throw new Error("unavailable");
    const invitation=value.invitation;
    el("owner-invitation").hidden=!(Object.hasOwn(value,"invitation") && value.phase==="verified");
    el("owner-invitation-form").hidden=invitation?.can_issue!==true;
    el("owner-invitation-confirm").checked=false;
    if(invitation)el("owner-invitation-review").textContent=invitation.issued
      ? "Invitation sent. The receptionist must review and accept it, then choose this practice."
      : `${invitation.practice_name} · Receptionist · Existing synthetic receptionist. Check setup after the receptionist signs in.`;
    csrf = value.csrf;
    el("owner-onboarding").hidden = false;
    el("owner-credentials").hidden = value.phase !== "credentials";
    el("owner-create").hidden = value.phase !== "pending";
    el("owner-inspect").hidden = value.phase !== "inspect";
    el("owner-identity").hidden = value.phase !== "verified";
    el("owner-status").textContent = ({credentials:"Create an account or sign in if registration may already have completed.",
      pending:"Confirm your first practice before creating it.", inspect:"Creation may have completed. Inspect the current account; do not submit another creation.",
      verified:"Owner account and practice verified. Administration handoff is ready."})[value.phase];
    if (value.phase === "verified") {
      const i = value.identity;
      if (!i || typeof i.email !== "string" || typeof i.practice_name !== "string" || i.role !== "PracticeOwner") throw new Error("unavailable");
      el("owner-identity").textContent = `${i.email} · ${i.practice_name} · ${i.role}`;
    }
    practitioner.presentOwner(value);
    practiceLocation.presentOwner(value);
    ownerPresentation.owner(value);
  }
  async function state() {
    const epoch=++ownerViewEpoch, token=csrf;
    practitioner.invalidateOwner();practiceLocation.invalidateOwner();
    const current=()=>ownerViewEpoch===epoch && csrf===token;
    try{
      const r = await fetch("/demo/stage1/owner/state", {credentials:"same-origin", cache:"no-store", redirect:"error"});
      if (!current() || !r.ok) throw new Error("unavailable");
      const v = await practitioner.decode(r,current);
      if(!current())throw new Error("stale");
      if (v.enabled === false) return;
      showOwner(v);
    }catch(error){if(current()){practitioner.invalidateOwner();practiceLocation.invalidateOwner();}throw error;}
  }
  async function post(action, body) {
    if (busy || practitioner.blocked() || practiceLocation.blocked()) return;
    const epoch=++ownerViewEpoch, token=csrf;
    practitioner.invalidateOwner(true);practiceLocation.invalidateOwner(true);
    const current=()=>ownerViewEpoch===epoch && csrf===token;
    busy = true;
    ownerPresentation.busy(true);
    el("owner-onboarding").querySelectorAll("button,input").forEach(n => n.disabled = true);
    try {
      const r = await fetch(`/demo/stage1/owner/${action}`, {method:"POST", credentials:"same-origin", cache:"no-store", redirect:"error",
        headers:{"Content-Type":"application/json", "X-CSRF-Token":token || ""}, body:JSON.stringify(body)});
      if (!current() || !r.ok) throw new Error("unavailable");
      const value=await practitioner.decode(r,current);
      if(!current())throw new Error("stale");
      showOwner(value);
      ownerPresentation.confirmed();
    } catch (_) {
      practitioner.invalidateOwner();practiceLocation.invalidateOwner();
      ownerPresentation.attention("The action could not be confirmed. Sign in or inspect the current account before continuing.",true);
      try { await state(); } catch (_) { /* Keep the uncertain action visible. */ }
    } finally {
      if (Object.hasOwn(body,"password")) body.password = "";
      el("owner-password").value = "";
      el("owner-onboarding").querySelectorAll("button,input").forEach(n => n.disabled = false);
      busy = false;
      practitioner.restore();practiceLocation.restore(); // Derive both CREATE states after the generic finalizer.
      ownerPresentation.busy(false);
    }
  }
  el("owner-credentials").addEventListener("submit", async e => {
    e.preventDefault();
    const action = e.submitter?.value;
    if (!["register", "signin"].includes(action)) return;
    const body = {email:el("owner-email").value, password:el("owner-password").value};
    el("owner-password").value = "";
    await post(action, body);
  });
  el("owner-create").addEventListener("submit", async e => {
    e.preventDefault();
    if (el("owner-confirm").checked) await post("create", {name:el("owner-name").value, confirmed:true});
  });
  el("owner-inspect").addEventListener("click", () => post("inspect", {}));
  el("owner-invitation-refresh").addEventListener("click",async()=>{if(!busy)try{await state();}catch(_){ownerPresentation.attention("Invitation setup is not available.");}});
  el("owner-invitation-form").addEventListener("submit",async e=>{e.preventDefault();if(el("owner-invitation-confirm").checked)await post("invite",{confirmed:true});});
  try { await state(); } catch (_) { /* Default-off and unavailable stay hidden. */ }
})();

// Patient projections are separate from the fixed appointment/Bureau target.
function initPatientRecords() {
  const panel = document.getElementById("patient-records");
  const el = id => document.getElementById("patient-record-" + id);
  let csrf = null, generation = 0, busy = false, available = false, inAppointments = false;
  let draft = null, predecessor = null, pendingPrepare = null, pendingKey = null, uncertain = false, selected = null;
  let prepareAttempts = 0;
  let bookingMeta = null, bookingEpoch = 0, bookingIdentity = null;
  let selectedBookingEnabled = false, bookingView = null, bookingSent = false, bookingUncertain = false;
  function clearBooking() {
    bookingView = null;
    el('booking-result').replaceChildren(); el('booking-progress').textContent = bookingSent
      ? 'The earlier booking result still needs checking. Do not send it again.' : '';
  }
  function bookingControls() {
    el('booking-context').textContent = bookingMeta
      ? 'Avery Shaw · ' + bookingMeta.date + ' · 14:00–17:00 (last start 16:30) · 30 minutes. No appointment type or location selected.'
      : '';
    el('booking-box').hidden = !(selectedBookingEnabled && bookingMeta && selected
      && selected.practice_id === bookingMeta.practice_id);
    el('booking-words').disabled = busy || bookingSent;
    el('booking-manual').disabled = el('booking-suggest').disabled = busy || bookingSent;
    el('booking-refresh').hidden = !bookingView || bookingSent;
    el('booking-readback').hidden = !bookingView?.receipt || bookingView.state === 'confirmed';
    el('booking-refresh').disabled = el('booking-readback').disabled = busy;
  }
  function renderBooking(view) {
    if (!view || typeof view !== 'object' || !uuid(view.patient?.id) || view.patient.id !== selected?.id
      || view.patient.practice_id !== selected?.practice_id || !uuid(view.practitioner?.id)
      || view.date !== bookingMeta?.date || view.duration_minutes !== bookingMeta?.duration_minutes
      || !safeText(view.timezone,128) || !Array.isArray(view.choices) || view.choices.length > 8
      || !['awaiting_reply','choice','clarification','review','expired','uncertain','confirmed'].includes(view.state))
      throw new Error('BOOKING_REPLY_UNAVAILABLE');
    const priorBookingState=bookingView?.state;
    bookingView = view;
    const result = el('booking-result'); result.replaceChildren();
    const line = text => { const p=document.createElement('p'); p.textContent=text; result.append(p); };
    line(label(view.patient) + ' · ' + view.practitioner.displayName + ' · ' + view.date
      + ' · ' + view.duration_minutes + ' minutes · ' + view.timezone);
    const expired = !Number.isFinite(Date.parse(view.expires_at)) || Date.now() >= Date.parse(view.expires_at);
    if (view.state === 'choice' && !expired && !bookingSent) {
      for (const choice of view.choices) {
        if (!safeText(choice.slot_ref,100) || !/^(?:[01][0-9]|2[0-3]):[0-5][0-9]$/.test(choice.start_time_local))
          throw new Error('BOOKING_REPLY_UNAVAILABLE');
        const button=document.createElement('button'); button.type='button'; button.className='quiet';
        button.textContent=choice.start_time_local; button.disabled=busy;
        button.addEventListener('click',()=>bookingAction('select',{slot_ref:choice.slot_ref})); result.append(button);
      }
    }
    if (view.state === 'review' && !expired && !bookingSent) {
      const review=view.review, command=review?.command;
      if (!review || !safeText(review.proposal_ref,100) || review.requires_confirmation !== true
        || !Array.isArray(review.warnings) || review.warnings.length || !command
        || command.patient_id !== selected.id || command.practitioner_id !== view.practitioner.id
        || command.appointment_date !== view.date || command.duration_minutes !== view.duration_minutes)
        throw new Error('BOOKING_REVIEW_UNAVAILABLE');
      line('Review: ' + command.appointment_date + ' at ' + command.start_time_local.slice(0,5)
        + ', ' + command.duration_minutes + ' minutes. ' + review.summary);
      const confirm=document.createElement('button'); confirm.type='button'; confirm.textContent='Confirm this appointment';
      confirm.disabled=busy; confirm.addEventListener('click',()=>bookingAction('confirm',{proposal_ref:review.proposal_ref}));
      result.append(confirm);
    }
    if (view.state === 'confirmed' && view.receipt && view.readback) {
      bookingUncertain=false;
      line('Appointment saved and checked: ' + view.receipt.appointment_date + ' at '
        + view.receipt.start_time_local.slice(0,5) + '.');
    }
    el('booking-progress').textContent = view.state === 'confirmed' ? 'Saved appointment verified.'
      : bookingSent || view.state === 'uncertain' ? 'The result is unresolved. Do not send the booking again.'
      : expired || view.state === 'expired' ? 'This request expired. No confirmation was sent.'
      : view.state === 'awaiting_reply' ? 'Request captured. A suggestion is not available yet; you can choose a time yourself.'
      : view.state === 'clarification' ? 'No eligible time is offered for this request. Make a fresh request or check the selected context; no appointment has been confirmed.'
      : view.state === 'choice' ? 'Choose the time you mean.' : 'Check the details, then confirm once.';
    bookingControls();
    if(view.state==='confirmed' && view.receipt && view.readback && priorBookingState!=='confirmed')
      document.dispatchEvent(new CustomEvent('raisa:selected-staff-facts'));
  }
  async function bookingAction(action, body) {
    if (busy || !csrf || !selectedBookingEnabled || !selected || !bookingMeta
      || bookingSent && !['readback'].includes(action)) return;
    const epoch=generation, person={...selected}, meta={...bookingMeta}, token=csrf;
    const current=()=>epoch===generation && token===csrf && selected?.id===person.id
      && selected?.practice_id===person.practice_id && JSON.stringify(bookingMeta)===JSON.stringify(meta);
    if (action==='confirm') { bookingSent=true; bookingUncertain=true; }
    busy=true; controls(); bookingControls();
    try {
      const response=await fetch('/demo/stage1/selected-staff-booking/'+action,{
        method:'POST',credentials:'same-origin',cache:'no-store',redirect:'error',
        headers:{'Content-Type':'application/json','X-CSRF-Token':token},body:JSON.stringify(body)});
      if (!current()) return;
      if (!response.body) throw new Error('BOOKING_REPLY_UNAVAILABLE');
      const reader=response.body.getReader(), chunks=[]; let size=0;
      while (true) {
        const part=await reader.read(); if (!current()) { await reader.cancel(); return; }
        if(part.done)break; size+=part.value.byteLength;
        if(size>16384){await reader.cancel();throw new Error('BOOKING_REPLY_UNAVAILABLE');} chunks.push(part.value);
      }
      const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.byteLength;}
      if (!response.ok) throw new Error('BOOKING_UNAVAILABLE');
      const view=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
      if (current()) renderBooking(view);
    } catch (_) {
      if (current()) {
        el('booking-result').replaceChildren();
        el('booking-progress').textContent = bookingSent
          ? 'The booking result is unresolved. Do not resend. Check your sign-in; a new confirmation is not permitted.'
          : 'Booking could not be prepared. Check your sign-in and selected patient.';
      }
    } finally { busy=false; controls(); bookingControls(); }
  }
  function captureBooking(manual) {
    if(!selected || !bookingMeta)return;
    bookingAction('capture',{patient_id:selected.id,date:bookingMeta.date,duration_minutes:bookingMeta.duration_minutes,
      instruction:el('booking-words').value.trim() || 'Book this selected patient on the shown date with the shown practitioner.',manual});
  }
  el('booking-manual').addEventListener('click',()=>captureBooking(true));
  el('booking-suggest').addEventListener('click',()=>captureBooking(false));
  el('booking-refresh').addEventListener('click',()=>bookingAction('status',{}));
  el('booking-readback').addEventListener('click',()=>bookingAction('readback',{}));

  const uuid = value => typeof value === "string" && /^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/.test(value);
  const say = value => { el("status").textContent = value; };
  function controls() {
    panel.querySelectorAll("button,input").forEach(node => { node.disabled = busy; });
    bookingControls();
    el("times-box").hidden = !(bookingMeta && selected && selected.practice_id === bookingMeta.practice_id);
    el("times").disabled = busy || uncertain || !bookingMeta || !selected || selected.practice_id !== bookingMeta.practice_id;
    el("prepare").disabled = busy || uncertain;
    el("prepare").textContent = pendingPrepare ? "Check prepared registration" : "Check registration";
    el("confirm").disabled = busy || uncertain || !draft?.can_confirm;
    el("recover").hidden = !uncertain;
    el("recover").disabled = busy || !csrf;
    el("registration").querySelectorAll("input").forEach(node => { node.disabled = busy || uncertain || !!pendingPrepare; });
  }
  function clearProjection(keepRecovery = false) {
    clearTimes(); clearBooking();
    const retainedKey = keepRecovery && uncertain && uuid(pendingKey) ? pendingKey : null;
    generation += 1;
    draft = predecessor = pendingPrepare = pendingKey = selected = null; uncertain = false; prepareAttempts = 0;
    pendingKey = retainedKey; uncertain = retainedKey !== null;
    el("results").replaceChildren();
    el("selected").textContent = ""; el("selected").hidden = true;
    el("review").hidden = true; el("summary").textContent = "";
    el("matches").replaceChildren(); el("distinct-label").hidden = true;
    el("search").reset(); el("registration").reset();
    el("registration-box").open = false;
    say(""); controls();
  }
  async function call(action, body, epoch) {
    if (epoch !== generation) throw new Error("CONTEXT_CHANGED");
    const response = await fetch("/demo/stage1/patient/" + action, {
      method: "POST", credentials: "same-origin", cache: "no-store", redirect: "error",
      headers: {"Content-Type": "application/json", "X-CSRF-Token": csrf || ""},
      body: JSON.stringify(body)
    });
    if (epoch !== generation) throw new Error("CONTEXT_CHANGED");
    const text = await response.text();
    if (epoch !== generation || text.length > 16384) throw new Error("REPLY_UNAVAILABLE");
    if (!response.ok) {
      const error = new Error("REPLY_UNAVAILABLE"); error.status = response.status; throw error;
    }
    const value = JSON.parse(text);
    if (!value || !Object.hasOwn(value, "result")) throw new Error("REPLY_UNAVAILABLE");
    return value.result;
  }
  function patient(row) {
    if (!row || !uuid(row.id) || !uuid(row.practice_id) ||
        typeof row.first_name !== "string" || typeof row.last_name !== "string" ||
        typeof row.date_of_birth !== "string") throw new Error("PATIENT_UNAVAILABLE");
    return row;
  }
  function label(row) { return row.first_name + " " + row.last_name + " · " + row.date_of_birth; }
  const keys = (value, names) => value !== null && typeof value === "object" && !Array.isArray(value) &&
    Object.keys(value).length === names.length && names.every(key => Object.hasOwn(value, key));
  const safeText = (value, max) => typeof value === "string" && value.length > 0 && value.length <= max &&
    value === value.trim() && !/[\u0000-\u001f\u007f]/.test(value);
  function day(value) {
    if (typeof value !== "string" || !/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(value)) return false;
    const [y,m,d] = value.split("-").map(Number), leap = y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0);
    return y >= 1 && m >= 1 && m <= 12 && d >= 1 && d <= [31,leap?29:28,31,30,31,30,31,31,30,31,30,31][m-1];
  }
  function clearTimes() {
    bookingEpoch += 1; el("times-result").replaceChildren(); el("times-status").textContent = "";
  }
  function metadata(value) {
    if (!keys(value,["practice_id","date","duration_minutes"]) || !uuid(value.practice_id) || !day(value.date) ||
        !Number.isInteger(value.duration_minutes) || value.duration_minutes < 1 || value.duration_minutes > 180) return null;
    return {practice_id:value.practice_id,date:value.date,duration_minutes:value.duration_minutes};
  }
  function validateTimes(value, person, meta) {
    if (!keys(value,["state","patient","practitioner","practice_id","timezone","date","duration_minutes","slots"]) ||
        value.state !== "ready" || value.practice_id !== meta.practice_id || value.date !== meta.date ||
        value.duration_minutes !== meta.duration_minutes || !safeText(value.timezone,128) ||
        !keys(value.patient,["id","practice_id","first_name","last_name","date_of_birth"]) ||
        value.patient.id !== person.id || value.patient.practice_id !== person.practice_id ||
        value.patient.first_name !== person.first_name || value.patient.last_name !== person.last_name ||
        value.patient.date_of_birth !== person.date_of_birth || !day(value.patient.date_of_birth) ||
        !safeText(value.patient.first_name,100) || !safeText(value.patient.last_name,100)) throw new Error("TIMES_UNAVAILABLE");
    const p=value.practitioner;
    if (!keys(p,["id","displayName","roleLabel","active","defaultLocation"]) || !uuid(p.id) ||
        !safeText(p.displayName,201) || !(p.roleLabel === null || safeText(p.roleLabel,100)) ||
        p.active !== true || p.defaultLocation !== null || !Array.isArray(value.slots) ||
        value.slots.length < 1 || value.slots.length > 32) throw new Error("TIMES_UNAVAILABLE");
    let previous = -1; const available = [];
    for (const slot of value.slots) {
      if (!keys(slot,["start_time","end_time","available"]) || typeof slot.available !== "boolean") throw new Error("TIMES_UNAVAILABLE");
      const parse = s => {
        if (typeof s !== "string" || !/^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}$/.test(s) || s.slice(0,10) !== meta.date) throw new Error("TIMES_UNAVAILABLE");
        const h=Number(s.slice(11,13)), m=Number(s.slice(14,16)), sec=Number(s.slice(17,19));
        if (h > 23 || m > 59 || sec > 59) throw new Error("TIMES_UNAVAILABLE");
        return h*3600+m*60+sec;
      };
      const start=parse(slot.start_time), end=parse(slot.end_time);
      if (start < previous || end <= start || end-start !== meta.duration_minutes*60) throw new Error("TIMES_UNAVAILABLE");
      previous=end; if (slot.available) available.push(slot.start_time.slice(11,16));
    }
    return {name:p.displayName,zone:value.timezone,times:available};
  }
  el("times").addEventListener("click", () => perform(async epoch => {
    if (!selected || !bookingMeta || selected.practice_id !== bookingMeta.practice_id) return;
    const tick=bookingEpoch, person={...selected}, meta={...bookingMeta}, token=csrf;
    const current = () => epoch === generation && tick === bookingEpoch && csrf === token &&
      selected && selected.id === person.id && selected.practice_id === person.practice_id &&
      selected.first_name === person.first_name && selected.last_name === person.last_name &&
      selected.date_of_birth === person.date_of_birth &&
      bookingMeta && JSON.stringify(bookingMeta) === JSON.stringify(meta);
    el("times-status").textContent="Checking times…";
    try {
      const response=await fetch("/demo/stage1/staff-booking/context",{method:"POST",credentials:"same-origin",
        cache:"no-store",redirect:"error",headers:{"Content-Type":"application/json","X-CSRF-Token":token},
        body:JSON.stringify({patient_id:person.id,date:meta.date,duration_minutes:meta.duration_minutes})});
      if (!current()) return;
      if (!response.ok) { const error=new Error("TIMES_UNAVAILABLE"); error.status=response.status; throw error; }
      if (!response.body) throw new Error("TIMES_UNAVAILABLE");
      const reader=response.body.getReader(), chunks=[]; let size=0;
      while (true) {
        const part=await reader.read(); if (!current()) { await reader.cancel(); return; }
        if (part.done) break; size+=part.value.byteLength;
        if (size > 32768) { await reader.cancel(); throw new Error("TIMES_UNAVAILABLE"); }
        chunks.push(part.value);
      }
      if (!current()) return;
      const bytes=new Uint8Array(size); let offset=0;
      for (const chunk of chunks) { bytes.set(chunk,offset); offset+=chunk.byteLength; }
      const view=validateTimes(JSON.parse(new TextDecoder("utf-8",{fatal:true}).decode(bytes)),person,meta);
      if (!current()) return;
      const heading=document.createElement("p"); heading.textContent=`${view.name} · ${meta.date} · ${meta.duration_minutes} minutes · ${view.zone}`;
      el("times-result").append(heading);
      if (view.times.length) { const list=document.createElement("ul"); for(const time of view.times) { const item=document.createElement("li"); item.textContent=time; list.append(item); } el("times-result").append(list); }
      else { const message=document.createElement("p"); message.textContent="No available times for this day."; el("times-result").append(message); }
      el("times-status").textContent="Times checked. Booking is a separate action.";
    } catch(error) {
      if (!current()) return;
      clearTimes(); if ([401,403].includes(error.status)) throw error;
      el("times-status").textContent="Times could not be checked. Please try again or check your sign-in.";
    }
  }));
  function showSelected(row, verb) {
    clearTimes(); clearBooking();
    selected = patient(row);
    controls();
    el("selected").textContent = verb + " " + label(selected);
    el("selected").hidden = false;
    say("Patient record checked. Appointment booking is a separate action.");
    // No event, DemoConfig mutation or implicit booking-patient handoff.
  }
  async function receiptRead(key, epoch) {
    const receipt = await call("receipt", {command_key: key}, epoch);
    if (epoch !== generation) throw new Error("CONTEXT_CHANGED");
    if (receipt.command_key !== key || !uuid(receipt.patient_id) || !uuid(receipt.practice_id)) throw new Error("RECEIPT_UNAVAILABLE");
    const row = patient(await call("read", {patient_id: receipt.patient_id}, epoch));
    if (epoch !== generation) throw new Error("CONTEXT_CHANGED");
    if (row.id !== receipt.patient_id || row.practice_id !== receipt.practice_id) throw new Error("READBACK_CHANGED");
    uncertain = false; draft = predecessor = null; pendingKey = null;
    el("review").hidden = true; el("registration").reset();
    showSelected(row, "Registered:");
  }
  async function perform(operation) {
    if (busy || !csrf) return;
    clearTimes();
    busy = true; controls();
    const epoch = generation;
    try { await operation(epoch); }
    catch (error) {
      if (epoch === generation) clearTimes();
      if (epoch === generation && [401, 403].includes(error.status)) {
        const unknown = uncertain;
        clearProjection(unknown); csrf = null; available = false; panel.hidden = true;
        document.getElementById("account-status").textContent = unknown
          ? "Sign in again and inspect the patient record. The registration result is still unverified."
          : "Your practice access needs checking. Sign in again before continuing.";
      } else if (epoch === generation && [400, 422].includes(error.status) && !uncertain &&
          pendingPrepare && error.prepareKey === pendingPrepare.command_key && prepareAttempts === 1) {
        // These statuses are reserved by the bridge for no-dispatch validation.
        pendingPrepare = null; prepareAttempts = 0; draft = null; el("review").hidden = true;
        say("Check the patient details and try again.");
      } else if (epoch === generation) say(uncertain
        ? "The result needs checking. Check this registration before starting another."
        : pendingPrepare ? "No registration has been confirmed. Check the prepared details again."
        : "Patient details could not be checked. Check your sign-in and try again.");
    }
    finally { busy = false; controls(); }
  }
  el("search").addEventListener("submit", event => {
    event.preventDefault();
    perform(async epoch => {
      const q = el("query").value.trim(), dob = el("dob").value;
      if (!q && !dob) { say("Enter a name or date of birth."); return; }
      if (q && q.length < 2) { say("Enter at least two characters of the patient name."); return; }
      const body = {limit: 10}; if (q) body.q = q; if (dob) body.date_of_birth = dob;
      clearTimes(); el("results").replaceChildren(); selected = null; el("selected").hidden = true; controls();
      const rows = await call("search", body, epoch);
      if (epoch !== generation) throw new Error("CONTEXT_CHANGED");
      if (!Array.isArray(rows) || rows.length > 20) throw new Error("RESULTS_UNAVAILABLE");
      for (const item of rows) {
        const row = patient(item), li = document.createElement("li"), button = document.createElement("button");
        button.type = "button"; button.className = "quiet"; button.textContent = label(row);
        button.addEventListener("click", () => perform(async current => {
          clearTimes();
          const fresh = patient(await call("read", {patient_id: row.id}, current));
          if (current !== generation) throw new Error("CONTEXT_CHANGED");
          if (fresh.id !== row.id || fresh.practice_id !== row.practice_id) throw new Error("READBACK_CHANGED");
          showSelected(fresh, "Selected:");
        }));
        li.append(button); el("results").append(li);
      }
      say(rows.length ? "Choose the person you mean." : "No matching patient found.");
    });
  });
  el("registration").addEventListener("input", () => {
    clearTimes();
    if (uncertain || busy || pendingPrepare) return;
    draft = null; el("review").hidden = true; controls();
  });
  el("registration").addEventListener("submit", event => {
    event.preventDefault();
    if (uncertain) return;
    perform(async epoch => {
      if (!pendingPrepare) {
        prepareAttempts = 0;
        const prior = predecessor;
        const first = el("first").value.trim(), last = el("last").value.trim(), birth = el("birth").value;
        if (![first, last].every(name => name.length >= 1 && name.length <= 100 && !/[\u0000-\u001f\u007f]/.test(name)) ||
            !/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(birth) || birth > new Date().toISOString().slice(0, 10)) {
          say("Enter a first name, last name and valid date of birth."); return;
        }
        pendingPrepare = {command_key: crypto.randomUUID(), new_registration: !prior,
          registration_intent_id: prior?.registration_intent_id || null,
          supersedes_command_id: prior?.command_id || null, supersedes_revision: prior?.draft_revision || null,
          body: {first_name: first, last_name: last, date_of_birth: birth, distinct_person: el("distinct").checked}};
      }
      const body = pendingPrepare, key = body.command_key;
      draft = null; el("review").hidden = true;
      prepareAttempts += 1;
      let result;
      try { result = await call("prepare", body, epoch); }
      catch (error) { error.prepareKey = key; throw error; }
      if (epoch !== generation) throw new Error("CONTEXT_CHANGED");
      if (result.state === "committed") {
        pendingPrepare = null; prepareAttempts = 0;
        pendingKey = key; uncertain = true;
        await receiptRead(key, epoch); return;
      }
      if (result.state !== "prepared" || result.command_key !== key || !uuid(result.command_id) ||
          !uuid(result.registration_intent_id) || !Number.isInteger(result.draft_revision) ||
          typeof result.body_digest !== "string" || !/^[0-9a-f]{64}$/.test(result.body_digest) ||
          !result.body || typeof result.can_confirm !== "boolean") throw new Error("DRAFT_UNAVAILABLE");
      draft = predecessor = result;
      if (!Array.isArray(result.advisory_matches) || result.advisory_matches.length > 20) throw new Error("MATCHES_UNAVAILABLE");
      el("matches").replaceChildren();
      for (const item of result.advisory_matches) {
        const li = document.createElement("li"); li.textContent = label(patient(item)); el("matches").append(li);
      }
      el("distinct-label").hidden = !result.requires_distinct_person_decision && !result.advisory_matches.length;
      el("summary").textContent = result.body.first_name + " " + result.body.last_name + " · " + result.body.date_of_birth;
      el("review").hidden = false;
      pendingPrepare = null; prepareAttempts = 0;
      el("review-title").focus();
      say(result.requires_distinct_person_decision
        ? "A similar record exists. Check the person before confirming a distinct registration."
        : "Check these details, then confirm registration.");
    });
  });
  el("confirm").addEventListener("click", () => {
    if (!draft?.can_confirm || uncertain) return;
    const shown = draft;
    perform(async epoch => {
      pendingKey = shown.command_key; uncertain = true; controls();
      try {
        await call("confirm", {command_key: shown.command_key, command_id: shown.command_id,
          draft_revision: shown.draft_revision, body_digest: shown.body_digest, confirmed: true}, epoch);
      } catch (error) {
        if (epoch !== generation || [401, 403].includes(error.status)) throw error;
        // Exactly one read follows an uncertain reply; never retry the write.
      }
      if (epoch !== generation) throw new Error("CONTEXT_CHANGED");
      await receiptRead(shown.command_key, epoch);
    });
  });
  el("recover").addEventListener("click", () => {
    if (uncertain && pendingKey) perform(epoch => receiptRead(pendingKey, epoch));
  });
  return {setAccount(value) {
    available = value?.phase === "selected" && value.patient_available === true &&
      typeof value.csrf === "string" && ["Receptionist", "PracticeOwner"].includes(value.identity?.role);
    const next = available ? value.csrf : null;
    const identity = value?.identity;
    const nextIdentity = available && value.phase === "selected" && identity?.role === "Receptionist" &&
      safeText(identity.email,254) && safeText(identity.practice_name,255)
      ? JSON.stringify([value.phase,identity.email,identity.role,identity.practice_name]) : null;
    const nextMeta = nextIdentity !== null ? metadata(value.staff_booking_context) : null;
    if (JSON.stringify(nextMeta) !== JSON.stringify(bookingMeta)) clearTimes();
    if (next !== csrf || nextIdentity !== bookingIdentity) clearProjection(uncertain);
    bookingMeta = nextMeta; bookingIdentity = nextIdentity;
    selectedBookingEnabled = value?.selected_staff_booking_available === true && nextMeta !== null;
    csrf = next; panel.hidden = !available || inAppointments; controls();
  }, setWorkspace(visible) {
    inAppointments = visible; panel.hidden = !available || inAppointments;
  }};
}
