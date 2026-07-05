# codex-sprint-r19-deepseek-reason-code-policy-source

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | integrated |
| Created | da69414 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r19-deepseek-reason-code-policy-source --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r19-deepseek-reason-code-policy-source --commit-message "Sprint R19 DeepSeek reason-code policy source" --message "codex-sprint-r19-deepseek-reason-code-policy-source ready for Codex review"` |

## Mission

DeepSeek Flash worker: inspect the current flat backend STATUS_REASON_CODES and frontend status-specific reason-code option lists, then propose or implement a minimal backend source-of-truth policy for status-specific reason-code applicability that the manifest can cite safely.

## Scope

### In Scope

app/schemas/appointments.py, docs/diary/diary.js reason-code constants, tests/test_reason_code_backend.py, tests for schema/policy parity.

### Out of Scope

Visible UI redesign, migrations, live diary smoke, raw appointment mutation semantics beyond reason-code validation, prompt changes, PHI/log ingestion.

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

Return a policy table and deterministic tests or a narrow implementation plan proving Cancelled/NoShow/DNA reason-code sets stay source-derived and frontend-display policy cannot silently drift.

## Merge Criteria

Ariadne can either integrate a minimal backend policy with tests or document a precise next-step without increasing mutation risk.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `app/schemas/appointments.py`, `docs/diary/diary.js`, `docs/diary/diary.html`, `tests/test_reason_code_backend.py`, plus manifest parity updates.
- Verification run: `.venv\Scripts\python.exe -m py_compile app\schemas\appointments.py tests\test_reason_code_backend.py`; `.venv\Scripts\pytest.exe tests\test_reason_code_backend.py -q`; then integrated in the focused R19 suite.
- Remaining risks: null reason codes remain accepted for grandfathering; requiredness should be tightened only with an explicit migration/backfill policy.
