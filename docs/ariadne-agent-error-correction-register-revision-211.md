# Ariadne agent error and correction register — revision 211

Date: 2026-08-11

Revision 211 adds AER-0245 and brings the register to 245 bounded incidents.

## AER-0245 — closed stage enum masked by the first validation failure

After correcting the invalid `medium` severity literal, deterministic validation
exposed a second closed-enum defect in the same register draft: `validation` is
not an admitted stage. The first enum failure had masked this independent field
violation. No report, test result, worker dispatch or candidate work was accepted
under either invalid entry.

The corrected fresh attempt uses the exact stage `deterministic_verification`.
AER-0244 and AER-0245 remain separate because register linkage is reserved for
same-attempt peers. The strengthened prevention control validates all enum-
valued fields in each complete proposed incident against the schema in one
prevalidation step, rather than stopping after correction of the first reported
field.
