# Yuri mailbox — historical-derived check-in adapter-test utility gap review

Date: 2026-08-24

Timestamp: 2026-08-24T15:21:43.2895486+10:00 (Australia/Brisbane)

Attention required: `no`

## Lay summary

We now know exactly what the first trove-derived scenario contributed. Its
historical fingerprint made the test traceable, and its nineteen-minute span
shifted the synthetic test clock. But it did not uncover a new check-in rule or
exercise a new behavior: it ran an ordinary Booked-to-Arrived success that the
existing synthetic tests already cover.

That means the trove has not been wasted. It has shown us how to use historical
material safely and, just as importantly, what does not yet count as useful
behavioral evidence. We should now stop attaching historical fingerprints to
more isolated atomic tests and instead test short synthetic stories in which
something changes before check-in completes.

## Technical summary

- Accepted candidate: `4cdc1df910c644116f686de472cc385b6a1b1bef`.
- Five structural measurements were provenance-only; the nineteen-minute span
  was a synthetic time parameter; none independently selected behavior.
- Incremental adapter branches: `0`; new business rules: `0`.
- Existing coverage already includes six success combinations and 68 hostile
  adapter mutations, plus replay and outcome-unknown paths.
- The next contract contains only three time-ordered authored-synthetic axis
  families and avoids a full combinatorial cross-product.
- Verification: 69 hostile review-contract mutations, 13 exact-HEAD focused
  tests and 337 combined tests passed; Ruff and compileall passed.
- No historical/local fixture, control or archive was opened in this review.

## Issues and closed surfaces

One bounded workflow incident covers a too-broad test substring, one unused
import, one output-silent PowerShell conditional and one missing conventional
clockwork efficacy projection. All were contained by the normal gates before
publication. No data, provider, product, runtime or protected-ref boundary
changed.

Further historical access, product changes, ordinary-practice activation,
provider/model calls, database/route/client/runtime work, deployment,
production, release, Pages and protected-ref movement remain closed.

## Place in the Raisa direction and next tranche

This converts the trove experiment from a vague promise into a measured input:
provenance and timing are useful, but meaningful check-in development requires
time-ordered state changes. The next tranche will freeze and rehearse a minimal
pairwise set of authored-synthetic stories across source/waiting-area,
authority/evidence/freshness and idempotency/outcome transitions. It will use
no historical data and will not change product behavior.
