# CF-D2 attempt 001 fixture-ordering recovery

Date: 2026-08-11

## Preserved failure

Immutable attempt 001 failed before any measured scenario or `SIGKILL`. Its
closed failure code was `unexpected_terminal_success`; all external-operation
counters were zero and exact owned-container cleanup passed. The evidence
artifact remains unchanged at SHA-256
`8e2519be3986a6dcb2721f83560a5c62bbb7ac6061f507a6479aab2f58c7b32e`.

## Bounded diagnosis

The authorised setup-only characterization stopped before the first scenario
participant. Registration calls 1–4, source-position production calls 5–6 and
the first position-one admission all passed. Fixture call 8 attempted
position-two admission for the same generation before position one had
advanced. PostgreSQL exited successfully but returned no allowlisted admission
row. No raw SQL, stdout, stderr, server log or identifier was retained.

This exactly explains attempt 001 and is consistent with the accepted CF-D1
protocol and frozen CF-D2 plan: a generation's position one is admitted and
applied before position two becomes the contiguous successor.

## Narrow correction

The inert SQL, contract, classifier, atomic members, recovery-anchor authority,
durability settings and claim boundary remain unchanged. The launcher now:

1. prepares four registrations, two source positions and only the four
   position-one admissions;
2. admits position two inside R01 after anchored position-one replay and inside
   R03 after committed recovery replay;
3. records those two least-privilege observer calls as scenario actions;
4. binds passing evidence to ten setup preconditions and up to six scenario
   actions; and
5. writes any fresh result only to immutable attempt 002.

This is the one bounded launcher/schema correction permitted by the frozen
plan. It authorises no SQL mutation, blind retry, weaker durability, provider,
product data, network, deployment, release or protected-ref change.
