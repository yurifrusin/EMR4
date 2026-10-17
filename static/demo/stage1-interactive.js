// Source-only UI. The same-origin adapter contract is specified beside this file.
// No demo identity, capability, signed proposal, or staff credential is kept by the browser.
import { initLocalVoice, initSpokenReply, createManualIntentHandoff } from "./stage1-local-voice.js";
const $ = id => document.getElementById(id);
const state = { session: null, request: null, appointment: null, offer: null,
  create: null, move: null, pendingKey: null, generation: 0, busy: false, requestReview: null, moveReview: null };
const text = (id, value) => { $(id).textContent = value == null ? "" : String(value); };
const show = (id, visible) => { $(id).hidden = !visible; };
let spoken = null;
const status = message => { spoken?.stop(); text("status", message); };
const dateTime = (date, clock, zone) => `${date} at ${clock} ${zone}`;
const uuid = () => crypto.randomUUID();

const intentHandoffs={request:createManualIntentHandoff(),move:createManualIntentHandoff()};
let localVoice=null;
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
function renderMapping(kind) {
  const check=$(kind+"-mapping-ack"),info=intentHandoffs[kind].inspect(intentSnapshot(kind));
  $(kind+"-mapping").hidden=!info.required;
  check.disabled=!info.supported || Boolean(localVoice && !localVoice.isIdle());
  check.checked=info.acknowledged;
  text(kind+"-mapping-status",!info.required?"Structured details only. No note needs mapping.":
    !info.supported?"Complete the current structured details before checking the note.":
    info.acknowledged?"Your check is recorded for these words, target and details. This does not verify their meaning.":
    "Transfer or correct the note's meaning in the structured details, then check that they match.");
}
function invalidateIntent(kind, cancelCapture=true) {
  intentHandoffs[kind].invalidate();
  if(kind==="request"){state.requestReview=null;show("request-review-box",false);}
  else clearPending();
  renderMapping(kind);
  if(cancelCapture)localVoice?.invalidateTarget();
}
function acceptMapping(kind) {
  const check=$(kind+"-mapping-ack");
  if(localVoice && !localVoice.isIdle()){
    check.checked=false;status("Finish or cancel dictation before checking the mapped details.");return;
  }
  if(!check.checked){invalidateIntent(kind);return;}
  try{intentHandoffs[kind].acknowledge(intentSnapshot(kind));}
  catch(_){check.checked=false;status("Complete the current details and check the editable note before review.");}
  renderMapping(kind);
}
function requireMappedReview(kind) {
  if(localVoice && !localVoice.isIdle())throw new Error("Finish or cancel dictation before review.");
  try{return intentHandoffs[kind].review(intentSnapshot(kind));}
  catch(_){throw new Error("Check that the current editable note matches these structured details before review.");}
}

