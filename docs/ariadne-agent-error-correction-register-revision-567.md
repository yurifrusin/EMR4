# Ariadne agent-error and correction register — revision 567

Date: 2026-08-19

Timestamp: 2026-08-19T21:22:00+10:00 (Australia/Brisbane)

## Revision scope

Revision 567 preserves AER-0657 and AER-0658 from the first relay-free
rollback/unknown-response database attempt.

The attempt failed before PostgreSQL started because the newly created server
did not pass profile admission. The acquisition helper raised before returning
the captured ID, so outer cleanup could not own the never-started container.
Cleanup then replaced the primary profile coordinate with a generic cleanup
coordinate. Exact label/ID/image/state/containment inspection permitted removal
of only the owned object, and matching residue is zero.

The correction makes network admission independent of Docker's runtime network
key, emits closed per-predicate coordinates, removes exactly owned acquisitions
inside the helper before a pre-return rejection, and preserves a primary error
when cleanup also reports a problem. Pure fixtures cover all four controls.
Attempt 001 remains consumed and no proof rerun is authorised.

## Population

- incidents: 658;
- corrected or explicitly contained: 658;
- open: 0;
- latest id: `AER-0658`.

No credential was delivered, no database process or SQL started, no success or
retry occurred, and no product, ordinary-practice, provider, deployment, Pages
or protected-ref surface opened.
