# review-codex-codex-command-proposal-review-harness

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/command-proposal-review-harness` |
| Source Task | `codex-command-proposal-review-harness` |
| Status | integrated |

## Review Request

Command proposal review harness ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - Added `orchestration/command_proposal_review.md` with a reusable Sprint 17
    command/proposal review harness, response-shape checklist, expected
    safe/warning/blocked classes, and PowerShell snippets for the create
    proposal endpoint.
  - Updated `orchestration/sprint_closeout.md` with a concise Sprint 17 pointer
    to the new harness and the integration questions Codex should report.
  - Added the plan artifact
    `orchestration/agent_inbox/codex/plan-codex-codex-command-proposal-review-harness.md`
    via the required plan-gate command.
- Verification run:
  - `git diff --check` -> passed; PowerShell reported only a CRLF-to-LF warning
    for the task packet touched by the plan/completion update.
  - `.venv\Scripts\python.exe -m pytest tests\test_appointment_proposals.py -q --tb=short -p no:randomly` was not runnable inside this disposable worktree because it has no local `.venv`.
  - `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m pytest tests\test_appointment_proposals.py -q --tb=short -p no:randomly` from this worker checkout -> 5 passed, with the existing pytest-asyncio loop-scope deprecation warning.
- Remaining risks:
  - The PowerShell snippets are review aids and were not live-run against a
    seeded dev API in this docs-only workstream.
  - Break-warning review depends on the selected practitioner/date having a
    configured break at the chosen time; the harness calls that out.
  - AX/AY may evolve proposal fields during integration, so Codex should
    reconcile final field names before treating snippets as the long-term
    developer contract.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-command-proposal-review-harness.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Integrated. Review harness gives reusable command/proposal vocabulary, PowerShell snippets, response-shape checks, and merge gates for future agent-safe workflows.
- Follow-up required: Keep harness field names aligned as update/status proposal contracts evolve.
