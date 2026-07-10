# claude-fable-ariadne-harness-consultant-review

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | reviewed |
| Created | 278663de |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-fable-ariadne-harness-consultant-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-fable-ariadne-harness-consultant-review --commit-message "Fable Ariadne harness consultant review" --message "claude-fable-ariadne-harness-consultant-review ready for Codex review"` |

## Mission

Act as Claude Fable / high-reasoning consultant. Review docs/ariadne-multi-agent-ssdlc-harness-blueprint.md and the current AGENTS.md sidecar harness baton. Provide a rigorous implementation plan to progress the Ariadne harness successfully while preserving its core aim: deterministic control of the orchestrator, SSDLC governance, context rehydration, cross-platform portability, one-agent-to-many-agent role elasticity, and EMR4-first extraction later.

## Scope

### In Scope

Read-only consulting and planning. Scope is AGENTS.md, docs/ariadne-multi-agent-ssdlc-harness-blueprint.md, and any directly relevant orchestration protocol docs needed to understand current worker handoff. Produce an implementation-plan packet only: critique, risk register, milestone sequence, minimum viable implementation slice, tests/evidence, and go/no-go gates.

### Out of Scope

No production code, no tests, no runtime wiring, no live subagent adapter implementation, no GUI, no Omnigent integration, no provider calls, no database writes, no EMR4 clinical/runtime behavior changes, no branch movement to master or handoff/current, no broad refactors, no edits outside the plan packet and required coordination status.

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

Plan-only consultant review. Run git diff --check before submit if any coordination file is edited. No application tests required unless the worker chooses to run read-only/static checks.

## Merge Criteria

Codex can integrate the review as a consultant plan if it gives a concrete ordered implementation path, identifies boundary risks, preserves docs/tests-only first implementation, and names explicit gates before live agent adapters, GUI authority, Omnigent dependency, or EMR4 runtime use.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Fulfilled by an explicit read-only `claude-fable-5` consultant run. The durable
Codex-side review artifact is:
`orchestration/agent_inbox/codex/review-claude-fable-ariadne-harness-implementation-plan.md`.

- Files changed: coordination artifacts only.
- Verification run: explicit Fable read-only consultation completed; `git diff --check` passed before Codex-side commit.
- Remaining risks: the first Claude headless worker pass used Opus rather than the explicit Fable alias; the final committed review artifact preserves the explicit `claude-fable-5` pass as authoritative for this request.
