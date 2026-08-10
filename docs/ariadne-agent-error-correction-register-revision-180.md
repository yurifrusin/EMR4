# Ariadne agent error and correction register — revision 180

Date: 2026-08-08

Revision 180 records AER-0208 and raises the bounded incident population to
208. Disposable Context Fabric behavior attempt 037 failed safely at
`BTR-E04`: the coordinator's ordinary read could see the immutable proofread
admission, but forced RLS hid the same row from the contracted `FOR UPDATE`
lock because the admission relation had no lock-only UPDATE policy.

The exact function-line and typed-node diagnosis is preserved without another
runtime. The bounded repair adds one coordinator-only lock-visibility policy
whose write check ends in `AND FALSE`; direct table DML, admission immutability,
entry-point authority and the typed body remain unchanged. No incident remains
open. Descendant resealing, inert regeneration, parse/catalogue proof,
independent veto and a further one-shot behavior rehearsal remain separate
steps.
