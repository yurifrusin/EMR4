# codex-sprint-r1-deepseek-scenario-integrity

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/sprint-r1-deepseek-scenario-integrity` |
| Status | submitted |
| Created | 788242c |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r1-deepseek-scenario-integrity --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r1-deepseek-scenario-integrity --commit-message "Sprint R1 DeepSeek Scenario Integrity" --message "codex-sprint-r1-deepseek-scenario-integrity ready for Codex review"` |

## Mission

DeepSeek Flash replaces the usual native Codex worker for this sprint. Add a bounded, low-cost fixture integrity lane for the Bernie receptionist scenario corpus: parseability, unique ids, required fields, stable categories, xfail metadata, and consistency notes that help Ariadne merge Claude and Antigravity outputs.

## Scope

### In Scope

1) Read orchestration/bernie_reception_scenario_workstream.md and the R1 packets. 2) Plan a test-only validator for tests/fixtures/bernie_scenarios/ that checks fixture parseability, unique scenario ids, required top-level fields, turn expectations, xfail reason shape, and category allow-list. 3) During implementation, edit only the validator/test files and optional fixture README/checklist owned by this lane. 4) Report any corpus ambiguity or schema mismatch as review notes rather than silently changing Antigravity-owned scenario intent.

### Out of Scope

No production app code. No backend replay/session harness. No Diary UI. No broad scenario authorship, prompt rewrites, GraphRAG, production logs, PHI, auto-mode, or clarification merge implementation.

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

py_compile on new validator/test files; focused pytest for fixture integrity tests; git diff --check; final git status --short --branch and git diff --stat before handback

## Merge Criteria

Integrity tests are small and deterministic, do not depend on live AI/provider calls, catch malformed fixtures without owning scenario meaning, and can run alongside Claude's replay harness without write conflicts

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `tests/test_bernie_scenario_integrity.py`; this task packet completion notes.
- Verification run: DeepSeek Flash attempted verification but could not resolve Python from the sandbox. Ariadne reran verification from the integration Python: `C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m py_compile tests\test_bernie_scenario_integrity.py` passed; `C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_integrity.py -q` passed as 9 skipped while the corpus directory is absent on this branch; `git diff --check` passed with a Windows CRLF warning only.
- Remaining risks: Validator is intentionally strict on category/outcome names and may need small allow-list additions when Antigravity's corpus is integrated. Full value is proven only after running against the submitted corpus branch.
