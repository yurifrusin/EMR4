// Inert synthetic preview. Only a future reviewed server adapter may supply a VM.
const VERSION = "appointment.list_projection.v2";
const COLUMNS = ["Start", "End", "Status", "Appointment"];
const BASE_KEYS = ["schema_version", "heading", "columns", "items", "warnings", "source", "practice_timezone", "affordances", "read_only"];
const ROW_KEYS = ["id", "practice_id", "source_version", "start_time", "end_time", "status", "display_label", "accessibility_label", "warnings"];
const SOURCE_KEYS = ["id", "revision", "captured_at", "total_count", "is_complete"];
const AFFORDANCE_KEYS = ["create", "update", "cancel", "confirm"];
const STATUSES = new Set(["Booked", "Confirmed", "Arrived", "InConsult", "Completed", "Cancelled", "NoShow", "DNA"]);
const ZONES = new Set(["Australia/Brisbane", "Australia/Sydney"]);
const UTC = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
const SNAPSHOT_VERSION = "appointment.read_render.snapshots.v1";
const VALIDATOR_SHA = "05e102af145ac8561c209108f8fb6e865d7b48a4fb598c9a5274c10d26e980d9";
const EXAMPLE_SHA = "7d2231e1434510b63b66a33439e34598577221f9cbed1e176097ac92091776cf";

function exactObject(value, names) {
  if (value === null || typeof value !== "object" || Object.getPrototypeOf(value) !== Object.prototype) return false;
  const descriptors = Object.getOwnPropertyDescriptors(value);
  const keys = Reflect.ownKeys(descriptors);
  return keys.length === names.length && names.every(name =>
    Object.hasOwn(descriptors, name) && Object.hasOwn(descriptors[name], "value") && descriptors[name].enumerable
  );
}
function exactArray(value, max) {
  return Array.isArray(value) && value.length <= max &&
    Reflect.ownKeys(value).length === value.length + 1 &&
    Array.from({ length: value.length }, (_, i) => Object.hasOwn(value, i)).every(Boolean);
}
function warnings(value, max) {
  return exactArray(value, max) && value.every(w => w === "TIME_UNCONFIRMED") && new Set(value).size === value.length;
}
function time(value) { return typeof value === "string" && UTC.test(value) && Number.isFinite(Date.parse(value)); }
function id(value) { return typeof value === "string" && UUID.test(value); }

function copyViewModel(candidate) {
  try {
    const unavailable = candidate && Object.hasOwn(candidate, "unavailable_reason");
    if (!exactObject(candidate, unavailable ? [...BASE_KEYS, "unavailable_reason"] : BASE_KEYS)) return null;
    if (candidate.schema_version !== VERSION || candidate.heading !== "Appointments" || candidate.read_only !== true) return null;
    if (!exactArray(candidate.columns, 4) || candidate.columns.length !== 4 ||
        candidate.columns.some((v, i) => v !== COLUMNS[i])) return null;
    if (!exactObject(candidate.affordances, AFFORDANCE_KEYS) || AFFORDANCE_KEYS.some(k => candidate.affordances[k] !== false)) return null;
    if (!exactArray(candidate.items, 32) || !warnings(candidate.warnings, 4)) return null;
    if (unavailable) {
      if (candidate.unavailable_reason !== "PROJECTION_UNAVAILABLE" || candidate.items.length || candidate.warnings.length ||
          candidate.source !== null || candidate.practice_timezone !== null) return null;
      return { unavailable: true };
    }
    if (!ZONES.has(candidate.practice_timezone) || !exactObject(candidate.source, SOURCE_KEYS)) return null;
    const source = candidate.source;
    if (!id(source.id) || !Number.isSafeInteger(source.revision) || source.revision < 1 ||
        !time(source.captured_at) || source.is_complete !== true || source.total_count !== candidate.items.length) return null;
    const rows = [];
    let lastKey = "";
    for (const item of candidate.items) {
      if (!exactObject(item, ROW_KEYS) || !id(item.id) || !id(item.practice_id) ||
          !Number.isSafeInteger(item.source_version) || item.source_version < 1 ||
          !time(item.start_time) || !time(item.end_time) || !STATUSES.has(item.status) ||
          !warnings(item.warnings, 1)) return null;
      const label = `Appointment ${rows.length + 1}`;
      const accessible = `${label}; starts ${item.start_time}; ends ${item.end_time}; status ${item.status}; timezone ${candidate.practice_timezone}`;
      const key = `${item.start_time}|${item.id}`;
      if (item.display_label !== label || item.accessibility_label !== accessible || key <= lastKey) return null;
      lastKey = key;
      rows.push({ start: item.start_time, end: item.end_time, status: item.status,
        label, accessible, warnings: [...item.warnings] });
    }
    return { unavailable: false, rows, warnings: [...candidate.warnings],
      source: { revision: source.revision, captured_at: source.captured_at, total_count: source.total_count },
      timezone: candidate.practice_timezone };
  } catch (_) { return null; }
}

