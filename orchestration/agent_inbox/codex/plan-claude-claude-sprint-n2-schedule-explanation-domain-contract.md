# plan-claude-claude-sprint-n2-schedule-explanation-domain-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-n2-schedule-explanation-domain-contract` |
| Status | pending_plan_review |
| Created | 2026-07-03 20:10 +1000 |
| Source HEAD | `0d112ef` |

## Plan Summary

Add a pure, read-only diary-domain schedule-explanation contract (7 distinct no-slot states) plus a deterministic copy catalog keyed by state/reason code, so Diary UI and Bernie can render without scenario-specific message branches. No route/UI/write-path/migration behaviour changes.

## My Understanding

app/services/diary already owns typed reception contracts (frames, policy, temporal, envelopes, capabilities); bernie/* are compatibility facades. Two gaps: explain_schedule is registered in capabilities.py:104 with implemented_as=None, and user-facing copy lives in scenario-specific message dicts (appointments.py:3402-3413) rather than a domain-owned catalog. Central invariant mirroring policy.py: searched_no_candidates is true ONLY when a valid search ran and returned zero; no-roster, day-off, outside-hours, breaks-only, fully-booked, elapsed-same-day-window are distinct states that take precedence and must never collapse into 'no times'.

## Intended Surface / Boundary

Only app/services/diary/: a new pure-contract module schedule_explanation.py, its __init__ exports, an optional bernie/ facade, one metadata-only edit to the explain_schedule capability entry, and a new test file. Explicitly unchanged: diary grid (docs/diary/*), booking slot/card/status/waiting-room UI, taskpane, Command Centre, appointments.py route behaviour, the live no-slot path, existing evidence_summaries/staff_actions dicts, and all write/proposal/confirm paths. Contract+catalog+tests only; not wired into any live response this sprint.

## Out Of Scope

No GraphRAG/K1, no persisted sessions, no unified confirm path, no HMAC/evidence changes, no auto-mode, no booking write changes, no UI redesign, no migration (pure contract, no DB). Does not replace appointments.py message dicts (deferred to a separately-reviewed UI-consumption step so behaviour stays identical now).

## Files I Expect To Edit

NEW app/services/diary/schedule_explanation.py (state enum, ScheduleExplanationEvidence input, ScheduleExplanation output, explain_schedule() classifier, copy catalog + get_schedule_explanation_copy()); EDIT app/services/diary/__init__.py (exports); NEW app/services/bernie/schedule_explanation.py (facade re-export); EDIT app/services/diary/capabilities.py (explain_schedule implemented_as metadata only); NEW tests/test_diary_schedule_explanation.py.

## Implementation Steps

1) ScheduleExplanationState enum with 7 members: no_roster_row, practitioner_unavailable, outside_request_window, breaks_only_window, fully_booked, same_day_window_elapsed, searched_no_candidates. 2) ScheduleExplanationEvidence(BaseModel, extra=forbid): pure deterministic facts (has_roster_row, practitioner_working, within_request_window, window_is_breaks_only, any_free_capacity, same_day_window_kind reusing temporal.SameDayWindowKind, search_ran, candidate_count, reference_date, payload) - no DB/network. 3) explain_schedule(evidence)->ScheduleExplanation with documented precedence ladder: no_roster_row > practitioner_unavailable > same_day_window_elapsed > outside_request_window > breaks_only_window > fully_booked > searched_no_candidates (only when search_ran and candidate_count==0); safe fallback otherwise, never a false 'no times'. 4) ScheduleExplanation output model (state, reason_code, basis, reference_date, payload; no embedded copy). 5) Frozen SCHEDULE_EXPLANATION_COPY catalog + ScheduleExplanationCopy (headline, staff_detail, staff_action; calm helpful tone per protocol) + total get_schedule_explanation_copy(). 6) Export from diary/__init__ and add bernie facade. 7) Set explain_schedule capability implemented_as to the new module path. 8) tests/test_diary_schedule_explanation.py: per-state precedence incl. adversarial mixes (search_ran+0 candidates but no roster => no_roster_row), catalog totality, extra=forbid rejection.

## Visual / Behavioural Acceptance Checks

git diff touches only the five listed files; appointments.py untouched. explain_schedule never returns searched_no_candidates unless search_ran and candidate_count==0 (asserted). Copy catalog total over all 7 states (asserted). New+existing diary/bernie domain tests pass; python -m compileall app/services/diary; git diff --check clean.

## Risks / Ambiguities

Classifier consumes a typed evidence model rather than reading DB/frames, keeping it pure/route-neutral; the router-side resolver that populates evidence from real roster/slot data is deliberately deferred and flagged as follow-up. breaks_only vs outside_request_window precedence is a documented judgment call Codex can reorder. Not replacing appointments.py dicts now is intentional to keep behaviour identical; a live swap would expand into behaviour-affecting UI-consumption scope and should be a separate accepted step.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
