# Raisa local-only historical Diary access boundary convergence — closeout

Date: 2026-08-24

Timestamp: 2026-08-24T02:33:58+10:00 (Australia/Brisbane)

Status: `accepted_pending_clockwork_publication`

Exact reviewed source: `7fef03bb8dc0acf38772850793e1aac35e878502`

## Lay outcome

The clockwork now has a precise gear for the historical Diary privacy gate. It
cannot turn from “historical data is forbidden” into “use the Diary” merely
because a model writes a plausible label. The only usable setting carries the
reviewed contract fingerprint and every limit together.

Existing denial-only records still work. A missing limit, a changed fingerprint,
an invented broader permission or a simultaneous deny-and-allow instruction is
rejected before the clock can publish it.

## Technical outcome

- three mutually exclusive modes are admitted: legacy full denial, typed full
  denial and the exact bounded local Diary probe;
- the probe requires ten immutable historical-boundary members plus the
  independent product/patient/appointment/clinical/protected-data denial;
- its contract SHA-256 is
  `e312d58d7743b9b4d79d8a947b765732eea142f47586e0bd1f4e738047802615`;
- ordinary closeout and user-decision transitions share the same validator;
- active-latch consistency uses that validator rather than a permanent
  hard-coded legacy token; and
- all 172 complete governance tests pass, with Ruff, compilation and diff
  checks clean.

One first closeout evidence draft manually expanded the abbreviated planning
commit and produced a wrong 40-character value. A `git rev-parse` readback
rejected it before staging or publication and supplied the exact replacement.
The first clockwork rehearsal then omitted the required prospective register
reading and was rejected before its verifier ran. Register revision 654
preserves both lapses: Git fields come only from captured machine output, and
an incident-bearing rehearsal materialises its deterministic revision reading
first.

No historical Diary file was opened, listed, searched, sampled, hashed or
parsed. No real archive path, provider, model, product, database, deployment,
Pages or protected ref was opened or changed.

## Next tranche

Proceed immediately to
`raisa-local-only-bounded-historical-diary-snapshot-measured-privacy-probe`.
Fresh planning must bind one exact ignored leaf root, one dense day, a maximum
of 80 non-recursive files, exact byte caps, parser digest, ignored output and
cleanup before content read. The only successful decision remains
`locally_restricted_candidate`, with no downstream authority.
