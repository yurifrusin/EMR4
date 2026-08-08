# Provider-free disposable PostgreSQL durability behavior/transaction rehearsal plan closeout

Date: 2026-08-08

Result:
`raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_pass`

Accepted independently reviewed planning source HEAD:
`07e8750548ed69aba5a19f693a72397121a340e5`

Runtime status: closed; no Docker or PostgreSQL behavior run occurred

## Accepted plan

The first database-backed behavior experiment for the Context Fabric durability
spine is now finite and implementation-ready. It contains exactly twenty
serial authored-synthetic scenarios: six entry-point, four trigger, three RLS
and privilege, four idempotency and three outer-transaction rollback cases.

The positive thread registers three isolated observer generations, commits one
synthetic update-confirm projection at stream position one, admits one
proofread PRIMARY, applies it through the coordinator and proves exact replay.
A separate position-two partition proves one immutable PRIMARY plus one bounded
CONFLICT. The negative cases cover missing source, old-claim reinvocation,
temporal member omission and erasure, immutable alias mutation, double update,
cross-practice denial, forbidden privileges and three post-entry-point aborts.

Every scenario has a fixed principal, fixture, transaction shape, expected
SQLSTATE/reason and allowlisted before/after count or digest. Bootstrap
superuser work is excluded from behavior evidence. No failed connection is
reused, no database value can choose later SQL or cleanup, and all Fabric
outputs remain `command_authority: false`.

## Isolation and authority

A future implementation may use only one newly owned, already-local
`postgres:16-bookworm` container with pull disabled, network `none`, no ports,
no mounts, tmpfs storage, fixed limits, argv-only execution and exact captured-
ID cleanup after ownership reverification. It may use only opaque authored-
synthetic fixture rows and the byte-identical accepted parent SQL.

This closeout opens implementation of that exact fixed-path rehearsal only. It
does not open the container run itself, an applied migration, application or
Diary wiring, operational credentials/persistence, watcher/listener/feed/source
access, product or patient data, provider calls, commands, deployment,
production, release, Pages or protected refs.

## Verification and resolved issues

The first r73 independent veto correctly found that raw-byte parent hashes were
not portable across Git LF/CRLF checkout. The repair applies one canonical
UTF-8/LF rule to all six text parents, rejects lone carriage returns and binds
the canonical function/trigger body-contract SHA-256
`634dbc5c1a5294c1ac2de6a913671cd968a9838aa763d4c2a4d229bbcd9c0271`.

That r73 receipt also reported an incorrect aggregate count. AER revision 92
preserves the valid P2 as AER-0111 and the verifier undercount as AER-0112.
Fresh r74 independently recomputed every parent hash and explicitly collected
and passed the exact `27 + 9 + 12 + 7 + 36 + 4 + 7 + 22 = 124` admitted
planning packet, plus one named baseline deselection and `79/79` AER tests. It
reported zero P0-P3 findings and left exact HEAD and worktree unchanged.

The final repository closeout advances the read-only programme map to
Continuity 233 / Compass 215. Its exact
`3 + 5 + 79 + 10 + 14 + 27 + 4 = 142` handover, archive, AER, Compass,
Continuity, planning and planning-continuity checks pass.

One pre-existing API Spine continuity-index defect remains deliberately
outside this tranche: three already-tracked check-in/Reception One OpenAPI
paths are absent from the idempotency index. The candidate changes no API Spine
file and makes no repair claim.

## Claim boundary and pause

Passing proves only that the exact first PostgreSQL behavior/transaction
experiment is safely and completely specified. It proves no function, trigger,
RLS, idempotency or rollback behavior yet.

The next dependency-satisfied action is the fixed-path provider-free rehearsal
harness, evidence schema and hostile tests, followed by a fresh exact-HEAD
implementation veto and then one twenty-scenario disposable-container run.
Concurrency, key rotation, retention execution, unknown-commit recovery,
applied migration and every operational/product boundary remain later gates.

Yuri explicitly requested a pause after this closeout, so that runtime
implementation is not started in this tranche.
