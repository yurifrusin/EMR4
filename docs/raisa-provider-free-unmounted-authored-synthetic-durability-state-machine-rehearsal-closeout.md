# Provider-free unmounted durability state-machine rehearsal closeout

Date: 2026-08-06

Status: accepted

Result:
`raisa_provider_free_unmounted_authored_synthetic_durability_state_machine_rehearsal_pass`

Exact independently reviewed source HEAD:
`95a2ed5e960c58686262b5e82ce2e89354a3860a`

## Outcome

The accepted source-specific durability contract now has a pure immutable
in-memory state-machine rehearsal for the patient-free
`diary.appointment_rescheduled.v1` family. It proves authored-synthetic
transitions for exact redelivery, contiguous relevant and irrelevant
observations, atomic receipt/watermark/obligation/audit/checkpoint changes,
gap/hold/rebase, restart reconstruction, future-fenced key rotation and
complete-census retention eligibility.

Thirty-three generated evidence cases pass. Every transition either returns a
fully verified successor or leaves the prior state byte-equivalent. Relevant
causes permanently retire stale frames and coalesce one obligation per frame
generation; corruption fully invalidates and requires rebase. Restart trusts a
separate recovery anchor before consulting candidate state. Retention requires
the module-owned typed authority for the complete backend-authored census.

## Recovery and acceptance reconciliation

Three preserved fresh vetoes rejected earlier candidates before acceptance:

1. structural receipt/audit forgeries and self-echoed incomplete retention;
2. coupled receipt/audit stories detached from canonical effects, key and
   lifecycle semantics; and
3. premature `FIVE_PLUS` bucketing plus ambiguous audit/rotation chronology.

Sol kept AER-0050 and the same recovery lease open throughout. The final
candidate derives exact internal cause cardinality from canonical audit
history, exports only the closed bucket and records minimal payload-free key
rotation revisions. Audit and rotation revisions are unique, disjoint and
exactly cover the lifecycle. The fresh fourth veto found no P0-P2 issue after
29/29 targeted attacks, 49/49 focused tests, 207/207 serial checks, Ruff and
diff validation. AER-0050 is corrected in register revision 48.

## Preserved evidence

All user-owned untracked files, especially `docs/branding/`, and every
unrelated Gate -1, Consultant, receipt/state, evidence and cost-ledger artifact
remain preserved and excluded.

## Claim boundary

This acceptance proves a pure provider-free, unmounted, authored-synthetic
state machine only. It does not prove cryptographic authenticity and creates no
application change, migration, database object, source/outbox/feed/watcher/
listener, operational persistence or credential, product read, patient or
product data flow, API route, provider call, command/write authority, runtime
wiring, deployment, production, release, Pages operation or protected-ref
authority.

## Next safe descendant

Under Yuri's standing uninterrupted-gate authority, proceed directly to a pure
provider-free unmounted migration-and-transaction architecture tranche. It may
freeze only the future PostgreSQL schema, isolation/locking, transaction and
rollback boundaries, RLS/role separation, producer-coordinate allocation,
credential binding, operational retention contract and database-backed
authored-synthetic acceptance design needed to implement this state machine
later.

It may not add a migration or database object, mount or read a source, persist
operational state, alter application code, handle patient/product data, add a
route, call a provider, carry command/write authority, wire runtime, deploy,
release, rebuild Pages or move protected refs. Implementation remains a later
separately bounded descendant.
