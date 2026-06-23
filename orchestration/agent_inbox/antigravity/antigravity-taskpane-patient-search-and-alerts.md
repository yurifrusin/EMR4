# antigravity-taskpane-patient-search-and-alerts

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | 1c7ad58 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-taskpane-patient-search-and-alerts --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-taskpane-patient-search-and-alerts --commit-message "Improve taskpane patient search and alerts" --message "Taskpane patient search and alert clarity ready for Codex review"` |

## Mission

Tighten the taskpane patient workflow around duplicate-safe searching and save-error visibility, especially where full-name search and patient detail alerts currently feel confusing.

## Scope

### In Scope

Taskpane HTML/JS/CSS only. Investigate and fix full-name patient search such as 'alice alston' returning no results when partial first-name search works. Improve patient details save-failure feedback so the user sees failure near the action area even when scrolled down. Keep the dark blue patient header as the visual divider; do not redesign the whole taskpane.

### Out of Scope

No backend API changes, no diary changes, no patient merge/delete implementation, no Command Centre redesign.

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

Run JS syntax checks, bump taskpane cache version, and provide manual verification steps for full-name search, duplicate-save failure visibility, and normal patient detail save.

## Merge Criteria

Search behaviour is more forgiving, save failures are obvious without scrolling, visual changes remain scoped to the taskpane patient workflow, and existing taskpane actions still work.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
