# Delete-confirm route-mounting readiness review

Date: 2026-08-17

Timestamp: 2026-08-17T03:27:22.8822751+10:00 (Australia/Brisbane)

## Lay summary

The cancellation machinery underneath the API is now complete enough that we
do not need another hidden infrastructure tranche before connecting it to the
HTTP route. The review found five remaining pieces, all at the doorway: give
the route its canonical address and hidden old alias, carry the signed proposal
version, supply server-owned identity/secrets/session factory, expose the small
public receipt instead of the full appointment, and return the same canonical
public bytes on first success and replay.

The important privacy line is explicit: the database's six-field receipt is
internal command truth. The public response is a separately validated minimal
projection; the route must never simply hand out the private stored bytes.

One worker report omitted its timestamp. That was caught before acceptance,
fixed once, and guarded by a test. A later pre-verifier receipt accidentally
put a tree ID where only commit IDs belong; the new Git-object guard stopped it
before Gemini ran. Both lessons are now in Ariadne's correction register.

## Technical summary

Exact reviewed candidate: `da03039f637d3808c8785a6d6fc95309650044d9`.

- 23/23 canonical-LF source bindings pass.
- Readiness matrix: 7 satisfied, 5 route-transition gaps, 0 blockers.
- 167/167 hostile contract mutations are rejected.
- Final provider-free closeout profile: 412 tests passed, including the 117-test
  pre-verifier focused/harness/API-Spine/latch/baton subset.
- Evidence JSON and report regenerate byte-identically.
- Ruff, compilation and whitespace pass.
- Fresh Gemini 3.7 Flash/high executed eight admitted commands, returned one
  `pass`, and left exact HEAD/tree/worktree clean.
- AER-0364 and AER-0365 close the timestamp and commit-ref-evidence incidents.

## Deliberately closed

No route, schema, API Spine behavior, database, SQL, capability, product data,
provider/credential activity, UI, deployment, production, release, Pages or
protected ref was opened. Raw compatibility DELETE remains separate.

## Place in Raisa

This is the final read-only checkpoint between the accepted cancellation truth
kernel and a real first-party Reception One command route. It confirms that the
next work is a narrow adapter/transport convergence, not another round of
database or authority-foundation design.

## Next

Proceed to a provider-free delete-confirm HTTP route-convergence tranche,
modelled on the accepted status-confirm route seam and limited to the five
named transition gaps. Yuri's attention is not required; standing authority
continues.
