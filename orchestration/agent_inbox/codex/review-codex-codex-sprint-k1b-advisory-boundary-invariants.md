# review-codex-codex-sprint-k1b-advisory-boundary-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-sprint-k1b-advisory-boundary-invariants` |
| Status | integrated |

## Review Request

codex-sprint-k1b-advisory-boundary-invariants ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/agent_inbox/codex/codex-sprint-k1b-advisory-boundary-invariants.md`; `orchestration/agent_inbox/codex/plan-codex-codex-sprint-k1b-advisory-boundary-invariants.md`
- Verification run: plan-gated only; ran `py -3 scripts\agent_worktrees.py handin`, read `AGENTS.md`, `orchestration/parallel_workstreams.md`, and this task packet, mapped relevant practice-knowledge/Bernie/diary test files with `rg`, then captured the implementation plan with `py -3 scripts\agent_worktrees.py plan ...`. No production tests were run because no production/test code was changed.
- Remaining risks: implementation still needs Codex/Ariadne approval before code changes; final K1b hook location may shift exact test file placement, but the submitted plan pins the required non-authority/fail-closed/provenance/stale non-interference invariants.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-sprint-k1b-advisory-boundary-invariants.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
