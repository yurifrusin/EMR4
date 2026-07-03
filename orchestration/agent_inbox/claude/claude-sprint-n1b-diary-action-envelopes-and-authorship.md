# claude-sprint-n1b-diary-action-envelopes-and-authorship

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | superseded |
| Created | c3385e4 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-n1b-diary-action-envelopes-and-authorship --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-n1b-diary-action-envelopes-and-authorship --commit-message "Sprint N1b diary action envelopes and authorship" --message "claude-sprint-n1b-diary-action-envelopes-and-authorship ready for Codex review"` |

## Mission

Implement amended N1b: add internal diary action envelopes, multi-author suggestion semantics, authorship metadata on diary action catalog entries, and deterministic boundary tests while preserving runtime behaviour.

## Scope

### In Scope

app/services/diary/ action envelope contracts only: DiaryActionIntent, DiaryActionProposal, DiaryActionConfirmation, DiaryActionSuggestion; author/channel enums; allowed_authors metadata on catalog entries; catalog completeness/authorship tests; temporal single-source tests; availability-provenance adversarial tests over evaluate_reception_context; suggestion-cannot-mutate tests at the contract layer. Keep existing API/JSON/UI behaviour unchanged.

### Out of Scope

No endpoint rewiring, no unified confirm path, no HMAC evidence changes, no migrations, no persisted sessions, no GraphRAG/K1 knowledge substrate, no UI/copy changes, no auto-mode, no route mutation behaviour changes.

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

Run focused diary/bernie domain tests, new envelope/authorship/boundary tests, focused reception_policy smoke if relevant, compileall, git diff --check. Existing public API payloads must remain unchanged.

## Merge Criteria

Internal contracts and tests only, no behaviour change, ready for N2/N3 future implementation.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: none by Claude. Claude remained in session-limit cooldown.
  Ariadne/Codex completed the N1b implementation from the accepted architecture
  plan.
- Verification run: see Sprint N1b closeout.
- Remaining risks: none from the skipped Claude lane.
