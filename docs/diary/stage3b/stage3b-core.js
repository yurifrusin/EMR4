(function exposeStage3BCore(root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  } else {
    root.Stage3BCore = api;
  }
}(typeof globalThis !== "undefined" ? globalThis : this, function buildStage3BCore() {
  "use strict";

  const OUTCOMES = Object.freeze(["completed", "completed_with_assistance", "aborted", "not_attempted"]);
  const CORRECTNESS = Object.freeze(["correct", "partly_correct", "incorrect", "not_applicable"]);
  const COMPREHENSION = Object.freeze(["clear", "uncertain", "incorrect", "not_applicable"]);
  const CONFIDENCE = Object.freeze(["high", "medium", "low", "not_recorded"]);
  const AMBIGUITY = Object.freeze(["safe_clarification", "unsafe_assumption", "not_applicable"]);
  const PROPOSAL = Object.freeze(["understood_not_committed", "mistaken_as_committed", "not_applicable"]);
  const ISSUE_FLAGS = Object.freeze([
    "could_not_find_entry",
    "route_not_obvious",
    "scope_not_understood",
    "blank_space_mistaken_for_availability",
    "selection_mistaken_for_booking",
    "proposal_mistaken_for_booking",
    "identity_assumed",
    "back_path_not_found",
    "ordinary_diary_escape_not_found",
    "facilitator_intervention",
    "participant_stopped"
  ]);

  function assertAllowed(value, allowed, label) {
    if (!allowed.includes(value)) throw new Error(`${label} is not allowlisted`);
    return value;
  }

  function assignedRoute(task, arm) {
    if (!task || !task.routeByArm) throw new Error("task route contract is missing");
    assertAllowed(arm, ["A", "B"], "counterbalance arm");
    return assertAllowed(task.routeByArm[arm], ["reception_one", "ordinary_diary"], "assigned route");
  }

  function createSessionId(participantCode, now) {
    const stamp = String(now || new Date().toISOString())
      .replace(/[^0-9]/g, "")
      .slice(0, 14);
    return `stage3b-${participantCode.toLowerCase()}-${stamp}`;
  }

  function createSession(config, data, now) {
    const participantCode = assertAllowed(config.participant_code, data.participantCodes, "participant code");
    const practiceBucket = assertAllowed(config.practice_bucket, data.practiceBuckets, "practice bucket");
    const arm = assertAllowed(config.counterbalance_arm, data.counterbalanceArms, "counterbalance arm");
    if (config.consent_voluntary !== true
        || config.consent_synthetic !== true
        || config.consent_no_recording !== true
        || config.consent_no_write !== true) {
      throw new Error("all consent attestations are required");
    }
    return {
      schema_version: "reception_one.stage3b.session.v1",
      session_id: createSessionId(participantCode, now),
      participant_code: participantCode,
      practice_bucket: practiceBucket,
      counterbalance_arm: arm,
      consent: {
        voluntary: true,
        authored_synthetic_only: true,
        no_prompt_transcript_or_recording: true,
        no_appointment_write: true
      },
      started_at: now || new Date().toISOString(),
      observations: []
    };
  }

  function normalizeObservation(input, session, task, recordedAt) {
    const issues = [...new Set(input.issue_flags || [])].sort();
    issues.forEach((item) => assertAllowed(item, ISSUE_FLAGS, "issue flag"));
    const taskId = String(task.id);
    const route = assignedRoute(task, session.counterbalance_arm);
    const assistance = Number(input.assistance_count);
    const elapsed = Number(input.elapsed_ms);
    if (!Number.isInteger(assistance) || assistance < 0 || assistance > 9) {
      throw new Error("assistance_count must be an integer from 0 to 9");
    }
    if (!Number.isInteger(elapsed) || elapsed < 0 || elapsed > 3600000) {
      throw new Error("elapsed_ms must be an integer from 0 to 3600000");
    }
    return {
      schema_version: "reception_one.stage3b.structured_observation.v1",
      session_id: session.session_id,
      participant_code: session.participant_code,
      practice_bucket: session.practice_bucket,
      counterbalance_arm: session.counterbalance_arm,
      task_id: taskId,
      assigned_route: route,
      route_visits: {
        reception_one: input.route_visits?.reception_one === true,
        ordinary_diary: input.route_visits?.ordinary_diary === true
      },
      elapsed_ms: elapsed,
      task_outcome: assertAllowed(input.task_outcome, OUTCOMES, "task outcome"),
      correctness: assertAllowed(input.correctness, CORRECTNESS, "correctness"),
      state_comprehension: assertAllowed(input.state_comprehension, COMPREHENSION, "state comprehension"),
      confidence: assertAllowed(input.confidence, CONFIDENCE, "confidence"),
      assistance_count: assistance,
      ordinary_diary_fallback: input.ordinary_diary_fallback === true,
      safe_ambiguity: assertAllowed(input.safe_ambiguity, AMBIGUITY, "safe ambiguity"),
      proposal_boundary: assertAllowed(input.proposal_boundary, PROPOSAL, "proposal boundary"),
      issue_flags: issues,
      recorded_at: recordedAt || new Date().toISOString()
    };
  }

  function upsertObservation(session, observation) {
    const index = session.observations.findIndex((item) => item.task_id === observation.task_id);
    if (index >= 0) session.observations.splice(index, 1, observation);
    else session.observations.push(observation);
    session.observations.sort((left, right) => left.task_id.localeCompare(right.task_id));
    return session;
  }

  function percentage(numerator, denominator) {
    return denominator ? Math.round((numerator / denominator) * 1000) / 10 : null;
  }

  function median(values) {
    if (!values.length) return null;
    const ordered = values.slice().sort((a, b) => a - b);
    const middle = Math.floor(ordered.length / 2);
    return ordered.length % 2
      ? ordered[middle]
      : Math.round((ordered[middle - 1] + ordered[middle]) / 2);
  }

  function thresholdStatus(measured, passed) {
    if (!measured) return "not_measured";
    return passed ? "passed" : "failed";
  }

  function scoreObservations(observations) {
    const rows = observations || [];
    const receptionRows = rows.filter((item) => item.assigned_route === "reception_one");
    const completedReception = receptionRows.filter((item) =>
      ["completed", "completed_with_assistance"].includes(item.task_outcome)
      && item.ordinary_diary_fallback === false
    );
    const ambiguityRows = rows.filter((item) => item.safe_ambiguity !== "not_applicable");
    const correctReversibleRows = rows.filter((item) =>
      ["S3B-02", "S3B-03", "S3B-07", "S3B-08"].includes(item.task_id)
    );
    const correctReversible = correctReversibleRows.filter((item) =>
      item.correctness === "correct"
      && !item.issue_flags.includes("back_path_not_found")
    );
    const receptionTimes = rows
      .filter((item) => item.assigned_route === "reception_one" && item.task_outcome.startsWith("completed"))
      .map((item) => item.elapsed_ms);
    const ordinaryTimes = rows
      .filter((item) => item.assigned_route === "ordinary_diary" && item.task_outcome.startsWith("completed"))
      .map((item) => item.elapsed_ms);
    const recallReceptionTimes = rows
      .filter((item) => ["S3B-02", "S3B-08"].includes(item.task_id)
        && item.assigned_route === "reception_one"
        && item.task_outcome.startsWith("completed"))
      .map((item) => item.elapsed_ms);
    const recallOrdinaryTimes = rows
      .filter((item) => ["S3B-02", "S3B-08"].includes(item.task_id)
        && item.assigned_route === "ordinary_diary"
        && item.task_outcome.startsWith("completed"))
      .map((item) => item.elapsed_ms);
    const receptionMedian = median(receptionTimes);
    const ordinaryMedian = median(ordinaryTimes);
    const recallReceptionMedian = median(recallReceptionTimes);
    const recallOrdinaryMedian = median(recallOrdinaryTimes);
    const fasterPercent = recallReceptionMedian !== null && recallOrdinaryMedian
      ? Math.round(((recallOrdinaryMedian - recallReceptionMedian) / recallOrdinaryMedian) * 1000) / 10
      : null;

    const safetyFailures = rows.filter((item) =>
      item.safe_ambiguity === "unsafe_assumption"
      || item.proposal_boundary === "mistaken_as_committed"
      || item.issue_flags.includes("selection_mistaken_for_booking")
      || item.issue_flags.includes("proposal_mistaken_for_booking")
      || item.issue_flags.includes("identity_assumed")
    );

    const gridFreeRate = percentage(completedReception.length, receptionRows.length);
    const ambiguityRate = percentage(
      ambiguityRows.filter((item) => item.safe_ambiguity === "safe_clarification").length,
      ambiguityRows.length
    );
    const correctReversibleRate = percentage(correctReversible.length, correctReversibleRows.length);
    return {
      schema_version: "reception_one.stage3b.score.v1",
      participant_records: rows.length,
      safety_gate: {
        status: safetyFailures.length ? "failed" : thresholdStatus(rows.length > 0, true),
        failure_count: safetyFailures.length
      },
      thresholds: {
        grid_free_completion: {
          target_percent: 80,
          measured_percent: gridFreeRate,
          status: thresholdStatus(receptionRows.length > 0, gridFreeRate >= 80)
        },
        safe_ambiguity_recovery: {
          target_percent: 90,
          measured_percent: ambiguityRate,
          status: thresholdStatus(ambiguityRows.length > 0, ambiguityRate >= 90)
        },
        correct_reversible_projections: {
          target_percent: 90,
          measured_percent: correctReversibleRate,
          status: thresholdStatus(correctReversibleRows.length > 0, correctReversibleRate >= 90)
        },
        low_interruption_notice_precision_recall: {
          target_percent: 90,
          measured_percent: null,
          status: "not_measured"
        },
        conversational_median_no_slower: {
          target: "reception_one_median_lte_ordinary_diary_median",
          reception_one_median_ms: receptionMedian,
          ordinary_diary_median_ms: ordinaryMedian,
          status: thresholdStatus(
            receptionMedian !== null && ordinaryMedian !== null,
            receptionMedian <= ordinaryMedian
          )
        },
        appointment_recall_faster: {
          target_percent: 20,
          nonblocking: true,
          measured_percent: fasterPercent,
          status: thresholdStatus(fasterPercent !== null, fasterPercent >= 20)
        }
      }
    };
  }

  function buildExport(session, exportedAt) {
    return {
      schema_version: "reception_one.stage3b.study_export.v1",
      evidence_mode: "authored_synthetic_participant_session",
      participant_scope: "representative_reception_staff_formative",
      exported_at: exportedAt || new Date().toISOString(),
      session: {
        session_id: session.session_id,
        participant_code: session.participant_code,
        practice_bucket: session.practice_bucket,
        counterbalance_arm: session.counterbalance_arm,
        started_at: session.started_at,
        consent: { ...session.consent }
      },
      exclusions: {
        contains_real_patient_data: false,
        contains_prompt_or_transcript_text: false,
        contains_free_text: false,
        contains_audio_or_video: false,
        contains_screen_recording: false,
        contains_provider_or_credential_data: false,
        appointment_write_available: false
      },
      observations: session.observations.map((item) => ({ ...item })),
      score: scoreObservations(session.observations)
    };
  }

  return Object.freeze({
    OUTCOMES,
    CORRECTNESS,
    COMPREHENSION,
    CONFIDENCE,
    AMBIGUITY,
    PROPOSAL,
    ISSUE_FLAGS,
    assignedRoute,
    createSession,
    normalizeObservation,
    upsertObservation,
    scoreObservations,
    buildExport
  });
}));
