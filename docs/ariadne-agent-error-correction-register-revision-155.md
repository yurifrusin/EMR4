# Ariadne agent error and correction register revision 155

Date: 2026-08-10

Status: corrected; database gate pending

Revision 155 adds AER-0181 and brings the register to 181 bounded incidents
with zero open incidents.

## AER-0181 — historical tests coupled to mutable live state

The expanded packet exposed two historical acceptance tests that correctly
preserved old evidence but incorrectly required that evidence to equal today's
live head. The support-grant characterization compared its old policy digest to
the new binding-RLS digest. The behavior-plan continuity test required the live
error register to remain at revision 146 and the historical twelve incidents to
remain its final rows.

The support test now reconstructs its exact historical catalogue and proves
that only the subsequently repaired policy digest differs from live state. The
continuity test locates and validates the exact AER-0160 through AER-0171 cohort
while permitting later closed revisions. Immutable evidence and history remain
unchanged.
