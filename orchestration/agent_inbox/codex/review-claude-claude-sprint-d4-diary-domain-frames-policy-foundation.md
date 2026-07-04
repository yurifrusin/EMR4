# review-claude-claude-sprint-d4-diary-domain-frames-policy-foundation

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-d4-diary-domain-frames-policy-foundation` |
| Status | queued |

## Review Request

claude-sprint-d4-diary-domain-frames-policy-foundation ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - EDIT app/services/diary/frames.py — added optional `search_horizon: Literal["same_day", "advance"] | None = None` to `BernieSlotSearchFrame`. Metadata-only; no outcome logic reads it. Comment explicitly records Ariadne amendment: a real searched_no_candidates result stays no_matching_times regardless of horizon.
  - EDIT app/services/diary/policy.py — added roster gap fallback in `evaluate_reception_context`: when a `roster_schedule` frame has `status == "unavailable"` and no `reason_code`, `add_reason("no_roster_row")` is called so `schedule_reason_codes` always carries at least one self-explaining entry. No change for frames that already carry an explicit `reason_code`.
  - NEW tests/test_bernie_d4_diary_domain_frames_policy.py — 16 focused tests: search_horizon field round-trips (None/same_day/advance), searched_no_candidates stays no_matching_times for all three horizon values (parametrised), policy predicates unchanged by horizon, roster_unavailable with no reason_code gets no_roster_row in schedule_reason_codes, roster_unavailable outcome always has schedule_explanation, explicit reason_code not clobbered by fallback, alias reason codes resolve through catalog, no_matching_times not emitted without a real slot_search frame, advisory-only frames never produce no_matching_times, legacy callers (no search_horizon) produce identical outcome to same_day callers.
- Verification run:
  - py_compile: app/services/diary/frames.py, app/services/diary/policy.py, tests/test_bernie_d4_diary_domain_frames_policy.py — all OK
  - pytest tests/test_bernie_d4_diary_domain_frames_policy.py -v: 16/16 passed
  - pytest tests/test_diary_schedule_explanations.py tests/test_bernie_booking_outcomes.py tests/test_bernie_context_frames.py -v: 58/58 passed (no regressions in adjacent suites)
  - git diff --check: clean
- Remaining risks:
  - Ariadne amendment applied: the original plan's "downgrade future-day empty searches to advisory" step was rejected and NOT implemented. This sprint adds only the search_horizon metadata field (no outcome logic change) and the roster gap fallback. Any future horizon-aware advisory routing remains out of scope pending a separate Ariadne-approved design.
  - route/frame builder (appointments.py) not updated: the amendment says "if straightforward" — adding search_horizon to the route requires determining how the route knows the horizon, which touches API layer concerns. Left for a follow-up if Ariadne decides it's worth a narrow targeted change.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-sprint-d4-diary-domain-frames-policy-foundation.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
