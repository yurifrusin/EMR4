# Raisa provider-free authored-synthetic historical Diary leading explicit time-token recovery rehearsal — closeout

Date: 2026-08-24

Timestamp: 2026-08-24T07:59:22.5874518+10:00 (Australia/Brisbane)

Status: `accepted_pending_clockwork_publication`

Exact reviewed source: `5a3c589873a104e948e65eaadacd2397f0621a3b`

## Lay outcome

We now have a deliberately fussy reader for a clock written at the beginning of
one Diary cell line. It accepts ordinary forms such as `09:00 - …`, but refuses
times hidden in the middle of text, attached to other characters, invalid
times, dates, phone numbers and email/contact-shaped lines. It gives the time
only to the words on that line and does not carry it into the next line.

It also discards the clock label before making its private stable fingerprint,
so presentation syntax does not become part of the recovered content identity.
The mechanism is ready for one fresh local measurement; it has not yet read the
historical files in this tranche.

## Technical outcome

- 7 positive formats and 16 hostile denial cases pass;
- 29 focused controls and 219 controls across 23 files pass;
- the leading-token-only integration reaches a contained synthetic candidate
  without weakening distinct-minute, interval, mapping-ratio, linkage, motion
  or leakage gates;
- the coordinate fallback is unchanged and no forward-fill state exists;
- clocked/unclocked payload HMAC tokens are byte-identical;
- Ruff, compileall, source/filesystem boundaries and diff checks pass; and
- historical access, provider calls, product effects and leakage are zero.

The first-use gate remains closed because this tranche created no historical-
derived reusable candidate. The next tranche may make one fresh metadata bind
and one no-retry 80-document local run at a new ignored root. It may not reuse a
prior attempt, publish raw values or open product/provider authority.

No ordinary-practice, product, database, provider/model, production,
deployment, release, Pages, protected-evidence or protected-ref authority is
opened. Local/origin `master` and `handoff/current` remain exactly
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.
