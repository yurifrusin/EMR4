# Ariadne agent error and correction register — revision 340

Date: 2026-08-17

Timestamp: 2026-08-17T17:20:27.8529286+10:00 (Australia/Brisbane)

Status: contained

## Revision

Revision 340 retains 387 bounded known incidents. No incident is open.

- AER-0385 and AER-0386 retain the two corrected preplanning/register evidence
  vocabulary defects.
- AER-0387 records thirteen excluded route-test failures caused by one
  pre-existing valid-fixture default that omitted the now-mandatory dedicated
  delete reason.
- A reason-only edit exposed deeper stale session/authority and HTTP-shape
  assumptions and was reverted. The suite is excluded from current acceptance
  pending a separate test-only rebind to the accepted adapter contract.
- Current route-convergence/product-adapter controls and all backend command
  semantics remain unchanged.

## Boundary

The containment changes no accepted source. It grants no product, data, provider, database,
deployment, release, Pages or protected-ref authority.
