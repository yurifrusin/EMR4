# claude-bernie-reception-domain-copilot-architecture-consult

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 1389579 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-bernie-reception-domain-copilot-architecture-consult --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-bernie-reception-domain-copilot-architecture-consult --commit-message "Bernie reception-domain copilot architecture consult" --message "claude-bernie-reception-domain-copilot-architecture-consult ready for Codex review"` |

## Mission

Plan-only consulting sprint. Review EMR4's current Bernie implementation as a reception-domain-specific copilot agent: interpreter, patient booking context, slot search, roster/schedule diagnostics, diary UI state machine, chat turns, transition/render guards, and tests. Produce a senior architectural implementation plan for the right way forward. Treat Claude Fable 5 as the consulting model for planning. Do not implement production code in this phase.

## Scope

### In Scope

Read and analyse AGENTS.md, orchestration/protocol_alerts.md, orchestration/parallel_workstreams.md, orchestration/sprint_closeout.md, orchestration/event_driven_statechart_architecture.md, orchestration/bernie_interaction_model.md, app/services/bernie_booking_interpreter.py, app/services/bernie_patient_context.py, app/services/bernie_slot_normalizer.py, app/routers/appointments.py, app/schemas/appointments.py, docs/diary/diary.js, docs/diary/diary.html, docs/diary/diary.css, review/test_diary_smoke.py, tests/test_bernie_*.py, tests/test_slot_search_proposal.py. Plan the domain-agent architecture, typed tools/facts, state machine boundaries, UI response voice, roster/schedule diagnostics, and test strategy.

### Out of Scope

No production code edits, no migrations, no UI changes, no backend route/schema changes, no broad root-to-branch API rewrite, no autonomous booking implementation, no live PHI, no Google/Vertex/OpenAI implementation changes, no direct booking mutation without staff confirmation. Do not run implementation after the plan. Stop after submitting the plan packet so Ariadne and Yuri can review it together.

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

Plan packet must include: diagnosis of current failure modes; proposed receptionist-domain capability/tool map; event/statechart boundaries; backend contract changes; UI response/copy strategy; test plan; migration/sprint breakdown; risks/dissent; explicit pause-before-execution note. Worker must run no production-code tests unless needed for read-only evidence; no production code changes are permitted.

## Merge Criteria

Ariadne reviews Claude/Fable 5 plan for architectural fit, safety, determinism, and implementation scope. Yuri reviews the plan with Ariadne before any implementation release. Implementation may proceed only after explicit Yuri approval and a separate 'complete sprint task' instruction.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
