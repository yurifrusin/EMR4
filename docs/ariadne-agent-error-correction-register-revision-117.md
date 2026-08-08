# Ariadne agent error and correction register revision 117

Date: 2026-08-08

Status: bounded register correction candidate

Revision 117 adds AER-0140 and brings the register to 140 bounded incidents.

## AER-0140 - PostgreSQL special-form correction did not cover body lowering

Attempt 017 passed artifact admission and reached `BTR-E01`, then returned
SQLSTATE `42883` at internal line 58 of
`register_observer_generation_v1`, with zero admitted scenarios and verified
cleanup. The coordinate maps to a renderer-generated count expression using
the invalid `pg_catalog.coalesce(...)` spelling.

This recurs from AER-0131. The prior correction changed only the behavior
snapshot generator and its test. It did not install an artifact-wide special-
form census, so the same invalid grammar survived in accepted entry-point and
trigger bodies.

Renderer 2.0.6 emits unqualified `COALESCE(...)` for every lowering path and
adds an artifact-wide recognizer rejection for the qualified spelling. A
hostile exact mutation proves the new guard. Fresh parse/catalogue rehearsal,
descendant rebinding, independent review and behavior rehearsal are still
required.
