# Ariadne agent error and correction register — revision 370

Date: 2026-08-18

Timestamp: 2026-08-18T09:47:05+10:00 (Australia/Brisbane)

Status: accepted bounded correction

## Revision

Revision 370 adds AER-0422. The first revision-369 validation packet found two
representation defects before candidate commit: the transport-separation test
still expected 291 agent-behavior incidents instead of 293, and the expanded
active-latch checkpoint was 528 characters against its 500-character maximum.

The correction advances the exact aggregate, shortens the checkpoint while
retaining all material gate counts, adds this incident and reruns register
generation plus the full focused continuity/adapter packet.

## Population

- incidents: 422;
- corrected or explicitly contained: 422;
- open: 0;
- latest id: `AER-0422`.

No product route, database, provider, deployment or protected ref opened.
