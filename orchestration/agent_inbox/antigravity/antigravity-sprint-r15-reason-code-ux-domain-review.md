# antigravity-sprint-r15-reason-code-ux-domain-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 828c3ee |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-r15-reason-code-ux-domain-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-r15-reason-code-ux-domain-review --commit-message "Sprint R15 reason-code UX/domain review" --message "antigravity-sprint-r15-reason-code-ux-domain-review ready for Codex review"` |

## Mission

Review Sprint R15 first-party Diary reason-code UX polish for receptionist safety, privacy, and taxonomy clarity. Focus on contextual dropdown options and the PATIENT_UNWELL privacy risk.

## Scope

### In Scope

docs/diary/diary.html, docs/diary/diary.js, docs/diary/diary.css, review/test_diary_smoke.py, docs/receptionist_review_r11.md, docs/receptionist_review_r12.md, and a new docs/receptionist_review_r15.md review artifact.

### Out of Scope

Do not implement production code in the plan gate. Do not change backend schemas or migrations. Do not broaden the taxonomy beyond first-party cancellation/status UI.

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

Plan must specify concrete reviewer checks for dropdown filtering, privacy copy, no PATIENT_UNWELL selectable in first-party UI, and existing reason-code smoke preservation.

## Merge Criteria

Submit a plan/review packet and docs/receptionist_review_r15.md with actionable acceptance criteria that Ariadne can integrate.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: docs/receptionist_review_r15.md
- Verification run: Internal review of existing receptionist guidelines (docs/receptionist_review_r11.md, docs/receptionist_review_r12.md), HTML elements in docs/diary/diary.html, JS logic in docs/diary/diary.js, and verification of review/test_diary_smoke.py Playwright assertions.
- Remaining risks: No production code changes were implemented (PLAN/REVIEW ONLY). The developer implementing this must ensure removing PATIENT_UNWELL from first-party UI does not break API paths or telemetry, and verify that the smoke tests continue to pass when options are filtered.
