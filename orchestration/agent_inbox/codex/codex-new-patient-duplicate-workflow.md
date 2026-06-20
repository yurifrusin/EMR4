# codex-new-patient-duplicate-workflow

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/new-patient-duplicate-workflow` |
| Status | queued |
| Created | 90a951f |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-new-patient-duplicate-workflow --commit-message "Harden new patient duplicate workflow" --message "New Patient duplicate workflow ready for Codex review"` |

## Mission

Harden New Patient creation around duplicate candidates and modal usability. Add a proper duplicate-warning step using the existing duplicate-candidates API and ensure the form has clear cancel/escape/success paths.

## Scope

### In Scope

EMR4 Sidebar/src/taskpane/taskpane.html, EMR4 Sidebar/src/taskpane/taskpane.css, EMR4 Sidebar/src/taskpane/taskpane.js, docs/taskpane mirrored files via sync_taskpane.py, focused patient/taskpane-adjacent tests or static checks if available.

### Out of Scope

Diary frontend, appointment patient-link backend, Command Centre clinical coding, OneDrive import tooling, ADHA/IHI live integration, OCR.

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

Run node --check on taskpane JS source and docs copy, git diff --check, sync_taskpane.py if taskpane source changes, and any focused patient tests if backend is touched. Include exact commands/results in the Codex review packet.

## Merge Criteria

New Patient modal can be cancelled/escaped, duplicate candidates are surfaced as a warning/confirm step before creation, successful creation gives clear next action, and docs/taskpane mirror is updated if source changes.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
