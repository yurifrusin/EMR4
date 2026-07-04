# plan-claude-claude-sprint-d4-diary-domain-frames-policy-foundation

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-d4-diary-domain-frames-policy-foundation` |
| Status | pending_plan_review |
| Created | 2026-07-04 15:45 +1000 |
| Source HEAD | `4cf9f68` |

## Plan Summary

Add a typed same-day/future request-horizon signal to the diary reception policy and booking-outcome classifier so a firm "no matching times" conclusion is only emitted when a real slot search covered the same requested day/window. Future-day empty searches downgrade to an advisory outcome, and roster/schedule unavailability always carries a self-explaining reason code. Backend diary-domain contract code only; additive/optional; no UI, no API contract, no migration.

## My Understanding

All three of Yuri concerns live in app/services/diary/ (policy.py, outcomes.py, schedule_explanations.py, frames.py, temporal.py), not in UI or API contracts. (1) temporal.py already classifies SameDayWindowKind (ok/not_same_day/window_fully_past/clamp_earliest) but policy.py and outcomes.py never consume it, so a future-day empty slot search is classified identically to a same-day empty search and becomes the hard no_matching_times outcome. (2) outcomes._build_schedule_explanation_payload only attaches an explanation when a schedule reason code already exists, so a roster_schedule frame with status=unavailable and no reason_code yields roster_unavailable with no schedule_explanation. (3) The no-candidates-only-after-real-search guardrail already exists (searched_no_candidates needs a slot_search frame; explain_schedule needs search_ran and candidate_count==0) and mostly holds; D4 hardens it with regression tests and ensures the horizon change cannot fabricate no-candidate copy.

## Intended Surface / Boundary

Backend diary-domain contract code only, all pure (no DB/clock/LLM/network): app/services/diary/policy.py (horizon-aware classification), app/services/diary/outcomes.py (self-explaining roster gap + advisory future path), app/services/diary/schedule_explanations.py (new future-advisory reason/copy + roster-gap fallback resolution), app/services/diary/frames.py (at most one additive optional field, e.g. search_horizon, default-safe). Tests under tests/.

## Out Of Scope

No frontend/diary.js/taskpane/Command Centre changes. No GraphRAG/vector store. No persisted Bernie DB session/table or migration. No new or changed API endpoints; no breaking response schema (additive optional fields only). No Fable/high-cost model. No master/handoff movement. Visually loaded words (cards, slots, panels, diary grid, waiting room, status) refer to existing UI surfaces that MUST NOT change; this sprint touches only the typed domain layer that feeds them.

## Files I Expect To Edit

app/services/diary/frames.py (optional additive field, default-safe); app/services/diary/schedule_explanations.py (new reason + copy + alias/fallback); app/services/diary/policy.py (horizon-aware predicate); app/services/diary/outcomes.py (roster_unavailable always self-explains; advisory future path); app/services/diary/__init__.py if new symbols are exported; tests/test_diary_schedule_explanations.py, tests/test_bernie_booking_outcomes.py, and a new focused horizon test module.

## Implementation Steps

1. Add additive optional search_horizon to BernieSlotSearchFrame (mirror on DiaryScheduleExplanationEvidence as needed), default None so existing frames/evidence classify exactly as today. 2. In policy.py derive a future-search-no-candidates distinction: a non-same-day empty search takes advisory semantics instead of search_ran_no_candidates; same-day empty search stays firm. Keep all current predicate names; add fields additively. 3. Add DiaryScheduleExplanationReason.future_search_advisory (title/staff prompt to check the roster for that week/confirm availability) and resolve a fallback reason (no_roster_row/practitioner_unavailable) for roster gaps with no explicit code so roster_unavailable always self-explains. 4. In outcomes.py: (a) guarantee roster_unavailable always attaches a schedule_explanation; (b) route future empty searches to advisory_warnings_present rather than no_matching_times while same-day empty search stays no_matching_times; preserve mutual exclusivity, precedence, and OUTCOME_SESSION_STATE consistency. 5. Preserve the no-candidates guardrail: no-candidate copy only when a real slot_search frame ran; add assertions the horizon change never fabricates it. 6. Update exports and keep assert_outcome_matches_state green for every branch.

## Visual / Behavioural Acceptance Checks

No pixels change. Behavioural/typed checks: same-day empty search still yields no_matching_times with searched_no_candidates copy; future-day empty search yields an advisory-family outcome, not a hard no-availability conclusion; roster_unavailable always carries a non-null schedule_explanation with authority=display_only; no-candidate copy never appears without a real slot-search frame; legacy frames/evidence omitting search_horizon classify identically to pre-D4. Verification: focused pytest for test_diary_schedule_explanations.py, test_bernie_booking_outcomes.py, new horizon tests, adjacent Bernie policy/frame suites; py_compile touched files; git diff --check.

## Risks / Ambiguities

Semantics of "advisory unless same day/window": I read future as not the same clinic day as the request reference date, matching evaluate_same_day_window; a wider current-window/per-week threshold could be intended, so I will flag for Ariadne. Precedence: horizon change must not weaken hard guardrail/stale/clarification dominance; it is inserted only at the empty-search branch. Additive-only guarantee: search_horizon must default so current callers (routes passing no horizon) keep todays behaviour, avoiding any API contract shift.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
