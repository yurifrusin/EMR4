(function exposeStage3AData(root, factory) {
  const data = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = data;
  } else {
    root.Stage3AData = data;
  }
}(typeof globalThis !== "undefined" ? globalThis : this, function buildStage3AData() {
  "use strict";

  const referenceDate = "2026-07-20";
  const practice = {
    id: "practice-synthetic-brisbane",
    label: "Synthetic Brisbane General Practice",
    location: "Brisbane Clinic",
    timezone: "Australia/Brisbane"
  };

  const practitioners = [
    { id: "practitioner-shera", displayName: "Dr Michael Shera", column: "Dr Shera" },
    { id: "practitioner-patel", displayName: "Dr Anika Patel", column: "Dr Patel" },
    { id: "practitioner-chen", displayName: "Nurse Lin Chen", column: "Nurse Chen" }
  ];

  const patients = [
    { id: "patient-margaret-thompson", displayName: "Margaret Thompson", synthetic: true },
    { id: "patient-margaret-thomson", displayName: "Margaret Thomson", synthetic: true },
    { id: "patient-john-ellis", displayName: "John Ellis", synthetic: true },
    { id: "patient-amy-wright", displayName: "Amy Wright", synthetic: true }
  ];

  const appointments = [
    {
      id: "appointment-margaret-friday-week",
      patientId: "patient-margaret-thompson",
      practitionerId: "practitioner-shera",
      date: "2026-07-31",
      startsAt: "14:15",
      endsAt: "14:45",
      status: "BOOKED",
      location: practice.location
    },
    {
      id: "appointment-margaret-six-months",
      patientId: "patient-margaret-thompson",
      practitionerId: "practitioner-shera",
      date: "2027-01-20",
      startsAt: "14:30",
      endsAt: "15:00",
      status: "CONFIRMED",
      location: practice.location
    },
    {
      id: "appointment-john-friday-week",
      patientId: "patient-john-ellis",
      practitionerId: "practitioner-shera",
      date: "2026-07-31",
      startsAt: "13:00",
      endsAt: "13:30",
      status: "BOOKED",
      location: practice.location
    },
    {
      id: "appointment-amy-friday-week",
      patientId: "patient-amy-wright",
      practitionerId: "practitioner-shera",
      date: "2026-07-31",
      startsAt: "15:30",
      endsAt: "16:00",
      status: "BOOKED",
      location: practice.location
    },
    {
      id: "appointment-margaret-patel",
      patientId: "patient-margaret-thompson",
      practitionerId: "practitioner-patel",
      date: "2026-08-14",
      startsAt: "09:00",
      endsAt: "09:30",
      status: "BOOKED",
      location: practice.location
    }
  ];

  const availability = [
    { id: "slot-shera-1445", practitionerId: "practitioner-shera", date: "2026-07-31", startsAt: "14:45", endsAt: "15:15" },
    { id: "slot-shera-1600", practitionerId: "practitioner-shera", date: "2026-07-31", startsAt: "16:00", endsAt: "16:30" }
  ];

  const scenarios = [
    { id: "S3A-01", title: "Relative-time appointment recall", goal: "Find Margaret Thompson's appointment about six months from the reference date with Dr Shera.", hint: "What time and date is Margaret Thompson's appointment in six months with Dr Shera?", routes: ["conversation", "grid"], gridDate: "2027-01-20" },
    { id: "S3A-02", title: "Authoritative appointment details", goal: "State the date, time, location, practitioner and status of Margaret's six-month appointment.", hint: "Tell me the details of Margaret Thompson's six-month appointment with Dr Shera.", routes: ["conversation", "grid"], gridDate: "2027-01-20" },
    { id: "S3A-03", title: "Practitioner time-window view", goal: "Inspect Dr Shera's bounded afternoon on Friday week. The appointment projection must be chronological.", hint: "Open Dr Shera's afternoon appointments on Friday week.", routes: ["conversation", "grid"], gridDate: "2026-07-31" },
    { id: "S3A-04", title: "Availability without a write", goal: "Find suitable Dr Shera availability on Friday week after 2 pm without booking.", hint: "Show Dr Shera's availability on Friday week after 2 pm.", routes: ["conversation", "grid"], gridDate: "2026-07-31" },
    { id: "S3A-05", title: "Proposal, not action", goal: "Prepare a synthetic booking proposal and verify that it is labelled as unwritten.", hint: "Prepare an appointment for Margaret Thompson with Dr Shera on Friday week after 2 pm.", routes: ["conversation"] },
    { id: "S3A-06", title: "Explicit confirmed create", goal: "Verify that this fixture refuses to commit. Sol runs the real visible confirmation and exact database check separately after the formative study.", hint: "Why can’t this study page confirm the appointment?", routes: ["conversation"] },
    { id: "S3A-07", title: "Identity ambiguity", goal: "Ask for Margaret without a surname and require a choice between two synthetic candidates.", hint: "Show me Margaret's upcoming appointments.", routes: ["conversation"] },
    { id: "S3A-08", title: "Stale or blocked request", goal: "Explain a stale proposal safely without claiming a mutation.", hint: "Confirm the old appointment proposal again.", routes: ["conversation"] },
    { id: "S3A-09", title: "Interrupted-session resume", goal: "Resume retained synthetic context without repeating a committed action.", hint: "Resume my appointment task.", routes: ["conversation"] },
    { id: "S3A-10", title: "Friday-week focused projection", goal: "Open only Dr Shera's afternoon on Friday week and return to the overview.", hint: "Bernie, open the Diary page for Dr Shera's afternoon appointments on Friday week.", routes: ["conversation", "grid"], gridDate: "2026-07-31" },
    { id: "S3A-11", title: "Patient upcoming projection", goal: "Show every authored future appointment for Margaret Thompson in chronological order. In the grid comparison, inspect each date offered by the date control.", hint: "Show me all of Margaret Thompson's upcoming appointments.", routes: ["conversation", "grid"], gridDate: "2026-07-31" },
    { id: "S3A-12", title: "Relevant committed-change attention", goal: "Click Relevant committed reschedule once, verify one concise notice, then click Show current context.", hint: "Follow the event-attention steps shown below.", routes: ["attention"], attentionSteps: ["fixture-relevant-reschedule"] },
    { id: "S3A-13", title: "Unsafe and unrelated suppression", goal: "Click the unrelated roster, foreign-practice and rolled-back fixtures in the displayed order; none may create a user-visible notice.", hint: "Follow the event-attention steps shown below.", routes: ["attention"], attentionSteps: ["fixture-unrelated-roster", "fixture-foreign-practice", "fixture-rolled-back"] },
    { id: "S3A-14", title: "Replay and ordering reconciliation", goal: "Click relevant reschedule, replay and delayed older revision in the displayed order; only the first may create a visible effect.", hint: "Follow the event-attention steps shown below.", routes: ["attention"], attentionSteps: ["fixture-relevant-reschedule", "fixture-replay-reschedule", "fixture-delayed-reschedule"] }
  ];

  const events = [
    {
      fixture_id: "fixture-relevant-reschedule",
      id: "event-relevant-reschedule-v2",
      label: "Relevant committed reschedule",
      event_type: "diary.appointment_rescheduled",
      evidence_mode: "authored_synthetic_fixture",
      practice_id: practice.id,
      committed: true,
      aggregate_id: "appointment-margaret-friday-week",
      aggregate_revision: 2,
      correlation_id: "correlation-synthetic-reschedule",
      relationship: "active_patient",
      current_read_id: "read-margaret-friday-week-v2"
    },
    {
      fixture_id: "fixture-unrelated-roster",
      id: "event-unrelated-roster-v1",
      label: "Unrelated committed roster change",
      event_type: "diary.roster_changed",
      evidence_mode: "authored_synthetic_fixture",
      practice_id: practice.id,
      committed: true,
      aggregate_id: "roster-practitioner-chen-2026-08-03",
      aggregate_revision: 1,
      correlation_id: "correlation-synthetic-roster",
      relationship: "unrelated",
      current_read_id: "read-roster-chen-v1"
    },
    {
      fixture_id: "fixture-foreign-practice",
      id: "event-foreign-practice-v1",
      label: "Foreign-practice event",
      event_type: "diary.appointment_cancelled",
      evidence_mode: "authored_synthetic_fixture",
      practice_id: "practice-synthetic-foreign",
      committed: true,
      aggregate_id: "appointment-foreign",
      aggregate_revision: 1,
      correlation_id: "correlation-synthetic-foreign",
      relationship: "active_patient",
      current_read_id: "read-foreign"
    },
    {
      fixture_id: "fixture-rolled-back",
      id: "event-rolled-back-v1",
      label: "Rolled-back change",
      event_type: "diary.appointment_rescheduled",
      evidence_mode: "authored_synthetic_fixture",
      practice_id: practice.id,
      committed: false,
      aggregate_id: "appointment-margaret-friday-week",
      aggregate_revision: 3,
      correlation_id: "correlation-synthetic-rollback",
      relationship: "active_patient",
      current_read_id: null
    },
    {
      fixture_id: "fixture-replay-reschedule",
      id: "event-relevant-reschedule-v2",
      label: "Replay of relevant reschedule",
      event_type: "diary.appointment_rescheduled",
      evidence_mode: "authored_synthetic_fixture",
      practice_id: practice.id,
      committed: true,
      aggregate_id: "appointment-margaret-friday-week",
      aggregate_revision: 2,
      correlation_id: "correlation-synthetic-reschedule",
      relationship: "active_patient",
      current_read_id: "read-margaret-friday-week-v2"
    },
    {
      fixture_id: "fixture-delayed-reschedule",
      id: "event-delayed-reschedule-v1",
      label: "Delayed older revision",
      event_type: "diary.appointment_rescheduled",
      evidence_mode: "authored_synthetic_fixture",
      practice_id: practice.id,
      committed: true,
      aggregate_id: "appointment-margaret-friday-week",
      aggregate_revision: 1,
      correlation_id: "correlation-synthetic-delayed",
      relationship: "active_patient",
      current_read_id: "read-margaret-friday-week-v2"
    }
  ];

  const currentReads = {
    "read-margaret-friday-week-v2": {
      projectionId: "projection-event-margaret-friday-week-v2",
      scope: "Margaret Thompson · Dr Shera · Friday 31 July 2026 · Brisbane Clinic",
      summary: "Margaret Thompson's appointment on Friday 31 July 2026 is now 2:45 pm–3:15 pm with Dr Shera.",
      asOf: "2026-07-20T10:30:00+10:00"
    },
    "read-roster-chen-v1": {
      projectionId: "projection-roster-chen-v1",
      scope: "Nurse Chen · Monday 3 August 2026",
      summary: "Nurse Chen's synthetic roster changed.",
      asOf: "2026-07-20T10:31:00+10:00"
    }
  };

  return {
    schema_version: "bernie.stage3a.study-fixtures.v1",
    evidence_mode: "authored_synthetic_fixture",
    referenceDate,
    practice,
    practitioners,
    patients,
    appointments,
    availability,
    scenarios,
    events,
    currentReads
  };
}));
