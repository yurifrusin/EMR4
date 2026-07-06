# claude-r28-fable-full-trove-readiness-review

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/fable-full-trove-readiness` |
| Status | integrated |
| Created | 374006cf |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-r28-fable-full-trove-readiness-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-r28-fable-full-trove-readiness-review --commit-message "Dispatch Fable full-trove readiness review" --message "claude-r28-fable-full-trove-readiness-review ready for Codex review"` |

## Mission

Claude Fable consult: review the post-R27 H-series profile layer and advise when EMR4 should use the full local diary trove, whether H15 semantic-gate work is ready, and what architecture should govern source-safe aggregate/profile refreshes, GraphRAG-shaped derived memory, and Bernie/Diary action grammar. Produce a plan/review packet only; do not edit production code.

## Scope

### In Scope

Read AGENTS.md, docs/h-series-profile-schema.md, docs/historical-diary-trove-plan.md, docs/historical-diary-trove-semantic-labelling-gate.md, relevant H-series docs, orchestration/protocol_alerts.md, orchestration/phase_programmes.md, orchestration/parallel_workstreams.md, orchestration/sprint_closeout.md, and the R27 review artifacts. Write a Claude/Fable plan packet or review artifact under orchestration/agent_inbox/codex only via the protocol plan/submit path.

### Out of Scope

Production code, tests, raw local_data, ignored JSON, semantic appointment labelling, provider calls, frontend UI, migrations, master/handoff movement, and any broad trove processing.

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

Plan/review artifact only; no production tests required. Must explicitly preserve no raw trove to LLM/provider, no fine-tuning on raw diary files, H15 closed unless Yuri approves, and deterministic backend write authority.

## Merge Criteria

Ariadne receives a high-reasoning Fable recommendation on the full-trove readiness gate, Fable timing, GraphRAG/derived-memory boundary, and next 2-4 sprint direction without code changes.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/agent_inbox/codex/plan-claude-claude-r28-fable-full-trove-readiness-review.md` (Fable readiness review captured via the protocol plan command, then expanded in place with the full review body); this task packet (status + these notes). No production code, tests, fixtures, raw local_data, ignored JSON, frontend, migrations, or provider files touched.
- Verification run: plan/review artifact only per packet; `git diff --check` clean. The review explicitly preserves: no raw trove to LLM/external provider, no fine-tuning on raw diary files, H15 closed unless Yuri approves a reviewed gate payload, and deterministic backend write authority.
- Remaining risks: recommendation defers broad trove processing and H15 opening behind native action grammar + replay consumer + H22 gate packet; if Ariadne/Yuri disagree with that ordering, the alternative paths and their rejection reasons are recorded in the packet's Risks section. Fable access lapses end of 2026-07-07, so this packet must stand as the durable decision framework without a follow-up Fable pass.
