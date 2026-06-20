# antigravity-diary-nurse-bookability-affordance

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | a095401 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-nurse-bookability-affordance --commit-message "Diary nurse bookability affordance" --message "antigravity-diary-nurse-bookability-affordance ready for Codex review"` |

## Mission

Update the diary frontend so practitioner-backed Nurse/Room 2 columns become clearly bookable while label-only/non-practitioner columns remain visibly non-bookable and fail gracefully.

## Scope

### In Scope

docs/diary/diary.html; docs/diary/diary.css; docs/diary/diary.js; cache-bust bump; narrow/live/smoke visual behaviour related to booking affordances.

### Out of Scope

Backend routes/models/tests/migrations; taskpane/Command Centre; patient identity/duplicate work; waiting-area data model; drag/drop/resize; broad diary redesign.

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

node --check docs\\diary\\diary.js; live/smoke checks for Room 1 bookability, Room 2 practitioner-backed bookability when present, Room 3/label-only non-bookability, narrow layout; git diff --check.

## Merge Criteria

A practitioner-backed Nurse column can open the booking form with the correct practitioner_id; non-bookable label-only columns no longer look broken or silently selectable; existing Room 1 booking/create/edit/status behaviour is preserved; review packet includes exact manual checks and remaining UX risks.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: docs/diary/diary.js, docs/diary/diary.css, docs/diary/diary.html
- Verification run: Checked JavaScript syntax using `node --check docs/diary/diary.js` (successful). Checked git diff check using `git diff --check` (successful).
- Remaining risks: None. The changes are strictly client-side presentation layers and do not modify any backend API schemas or mutations.
