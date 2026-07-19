(function exposeStage3ACore(root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  } else {
    root.Stage3ACore = api;
  }
}(typeof globalThis !== "undefined" ? globalThis : this, function buildStage3ACore() {
  "use strict";

  function normalize(value) {
    return String(value || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
  }

  function includesAll(text, terms) {
    return terms.every((term) => text.includes(term));
  }

  function person(data, id) {
    return data.patients.find((item) => item.id === id)
      || data.practitioners.find((item) => item.id === id);
  }

  function appointmentView(data, appointment) {
    const patient = person(data, appointment.patientId);
    const practitioner = person(data, appointment.practitionerId);
    return {
      appointmentId: appointment.id,
      patient: patient.displayName,
      practitioner: practitioner.displayName,
      date: appointment.date,
      startsAt: appointment.startsAt,
      endsAt: appointment.endsAt,
      status: appointment.status,
      location: appointment.location
    };
  }

  function interpretTask(taskId, rawText, data) {
    const text = normalize(rawText);
    if (!text) {
      return { kind: "clarification", code: "empty_request", message: "What would you like to know about the synthetic Diary?" };
    }

    const future = data.appointments.filter((item) => item.patientId === "patient-margaret-thompson");
    const sixMonth = data.appointments.find((item) => item.id === "appointment-margaret-six-months");
    const fridayWeek = data.appointments.filter((item) => item.practitionerId === "practitioner-shera" && item.date === "2026-07-31");

    if (taskId === "S3A-06") {
      return {
        kind: "boundary",
        code: "authoritative_confirmation_separate",
        message: "This fixture surface cannot confirm or commit. Run S3A-06 separately through the visible local Diary confirmation path."
      };
    }

    if (taskId === "S3A-07" || (text.includes("margaret") && !text.includes("thompson") && !text.includes("thomson"))) {
      return {
        kind: "clarification",
        code: "patient_identity_ambiguous",
        message: "Which synthetic patient do you mean?",
        candidates: ["Margaret Thompson", "Margaret Thomson"]
      };
    }

    if (taskId === "S3A-08" || includesAll(text, ["confirm", "old", "proposal"])) {
      return {
        kind: "blocked",
        code: "stale_context",
        message: "That proposal is stale. I have not changed the Diary. Refresh the current slots before preparing a new proposal."
      };
    }

    if (taskId === "S3A-09" || text.includes("resume")) {
      return {
        kind: "answer",
        code: "retained_context_resumed",
        message: "Resumed the synthetic slot-review context. No committed action was repeated.",
        projection: {
          id: "projection-resumed-availability",
          type: "availability",
          scope: "Dr Shera · Friday 31 July 2026 · after 2 pm · Brisbane Clinic",
          items: data.availability.slice()
        }
      };
    }

    if (taskId === "S3A-05" || text.includes("prepare") || text.includes("book")) {
      if (!includesAll(text, ["margaret", "shera"])) {
        return { kind: "clarification", code: "proposal_details_missing", message: "Which patient and practitioner should the synthetic proposal use?" };
      }
      return {
        kind: "proposal",
        code: "proposal_ready_no_write",
        message: "Proposal only: Margaret Thompson with Dr Shera on Friday 31 July 2026, 2:45 pm–3:15 pm. Nothing has been written.",
        projection: {
          id: "projection-proposal-margaret-shera",
          type: "proposal",
          scope: "Margaret Thompson · Dr Shera · Friday 31 July 2026 · Brisbane Clinic",
          items: [data.availability[0]]
        }
      };
    }

    if (taskId === "S3A-04" || text.includes("availability")) {
      if (!includesAll(text, ["shera", "friday"])) {
        return { kind: "clarification", code: "availability_scope_missing", message: "Which practitioner and date should I check?" };
      }
      return {
        kind: "answer",
        code: "availability_found_no_write",
        message: "Dr Shera has two synthetic 30-minute options after 2 pm on Friday week. No appointment has been created.",
        projection: {
          id: "projection-shera-availability-friday-week",
          type: "availability",
          scope: "Dr Shera · Friday 31 July 2026 · 2 pm–5 pm · Brisbane Clinic",
          items: data.availability.slice()
        }
      };
    }

    if (["S3A-03", "S3A-10"].includes(taskId) || includesAll(text, ["shera", "afternoon", "friday"])) {
      if (!includesAll(text, ["shera", "friday"])) {
        return { kind: "clarification", code: "practitioner_window_missing", message: "Which practitioner and Friday do you mean?" };
      }
      return {
        kind: "answer",
        code: "practitioner_window_found",
        message: "Showing Dr Shera's synthetic afternoon on Friday 31 July 2026.",
        projection: {
          id: "projection-shera-friday-week-afternoon",
          type: "practitioner_window",
          scope: "Dr Shera · Friday 31 July 2026 · 12 pm–5 pm · Brisbane Clinic",
          items: fridayWeek.map((item) => appointmentView(data, item))
        }
      };
    }

    if (taskId === "S3A-11" || (text.includes("margaret thompson") && text.includes("upcoming"))) {
      return {
        kind: "answer",
        code: "patient_upcoming_found",
        message: `Margaret Thompson has ${future.length} authored upcoming appointments.`,
        projection: {
          id: "projection-margaret-upcoming",
          type: "patient_upcoming",
          scope: "Margaret Thompson · all upcoming appointments · Brisbane Clinic",
          items: future.map((item) => appointmentView(data, item))
        }
      };
    }

    if (["S3A-01", "S3A-02"].includes(taskId) || (includesAll(text, ["margaret thompson", "shera"]) && (text.includes("six month") || text.includes("details")))) {
      if (!includesAll(text, ["margaret thompson", "shera"])) {
        return { kind: "clarification", code: "appointment_identity_missing", message: "Please include the synthetic patient's full name and practitioner." };
      }
      const view = appointmentView(data, sixMonth);
      return {
        kind: "answer",
        code: "appointment_found",
        message: "Margaret Thompson is booked with Dr Michael Shera at Brisbane Clinic on Wednesday 20 January 2027 from 2:30 pm to 3:00 pm. Status: confirmed.",
        projection: {
          id: "projection-margaret-six-months",
          type: "patient_upcoming",
          scope: "Margaret Thompson · Dr Shera · January 2027 · Brisbane Clinic",
          items: [view]
        }
      };
    }

    return {
      kind: "clarification",
      code: "unsupported_or_ambiguous_fixture_request",
      message: "I cannot safely map that wording to this scenario's deterministic synthetic contract. Could you restate the patient, practitioner, and time scope?"
    };
  }

  function createAttentionState() {
    return {
      seenEventIds: new Set(),
      aggregateRevisions: new Map(),
      visibleNoticeCount: 0
    };
  }

  function evaluateAttentionEvent(event, state, context, data) {
    const base = {
      eventId: event.id,
      eventType: event.event_type,
      evidenceMode: event.evidence_mode,
      attention: "silent",
      visible: false,
      reasonCode: null,
      projection: null
    };

    if (!event.committed) {
      return { ...base, reasonCode: "uncommitted_or_rolled_back" };
    }
    if (event.practice_id !== context.practiceId) {
      return { ...base, reasonCode: "foreign_practice" };
    }
    if (state.seenEventIds.has(event.id)) {
      return { ...base, reasonCode: "duplicate_event" };
    }

    const priorRevision = state.aggregateRevisions.get(event.aggregate_id) || 0;
    if (event.aggregate_revision <= priorRevision) {
      state.seenEventIds.add(event.id);
      return { ...base, reasonCode: "stale_or_out_of_order" };
    }

    state.seenEventIds.add(event.id);
    state.aggregateRevisions.set(event.aggregate_id, event.aggregate_revision);

    if (event.relationship === "unrelated") {
      return { ...base, reasonCode: "unrelated_to_retained_task" };
    }

    const freshRead = data.currentReads[event.current_read_id];
    if (!freshRead) {
      return { ...base, reasonCode: "fresh_scoped_read_unavailable" };
    }

    state.visibleNoticeCount += 1;
    return {
      ...base,
      attention: "concise",
      visible: true,
      reasonCode: "relevant_committed_change_confirmed_by_fresh_read",
      message: freshRead.summary,
      projection: {
        id: freshRead.projectionId,
        type: "event_context",
        scope: freshRead.scope,
        asOf: freshRead.asOf,
        items: [freshRead]
      }
    };
  }

  function routeOrderFor(scenario, scenarioIndex, counterbalance) {
    if (scenario.routes.length < 2) {
      return scenario.routes.slice();
    }
    const conversationFirst = counterbalance === "A" ? scenarioIndex % 2 === 0 : scenarioIndex % 2 !== 0;
    return conversationFirst ? ["conversation", "grid"] : ["grid", "conversation"];
  }

  return {
    normalize,
    interpretTask,
    createAttentionState,
    evaluateAttentionEvent,
    routeOrderFor
  };
}));
