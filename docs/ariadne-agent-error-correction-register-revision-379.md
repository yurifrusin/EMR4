# Ariadne agent error and correction register — revision 379

Date: 2026-08-18

Timestamp: 2026-08-18T13:22:34+10:00 (Australia/Brisbane)

Status: accepted correction

## Revision

Revision 379 adds AER-0431. Sol manually estimated future local times for the
revision 377 and 378 evidence instead of copying the machine clock. Immediate
readback showed `2026-08-18T13:22:34.3122671+10:00` while the authored fields
said 13:35 and 13:44.

All four affected JSON/Markdown timestamp fields now use that machine-read
value. The correction occurred before Gemini dispatch, changed no product
source and made no provider call. Every later durable timestamp must be copied
from an immediately preceding machine readback.

## Population

- incidents: 431;
- corrected or explicitly contained: 431;
- open: 0;
- latest id: `AER-0431`.

No product data, deployment, release, Pages or protected-ref action occurred.
