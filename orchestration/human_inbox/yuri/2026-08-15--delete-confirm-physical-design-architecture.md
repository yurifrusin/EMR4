# Delete-confirm physical-design architecture — paired closeout

Date: 2026-08-15

Timestamp: 2026-08-15T16:35:48+10:00 (Australia/Brisbane)

Attention required: `no`

Product engine after closeout: `paused_at_yuris_request`

## Lay summary

We have finished the blueprint for making appointment cancellation obey the
same “kernel of truth” discipline as the newer Reception One commands.

In plain terms, the backend will eventually check a receptionist's current
authority against a database-owned version, make the cancellation and its
audit/receipt together, and give one losing or winning transaction an exact,
replayable outcome. It will not rely on a stale screen, an old login claim, a
model suggestion or an event cue. A later fresh display is useful, but it is
not allowed to rewrite history about whether the cancellation committed.

This remains a blueprint, not live cancellation code. It touched no patient or
product data, database, deployed route or production system.

Gemini 3.7 Flash/high is now our live independent Antigravity reviewer in place
of 3.6. As requested, there was no ceremonial trial: its first real job was
this tranche. It passed the exact review and left the candidate unchanged.

One workflow mistake was caught before review: the orchestrator began a draft
using a guessed expansion of Git's short commit display. The draft was rejected
and corrected from literal Git output before any model call. It is recorded as
AER-0329 so the recurrence remains visible.

The next natural product step would turn this blueprint into an unmounted,
still non-running schema/transaction scaffold. As requested, we are pausing
before opening that tranche. The immediate next activity is instead a
read-only assessment of PrimeIntellect's `prime-agent` claims and code for
useful Ariadne harness ideas.

## Technical summary

Accepted result:
`raisa_provider_free_unmounted_delete_confirm_physical_design_architecture_pass`
at reviewed source `3fd22ba69f96c0378538ea27c6bea444fcb81936`.

The contract freezes:

- `users.authority_generation BIGINT` as PostgreSQL-owned monotonic authority;
- normalized exact grants `appointment.cancel.confirm` and
  `appointment.read`, with no role-derived or automatic backfill;
- two full current-authority checks around the locked appointment/idempotency
  classification;
- existing appointment state version `n -> n + 1`, `Cancelled`, ten exact
  mandatory reason codes and separately nullable 500-character text;
- one additive `authority_generation` field on the private completed receipt;
- a six-field canonical byte response used identically for first delivery and
  replay after constant-time integrity verification;
- versioned delete audit with human warnings separated from internal evidence;
- `READ COMMITTED`, lock order authority fence -> appointment -> idempotency,
  one cumulative 2000 ms wait budget and no effect retry; and
- a new post-commit transaction requiring current `appointment.read`, with
  readback explicitly not commit evidence.

Evidence:

- 20/20 source hashes;
- 166/166 hostile mutations rejected;
- 63/63 exact reviewer focused tests;
- 36/36 reviewer API Spine tests;
- 196/196 canonical fast-profile repository tests;
- Ruff, maintained-source compilation, Diary syntax and whitespace pass; and
- one fresh schema-constrained Gemini 3.7 Flash/high `pass`, exact HEAD before
  and after, clean postcondition and no fallback.

Deliberately closed: application/migration/service/route implementation,
executable DDL/SQL, database/lock behaviour, capability provisioning, mounted
runtime, product/patient/clinical/protected data, product provider/ADC,
watcher/event authority, command/write, credentials/IAM, deployment,
production, release, Pages and protected refs.

Planned but paused product candidate:
`provider_free_unmounted_delete_confirm_physical_schema_and_transaction_scaffold_implementation`.
