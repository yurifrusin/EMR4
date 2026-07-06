# claude-fable-100-sprint-strategy-map

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | 299e0a28 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-fable-100-sprint-strategy-map --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-fable-100-sprint-strategy-map --commit-message "Fable 100-Sprint Strategy Map" --message "claude-fable-100-sprint-strategy-map ready for Codex review"` |

## Mission

Act as Fable, a high-reasoning Claude strategy collaborator for Ariadne. Review the recent EMR4 state and propose the best next roughly 100 or greater sprints, with adaptation checkpoints and explicit sequencing rationale. Produce a plan/review artifact only; do not implement code.

## Scope

### In Scope

Read AGENTS.md, implementation_plan.md, orchestration/phase_programmes.md, orchestration/sprint_closeout.md current H69 closeout, orchestration/parallel_workstreams.md next-sprint section, orchestration/api_spine_programme.md, orchestration/access_ai_api_design.md, orchestration/bernie_release_gates.md, and relevant recent H-series/Bernie/Access AI/API-spine notes as needed. Map sprint bands across active programmes, identify dependencies/gates, name first 5-10 concrete tactical sprints, call out adaptation checkpoints at least every 10 sprints and on major gate failures, and identify where stale inbox/Claude residue cleanup fits as an enabling stream.

### Out of Scope

No production code changes, no runtime route/provider/database/UI implementation, no broad historical diary trove processing, no H15/H-series runtime imports, no memory/RAG/GraphRAG wiring, no provider calls, no raw/ignored local-data reads, no committing generated strategy as final Ariadne synthesis.

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

Plan artifact exists under orchestration/agent_inbox/codex/ or docs/orchestration as directed by protocol; git diff --check on changed markdown; no app/, tests/, scripts/, provider, database, UI, or local_data files changed.

## Merge Criteria

Ariadne can synthesize the artifact into a durable 100+ sprint strategy map that preserves blocked runtime/provider/trove boundaries, includes explicit checkpoints, and gives a clear first tactical band without mistaking cleanup for the main strategy objective.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: Fable review integrated from clean strategy worktree branch
  `claude/fable-100-sprint-strategy-map` as
  `orchestration/agent_inbox/codex/review-claude-fable-100-sprint-strategy-map.md`;
  Ariadne synthesis recorded in
  `orchestration/ariadne_fable_100_sprint_strategy_map.md`.
- Verification run: Fable branch reported `git diff --check` exit 0; Ariadne
  still needs final diff hygiene after synthesis edits.
- Remaining risks: This strategy map is directional, not approval to open live
  providers, historical diary trove mining, H15/H-series runtime imports,
  memory/RAG/GraphRAG, or database-write authority.
