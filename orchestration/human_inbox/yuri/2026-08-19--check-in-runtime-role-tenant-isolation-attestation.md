# Check-in runtime role and tenant isolation — paired closeout summary

Date: 2026-08-19

Timestamp: 2026-08-19T16:42:31.0085024+10:00 (Australia/Brisbane)

Status: accepted at Continuity 334 / Compass 316; Yuri's attention is not
required.

## Lay summary

The proposed ordinary check-in database identity has now been tried safely in
a completely disposable local PostgreSQL environment. It could work only with
the synthetic rows belonging to its selected synthetic practice. It could not
see or change the other synthetic practice, could not become the database
administrator, and was deleted before the disposable database was removed.

Nothing was enabled for a real practice. No real secret, existing database,
patient, appointment or clinical information was used. The normal check-in
feature remains default-off and ordinary admission remains zero.

The rehearsal passed on its first database run, cleaned up completely, and
received a clean independent Gemini veto. It also exposed one useful workflow
improvement: four tests for the new clockwork were tied to the moving current
state even though they were intended to replay an old fault scenario. They now
take their reading from the exact historical Git object, so later clock ticks
should no longer cause those four avoidable reruns.

## Technical summary

- Reviewed candidate:
  `6a2832575e9b4df5c40a13984db7281e79814a94`.
- PostgreSQL: cached `postgres:16-bookworm`, internal network, no published
  port, tmpfs, fixed in-process loopback relay, random in-memory credentials,
  captured-ID cleanup.
- Role: LOGIN plus exact negative attributes, zero memberships/ownership/
  product privileges, only CONNECT + probe USAGE + four probe-table DML grants.
- RLS: admin-owned table, enabled and forced, equal transaction-local tenant
  `USING`/`WITH CHECK` expressions.
- Behavior: 12/12 scenarios; exact `42501` for cross-tenant insert and admin
  `SET ROLE`; cross-tenant read/update/delete zero; same-tenant positive
  controls passed; setting reset passed.
- Evidence: 302/302 contract and 159/159 manifest mutations rejected, zero
  escapes, closed schemas, sanitized attestation digest binding, role/container/
  network absence.
- Verification: focused 19/19; material surrounding 145 passed with five
  frozen historical mutable-current assertions excluded; clockwork 6/6 after
  pinning replay to full source
  `f98baaa5c57cfcf00f8d2e6cd0d1113d4a59ed6e`; Gemini 10/10 commands and clean
  `pass`.

## Issues and deliberately closed surfaces

Construction exposed a missing JSON brace, an invalid test escape, several
brittle Markdown literals, five previously known generation-stale historical
assertions, and the four recurring mutable-HEAD clockwork tests. Each was
contained before acceptance; the recurring clockwork defect received the
narrow full-Git fixture repair. One verifier preflight draft also failed
closed before dispatch and was corrected. No model review, database cleanup,
worktree postcondition, provider transport or protected-boundary failure
occurred.

Still deliberately closed: ordinary-practice activation; feature/allowlist,
product/config/API/client/status/grammar/waiting-area changes; real secrets;
existing/product databases; product/patient/clinical/protected data; occupied
DeepSeek HMR; production runtime; deployment; release; Pages; and protected
refs.

## Place in Raisa and next tranche

The environment vocabulary is no longer purely architectural: its restricted
database role and tenant separation are physically representable in a bounded
synthetic instance. The remaining operational evidence gap is transaction
recovery.

Next:
`raisa-provider-free-disposable-postgresql-default-off-check-in-rollback-unknown-commit-recovery-rehearsal`.
It will freeze and exercise only an authored-synthetic disposable transaction
probe for commit, rollback and ambiguous-result recovery, with zero ordinary
release and exact cleanup.

Yuri's attention is not genuinely required; standing uninterrupted-
development authority applies.

The fourth live clockwork tick passed exactly once at generation/bundle
`503aa76307da93745abbca25f209a6841118660d02cb171ea576f4eaede5c7f5`,
lease sequence 4, with zero drift, zero dual ownership, zero caller-derived
fields and no bespoke updater. The successor latch is active for the rollback/
unknown-commit rehearsal. The non-PHI continuing Pushover notification
succeeded with request `70fee954-0528-44b2-8961-f93c60828818`.
