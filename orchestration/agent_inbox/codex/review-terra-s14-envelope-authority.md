# S14 Terra Acceptance - Envelope Authority Cross-Contract Hardening

Decision: accepted on staging after a Terra-owned confirmation-author correction.
Protected master and S15 remain closed pending separate Sol authorization.

## Accepted Scope

S14 adds registered-author validation to `DiaryActionIntent` without a tier
restriction. The policy seam now resolves grammar aliases before direct names
for action semantics, while direct capability names remain supported. Cross-
contract tests cover aliases, direct names, planned verbs, and unknown names.

Terra rejected the initial Gemini interpretation that a confirm-tier alias such
as `move` may inherit Bernie authorship from adjacent `propose_edit`. Registered
confirm-tier aliases now require `staff_ui`, preserving the existing signed-
confirmation/staff-only boundary. This is construction-time validation only;
it does not add route, RBAC, command, provider, database, or write authority.

The API Spine remains unchanged: GraphQL is read-only, and REST appointment
proposal/confirmation commands retain their idempotency, evidence, freshness,
revalidation, and audit boundaries.

## Worker Evidence

The Gemini 3.5 Flash/high artifact is preserved at
`orchestration/agent_inbox/antigravity/s14-envelope-authority-completion.md`.
It records candidate `3dc11eb9`; the artifact commit is retained separately.
Terra's subsequent correction is explicitly recorded here rather than changing
the worker artifact.

The initial `agy` print invocation placed the prompt after flags, causing a CLI
mode-help response with no worktree change or artifact. A minimal local prompt
probe established the correct argument order. The same Gemini lane then ran in
the disposable worktree from `03:08:59Z` to `03:12:52Z` (about 233 seconds,
advisory), returned exit code zero, committed its candidate, and wrote the
artifact. No S14 `agy` process remained before the owner record was released.

## Verification

The final staging suite passed:

```text
31 passed: tests/test_envelope_capability_policy.py
195 passed: envelope, boundary, capability-manifest, grammar, route-contract,
route-coverage, workflow-chain, and API-Spine artifact suites
```

`python -m py_compile` for the changed Diary modules and `git diff --check`
also pass. Evidence is deterministic and local, not live-provider,
live-backend, or external-client evidence.

## S14 Metrics

| Metric | Result |
| --- | --- |
| Sol interventions / escalation reason | 0 / none |
| Terra planning/acceptance corrections | 1 Gemini CLI argument-order transport correction; 1 final staff-only confirm-alias correction with whitespace cleanup |
| Worker launches / retries / stalls / marker corrections | 1 completed Gemini work lane; 1 no-work CLI attempt and 1 local prompt probe; 1 same-lane transport retry; 0 stalls; 0 marker corrections |
| Lifecycle defects | 1 CLI argument-order dispatch defect; no process/owner leak |
| Consultations | 0 Conductor, 0 verifier |
| Invalid integrations / manifest variances | 0 / 0 |
| Duplicated-context events | 0 |
| Models used | Terra and Gemini 3.5 Flash/high. DeepSeek, Claude, Conductor, and verifier were unnecessary because Gemini provided the required independent adversarial view and deterministic acceptance found the one material gap. |
| Advisory duration | About 233 seconds from durable local owner timestamps for the completed Gemini lane |
| Coordination vs product/test added lines | 220 / 225 through S14 acceptance |
| Final correction work | Registered confirm-tier aliases are staff-only; trailing whitespace removed; one regression test added. |

## Closed Gates

Terminal-to-active status policy remains user-owned. Provider/live-provider,
schema/database, deployment/release, external patient client, H15/H-series,
historical trove, memory/RAG/GraphRAG, GraphQL mutation, UI delivery, new
confirmation action/route, and new write authority remain closed.
