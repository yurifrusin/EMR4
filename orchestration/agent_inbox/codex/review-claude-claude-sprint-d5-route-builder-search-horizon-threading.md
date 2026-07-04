# review-claude-claude-sprint-d5-route-builder-search-horizon-threading

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-d5-route-builder-search-horizon-threading` |
| Status | queued |

## Review Request

claude-sprint-d5-route-builder-search-horizon-threading ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - EDIT app/routers/appointments.py — added pure helper `_derive_search_horizon(reference_date, normalization) -> Optional[Literal["same_day","advance"]]` (derives same_day/advance/None by comparing normalization.constraint.date_from to reference_date; past dates and missing normalization/constraint → None). In `_build_bernie_reception_context`, when `search_ran=True`, compute `_horizon` once at block entry and pass `search_horizon=_horizon` to the `searched_with_candidates` and `searched_no_candidates` BernieSlotSearchFrame construction sites only. The `not_run` and `blocked` frames are left at the default `None` because no search executed against a resolved date in those branches. No changes to policy/outcome/schedule_explanations modules.
  - NEW tests/test_bernie_d5_route_builder_search_horizon.py — 16 focused tests: `_derive_search_horizon` unit tests (same_day/advance/past→None/None normalization/no constraint); `_build_bernie_reception_context` frame-level tests proving searched_with_candidates and searched_no_candidates carry correct horizon (same_day/advance/None); not_run and blocked frames stay horizon=None; parametrized outcome test proving searched_no_candidates → no_matching_times for all three horizon values with horizon assertion; policy-predicate stability across same_day vs advance.
- Verification run:
  - py_compile: app/routers/appointments.py, tests/test_bernie_d5_route_builder_search_horizon.py — both OK
  - pytest tests/test_bernie_d5_route_builder_search_horizon.py -v: 16/16 passed
  - pytest tests/test_bernie_d4_diary_domain_frames_policy.py tests/test_diary_schedule_explanations.py tests/test_bernie_booking_outcomes.py tests/test_bernie_context_frames.py -v: 74/74 passed (no regressions)
  - git diff --check: clean
- Remaining risks:
  - The Ariadne/Gemini amendment is fully applied: no policy/outcome code reads search_horizon. A genuine searched_no_candidates result stays no_matching_times for same_day, advance, and None horizons alike (parametrized test proves this).
  - Date-range searches (date_from..date_to spanning forward) are labelled by their start date; a range starting today reads as same_day. This is metadata-only and documented in the helper docstring.
  - Past date_from (date_from < reference_date) maps to None rather than a fabricated label; such requests should not arise for forward booking searches but are handled defensively.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-sprint-d5-route-builder-search-horizon-threading.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
