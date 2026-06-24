# codex-security-alert-triage-harness

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/security-alert-triage` |
| Status | superseded |
| Created | fca99d2 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-security-alert-triage-harness --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-security-alert-triage-harness --commit-message "Security alert triage harness" --message "codex-security-alert-triage-harness ready for Codex review"` |

## Mission

As a Codex worker/security-manager, plan and then create an Ariadne-facing triage harness for current GitHub Security alerts after Sprint 20. Inventory CodeQL, Dependabot, secret scanning, and security workflow state with gh, classify alerts into fix-now/defer/noise, and identify which alerts should be closed by code fixes this sprint.

## Scope

### In Scope

orchestration/security_alert_triage.md or a similarly named orchestration report; gh read-only security queries; optional safe documentation updates to link the triage harness from existing security baseline notes.

### Out of Scope

No production app code changes unless Ariadne explicitly folds a tiny safe fix into integration; no secret disclosure in committed files; no dismissing GitHub alerts; no cloud/key rotation; no master/handoff integration.

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

Run gh auth status; query open code-scanning, secret-scanning, dependabot, and recent security workflow runs; ensure any saved report redacts secrets and includes enough alert IDs/rules/paths for Ariadne review.

## Merge Criteria

Report is complete enough for Ariadne to prioritize Sprint 21 integration; secrets are not exposed; alert classification is concrete; branch submits cleanly for review.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- `orchestration/security_alert_triage.md`
- Verification run: Ariadne directly ran `gh` metadata queries for CodeQL,
  Dependabot, secret scanning, and recent workflow state after the Codex worker
  repeatedly stopped on local tooling issues. No secret values were committed.
- Remaining risks: The worker branch remains plan-only; Ariadne-owned report
  supersedes that worker implementation for Sprint 21. GitHub CodeQL alerts
  will not close until analysis re-runs on integrated `master`.
