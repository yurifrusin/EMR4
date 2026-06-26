# claude-bernie-slot-normalize-endpoint-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | superseded |
| Created | f2e94f7 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-bernie-slot-normalize-endpoint-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-bernie-slot-normalize-endpoint-contract --commit-message "Bernie Slot Normalize Endpoint Contract" --message "claude-bernie-slot-normalize-endpoint-contract ready for Codex review"` |

## Mission

Plan first, then after approval expose the deterministic Bernie slot-search command normalizer through a narrow, non-mutating backend route/tool contract.

## Scope

### In Scope

Plan packet first; after approval add a role-gated/practice-scoped backend endpoint or route helper that accepts SlotSearchCommandIn, calls normalize_slot_search_command with an explicit deterministic reference date where needed, returns SlotSearchCommandResult, and adds focused tests for auth, shape, invalid input, non-mutation, no DB writes, no LLM/search execution, and compatibility with SlotSearchProposalIn.

### Out of Scope

Diary UI, taskpane, Command Centre, Gemini/LLM parsing, autonomous agent/tool execution, appointment creation, slot-search execution beyond normalizer invocation, audit mutation, SMS, billing, patient demographics, resource admin, migrations unless strictly unavoidable, and DB-backed name-to-UUID resolution.

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

Plan packet first; after approval py_compile touched backend modules/tests, focused pytest for the new normalize endpoint/route contract and existing normalizer tests, adjacent slot-search proposal tests if schemas/routes are touched, no DB/LLM/search execution proof, and git diff --check.

## Merge Criteria

Codex can verify the route/tool contract is deterministic, non-mutating, scoped, covered by focused tests, and compatible with the Sprint 38/39 Bernie pipeline without changing any visible UI or live appointment creation behavior.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: None by Claude for this sprint.
- Verification run: Not run by Claude. Claude hit a session/quota limit before plan submission.
- Remaining risks: Superseded by the Codex worker fallback on `codex/bernie-slot-normalize-endpoint`, integrated in Sprint 40.
