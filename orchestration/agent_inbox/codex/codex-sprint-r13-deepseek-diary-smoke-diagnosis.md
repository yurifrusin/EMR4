# codex-sprint-r13-deepseek-diary-smoke-diagnosis

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/sprint-r13-diary-smoke-diagnosis` |
| Status | integrated |
| Created | 137482c |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r13-deepseek-diary-smoke-diagnosis --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r13-deepseek-diary-smoke-diagnosis --commit-message "Sprint R13 DeepSeek Diary smoke failure diagnosis" --message "codex-sprint-r13-deepseek-diary-smoke-diagnosis ready for Codex review"` |

## Mission

Plan then diagnose the 12 unrelated Bernie session/pilot full Diary smoke failures observed during R12 closeout. Classify each failure as stale harness assumption, real regression, missing fixture state, or environment issue, and identify the smallest safe repair path.

## Scope

### In Scope

Plan gate first. After approval, read-only diagnosis plus a tangible artifact under docs/ or orchestration summarizing failing tests, likely root causes, implicated selectors/routes/session mocks, and recommended minimal fixes. Small non-overlapping diagnostic helper edits are allowed only if explicitly needed after plan approval.

### Out of Scope

Production behaviour changes, broad Diary UI redesign, backend route rewrites, deleting or weakening existing tests, live Gemini/Office/GitHub Pages calls, and any edits overlapping the focused-fix worker without Ariadne approval.

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

Run or cite the failing full Diary smoke command, focused individual failing tests where feasible, source inspection, git diff --check if files change.

## Merge Criteria

Ariadne can map each of the 12 failures to a specific cause and decide whether the focused-fix lane is safe to integrate.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: orchestration/sprint-r13-diary-smoke-diagnosis.md (diagnosis artifact)
- Verification run: Full diary smoke via `pytest review\test_diary_smoke.py -q --tb=short --junitxml=review/diary-review.xml` captured 12/12 failures; source inspection of diary.js:2460-2472 (isTokenExpired), diary.js:57-66 (shouldUseBernieServerSession), diary.js:3833-3835 (loadDiary early return), diary.js:5373-5374 (checkBerniePilotEligibility early return); validated JWT split length with Node REPL
- Remaining risks: Zero production code risk — the fix is a harness token value only. 13 occurrences to update. The dummy JWT has no `exp` field; if isTokenExpired logic changes to require exp, harness needs another update. R12 reason-code coverage is orthogonal and should survive unchanged.
