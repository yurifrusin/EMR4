# Yuri update — time-ordered check-in context rehearsal

Date: 2026-08-24

Timestamp: 2026-08-24T16:22:26.0503913+10:00 (Australia/Brisbane)

Yuri attention required: `no`

## Lay summary

We have replaced the first trove-derived atomic success with a genuinely more
useful synthetic exercise: 30 short check-in stories where something changes
between the initial proposal and the attempted action. That compact set covers
all the pairwise combinations that a 120-case grid would cover.

The adapter stopped in the right order when an appointment, receptionist,
confirmation evidence, waiting area or command state changed. Replay,
rollback, uncertain commit and unavailable readback also stayed fail closed.
The historical diary trove was not read at all in this tranche.

## Technical summary

- exact candidate: `203f297d610ee30ce6c9d50243999ed4a8041df4`;
- 30 scenarios / 74 cross-family pairs / 16 passing unmasked witnesses;
- 72 hostile contract mutations rejected;
- 14 focused and 264 combined exact-HEAD test nodes passed;
- Ruff, compileall, generation idempotence and Git-diff hygiene passed;
- product adapter blob unchanged; no API Spine file changed; and
- no historical/local data, database, route execution, provider, network,
  ordinary-practice, production or protected-ref surface opened.

One contained workflow incident records an over-broad privacy substring, a
receipt evidence-root mistake, a long-test session handle that was not retained
and a descriptive incident label outside the clockwork's typed vocabulary. All
four were corrected before acceptance; none affected product or data.

## Place in Raisa and next work

This converts a measured weakness of the first trove-derived test—provenance
without new behavioral coverage—into efficient temporal control evidence. The
next read-only tranche compares it with existing database-backed, route and
role/tenant evidence to identify whether one genuinely incremental operational
rehearsal remains worthwhile. No permission pause is required.
