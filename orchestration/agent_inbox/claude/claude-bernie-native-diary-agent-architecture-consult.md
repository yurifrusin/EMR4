# claude-bernie-native-diary-agent-architecture-consult

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 97c3ca8 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-bernie-native-diary-agent-architecture-consult --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-bernie-native-diary-agent-architecture-consult --commit-message "Bernie native diary agent architecture consult" --message "claude-bernie-native-diary-agent-architecture-consult ready for Codex review"` |

## Mission

Act as an external architecture consultant for EMR4. Review the current Bernie diary-agent direction and propose a concrete architectural path toward Bernie becoming a native agentic layer of the EMR4 diary domain rather than a chatbot bolted onto diary UI/API surfaces.

## Scope

### In Scope

Architecture only: diary native capability model, event/state model, bounded backend domain module, capability/action grammar, deterministic scheduling and roster authority, Bernie conversational/reasoning responsibilities, guardrail/state-machine responsibilities, UI state rendering responsibilities, migration path from current Sprint 104-107 code, and where GraphRAG or knowledge-graph techniques do or do not belong for Bernie, Rayleen, Scribe, Consultant, and Davida.

### Out of Scope

Do not implement production code. Do not launch a sprint implementation. Do not edit app runtime files. Do not propose replacing deterministic diary slot/roster logic with LLM or GraphRAG decisions. Do not move master or handoff/current.

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

Submit a written architecture review/plan packet to Codex's inbox. It must include concrete phases, first implementation sprint recommendation, risks, migration strategy, and explicit boundaries between deterministic diary logic, Bernie-authored natural language, transition/state policy, and graph/retrieval layers.

## Merge Criteria

Codex/Ariadne can review the plan packet, compare it to EMR4 handover/protocol documents, and discuss it with Yuri before any implementation work is authorized.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
