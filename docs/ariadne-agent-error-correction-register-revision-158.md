# Ariadne agent error and correction register revision 158

Date: 2026-08-10

Status: corrected; fresh catalogue and behavior evidence required

Revision 158 adds AER-0184 and brings the register to 184 bounded incidents
with zero open incidents.

## AER-0184 — body-program input collided with a relation column

Behavior attempt 032 reached the first proofread-observation read in BTR-E03.
PostgreSQL rejected it with SQLSTATE `42702`: the renderer had emitted the
fully qualified admission-table column `source_position` on one side of a
predicate and the identically named, but unqualified, function input on the
other. The rehearsal released no result, observed zero scenarios, removed its
owned container and verified absence.

A deterministic diagnosis bound the failure to exact source and artifact
bytes and proved the same collision in exactly three `SELECT_SET` predicates.
No second database run was used for diagnosis. The renderer now lowers every
body-program input to a `cf_arg_` physical namespace in program signatures and
all input references. The support function, logical body contract, 20 frozen
behavior scenarios and authority boundaries are unchanged. The regenerated
artifact must receive fresh PostgreSQL catalogue characterization, an exact
rerun, behavior-parent rebinding and an independent exact-head veto before the
next behavior attempt.
