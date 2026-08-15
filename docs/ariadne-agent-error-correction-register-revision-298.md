# Ariadne agent error and correction register — revision 298

Date: 2026-08-15

Timestamp: 2026-08-15T22:21:43+10:00 (Australia/Brisbane)

Revision 298 records AER-0337. At this revision the register contains 337
bounded known incidents, all corrected or contained by an explicit control.

AER-0337 records the immediate recurrence of unsafe validation composition
after AER-0334 and its explicit no-chaining reminder. Sol again joined
validation and readback commands with semicolons, allowing a later exit status
to mask an earlier failure in principle.

No chained aggregate outcome was admitted. Every affected gate was rerun as a
separate process and its exit observed independently. The recurrence now fixes
the stronger mechanical rule: after a no-chaining incident, one process call is
used per validation or readback gate without exception.
