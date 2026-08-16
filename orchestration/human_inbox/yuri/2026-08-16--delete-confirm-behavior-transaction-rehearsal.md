# Yuri closeout — delete-confirm behavior/transaction rehearsal

Date: 2026-08-16

Timestamp: 2026-08-16T14:56:08.8155653+10:00 (Australia/Brisbane)

Attention required: `no`

## Lay summary

The cancellation foundation has crossed an important boundary: we have now
watched the real database machinery enforce the rules, not merely represented
those rules in code and schema.

In one entirely disposable synthetic PostgreSQL environment, Raisa's future
cancellation path proved that authority is denied unless explicitly granted,
that a grant can be revoked, that stale authority is rejected, and that a
cancellation, its attributable audit entry and its private receipt either all
succeed together or all disappear together. A lost response can be replayed
from the stored receipt without cancelling twice. Partial work, late revocation
and time exhaustion release nothing.

All 9 authority groups and 11 transaction groups passed, the disposable
database and its private network were removed, and an independent Gemini 3.7
Flash/high review passed on an unchanged clean copy.

This still is not a live cancellation feature. No route was connected, no real
appointment or person data was used, and no UI changed. The next product step
is a read-only inspection of the remaining route-to-kernel seam before we
decide whether it is safe and mechanically straightforward to converge.

## Technical summary

- Accepted semantic/review source:
  `49dd2aaa72877adb844da4d0d5d5bb28039c90c8`.
- Result:
  `raisa_provider_free_disposable_postgresql_delete_confirm_behavior_transaction_rehearsal_pass`.
- Evidence: 9 authority groups, 11 transaction groups, 122 hostile mutations,
  43 owned tests, 36 reviewer API Spine tests, current lineage/API Spine gates,
  canonical 196-test profile and exact cleanup.
- Independent veto: one Gemini 3.7 Flash/high `pass`; HEAD before/after exact and
  worktree clean.
- Product service unchanged at SHA-256
  `8e0f0e06471560b328e5ab7af6cc9981c20ca4a58ec9eec74dbd412979f85533`.
- Register revision 309 binds AER-0348 through AER-0356; none remains open.

The most useful workflow lesson is AER-0354/AER-0356: manual completion of
short Git hashes recurred even though the prose rule was clear. Direct Git
checks caught both before they mattered. We will replace that weak human-text
control with machine resolution/comparison of structured Git object IDs. This
is exactly the continuous Ariadne self-correction protocol you endorsed: an
observed workflow failure becomes a bounded, tested harness control rather than
permanent ceremony.

## Deliberately closed

Product databases and data, provisioning, mounted/called routes, public
contracts and UI, concurrency/restart/unknown commit, providers/ADC/credentials,
patient/clinical/protected evidence, deployment, production, release, Pages and
protected refs remain closed. `docs/branding/` and all unrelated untracked files
remain untouched.

## Next

Proceed without a permission pause to the provider-free read-only delete-
confirm route-convergence admission review, with the narrow Git-object-ID
harness control carried alongside it. Yuri's attention is not presently
required.
