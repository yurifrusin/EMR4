# claude-revise-bernie-native-diary-plan-with-ariadne-yuri-amendments

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | c1589b5 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-revise-bernie-native-diary-plan-with-ariadne-yuri-amendments --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-revise-bernie-native-diary-plan-with-ariadne-yuri-amendments --commit-message "Revise Bernie native diary plan with Ariadne Yuri amendments" --message "claude-revise-bernie-native-diary-plan-with-ariadne-yuri-amendments ready for Codex review"` |

## Mission

Review Fable's Bernie native diary agent architecture consult together with Ariadne/Yuri amendment notes, then produce a revised implementation-ready architecture plan for the first sprint sequence. This is a plan revision and stress-test, not an implementation sprint.

## Scope

### In Scope

Read the original Fable plan packet, orchestration/bernie_native_diary_agent_notes.md, and relevant handover/protocol docs. Address three amendments: move reception frames and deterministic reception policy into the new diary/reception domain in amended N1; treat suggested next actions as multi-author human/agent conversational inputs that must normalize to typed DiaryActionIntent before validation/mutation; reconsider GraphRAG timing in light of Yuri's counterargument that Bernie may be the safest low-risk proving ground for EMR4's graph/retrieval substrate because its knowledge base is simple and verifiable. Produce a revised concrete sprint path, especially N1/N2, with boundaries, risks, and acceptance checks.

### Out of Scope

Do not implement production code. Do not edit app runtime files, tests, migrations, docs outside orchestration plan/review packets, or UI assets. Do not move master or handoff/current. Do not authorize implementation without Yuri/Ariadne approval.

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

Submit a revised architecture plan packet to Codex's inbox. It must clearly state whether Fable accepts, modifies, or rejects each amendment; provide an implementation-ready N1 recommendation; explain GraphRAG/testbed implications; and preserve deterministic diary authority over availability and mutations.

## Merge Criteria

Codex/Ariadne and Yuri can review the revised packet and decide whether to dispatch the first implementation sprint.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
