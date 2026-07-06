# codex-r29-action-grammar-adversarial-review

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/r29-action-grammar-adversarial-review` |
| Status | integrated |
| Created | c610e1de |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-r29-action-grammar-adversarial-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-r29-action-grammar-adversarial-review --commit-message "Dispatch R29 action grammar adversarial review" --message "codex-r29-action-grammar-adversarial-review ready for Codex review"` |

## Mission

Adversarial review for R29 native Bernie/Diary action grammar plan. Challenge overbroad grammar, hidden write authority, route compatibility risks, terminology drift, missing confirmation/evidence invariants, and whether H-series/full-trove concerns are being mixed into action grammar too early. Review/plan artifact only unless Ariadne later approves implementation.

## Scope

### In Scope

Read the R28 Fable full-trove readiness packet, AGENTS.md, protocol alerts, existing Bernie capability/session/policy/frames/temporal modules, appointments proposal/confirm routes, appointment schemas, and relevant tests. Produce a concise adversarial review artifact under docs/adversarial/ or a Codex plan packet with concrete risks and acceptance criteria.

### Out of Scope

Production code edits, frontend UI, raw trove/local_data, semantic labelling, provider calls, migrations, broad route rewrites, and master/handoff movement.

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

Review artifact inspection; if tests are proposed, describe exact focused tests but do not implement unless explicitly approved.

## Merge Criteria

Ariadne receives independent challenge before approving the R29 implementation plan.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: docs/adversarial/r29_action_grammar_adversarial_review.md (new adversarial review artifact, 18.7 KB, 210 lines, sections 0-10 covering overbroad grammar, hidden write authority, route compatibility risks, terminology drift, missing invariants, H-series boundary, concrete attack vectors, positive design requirements, adversarial questions, and verdict)
- Verification run: Source-safe review artifact inspection only per packet scope. No production code, tests, frontend, raw local_data, ignored JSON, migrations, or provider files touched. The artifact explicitly preserves: H15 closed, deterministic backend write authority, no trove content in grammar decisions, no semantic inference from neutral event classes.
- Remaining risks: recommended pre-merge gates are documented in section 10 (Literal die on writes_authorized, confirm-gate precondition on every confirm-tier action, zero H-series references, golden test). If the Claude implementation lane ignores any of the four gates, the grammar could introduce a parallel confirm-authority path or hidden write grant. The H15 semantic gate depends on Yuri approving a reviewed gate payload after the grammar and replay consumer exist - not before.
