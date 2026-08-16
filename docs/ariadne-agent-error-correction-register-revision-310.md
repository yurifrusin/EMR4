# Ariadne agent error and correction register — revision 310

Date: 2026-08-16

Timestamp: 2026-08-16T15:54:27.0954226+10:00 (Australia/Brisbane)

## Result

Revision 310 preserves 357 bounded known incidents. All are corrected or
explicitly contained; none is open.

This revision adds AER-0357. The first independent veto for the combined
delete-confirm route-convergence and Git-object-resolution tranche correctly
rejected a raw-byte SHA-256 binding that was stable in the primary checkout but
not in the clean verifier worktree. Equal committed text had CRLF in the
primary worktree and LF in the verifier worktree.

The defect recurs AER-0349's exact checkout-stability signature. It is corrected
by strict UTF-8 CRLF-to-LF canonical hashing for every bound text input, bare
carriage-return rejection, the exact corrected digest and a focused LF/CRLF
equivalence regression. The rejected receipt remains immutable. No route,
database, provider, product data, protected evidence, publication or
protected-ref action occurred.

## Boundary

This is workflow evidence, not a model or provider quality claim. The route
verdict remains unaccepted until the distinct corrected candidate passes its
deterministic gates and fresh independent veto. No raw prompts, credentials,
patient, clinical, product-derived or protected evidence is introduced.