function element(tag, className, value) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (value !== undefined) node.textContent = value;
  return node;
}
function local(value, zone, dateOnly = false) {
  const options = dateOnly
    ? { timeZone: zone, day: "numeric", month: "short", year: "numeric" }
    : { timeZone: zone, hour: "2-digit", minute: "2-digit", hour12: false };
  return new Intl.DateTimeFormat("en-AU", options).format(new Date(value));
}
function presentedRow(row, zone) {
  const startTime = local(row.start, zone);
  const startDate = local(row.start, zone, true);
  const endTime = local(row.end, zone);
  const endDate = local(row.end, zone, true);
  const warningText = row.warnings.length ? "Time not confirmed" : "";
  const accessible = `${row.label}; starts ${startTime} on ${startDate} ${zone}; ends ${endTime} on ${endDate} ${zone}; status ${row.status}${warningText ? "; " + warningText : ""}`;
  return { ...row, startTime, startDate, endTime, endDate, warningText, accessible };
}
function warningNode() { return element("p", "warning", "Time not confirmed"); }
function empty(root, accepted) {
  root.replaceChildren(
    element("p", "empty-title", accepted ? "No appointments in this snapshot." : "Appointment list unavailable"),
    ...(accepted ? [] : [element("p", "empty-copy", "No appointment information is shown.")])
  );
}
function sourceLine(snapshot) {
  const line = element("p", "source-line");
  const updated = element("span", "", `Captured ${local(snapshot.source.captured_at, snapshot.timezone)} on ${local(snapshot.source.captured_at, snapshot.timezone, true)}`);
  const revision = element("span", "", `Source revision ${snapshot.source.revision}`);
  const zone = element("span", "", `Practice time: ${snapshot.timezone}`);
  const complete = element("span", "", `Complete snapshot · ${snapshot.source.total_count} appointment${snapshot.source.total_count === 1 ? "" : "s"}`);
  line.append(updated, revision, zone, complete);
  return line;
}
function cell(label, value, detail) {
  const block = element("div", "cell");
  block.append(element("span", "cell-label", label), element("strong", "cell-value", value));
  if (detail) block.append(element("span", "secondary", detail));
  return block;
}
function list(snapshot) {
  const wrap = element("div", "list-view");
  const head = element("div", "list-head");
  COLUMNS.forEach(name => head.append(element("span", "", name)));
  const rows = element("ol", "appointment-list");
  for (const row of snapshot.rows) {
    const item = element("li", "appointment-row");
    item.setAttribute("aria-label", row.accessible);
    item.append(
      cell("Start", row.startTime, row.startDate),
      cell("End", row.endTime, row.endDate),
      cell("Status", row.status),
      cell("Appointment", row.label, row.warningText)
    );
    rows.append(item);
  }
  wrap.append(head, rows);
  return wrap;
}
function table(snapshot) {
  const wrap = element("div", "table-scroll");
  const tableNode = element("table", "");
  const caption = element("caption", "sr-only", "Appointments");
  const thead = element("thead", "");
  const heading = element("tr", "");
  COLUMNS.forEach(name => { const th = element("th", "", name); th.scope = "col"; heading.append(th); });
  thead.append(heading);
  const body = element("tbody", "");
  for (const row of snapshot.rows) {
    const tr = element("tr", "");
    tr.setAttribute("aria-label", row.accessible);
    [
      `${row.startTime} · ${row.startDate}`,
      `${row.endTime} · ${row.endDate}`,
      row.status,
      row.warningText ? `${row.label} · ${row.warningText}` : row.label,
    ].forEach(value => tr.append(element("td", "", value)));
    body.append(tr);
  }
  tableNode.append(caption, thead, body);
  wrap.append(tableNode);
  return wrap;
}

export function renderReadOnly(root, candidate, view = "list") {
  const snapshot = copyViewModel(candidate);
  if (!snapshot || snapshot.unavailable) { empty(root, false); return false; }
  try {
    const presented = { ...snapshot, rows: snapshot.rows.map(row => presentedRow(row, snapshot.timezone)) };
    const nodes = [sourceLine(presented)];
    if (presented.warnings.length) nodes.push(warningNode());
    if (presented.rows.length) nodes.push(view === "table" ? table(presented) : list(presented));
    else nodes.push(element("p", "empty-title", "No appointments in this snapshot."));
    root.replaceChildren(...nodes);
    return true;
  } catch (_) { empty(root, false); return false; }
}

function validSnapshotMap(map) {
  return exactObject(map, ["schema_version", "validator_sha256", "example_sha256", "fixed_as_of", "accepted", "rejected"])
    && map.schema_version === SNAPSHOT_VERSION && map.validator_sha256 === VALIDATOR_SHA
    && map.example_sha256 === EXAMPLE_SHA && map.fixed_as_of === "2026-10-12T00:01:00Z"
    && exactObject(map.accepted, ["normal", "fallback"])
    && exactObject(map.rejected, ["fallback"])
    && JSON.stringify(map.accepted.normal) === JSON.stringify(map.accepted.fallback)
    && copyViewModel(map.accepted.normal)?.unavailable === false
    && copyViewModel(map.accepted.fallback)?.unavailable === false
    && copyViewModel(map.rejected.fallback)?.unavailable === true;
}
const root = document.getElementById("appointment-render");
const viewChoice = document.getElementById("view-choice");
const modeChoice = document.getElementById("mode-choice");
const scenarioChoice = document.getElementById("scenario-choice");
const modeIndicator = document.getElementById("mode-indicator");
if (root && viewChoice && modeChoice && scenarioChoice && modeIndicator) {
  import("./generated-snapshots.js").then(module => {
    const map = module.default;
    if (!validSnapshotMap(map)) return;
    const update = () => {
      const mode = modeChoice.value === "fallback" ? "fallback" : "normal";
      const candidate = scenarioChoice.value === "accepted" ? map.accepted[mode] : map.rejected.fallback;
      modeIndicator.textContent = scenarioChoice.value === "accepted"
        ? (mode === "fallback" ? "Fallback view · validated synthetic snapshot" : "Normal view · validated synthetic snapshot")
        : "Rejected input · generic empty view";
      renderReadOnly(root, candidate, viewChoice.value);
    };
    [viewChoice, modeChoice, scenarioChoice].forEach(control => {
      control.disabled = false;
      control.addEventListener("change", update);
    });
    update();
  }).catch(() => { empty(root, false); });
}
