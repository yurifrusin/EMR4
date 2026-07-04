# claude-sprint-d4-diary-domain-frames-policy-foundation

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | 8f0468b |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-d4-diary-domain-frames-policy-foundation --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-d4-diary-domain-frames-policy-foundation --commit-message "Sprint D4 diary domain frames policy foundation" --message "claude-sprint-d4-diary-domain-frames-policy-foundation ready for Codex review"` |

## Mission

Plan and then, after Ariadne approval, implement a narrow backend diary-domain sprint that strengthens Bernie as a native diary-domain receptionist copilot. Focus on existing app/services/diary frames, policy, outcomes, patient booking context, roster/schedule explanation, and tests. The sprint must avoid UI changes and avoid GraphRAG/persisted-session/broad API rewrites.

## Scope

### In Scope

Read existing app/services/diary modules and Bernie compatibility facades; identify the smallest missing domain-layer capability that addresses Yuri's recent concern: future patient bookings should be advisory unless same requested day/window, roster/schedule unavailability should explain itself, and no-candidates copy must only be allowed after a real slot search. Propose concrete files/tests, then wait at the plan gate.

### Out of Scope

No frontend/taskpane/diary.js changes. No GraphRAG/vector store. No persisted Bernie database sessions. No broad API review. No Fable/high-cost model unless explicitly requested. No master/handoff movement.

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

Focused pytest for the diary-domain policy/outcome/frame tests plus any new tests; py_compile touched files; git diff --check.

## Merge Criteria

Ariadne can integrate only if the change is backend-domain bounded, preserves current API contracts, strengthens typed frame/policy semantics, and has passing focused tests.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - EDIT app/services/diary/frames.py - added optional `search_horizon: Literal["same_day", "advance"] | None = None` to `BernieSlotSearchFrame`. Metadata-only; no outcome logic reads it. Comment explicitly records Ariadne amendment: a real searched_no_candidates result stays no_matching_times regardless of horizon.
  - EDIT app/services/diary/policy.py - added roster gap fallback in `evaluate_reception_context`: when a `roster_schedule` frame has `status == "unavailable"` and no `reason_code`, `add_reason("no_roster_row")` is called so `schedule_reason_codes` always carries at least one self-explaining entry. No change for frames that already carry an explicit `reason_code`.
  - NEW tests/test_bernie_d4_diary_domain_frames_policy.py - 16 focused tests: search_horizon field round-trips (None/same_day/advance), searched_no_candidates stays no_matching_times for all three horizon values (parametrised), policy predicates unchanged by horizon, roster_unavailable with no reason_code gets no_roster_row in schedule_reason_codes, roster_unavailable outcome always has schedule_explanation, explicit reason_code not clobbered by fallback, alias reason codes resolve through catalog, no_matching_times not emitted without a real slot_search frame, advisory-only frames never produce no_matching_times, legacy callers (no search_horizon) produce identical outcome to same_day callers.
- Verification run:
  - py_compile: app/services/diary/frames.py, app/services/diary/policy.py, tests/test_bernie_d4_diary_domain_frames_policy.py - all OK
  - pytest tests/test_bernie_d4_diary_domain_frames_policy.py -v: 16/16 passed
  - pytest tests/test_diary_schedule_explanations.py tests/test_bernie_booking_outcomes.py tests/test_bernie_context_frames.py -v: 58/58 passed (no regressions in adjacent suites)
  - git diff --check: clean
- Remaining risks:
  - Ariadne amendment applied: the original plan's "downgrade future-day empty searches to advisory" step was rejected and NOT implemented. This sprint adds only the search_horizon metadata field (no outcome logic change) and the roster gap fallback. Any future horizon-aware advisory routing remains out of scope pending a separate Ariadne-approved design.
  - route/frame builder (appointments.py) not updated: the amendment says "if straightforward" - adding search_horizon to the route requires determining how the route knows the horizon, which touches API layer concerns. Left for a follow-up if Ariadne decides it's worth a narrow targeted change.

## Codex Integration Outcome

Integrated by Ariadne in Sprint D4 at `22d1aa0` after rejecting the risky future-empty-search downgrade from the original plan. Focused verification passed locally before master push.
