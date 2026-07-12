# S6 Lane 1: Diary Smoke Diagnosis And Repair

Sprint: S6
Role: implementation owner
Resource: `deepseek-flash-workers` instance 1
Conductor plan: `plan-deepseek-pro-post-s5-next-sprint.md`
Completion artifact: `orchestration/agent_inbox/codex/review-deepseek-s6-diag-smoke.md`

Diagnose and repair the eight reproducible failures in
`review/test_diary_smoke.py`. Begin by reproducing the current eight-failure
baseline and tracing each failure against current `?smoke=true` behavior. The
Conductor's GraphQL/mock explanation is a hypothesis, not permission to weaken
assertions. Determine whether each test should use an existing live-review mode,
intercept GraphQL, or update a stale network expectation while preserving the
behavioral safety contract.

Ownership: edit only `review/test_diary_smoke.py`. Read production diary code as
needed but do not change it. Do not skip, xfail, delete, or broadly relax tests.
No runtime gate, backend, provider, GraphQL readiness, deployment, product
policy, or terminal-status change is allowed.

Required evidence:

1. Before transcript showing exactly eight failures.
2. Root cause for each failure group.
3. Minimal test-harness-only diff.
4. After transcript showing zero failures for the complete smoke file.
5. `node --check docs/diary/diary.js` and `git diff --check` pass.
6. Boundary statement confirming only `review/test_diary_smoke.py` changed.

Create the artifact skeleton first and append evidence. End only when complete:

```text
STATUS: complete
```
