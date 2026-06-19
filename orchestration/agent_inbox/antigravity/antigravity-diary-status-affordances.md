# antigravity-diary-status-affordances

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | 62cfeaa |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-status-affordances --commit-message "Refine diary status affordances" --message "Diary status affordances ready for Codex review"` |

## Mission

Improve the read-only diary so appointment lifecycle/status is easier to scan as patient-flow visibility, without adding status mutation controls.

## Scope

### In Scope

Edit docs/diary/diary.html, docs/diary/diary.css, and docs/diary/diary.js only. Build on the existing appointment.status rendering and colored left-border accent. Make statuses like Confirmed, Arrived, InConsult, Completed, Cancelled/NoShow/DNA visually distinct but restrained. Prefer a clear colored bar/status accent system over chevrons. Preserve date picker, Now marker, roster-driven columns, smoke mode, long appointments, booking notes, narrow layout, and read-only behavior. Update smoke fixtures only if useful for visual coverage. Bump diary cache version if diary assets change. Fill Completion Notes before submit.

### Out of Scope

Do not edit backend app files, tests except tiny smoke fixture notes, taskpane, Command Centre, Gemini/AI code, booking create/edit/delete/drag/drop, or status update controls. Do not introduce clickable status mutation behavior.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Work only inside the stated scope unless the user or Codex expands it.
5. Do not merge to `master`.
6. Do not move `handoff/current`.
7. Run the verification listed below.
8. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
9. Finish with the submit command above.

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

Run node --check docs\diary\diary.js. Manually smoke-test or describe browser checks for live/smoke/narrow views: statuses are readable, appointment text remains legible, date picker/Now/Refresh still work, and no mutation UI appears.

## Merge Criteria

Diary status/readiness is easier to scan in read-only mode; existing lifecycle styling is preserved or improved; no booking/status mutation behavior is introduced; changes are scoped to docs/diary with cache-bust updated if needed.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
