// Source-only UI. The same-origin adapter contract is specified beside this file.
// No demo identity, capability, signed proposal, or staff credential is kept by the browser.
import { initLocalVoice, initSpokenReply } from "./stage1-local-voice.js";
const $ = id => document.getElementById(id);
const state = { session: null, request: null, appointment: null, offer: null,
  create: null, move: null, pendingKey: null, generation: 0, busy: false };
const text = (id, value) => { $(id).textContent = value == null ? "" : String(value); };
const show = (id, visible) => { $(id).hidden = !visible; };
let spoken = null;
const status = message => { spoken?.stop(); text("status", message); };
const dateTime = (date, clock, zone) => `${date} at ${clock} ${zone}`;
const uuid = () => crypto.randomUUID();

async function api(method, action, body, key) {
  if (!state.session) throw new Error("No verified demo session.");
  const response = await fetch("/demo/stage1/action", {
    method: "POST", credentials: "same-origin", cache: "no-store", redirect: "error",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": state.session.csrf },
    body: JSON.stringify({ method, action, body, idempotency_key: key || null }),
  });
  if (!response.ok) {
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
function clearPending() {
  spoken?.stop();
  state.create = state.move = state.offer = null;
  show("create-review", false); show("move-review", false);
}
function displayRequest(request, original, options = []) {
  state.request = request;
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
}
function displayStaff(data) {
  if (!data || !data.request) { text("staff-request", "Request unavailable."); return; }
  state.request = data.request;
  state.appointment = data.appointment || null;
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
  try {
    const value = requestFields();
    if (!state.request || state.request.state !== "draft") throw new Error("Refresh the draft request before submitting.");
    text("request-summary", `Follow-up on ${value.date}, between ${value.earliest_local} and ${value.latest_local} ${state.session.zone}. No booking is being made yet.`);
    show("request-review-box", true); $("request-submit").focus();
  } catch (error) { status(error.message); }
}
async function submitRequest() {
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
    const result = await api("read", "propose_move", { appointment_ref: appointment.ref,
      source_state_version: appointment.state_version, target_date: date, target_start_local: local_time });
    if (!result.safe || !result.proposal_ref) throw new Error("Move unavailable. Refresh the appointment.");
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
$("request-edit").addEventListener("click", () => { spoken?.stop(); show("request-review-box", false); $("request-date").focus(); });
$("request-submit").addEventListener("click", submitRequest);
$("patient-refresh").addEventListener("click", refresh);
$("staff-refresh").addEventListener("click", refresh);
$("create-confirm").addEventListener("click", confirmCreate);
$("create-cancel").addEventListener("click", () => { clearPending(); $("staff-offers").querySelector("button")?.focus(); });
$("move-propose").addEventListener("click", reviewMove);
$("move-confirm").addEventListener("click", confirmMove);
$("move-cancel").addEventListener("click", () => { clearPending(); $("move-date").focus(); });
$("reconcile").addEventListener("click", async () => {
  status("Checking the original action with its existing command key…");
  try {
    const result = await api("read", "reconcile", null);
    if (state.session.persona === "patient") displayRequest(result.request, result.original_booking, result.options); else displayStaff(result);
    show("reconcile", result.uncertain === true);
    status(result.uncertain === true ? "Outcome remains uncertain; no new action was started." : "Original action reconciled; current facts refreshed.");
  } catch (_) { show("reconcile", true); status("Original action remains uncertain. No new action was started."); }
});
for (const id of ["request-date", "request-earliest", "request-latest", "patient-words"]) $(id).addEventListener("input", () => show("request-review-box", false));
for (const id of ["move-date", "move-time", "move-words"]) $(id).addEventListener("input", () => { state.move = null; show("move-review", false); });

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
  initLocalVoice(() => state.session, () => spoken?.stop());
  await refresh();
} catch (error) { status(error.message); }
