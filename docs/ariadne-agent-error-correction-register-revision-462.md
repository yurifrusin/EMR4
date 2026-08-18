# Ariadne agent error and correction register — revision 462

Date: 2026-08-18

Timestamp: 2026-08-18T22:50:55.0803573+10:00 (Australia/Brisbane)

Status: accepted register correction

## Correction

AER-0540 preserves the revision-461 peer-link validation failure. Six new rows
used `related_incident_ids` to describe recurrence across distinct attempts,
but the register reserves those links for exact same-attempt peers. Their arrays
are now empty; the narrative and recurrence signatures retain the relationships.

Revision 462 contains 540 bounded incidents. All are corrected or contained;
none is open. No product or authority boundary changes.
