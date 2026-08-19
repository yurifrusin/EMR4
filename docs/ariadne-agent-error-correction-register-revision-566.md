# Ariadne agent-error and correction register — revision 566

Date: 2026-08-19
Timestamp: 2026-08-19T11:53:31.2243631+10:00 (Australia/Brisbane)

## Revision scope

Revision 566 preserves AER-0656, a recurrence of the repeated-value patch hazard. The first resource correction for AER-0655 matched the same string in AER-0556, changing that earlier historical incident while leaving AER-0655 unchanged.

A read-only current-versus-HEAD comparison identified the exact unintended field. The correction restores AER-0556, patches AER-0655 only with incident-ID context and admits AER-0656 to the existing recurrence fixture. The register contains 656 incidents, all corrected or contained and none open.

Final end-to-end rehearsal and closeout cost is twenty-five reruns. The exact corrected Gemini input remains sixteen; all nine post-review closeout reruns are reported separately. Projected clockwork-owned representative steady-state corrective reruns remain zero.

## Prevention

Every repeated-value register patch includes exact `incident_id` and field context. Before pattern regeneration, all pre-existing incident fields are compared read-only to HEAD so an unintended historical mutation fails closed.
