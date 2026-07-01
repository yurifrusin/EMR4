# review-codex-codex-sprint98-bernie-release-gates

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint98-bernie-release-gates` |
| Source Task | `codex-sprint98-bernie-release-gates` |
| Status | queued |

## Review Request

codex-sprint98-bernie-release-gates ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/agent_inbox/codex/plan-codex-codex-sprint98-bernie-release-gates.md`; source packet status/notes only.
- Verification run: `python scripts\agent_worktrees.py handin --agent codex`; inspected `orchestration/bernie_release_gates.md`, `review/test_diary_smoke.py`, `scripts/smoke_bernie_interpreter.py`, existing Bernie backend tests, `orchestration/sprint_closeout.md`, `orchestration/parallel_workstreams.md`, and protocol alerts. No production tests run because this is plan-only.
- Remaining risks: Implementation workers may touch the same review harness; Ariadne should reconcile selector/test naming after backend/UI plans are accepted.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-sprint98-bernie-release-gates.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
