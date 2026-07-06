# claude-sprint108-bernie-access-ai-backend-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/sprint108-bernie-access-ai-backend` |
| Status | superseded |
| Created | f781b969 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint108-bernie-access-ai-backend-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint108-bernie-access-ai-backend-contract --commit-message "Sprint 108 Bernie Access AI backend contract" --message "claude-sprint108-bernie-access-ai-backend-contract ready for Codex review"` |

## Mission

Plan and then implement the minimal backend/API hardening needed so Bernie booking-instruction interpretation is unambiguously routed through Access AI for live/provider-capable paths while disabled/fake paths remain local, default-disabled, no-write, and staff-confirmation safe.

## Scope

### In Scope

Inspect app/services/bernie_booking_interpreter.py, app/routers/appointments.py, Access AI service/audit/entitlement contracts, and tests/test_bernie_interpret_booking_instruction.py. Add focused tests and small code changes only if needed to prove: live/provider-capable interpretation uses AccessAiService; Access AI audit metadata is persisted only for provider-capable invocation; disabled/fake modes call no provider and write no Access AI audit rows; route performs no slot search/proposal/confirmation/appointment mutation; raw instruction/provider payload is not logged in audit metadata.

### Out of Scope

No live provider enablement, no production GCP/ADC changes, no autonomous booking writes, no appointment proposal/confirm route rewrites, no GraphQL mutations, no database migrations except if a test proves an already-reviewed audit schema bug, no H15/trove, no memory/RAG/GraphRAG, no UI files.

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

py_compile touched Python files; pytest tests/test_bernie_interpret_booking_instruction.py tests/test_access_ai_service.py tests/test_ai_audit_events.py -q; git diff --check.

## Merge Criteria

Backend contract remains additive and default-disabled; focused tests prove provider-capable path crosses Access AI and disabled/fake paths stay local/no-write/no-audit; no blocked gate opens.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `orchestration/agent_inbox/codex/plan-claude-claude-sprint108-bernie-access-ai-backend-contract.md`
- Verification run:
  - Claude plan accepted by Ariadne; no Claude implementation was requested after
    DeepSeek covered the accepted backend test gaps.
- Remaining risks:
  - None for this lane. The source task is superseded only to avoid same-file
    overlap with the integrated DeepSeek backend hardening lane.
