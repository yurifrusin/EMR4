# codex-sprint-r20-deepseek-manifest-adversarial-tests

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | integrated |
| Created | e0406aa |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r20-deepseek-manifest-adversarial-tests --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r20-deepseek-manifest-adversarial-tests --commit-message "Sprint R20 DeepSeek manifest adversarial tests" --message "codex-sprint-r20-deepseek-manifest-adversarial-tests ready for Codex review"` |

## Mission

DeepSeek Flash worker: design or implement deterministic adversarial tests for manifest consumption. Probe for write-authority phrasing, PHI/leakage keys, raw code/source dumping, confirm-grade evidence leakage, and prompt text that could let Bernie bypass backend policy.

## Scope

### In Scope

app/services/diary/capability_manifest.py, tests/test_bernie_diary_capability_manifest.py, any new prompt-consumption helper tests if Claude adds a helper, orchestration review notes.

### Out of Scope

Live AI calls, prompt evaluation with a model, database migrations, frontend UI, mutating appointment routes.

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

Return focused tests or an adversarial checklist that can be integrated without live AI, and run py_compile/pytest for touched tests.

## Merge Criteria

Ariadne receives concrete negative tests/checks that reduce risk before the manifest is used in Bernie prompts.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `tests/test_bernie_diary_capability_manifest.py`.
- Verification run: `.venv\Scripts\python.exe -m py_compile tests\test_bernie_diary_capability_manifest.py`; `.venv\Scripts\pytest.exe tests\test_bernie_diary_capability_manifest.py -q` (20 passed); integrated again in the combined R20 manifest gate.
- Remaining risks: pattern-based prompt-safety scans are heuristic; deeper prompt evaluation should be a separate non-live or fake-provider sprint before any live provider wiring.
