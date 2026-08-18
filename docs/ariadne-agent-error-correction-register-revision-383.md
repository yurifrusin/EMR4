# Ariadne agent error and correction register — revision 383

Date: 2026-08-18

Timestamp: 2026-08-18T13:59:27.4403150+10:00 (Australia/Brisbane)

Status: accepted correction

## Revision

Revision 383 adds AER-0436 and AER-0437. The pushed terminal latch checkpoint
ended its correction range at AER-0434 while register revision 382 and the
Current Baton already accepted AER-0435. The checkpoint now names the complete
AER-0426 through AER-0435 range before the successor latch opens.

During the successor's full AGENTS.md rehydration, the final chunk read used
the file's byte length as a character substring bound and exceeded the text by
two characters. A separate character-length readback returned 80261 and the
exact remaining 10261 characters were then read successfully.

No product source, accepted result, provider call, deployment or protected ref
changed.

## Population

- incidents: 437;
- corrected or explicitly contained: 437;
- open: 0;
- latest id: `AER-0437`.
