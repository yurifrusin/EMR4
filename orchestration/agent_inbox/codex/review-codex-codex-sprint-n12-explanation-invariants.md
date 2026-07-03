# review-codex-codex-sprint-n12-explanation-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-sprint-n12-explanation-invariants` |
| Status | integrated |

## Review Request

codex-sprint-n12-explanation-invariants ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/agent_inbox/codex/codex-sprint-n12-explanation-invariants.md`; `orchestration/agent_inbox/codex/plan-codex-codex-sprint-n12-explanation-invariants.md`.
- Verification run: Plan gate only; read named invariant targets with `rg`; no production tests run because no production code or test code was edited.
- Remaining risks: Rich explanation payload schema may still need Ariadne approval before executable tests can target final fields; prefer backend-only invariants unless `review/test_diary_smoke.py` needs a narrow rendered-copy check; stale-state invariant may need to cover both session revision and signed confirm-evidence freshness.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-sprint-n12-explanation-invariants.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Integrated. Zeno's invariant plan was accepted and folded into
  backend outcome tests plus Diary smoke coverage.
- Follow-up required: Preserve display-only authority when K1b retrieval is
  wired into Bernie.
