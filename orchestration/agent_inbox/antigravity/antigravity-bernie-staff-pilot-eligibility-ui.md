# antigravity-bernie-staff-pilot-eligibility-ui

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | a4f6078 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-bernie-staff-pilot-eligibility-ui --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-bernie-staff-pilot-eligibility-ui --commit-message "Dispatch Sprint 60 Bernie pilot UI gate" --message "Sprint 60 dispatched: Bernie staff pilot eligibility UI gate"` |

## Mission

Consume the Sprint 59 backend pilot eligibility endpoint before showing Bernie review outside explicit dev/query mode. Keep ordinary production exposure default-off and make any eligible exposure clearly labelled as pilot/supervised.

## Scope

### In Scope

Antigravity may modify diary frontend files and deterministic review harness files only as needed. Add a narrow route-intercepted/smoke-gated UI path that calls /api/v1/appointments/bernie/pilot-eligibility, shows no Bernie review affordance when ineligible/default-off, and shows a clearly labelled pilot/supervised launch affordance only when the eligibility response is eligible. Preserve existing ernie_dev_review=true behavior and fixture-state tooling. Add/update Playwright review checks proving default-off absence, eligible pilot visibility, endpoint interception, no confirm-Bernie POST before explicit staff approval, and no live writes.

### Out of Scope

No backend changes, no auth/config changes, no normal default exposure without eligible response, no autonomous writes, no PHI, no Google/Gemini/provider calls, no appointment mutation semantics, no taskpane/Command Centre/Office dialog/resource admin/billing/SMS work.

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

Plan must name exact files and deterministic checks. Implementation verification should include node syntax if JS changed, frontend version integrity if assets changed, route-intercepted Playwright/pytest review checks for ineligible and eligible pilot states, proof no confirm-Bernie POST before explicit approval, proof existing dev/query review behavior still works, and git diff hygiene.

## Merge Criteria

Integrate only if the pilot UI remains default-hidden, depends on the backend eligibility response for staff-visible exposure, is clearly labelled as supervised/pilot, preserves dev/query mode, has deterministic route-intercepted tests, and performs no live writes in tests.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
