# claude-sprint-k1b-advisory-retrieval-route-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | superseded |
| Created | 736a9ce |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-k1b-advisory-retrieval-route-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-k1b-advisory-retrieval-route-contract --commit-message "Dispatch Sprint K1b Claude advisory retrieval plan" --message "claude-sprint-k1b-advisory-retrieval-route-contract ready for Codex review"` |

## Mission

Plan the backend/domain route contract for wiring the existing typed practice-knowledge substrate into Bernie responses as advisory retrieval only, so Bernie can surface safe practice facts or hints while deterministic diary/search/confirm state remains authoritative.

## Scope

### In Scope

app/services/practice_knowledge/; app/services/bernie or app/services/diary adapters that consume advisory facts; app/routers/appointments.py Bernie interpret/supervised response seams; schemas for advisory retrieval envelopes if needed; focused tests proving retrieval cannot set availability, policy hard blocks, confirm affordance, freshness/audit evidence, or write payloads.

### Out of Scope

Graph/vector store deployment; persisted PHI knowledge/session tables; auto-mode; broad API rewrite; taskpane/Command Centre changes; real PHI; using retrieval to decide slot truth, roster truth, confirmation, or writes.

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

Plan first only. Later implementation should run practice_knowledge tests, Bernie route/outcome/confirm/evidence tests, py_compile for touched Python, and git diff --check.

## Merge Criteria

Plan names the advisory envelope, route insertion point, boundary tests, PHI/provenance posture, and fail-closed behaviour when retrieval is unavailable or irrelevant.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
