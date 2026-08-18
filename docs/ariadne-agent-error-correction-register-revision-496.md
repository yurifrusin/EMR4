# Ariadne agent error and correction register — revision 496

Date: 2026-08-19

Timestamp: 2026-08-19T02:07:27.8169654+10:00 (Australia/Brisbane)

Status: accepted closed register update

## Change

AER-0575 records a recurrence of AER-0548: a read-only one-off Python
inspection omitted explicit UTF-8 decoding and failed on Windows before parsing
the Continuity graph. No file was written and canonical state was unchanged.

Revision 496 contains 575 bounded incidents. All are corrected or contained;
none is open.

## Prevention

Subsequent closeout inspection and publication use the typed Continuity path,
which centralizes UTF-8 loading. Until that path is canonically adopted, every
remaining one-off `Path.read_text` call must state `encoding="utf-8"`
explicitly.
