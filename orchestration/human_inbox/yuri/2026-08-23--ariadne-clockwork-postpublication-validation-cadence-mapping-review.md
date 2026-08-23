# Clockwork validation-cadence map

Date: 2026-08-23

Timestamp: 2026-08-23T20:54:02.4308423+10:00 (Australia/Brisbane)

Yuri attention required: **no**

## Lay summary

The main conclusion is to keep the safety tests but stop making the operator
coordinate them by hand. The 120 tests before publication and the same 120
afterward look repetitive, but they inspect different clock states. The extra
42 tests inspect the moving continuation latch and caught the defect we saw.

One manual reading really is redundant: publication already validates the live
state after it commits. Asking for that identical reading again immediately
does not add safety.

## Technical summary

- 3 semantic commands;
- 120 prepublication governance tests;
- 162 postpublication tests = the phase-shifted 120 + 42 unique preflight;
- inline and manual live checks use the same validator;
- zero tests removed or weakened; and
- one explicit-stage path typo contained before staging and queued as AER-1133.

## Place in Raisa and next tranche

The next ergonomic step is a single provider-free closeout entrypoint. It will
choose the correct repository interpreter, preserve the existing tests, retain
the inline live reading and emit exact stage paths so the model no longer
retypes them. Its first rehearsal will not automatically stage or publish.

No provider, worker, product/data source, runtime, deployment, release, Pages,
protected evidence or protected-ref movement is opened.
