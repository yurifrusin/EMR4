# claude-bernie-bounded-domain-extraction-foundation

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 671883f |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-bernie-bounded-domain-extraction-foundation --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-bernie-bounded-domain-extraction-foundation --commit-message "Bernie bounded domain extraction foundation" --message "claude-bernie-bounded-domain-extraction-foundation ready for Codex review"` |

## Mission

Implement the approved first slice of the Fable 5 Bernie architecture plan: extract Bernie backend-domain code toward a bounded app/services/bernie package and define persistence-shaped session/event contracts without introducing a database session table yet. Preserve existing external JSON/API behaviour and diary UI behaviour.

## Scope

### In Scope

Create or update app/services/bernie/ modules as needed for domain boundaries. Move or wrap existing pure/backend Bernie logic behind bounded modules where low-risk: interpreter facade, patient booking context alias/wrapper, slot normalizer alias/wrapper, temporal/session/event contract scaffolding, capability/tool registry skeleton. Update imports minimally. Add focused tests proving the new domain modules exist and do not change current interpreter/supervised booking/slot-search behaviour. Coordination notes may be updated if needed.

### Out of Scope

No persisted Bernie session table, no Alembic migration, no diary UI refactor, no frontend render-from-server-state migration, no typed context-frame enforcement yet, no API response breaking changes, no autonomous booking, no live provider behaviour changes, no broad app/routers/appointments.py rewrite beyond safe import/wrapper extraction, no deletion of existing sprint-named tests.

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

Run py_compile on touched backend modules; run focused Bernie backend suites including tests/test_bernie_interpret_booking_instruction.py, tests/test_bernie_supervised_booking_wrapper.py, tests/test_bernie_no_slot_suggestions.py, tests/test_bernie_sprint104_state_memory.py, tests/test_bernie_turn_contract.py, tests/test_slot_search_proposal.py; run git diff --check. If scope grows or tests expose larger router surgery, stop and report rather than expanding unilaterally.

## Merge Criteria

No production behaviour regression; existing public JSON contracts remain compatible; app/services/bernie has a clear domain boundary and persistence-shaped session/event contract ready for later Sprint C; Ariadne can review the diff without large unrelated rewrites; all listed verification passes or failures are clearly explained.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
