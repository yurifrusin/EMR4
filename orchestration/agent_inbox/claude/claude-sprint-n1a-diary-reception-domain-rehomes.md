# claude-sprint-n1a-diary-reception-domain-rehomes

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | accepted |
| Created | d76f100 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-n1a-diary-reception-domain-rehomes --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-n1a-diary-reception-domain-rehomes --commit-message "Sprint N1a diary reception domain rehomes" --message "claude-sprint-n1a-diary-reception-domain-rehomes ready for Codex review"` |

## Mission

Implement amended N1a: create the native app/services/diary/ reception domain package and rehome the pure diary/reception modules from app/services/bernie/ without behaviour change.

## Scope

### In Scope

Pure moves/facades only: rehome the action/capability catalog, canonical temporal policy, reception context frames, and deterministic reception policy into app/services/diary/; leave app/services/bernie/ compatibility facades so existing imports still work; keep wire strings reception_policy and bernie.reception_context.v1 byte-identical; update imports only where safe; add/adjust tests only to prove facade identity and byte-identical contract preservation.

### Out of Scope

No action envelopes, no allowed_authors, no suggestion semantics, no GraphRAG/knowledge substrate, no migrations, no UI changes, no copy changes, no route behaviour changes, no auto-mode.

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

Run focused backend tests for Bernie/diary domain package, context frames, interpreter, temporal policy; run any import/facade identity tests added; run git diff --check. Behaviour and JSON contracts must be unchanged.

## Merge Criteria

Pure rehome/facade implementation with passing focused tests and no runtime/UI behaviour changes; ready for Ariadne integration before N1b.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
