# Raisa provider-free governance clockwork historical-derived first-use materialisation subgate rehearsal — report

Date: 2026-08-24

Timestamp: 2026-08-24T10:49:51.2828508+10:00 (Australia/Brisbane)

Result: `accepted_closed_mode_no_private_access_or_write`

Reviewed source: `f3bb82b872873c1f1c6b58a31e3a008aac2a9d1f`

## Conclusion

The clockwork can now represent the narrow authority needed by one future
first-use fixture attempt. The representation is an eight-box form: it binds
the exact contract bytes and full candidate-gate source, requires a digest-
bound gate receipt before writing, permits at most one minimised structural
fixture, requires non-admission to write nothing, requires written bytes to
match the admitted digest, and makes the authority non-transitive.

It is impossible to combine that form with the old denial or measurement
forms. Every omitted box, mixed form, altered digest, altered Git source and
unknown allowance fails closed.

## Evidence and authority

Six focused controls and 131 surrounding clockwork, transaction, latch and
baton controls pass. Ruff, compileall, exact contract hashing and Git-diff
checks also pass. The previous legacy denial, typed denial and measured privacy
probe remain unchanged.

No historical file or ignored attempt output was read. No fixture or writer was
created. No provider, product, database, client, runtime, ordinary-practice,
publication or protected-ref authority was exercised.

## Workflow reading

The first preplanning receipt included two implementation paths where the
receipt schema accepts authority/evidence documents only. It rejected before
planning; removing those two pointers produced the passing five-source receipt.
This is recorded as AER-1152. The first bound closeout rehearsal then found that
the new human register note omitted its required machine-readable revision
comment. One direct read-only tick exposed `tick_incident_revision_reading`;
the exact comment was added and AER-1153 records that closeout-form cost. Neither
incident caused a plan, implementation, private-data or provider rerun.

## Next work

The next tranche may now use the complete new form for one local-only,
no-retry attempt. It may nominate the already bounded single leaf root and
dense day, hold private intermediates in memory, evaluate one minimised check-
in-context candidate, and atomically write one ignored local-test fixture only
if the exact gate admits its digest. Any block, revision requirement, mismatch
or error writes nothing and cleans up.
