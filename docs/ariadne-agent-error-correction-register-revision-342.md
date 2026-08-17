# Ariadne agent error and correction register — revision 342

Date: 2026-08-17

Timestamp: 2026-08-17T18:41:05.9642049+10:00 (Australia/Brisbane)

Status: corrected

## Revision

Revision 342 retains 389 bounded known incidents. No incident is open.

- AER-0388 remains the corrected stale Compass current-position sentinel.
- AER-0389 preserves both subsequent full-register rejections: the first found
  two stale revision literals, one stale incident-count literal and the
  not-yet-regenerated committed pattern report; the first correction then
  missed the explicit ordered-ID range and one older aggregate-count block;
  the second correction then missed the exhaustive recurring-pattern equality;
  the third separated the new recurrence but left its obsolete expected object
  in the exhaustive list; the fourth left one self-test phrase stale.
- All exact sentinels and aggregate fields now bind revision 342 and 389
  incidents, the canonical pattern report is regenerated from the validator,
  and the complete register file is rerun as the only acceptance packet.
- The candidate product source and exact independent review remain unchanged.

## Boundary

This is closeout harness maintenance only. It changes no product source, API,
route, database or accepted candidate and grants no data, provider, deployment,
release, Pages or protected-ref authority.
