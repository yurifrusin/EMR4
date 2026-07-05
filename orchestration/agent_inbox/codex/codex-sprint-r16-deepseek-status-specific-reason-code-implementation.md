# codex-sprint-r16-deepseek-status-specific-reason-code-implementation

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | queued |
| Created | 07a33fd |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r16-deepseek-status-specific-reason-code-implementation --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r16-deepseek-status-specific-reason-code-implementation --commit-message "Sprint R16 DeepSeek status-specific reason-code implementation" --message "codex-sprint-r16-deepseek-status-specific-reason-code-implementation ready for Codex review"` |

## Mission

Implement status-specific first-party Diary reason-code filtering on top of R15: Cancelled, DNA, and NoShow should receive narrower option lists while PATIENT_UNWELL remains display-only and never selectable.

## Scope

### In Scope

docs/diary/diary.js, docs/diary/diary.html only if cache-bust/static fallback changes are needed, and review/test_diary_smoke.py for targeted verification.

### Out of Scope

No backend changes. Do not remove stored-value label compatibility for PATIENT_UNWELL. Do not touch unrelated Diary flows, Bernie, waiting room, or audit history.

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

Run node --check docs/diary/diary.js and focused pytest -k reason_code; specify full smoke need if visible behaviour changes.

## Merge Criteria

Submit plan first; after approval submit a narrow diff or exact patch notes with verification.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
