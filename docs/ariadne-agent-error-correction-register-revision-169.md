# Ariadne agent error and correction register — revision 169

Date: 2026-08-10

Revision 169 adds corrected incident `AER-0195`. Behavior attempt 035 exposed a
structural RLS mismatch: the coordinator-owned durability transition must lock
and, on bounded rebase branches, update `context_observer_generation`, while
the generation UPDATE policy admitted only lifecycle sessions. PostgreSQL
therefore hid the existing row from `SELECT FOR UPDATE` and the entry point
failed closed with `CF004` before any scenario committed.

The correction aligns `pol_cf_06_update` with the already-granted coordinator
entry point without granting direct table access. Deterministic hostile tests
retain that boundary, and regenerated descendants still require fresh
parse/catalogue proof and independent review before another behavior run.