async function api(method, action, body, key) {
  if (!state.session) throw new Error("No verified demo session.");
  const response = await fetch("/demo/stage1/action", {
    method: "POST", credentials: "same-origin", cache: "no-store", redirect: "error",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": state.session.csrf },
    body: JSON.stringify({ method, action, body, idempotency_key: key || null }),
  });
  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      state.session=null;invalidateIntent("request");invalidateIntent("move");
    }
    if (response.status === 409) throw new Error("Current facts changed. Refresh and review again.");
    throw new Error("The action could not be verified. Refresh current facts before another action.");
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
  labParagraph(root, `This report includes reviewed attempts through Native08. The authored catalog has ${progress.catalog_cases} distinct cases in ${progress.catalog_families} families. Its prior evidence review classified ${dispositions.current_controls} current controls, ${dispositions.qualified_reused_boundaries} reused boundaries and ${dispositions.not_run} NOT_RUN cases. Test attempts, phase reports and delivered records below are separate counts; they do not increase catalog coverage.`);
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
    title.textContent = `${labels[example.case_id] ?? example.case_id} · ${example.evidence_kind === "NATIVE04_DELIVERED_CONTROL" ? "delivered control" : "reused boundary"}`; card.append(title);
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
  spoken?.stop();
  state.create = state.move = state.offer = state.moveReview = null;
  show("create-review", false); show("move-review", false);
}
function displayRequest(request, original, options = []) {
  const previousTarget=selectedVoiceTarget();
  state.request = request;
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
  const message = booked
    ? `This request led to a booking. ${original?.source === "completed_create_command_result" ?
      `Original booking result: ${dateTime(original.date, original.start_local, original.zone)}. ` :
      "The original booking command result is unavailable in this demo session. "}Current appointment time from readback: ${request.booked_start_time}. Current status: ${request.booked_status}.`
    : request.state === "submitted"
      ? "Request received. Reception One has not confirmed a booking. No time is reserved."
      : request.state === "draft" ? "Draft request. Review and send when ready." : `Request state: ${request.state}.`;
  text("patient-outcome", message);
  renderMapping("request");
}
function displayStaff(data) {
  if (!data || !data.request) { text("staff-request", "Request unavailable."); return; }
  state.request = data.request;
  state.appointment = data.appointment || null;
  invalidateIntent("move");
  const r = data.request;
  facts($("staff-request"), [
    ["Request", r.state], ["Source", "Synthetic patient web text"],
    ["Identity", "Fictional demo session; no real patient identity"],
    ["Preference", r.preference_date && r.earliest_local && r.latest_local
      ? `${r.preference_date}, ${r.earliest_local}–${r.latest_local} ${r.practice_timezone}` : "Not submitted"],
    ["Request version", r.request_version],
    ["Original booking result", data.original_booking?.source === "completed_create_command_result"
      ? dateTime(data.original_booking.date, data.original_booking.start_local, data.original_booking.zone)
      : "Unavailable in this demo session"],
  ]);
  const appt = data.appointment;
  show("move-area", Boolean(appt));
  if (appt) {
    facts($("diary"), [["Current appointment", dateTime(appt.date, appt.start_local, appt.zone)],
      ["Status", appt.status], ["Patient", appt.patient_label], ["Practitioner", appt.practitioner_label],
      ["Type", appt.type_label], ["Duration", `${appt.duration_minutes} minutes`], ["Location", appt.location_label],
      ["State version", appt.state_version]]);
  } else $("diary").replaceChildren();
  const offers = $("staff-offers"); offers.replaceChildren();
  if (Array.isArray(data.options)) for (const option of data.options) {
    const row = document.createElement("div"); row.className = "offer";
    const label = document.createElement("span"); label.textContent = dateTime(option.date, option.local_time, option.zone);
    const button = document.createElement("button"); button.type = "button"; button.textContent = "Review this time";
    button.addEventListener("click", () => reviewCreate(option)); row.append(label, button); offers.append(row);
  }
  if (!data.options?.length && r.state === "submitted") text("staff-outcome", "No current option is available. Offer an alternative through the reviewed backend flow.");
}
async function refresh() {
  invalidateIntent("request");invalidateIntent("move");
  clearPending(); state.pendingKey = null; const generation = ++state.generation;
  status("Refreshing current facts…");
  try {
    const result = await api("read", "refresh", null);
    if (generation !== state.generation) return;
    if (state.session.persona === "patient") displayRequest(result.request, result.original_booking, result.options);
    else displayStaff(result);
    show("reconcile", result.uncertain === true);
    status(result.uncertain === true ? "An earlier action is still uncertain. Check that original action before any new confirmation." :
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
    const value = requestFields();
    if (!state.request || state.request.state !== "draft") throw new Error("Refresh the draft request before submitting.");
    state.requestReview=requireMappedReview("request");
    text("request-summary", `Follow-up on ${value.date}, between ${value.earliest_local} and ${value.latest_local} ${state.session.zone}. No booking is being made yet.`);
    show("request-review-box", true); $("request-submit").focus();
  } catch (error) { status(error.message); }
}
async function submitRequest() {
  if((localVoice && !localVoice.isIdle()) ||
      !intentHandoffs.request.isReviewCurrent(intentSnapshot("request"),state.requestReview)){
    show("request-review-box",false);status("Review the current mapped details before sending the request.");return;
  }
  try {
    if (state.busy) return;
    const value = requestFields();
    const key = state.pendingKey || uuid(); state.pendingKey = key; state.busy = true;
    status("Sending request…");
    const result = await api("write", "submit_request", { ...value, request_version: state.request.request_version,
      reason_code: "follow_up" }, key);
    state.pendingKey = null; show("request-review-box", false); displayRequest(result.request, result.original_booking, result.options);
    status("Request result read back from the server.");
  } catch (_) { show("reconcile", true); status("Submission outcome uncertain. Check the original action before another request."); }
  finally { state.busy = false; }
}
async function reviewCreate(option) {
  clearPending(); status("Checking this time against current request and availability…");
  try {
    const result = await api("read", "propose_create", { request_version: state.request.request_version, selected: option });
    if (!result.safe || !result.proposal_ref) throw new Error("This option is unavailable. Refresh current facts.");
    state.create = result.proposal_ref;
    text("create-summary", `Create a follow-up for ${result.patient_label} with ${result.practitioner_label} on ${dateTime(option.date, option.local_time, option.zone)}. This is a fresh proposal, not a booking.`);
    show("create-review", true); $("create-confirm").focus(); status("Review the proposed booking before confirmation.");
  } catch (error) { status(error.message); }
}
async function confirmCreate() {
  if (!state.create || state.busy) return;
  state.busy = true; const key = state.pendingKey || uuid(); state.pendingKey = key;
  status("Confirming booking and checking committed readback…");
  try {
    const result = await api("write", "confirm_create", { proposal_ref: state.create }, key);
    state.pendingKey = null; clearPending();
    if (result.outcome !== "committed" || !result.appointment) throw new Error("No verified booking readback.");
    const current = await refresh();
    if (!current?.appointment || !current.appointment.zone ||
        current.appointment.ref !== result.appointment.ref ||
        current.appointment.date !== result.appointment.date ||
        current.appointment.start_local !== result.appointment.start_local)
      throw new Error("Booking readback did not match the command result.");
    const message = `Booking confirmed for ${dateTime(current.appointment.date, current.appointment.start_local, current.appointment.zone)}. You can still view the original request.`;
    status(message); spoken?.offer(message);
  } catch (_) { clearPending(); show("reconcile", true); status("Booking outcome uncertain. Check the original action before another confirmation."); }
  finally { state.busy = false; }
}
async function reviewMove() {
  clearPending();
  const appointment = state.appointment, date = $("move-date").value, local_time = $("move-time").value;
  if (!appointment || !date || !local_time) { status("Select a current appointment, new date and time."); return; }
  status("Checking the exact appointment and proposed time…");
  try {
    const mappedReview=requireMappedReview("move");
    const result = await api("read", "propose_move", { appointment_ref: appointment.ref,
      source_state_version: appointment.state_version, target_date: date, target_start_local: local_time });
    if(!intentHandoffs.move.isReviewCurrent(intentSnapshot("move"),mappedReview))
      throw new Error("The note, selected appointment or details changed. Review them again.");
    if (!result.safe || !result.proposal_ref) throw new Error("Move unavailable. Refresh the appointment.");
    state.moveReview=mappedReview;
    state.move = result.proposal_ref;
    facts($("move-summary"), [["Before", dateTime(appointment.date, appointment.start_local, appointment.zone)],
      ["After", dateTime(date, local_time, appointment.zone)], ["Patient unchanged", appointment.patient_label],
      ["Practitioner unchanged", appointment.practitioner_label], ["Type unchanged", appointment.type_label],
      ["Duration unchanged", `${appointment.duration_minutes} minutes`], ["Location unchanged", appointment.location_label]]);
    show("move-review", true); $("move-confirm").focus(); status("Review the time-only move. The original appointment has not changed.");
  } catch (error) { status(error.message); }
}
async function confirmMove() {
  if (!state.move || state.busy) return;
  if((localVoice && !localVoice.isIdle()) ||
      !intentHandoffs.move.isReviewCurrent(intentSnapshot("move"),state.moveReview)){
    clearPending();status("Review the current mapped move before confirming.");return;
  }
  const before = state.appointment;
  state.busy = true; const key = state.pendingKey || uuid(); state.pendingKey = key;
  status("Confirming move and checking the same appointment…");
  try {
    const result = await api("write", "confirm_move", { proposal_ref: state.move }, key);
    state.pendingKey = null; clearPending();
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
    const message = `The same appointment was moved to ${dateTime(current.appointment.date, current.appointment.start_local, current.appointment.zone)}.`;
    status(message); spoken?.offer(message);
  } catch (_) { clearPending(); show("reconcile", true); status("Move outcome uncertain. Check the original action before another confirmation."); }
  finally { state.busy = false; }
}

$("request-review").addEventListener("click", reviewRequest);
$("request-edit").addEventListener("click", () => { invalidateIntent("request"); spoken?.stop(); show("request-review-box", false); $("request-date").focus(); });
$("request-submit").addEventListener("click", submitRequest);
$("patient-refresh").addEventListener("click", refresh);
$("staff-refresh").addEventListener("click", refresh);
$("create-confirm").addEventListener("click", confirmCreate);
$("create-cancel").addEventListener("click", () => { invalidateIntent("move"); clearPending(); $("staff-offers").querySelector("button")?.focus(); });
$("move-propose").addEventListener("click", reviewMove);
$("move-confirm").addEventListener("click", confirmMove);
$("move-cancel").addEventListener("click", () => { invalidateIntent("move"); clearPending(); $("move-date").focus(); });
$("reconcile").addEventListener("click", async () => {
  invalidateIntent("request");invalidateIntent("move");
  status("Checking the original action with its existing command key…");
  try {
    const result = await api("read", "reconcile", null);
    if (state.session.persona === "patient") displayRequest(result.request, result.original_booking, result.options); else displayStaff(result);
    show("reconcile", result.uncertain === true);
    status(result.uncertain === true ? "Outcome remains uncertain; no new action was started." : "Original action reconciled; current facts refreshed.");
  } catch (_) { show("reconcile", true); status("Original action remains uncertain. No new action was started."); }
});
for (const id of ["request-date", "request-earliest", "request-latest", "patient-words"]) $(id).addEventListener("input", () => invalidateIntent("request"));
for (const id of ["move-date", "move-time", "move-words"]) $(id).addEventListener("input", () => invalidateIntent("move"));
for(const kind of ["request","move"]) $(kind+"-mapping-ack").addEventListener("change",()=>acceptMapping(kind));

try {
  const response = await fetch("/demo/stage1/session", { credentials: "same-origin", cache: "no-store", redirect: "error" });
  if (!response.ok) throw new Error("The local demo session is unavailable.");
  const session = await response.json();
  if (!session || !["patient", "staff"].includes(session.persona) || !session.csrf || !session.zone || !session.demo_clock)
    throw new Error("The local demo session is incomplete.");
  state.session = session;
  text("role", session.persona === "patient" ? "Alex · patient request" : "Reception One · staff");
  text("title", session.persona === "patient" ? "Ask for a follow-up" : "Review and confirm appointments");
  text("intro", session.persona === "patient" ? "Choose a preferred time. Reception One will review it before any booking exists." : "Review the current request, confirm a new booking, then move the same appointment if needed.");
  text("clock", `Fixed demonstration clock: ${session.demo_clock} · Practice timezone: ${session.zone}`);
  document.querySelectorAll(".zone").forEach(node => { node.textContent = session.zone; });
  show("patient", session.persona === "patient"); show("staff", session.persona === "staff");
  spoken = initSpokenReply(() => state.session);
  localVoice=initLocalVoice(() => state.session, () => {
    spoken?.stop();invalidateIntent(intentKind(),false);
  }, currentVoiceTarget, () => invalidateIntent(intentKind(),false), () => {
    renderMapping("request");renderMapping("move");
  });
  renderMapping("request");renderMapping("move");
  await refresh();
} catch (error) { status(error.message); }
