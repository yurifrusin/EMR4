# antigravity-sprint-n11-diary-roster-explanation-ux-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | e82a885 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-n11-diary-roster-explanation-ux-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-n11-diary-roster-explanation-ux-review --commit-message "Sprint N11 Diary roster explanation UX review" --message "antigravity-sprint-n11-diary-roster-explanation-ux-review ready for Codex review"` |

## Mission

Plan the Diary rendering changes needed to consume typed schedule/roster explanation outcomes without scripted or misleading copy, keeping Bernie friendly, familiar, and professional while not inventing booking truth.

## Scope

### In Scope

Plan first. docs/diary/diary.js, diary.css/html only if needed, review/test_diary_smoke.py. Focus on visible Bernie panel copy/state/rendering for roster unavailable, no matching times, advisory-only warnings, clarification, and stale conflict.

### Out of Scope

No production code before plan approval. No backend schema implementation except recommendations, no persisted sessions, GraphRAG, auto-mode, taskpane, Command Centre, broad UI redesign, or local UI-derived roster truth.

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

Plan must specify route-intercepted Diary smoke assertions for roster-unavailable copy from typed outcome, no false no-slot copy, advisory warning not blocking, stale conflict preserved, no confirm affordance from outcome alone, and no PHI in storage.

## Merge Criteria

Plan keeps Diary render-from-state/domain-truth, avoids patient-specific brittle copy, and makes old payload fallback safe.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: Plan phase only; Ariadne implemented the accepted UI slice in docs/diary/diary.js, docs/diary/diary.html, and review/test_diary_smoke.py.
- Verification run: Ariadne ran full deterministic Diary smoke plus focused backend/outcome suites; see orchestration/sprint_closeout.md.
- Remaining risks: Further natural-language roster detail remains future work once route payloads carry richer practitioner/date wording.
