# Tranche closeout — CF-D2 restart and unknown-commit rehearsal

Date: 2026-08-11

Result: `stopped_without_pass`

Yuri attention required: `yes`

## Lay summary

The restart test did not reach a restart. The first run found that the test was
trying to prepare step two before step one had advanced; that narrow test-order
problem was corrected under the single repair allowance. The second run then
prepared all ten synthetic prerequisites correctly, but stopped immediately
before the first simulated crash with a deliberately terse error that cannot
safely tell us which of two adjacent checks disagreed.

Nothing touched real practice data, a provider, a product source or the
network. Both disposable database containers were removed and proven absent.
The safe outcome is therefore “not proved,” not “failed product behavior” and
not a guessed success.

## Technical summary

- Attempt 001: pre-scenario fixture failure, zero `SIGKILL`; immutable evidence
  preserved and exact cleanup passed.
- Bounded diagnosis: fixture ordinal 8 attempted position-two admission before
  position-one progress; no raw SQL or output was retained.
- Single authorised correction: setup reduced to ten valid preconditions;
  successor admission moved to R01/R03 after predecessor progress; attempt 002
  received a distinct immutable path.
- Attempt 002 source:
  `28cd0ce6639fd831960c57d5289b08f3d36ca3fb`.
- Attempt 002: all ten preconditions passed; failure
  `scenario/unexpected_terminal_success`; zero scenario records, restarts and
  `SIGKILL`; exact cleanup passed.
- Evidence SHA-256:
  `a7e88a267d597ba41d245df926a66ddb6bd98cf000afc46f269871b48604d6b6`.
- AER-0278/AER-0279: contained at register revision 246.

## Deliberately still closed

Crash/restart and unknown-commit claims, another diagnostic or runtime attempt,
key rotation, retention/purge, operational database/source or watcher access,
real/product/patient/clinical data, providers, credentials, reusable runtime,
tools/commands, deployment, production, release, Pages and protected refs.

## Decision requested

Please choose whether to:

1. authorise a fresh narrowly reviewed CF-D2 recovery descendant, beginning
   with coordinate-specific closed failure evidence before any runtime; or
2. close CF-D2 as unproved and select another independent direction.

No later durability tranche will start until this fork is resolved.
