# review-codex-codex-sprint105-bernie-turn-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint105-bernie-turn-invariants` |
| Source Task | `codex-sprint105-bernie-turn-invariants` |
| Status | queued |

## Review Request

codex-sprint105-bernie-turn-invariants ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `orchestration/agent_inbox/codex/plan-codex-codex-sprint105-bernie-turn-invariants.md`
  - `orchestration/agent_inbox/codex/codex-sprint105-bernie-turn-invariants.md`
- Verification run:
  - `C:\Users\sarashera\emr4\.venv\Scripts\python.exe C:\Users\sarashera\emr4\scripts\agent_worktrees.py handin --agent codex`
  - `C:\Users\sarashera\emr4\.venv\Scripts\python.exe C:\Users\sarashera\emr4\scripts\agent_worktrees.py plan --agent codex --task codex-sprint105-bernie-turn-invariants ...`
  - `git status --short --branch`
- Remaining risks:
  - Plan gate only; no backend/UI implementation or test execution yet.
  - Ariadne may need to normalize exact evidence field names across Claude and Antigravity plans before implementation release.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-sprint105-bernie-turn-invariants.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
