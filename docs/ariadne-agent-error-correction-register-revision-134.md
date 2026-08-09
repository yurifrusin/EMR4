# Ariadne agent error and correction register revision 134

Date: 2026-08-09

Status: bounded register correction candidate

Revision 134 adds AER-0159 and brings the register to 159 bounded incidents
with zero open incidents.

## AER-0159 â€” numeric-times-interval renderer and fixture defect

Behavior attempt 024 passed BTR-E01 and stopped at BTR-E02 with SQLSTATE
`42883`, zero complete scenarios and verified exact-container cleanup. The
corrected fixed-shape diagnosis resolved five candidate functions/operators and
proved the sole missing signature was PostgreSQL `integer * interval`; raw
database text was hashed and not persisted.

The defect existed in two repository-authored generation surfaces: both typed
timestamp-offset renderer opcodes emitted numeric-times-interval SQL, and the
independent closed BTR-E02 synthetic payload builder repeated the same invalid
shape. Renderer 2.0.11 and the fixture now construct typed intervals with named
`make_interval` arguments, while the independent recognizer and hostile tests
reject the predecessor spelling. The immutable typed body, frozen twenty
scenarios and authority ceiling are unchanged. Fresh inert regeneration,
separate parse characterization/exact proof, behavior rebind and independent
veto remain required before the next behavior attempt.
