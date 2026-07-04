# claude-sprint-d5-route-builder-search-horizon-threading

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | 1fce3b7 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-d5-route-builder-search-horizon-threading --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-d5-route-builder-search-horizon-threading --commit-message "Sprint D5 route builder search horizon threading" --message "claude-sprint-d5-route-builder-search-horizon-threading ready for Codex review"` |

## Mission

Implement a narrow backend-only D5 that threads the D4 metadata-only search_horizon field into BernieSlotSearchFrame where the appointment route/frame builder already has enough date context. Preserve outcome semantics: genuine searched_no_candidates remains no_matching_times regardless of horizon.

## Scope

### In Scope

Read _build_bernie_reception_context and callers in app/routers/appointments.py, app/services/diary/frames.py, policy/outcome tests. Add the smallest route/domain change to set search_horizon to same_day or advance when safe, or document why unknown remains necessary. Add focused tests proving route-built frames carry expected horizon and no outcome semantics change.

### Out of Scope

No frontend/UI/taskpane/diary.js. No GraphRAG. No persisted session tables/migrations. No broad API review. Do not downgrade future empty searched-no-candidates to advisory. Do not change user-facing copy.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Before editing project code, write an implementation plan and stop. The plan
   must be shown in the agent GUI and captured for Codex with the plan command
   above. Do not code until the user/Codex says `complete sprint task`.
5. After plan approval, work only inside the stated scope unless the user or Codex
   expands it.
6. Do not merge to `master`.
7. Do not move `handoff/current`.
8. Run the verification listed below.
9. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
10. Finish with the submit command above.

## Implementation Plan Requirements

Before coding, the implementation plan must include:

- My Understanding
- Intended Surface / Boundary
- Out of Scope
- Files I Expect To Edit
- Implementation Steps
- Visual / Behavioural Acceptance Checks
- Risks / Ambiguities

Pay special attention to visually loaded words such as cards, slots, stacking,
panels, waiting room, diary grid, booking slot, and status. State exactly which
surface is affected and which nearby surfaces must not change.

## Hard Stop Rules

- Do not push to `master` or `handoff/current`.
- Do not manually work around a failed protocol command (`handin`, `sync`, `submit`,
  `realign`, or related orchestration commands).
- Report every protocol-followed command back to Codex/orchestrator, whether it
  succeeds or fails. For success, include the command, working directory, branch,
  and short success result.
- If any protocol command refuses to run or fails, stop and report the exact command,
  working directory, branch, `git status --short --branch`, and error output to the
  orchestrator. On push failure, `submit` will also try to publish a
  `submit-alert/...` branch for Codex to poll.
- If these instructions conflict with remembered prior protocol, trust the current
  `handin` alerts and this task packet.

## Verification

py_compile touched files; focused pytest for new D5 tests plus D4 frame/policy tests, diary schedule explanation tests, Bernie booking outcome tests; git diff --check.

## Merge Criteria

Ariadne can integrate only if the change is additive, backend-bounded, preserves all current outcome semantics, and verifies route-built context frames without brittle UI dependencies.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - EDIT app/routers/appointments.py - added pure helper `_derive_search_horizon(reference_date, normalization) -> Optional[Literal["same_day","advance"]]` (derives same_day/advance/None by comparing normalization.constraint.date_from to reference_date; past dates and missing normalization/constraint -> None). In `_build_bernie_reception_context`, when `search_ran=True`, compute `_horizon` once at block entry and pass `search_horizon=_horizon` to the `searched_with_candidates` and `searched_no_candidates` BernieSlotSearchFrame construction sites only. The `not_run` and `blocked` frames are left at the default `None` because no search executed against a resolved date in those branches. No changes to policy/outcome/schedule_explanations modules.
  - NEW tests/test_bernie_d5_route_builder_search_horizon.py - 16 focused tests: `_derive_search_horizon` unit tests (same_day/advance/past->None/None normalization/no constraint); `_build_bernie_reception_context` frame-level tests proving searched_with_candidates and searched_no_candidates carry correct horizon (same_day/advance/None); not_run and blocked frames stay horizon=None; parametrized outcome test proving searched_no_candidates -> no_matching_times for all three horizon values with horizon assertion; policy-predicate stability across same_day vs advance.
- Verification run:
  - py_compile: app/routers/appointments.py, tests/test_bernie_d5_route_builder_search_horizon.py - both OK
  - pytest tests/test_bernie_d5_route_builder_search_horizon.py -v: 16/16 passed
  - pytest tests/test_bernie_d4_diary_domain_frames_policy.py tests/test_diary_schedule_explanations.py tests/test_bernie_booking_outcomes.py tests/test_bernie_context_frames.py -v: 74/74 passed (no regressions)
  - git diff --check: clean
- Remaining risks:
  - The Ariadne/Gemini amendment is fully applied: no policy/outcome code reads search_horizon. A genuine searched_no_candidates result stays no_matching_times for same_day, advance, and None horizons alike (parametrized test proves this).
  - Date-range searches (date_from..date_to spanning forward) are labelled by their start date; a range starting today reads as same_day. This is metadata-only and documented in the helper docstring.
  - Past date_from (date_from < reference_date) maps to None rather than a fabricated label; such requests should not arise for forward booking searches but are handled defensively.
