(function exposeYuriWalkthroughCore(root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  } else {
    root.YuriWalkthroughCore = api;
  }
}(typeof globalThis !== "undefined" ? globalThis : this, function buildYuriWalkthroughCore() {
  "use strict";

  const RESULTS = Object.freeze(["worked", "partly_worked", "did_not_work", "skipped"]);
  const ORIENTATION = Object.freeze(["clear", "mixed", "unclear", "not_applicable"]);
  const RELATIVE_VALUE = Object.freeze([
    "reception_one_better",
    "about_same",
    "ordinary_diary_better",
    "not_compared"
  ]);
  const OVERALL_VALUE = Object.freeze([
    "clear_advance",
    "promising_needs_revision",
    "not_yet_useful",
    "not_assessed"
  ]);
  const DESIGN_PARTNER_READINESS = Object.freeze([
    "not_ready",
    "ready_after_revision",
    "ready_now",
    "not_assessed"
  ]);
  const DIRECTION = Object.freeze(["supports", "neutral", "concern", "not_assessed"]);
  const ISSUE_FLAGS = Object.freeze([
    "entry_not_obvious",
    "wording_too_technical",
    "scope_unclear",
    "diary_context_lost",
    "date_orientation_unclear",
    "projection_less_helpful_than_grid",
    "selection_or_proposal_unclear",
    "back_path_unclear",
    "visual_density",
    "ordinary_diary_fallback_needed",
    "task_not_supported"
  ]);
  const MAX_NOTE_LENGTH = 1200;

  function assertAllowed(value, allowed, label) {
    if (!allowed.includes(value)) throw new Error(`${label} is not allowlisted`);
    return value;
  }

  function normalizeNote(value, label) {
    const note = String(value || "").trim();
    if (note.length > MAX_NOTE_LENGTH) {
      throw new Error(`${label} must be ${MAX_NOTE_LENGTH} characters or fewer`);
    }
    return note;
  }

  function reviewId(now) {
    const stamp = String(now || new Date().toISOString())
      .replace(/[^0-9]/g, "")
      .slice(0, 14);
    return `yuri-walkthrough-${stamp}`;
  }

  function createReview(acknowledged, now) {
    if (acknowledged !== true) {
      throw new Error("Acknowledge the synthetic demonstration before continuing.");
    }
    return {
      schema_version: "reception_one.yuri_internal_walkthrough.session.v1",
      review_id: reviewId(now),
      reviewer_scope: "yuri_internal_product_critique",
      acknowledgement: {
        authored_synthetic_only: true,
        no_real_diary_effect: true,
        no_real_person_or_practice_details_in_notes: true
      },
      started_at: now || new Date().toISOString(),
      task_reviews: [],
      final_review: null
    };
  }

  function normalizeTaskReview(input, taskIds, recordedAt) {
    const allowedTaskIds = Array.from(taskIds || []);
    const issues = [...new Set(input.issue_flags || [])].sort();
    issues.forEach((item) => assertAllowed(item, ISSUE_FLAGS, "issue flag"));
    return {
      schema_version: "reception_one.yuri_internal_walkthrough.task_review.v1",
      task_id: assertAllowed(String(input.task_id), allowedTaskIds, "task id"),
      result: assertAllowed(input.result, RESULTS, "task result"),
      orientation: assertAllowed(input.orientation, ORIENTATION, "orientation"),
      relative_value: assertAllowed(input.relative_value, RELATIVE_VALUE, "relative value"),
      ordinary_diary_fallback_used: input.ordinary_diary_fallback_used === true,
      issue_flags: issues,
      product_note: normalizeNote(input.product_note, "product note"),
      recorded_at: recordedAt || new Date().toISOString()
    };
  }

  function upsertTaskReview(review, taskReview) {
    const index = review.task_reviews.findIndex((item) => item.task_id === taskReview.task_id);
    if (index >= 0) review.task_reviews.splice(index, 1, taskReview);
    else review.task_reviews.push(taskReview);
    review.task_reviews.sort((left, right) => left.task_id.localeCompare(right.task_id));
    return review;
  }

  function normalizeFinalReview(input, recordedAt) {
    return {
      schema_version: "reception_one.yuri_internal_walkthrough.final_review.v1",
      overall_value: assertAllowed(input.overall_value, OVERALL_VALUE, "overall value"),
      design_partner_readiness: assertAllowed(
        input.design_partner_readiness,
        DESIGN_PARTNER_READINESS,
        "design-partner readiness"
      ),
      directions: {
        foreground_projection_window: assertAllowed(
          input.foreground_projection_window,
          DIRECTION,
          "foreground projection direction"
        ),
        date_first_page_turn: assertAllowed(
          input.date_first_page_turn,
          DIRECTION,
          "date-turn direction"
        ),
        bureau_workflow: assertAllowed(input.bureau_workflow, DIRECTION, "Bureau direction"),
        text_before_push_to_talk: assertAllowed(
          input.text_before_push_to_talk,
          DIRECTION,
          "text-before-voice direction"
        )
      },
      product_note: normalizeNote(input.product_note, "overall product note"),
      recorded_at: recordedAt || new Date().toISOString()
    };
  }

  function summarize(review, totalTasks) {
    const rows = review.task_reviews;
    return {
      tasks_available: Number(totalTasks),
      tasks_recorded: rows.length,
      worked: rows.filter((item) => item.result === "worked").length,
      partly_worked: rows.filter((item) => item.result === "partly_worked").length,
      did_not_work: rows.filter((item) => item.result === "did_not_work").length,
      skipped: rows.filter((item) => item.result === "skipped").length,
      ordinary_diary_fallback_count: rows.filter(
        (item) => item.ordinary_diary_fallback_used
      ).length,
      threshold_claim: "not_applicable_internal_formative"
    };
  }

  function buildExport(review, totalTasks, exportedAt) {
    const hasNotes = review.task_reviews.some((item) => item.product_note.length > 0)
      || Boolean(review.final_review?.product_note);
    return {
      schema_version: "reception_one.yuri_internal_walkthrough.export.v1",
      evidence_mode: "authored_synthetic_yuri_internal_formative",
      review_scope: "single_owner_internal_product_critique",
      exported_at: exportedAt || new Date().toISOString(),
      session: {
        review_id: review.review_id,
        reviewer_scope: review.reviewer_scope,
        acknowledgement: { ...review.acknowledgement },
        started_at: review.started_at
      },
      exclusions: {
        representative_participant_evidence: false,
        usability_threshold_claim: false,
        contains_real_patient_or_practice_data: false,
        contains_prompt_or_transcript_text: false,
        contains_audio_video_or_screen_recording: false,
        contains_provider_or_credential_data: false,
        contains_free_form_product_notes: hasNotes,
        appointment_write_available: false
      },
      task_reviews: review.task_reviews.map((item) => ({ ...item })),
      final_review: review.final_review ? {
        ...review.final_review,
        directions: { ...review.final_review.directions }
      } : null,
      summary: summarize(review, totalTasks)
    };
  }

  return Object.freeze({
    RESULTS,
    ORIENTATION,
    RELATIVE_VALUE,
    OVERALL_VALUE,
    DESIGN_PARTNER_READINESS,
    DIRECTION,
    ISSUE_FLAGS,
    MAX_NOTE_LENGTH,
    createReview,
    normalizeTaskReview,
    upsertTaskReview,
    normalizeFinalReview,
    summarize,
    buildExport
  });
}));
