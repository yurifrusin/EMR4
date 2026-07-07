# antigravity-sprint152-create-proposal-client-compatibility

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | a3783d74 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint152-create-proposal-client-compatibility --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint152-create-proposal-client-compatibility --commit-message "Sprint 152 create-proposal client compatibility acceptance" --message "antigravity-sprint152-create-proposal-client-compatibility ready for Codex review"` |

## Mission

Assess receptionist/client compatibility risk for enforcing Idempotency-Key minLength: 8 on create-proposal at runtime versus keeping current non-blank compatibility.

## Scope

### In Scope

Read AGENTS.md, protocol alerts, latest closeout, Sprint 150/151 docs/tests, and current create-proposal callers in backend tests and diary/Bernie client surfaces. Produce a tangible acceptance/review packet that states whether any visible client/workflow risk argues against immediate minLength enforcement.

### Out of Scope

Do not edit production code during planning. Do not change diary UI, taskpane, backend routes, OpenAPI schema, providers, GraphQL, H15/H-series, memory/RAG/GraphRAG, or raw trove material.

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

Prefer rg/static inspection. If you recommend runtime enforcement, name the exact frontend/backend tests or smoke checks required. If you recommend deferral, name the compatibility guard Ariadne should add.

## Merge Criteria

Ariadne gets a clear product/client compatibility verdict for Sprint 152 closeout and can integrate it into the API-spine decision artifact.

## Completion Notes

- Files changed: plan/review packet only; no production code, tests, OpenAPI, diary UI, taskpane, or migrations.
- Verification run: read-only/static review by Antigravity; Ariadne ran the focused Sprint 152 API-spine pytest suite after integration.
- Integration result: partially accepted as dissent. Ariadne accepted the finding that future diary-generated keys can easily be 8+ characters, but rejected immediate runtime enforcement because current readiness is not proven and sibling proposal routes remain unwired.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
