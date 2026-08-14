# Sol acceptance — Reception One same-update-family multi-change kernel rehearsal

Date: 2026-08-15

Timestamp: 2026-08-15T00:46:56+10:00 (Australia/Brisbane)

Decision: accept

Accepted reviewed source: `3dd5f3b39ed98a2d562685d1d1567a359930c693`

Result: `raisa_reception_one_same_update_family_multi_change_kernel_rehearsal_pass`

## Acceptance reasoning

The frozen M1-M7 matrix is satisfied without product-source change. The
ordinary update proposal carries practitioner, local time and duration as one
closed command and remains non-mutating. Confirmation uses the existing
practice-scoped lock, signed freshness evidence, confirm-time re-proposal,
exact command comparison, conflict/practitioner checks, one update/audit flush,
one idempotency completion and one commit.

The successful scenario changes all three values in one appointment outcome
and binds exactly one update audit plus one completed idempotency row. Stale
subject truth, a newly created target conflict and target-practitioner
inactivation each deny the complete candidate without retained candidate
effects. Fresh-session replay is exact and mutation-free; different-body key
reuse conflicts. Failure injection after update and audit flush but before
commit proves transaction-wide rollback before a clean same-key retry and
later replay.

## Evidence reconciliation

Sol independently read the entire test module and reproduced the exact 412-test
packet after integrating only its one-file commit. Ruff, JSON and whitespace
checks pass. The task-baseline-to-candidate diff contains 32 bounded plan, test
and orchestration paths and no product source.

Fresh Gemini 3.6 Flash/high independently returned one schema-constrained
`pass` after exactly 109 core, 69 continuity and 234 register tests. Its
before/after HEAD is exact
`3dd5f3b39ed98a2d562685d1d1567a359930c693`; its review worktree remained
clean. The final continuity-inclusive closeout packet then passed 438 tests
across eleven modules.

AER-0309, AER-0310 and AER-0311 preserve and correct three workflow defects
without supplying acceptance evidence. The initial 120-second local aggregate
run is non-evidence; the complete locked rerun passed.

## Authority finding

No product/UI, backend, API/OpenAPI/GraphQL, database schema, migration,
event/watcher, adapter, provider, credential/IAM, patient/product/clinical
data, deployment, production, release, Pages or protected ref changed.
`docs/branding/` and every unrelated untracked file remain excluded.

The next safe descendant is one provider-free Reception One combined editor
composition over the now-proven existing update command. It must retain one
proposal, one explicit human confirmation, fresh readback and distinct status
semantics. Standing authority applies and no user-attention fork is present.
