# Ariadne agent error and correction register revision 157

Date: 2026-08-10

Status: corrected; fresh verifier required

Revision 157 adds AER-0183 and brings the register to 183 bounded incidents
with zero open incidents.

## AER-0183 — verifier passed an exact-count mismatch

The first binding-RLS veto remained clean and reported every substantive
challenge as passing. It also correctly reported 553 passed tests. Its packet,
however, required exactly 552 and explicitly required `revision_required` for
any count mismatch. The verifier nevertheless returned `pass`, so Sol rejected
the decision. No candidate semantic defect, Docker run or database contact was
observed.

The stale count arose because AER-0182 added one exact register test after the
earlier 552-test collection. AER-0183 itself adds one further register test, so
the final count must be recollected on the new exact HEAD before a fresh
Antigravity project is dispatched. A verifier-reported count is now compared
to the immutable packet before any pass can be accepted.
