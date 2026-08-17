# Ariadne agent error and correction register — revision 332

Date: 2026-08-17

Timestamp: 2026-08-17T11:36:20.4463873+10:00 (Australia/Brisbane)

Status: corrected and contained

## Revision

Revision 332 records 381 bounded known incidents. No incident is open.

- AER-0380 continues to contain both exhausted Gemini 3.7 Antigravity
  transports without inferring a reviewer decision.
- AER-0381 records that the first blocked-state orchestrator receipt correctly
  projected the latch and terminal handback but incorrectly left
  `worker_dispatch_permitted` true because that field depended only on receipt
  validation errors.
- The preflight now permits worker dispatch only when the receipt has no errors,
  the active operation is exactly `in_progress`, and user attention is false.
  A blocked-state regression proves a valid terminal receipt cannot dispatch.

## Boundary

The repair changes only Ariadne receipt admission. No worker was dispatched
from the unsafe receipt, and no Raisa product, data, provider product call,
database, deployment, release, Pages or protected ref changed.
