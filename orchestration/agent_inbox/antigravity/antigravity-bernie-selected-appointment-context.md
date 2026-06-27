# antigravity-bernie-selected-appointment-context

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | 3ec6b1b |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-bernie-selected-appointment-context --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-bernie-selected-appointment-context --commit-message "Dispatch Bernie selected appointment context sprint" --message "Plan for Bernie selected appointment context"` |

## Mission

Plan first, then after approval replace the temporary typed-only Bernie pilot context path with a real diary-selected appointment context source, so staff can click an existing linked appointment and use its practitioner/patient context for the gated Bernie pilot review.

## Scope

### In Scope

Plan packet first. After approval, docs/diary UI assets and review/test harness only as needed; detect the currently active diary appointment; expose a compact 'Use selected appointment' context affordance in the existing Bernie pilot context panel when the selected appointment has a real practitioner_id and linked patient_id; set Bernie pilot context from that appointment only after explicit staff action; keep the existing manual ID fields as a fallback/dev escape hatch; keep provisional/unlinked/no-practitioner appointments blocked with clear messages; no context IDs in URL, localStorage, or sessionStorage; preserve staff instruction input and existing confirmation approval gate; bump diary asset versions if runtime assets change.

### Out of Scope

Backend routes/schemas/models, database migrations, autonomous booking, broad patient/practitioner search, patient record lookup UI, taskpane, Command Centre, billing, SMS, resource admin, changing appointment create/edit/status behavior, PHI-heavy logging, query-string context intake beyond existing harness/dev parameters, and unrelated diary redesign.

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

Plan packet first. After approval run bundled node --check docs/diary/diary.js, focused route-intercepted Playwright checks for selected linked appointment context, selected provisional/unlinked blocked context, no-selection blocked context, no URL/storage context persistence, staff instruction flow still body-only, full review/test_diary_smoke.py harness if diary runtime assets change, frontend version integrity, and git diff --check.

## Merge Criteria

Codex can merge when the plan is accepted, implementation stays within diary/review assets, selected linked appointments can explicitly supply Bernie pilot practitioner/patient context, missing/provisional/unlinked context remains blocked, manual ID entry remains fallback only, no context or instruction text is persisted to URL/localStorage/sessionStorage, existing confirmation requires checkbox approval, and deterministic checks pass.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
