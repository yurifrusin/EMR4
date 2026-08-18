# Ariadne agent error and correction register — revision 520

Date: 2026-08-19

Timestamp: 2026-08-19T04:37:32.9752761+10:00 (Australia/Brisbane)

Status: accepted correction and containment update

## Change from revision 519

AER-0601 preserves rejection of revision 519. AER-0600 incorrectly used
`related_incident_ids` to link a recurrence from a different attempt. The
canonical validator stopped before pattern generation with an exact peer-
linkage mismatch.

Revision 520 removes that cross-attempt peer link. Recurrence membership is
derived only from the shared recurrence signature; peer linkage remains
limited to one exact attempt identity. Candidate and protected refs were
unchanged.

## Register state

Revision 520 contains 601 bounded incidents. All are corrected or contained;
none is open. The closeout-fixture recurrence still binds AER-0319, AER-0402,
AER-0599 and AER-0600. AER-0601 is the first preserved occurrence of invalid
cross-attempt peer linkage.

## Clockwork consequence

Peer linkage and recurrence membership are separate derived gears. The
clockwork must derive the former from exact attempt identity and the latter
from recurrence signature, leaving neither as a manually selected field.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.
