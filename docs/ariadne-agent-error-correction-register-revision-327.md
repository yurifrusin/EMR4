# Ariadne agent error and correction register — revision 327

Date: 2026-08-17

Timestamp: 2026-08-17T08:52:23.3569291+10:00 (Australia/Brisbane)

Status: corrected and contained

## Revision

Revision 327 records 376 bounded known incidents. No incident is open.

- AER-0376 preserves a recurrence of AER-0370 before helper-repair
  preexecution. Sol manually expanded displayed short prefix `50016230` into a
  nonexistent full object ID instead of first copying `git rev-parse HEAD`.
- An immediate exact Git check exposed the uncommitted mismatch before receipt
  generation, staging, database execution or external review. The latch now
  contains exact machine-resolved commit
  `50016230060aa15884a09b2d6e707b431d0835fa`.
- The agreed post-closeout workflow review will prioritize machine-populated
  ref snapshots so full object IDs are no longer transcribed manually.

## Boundary

No candidate code, product state, database, provider, deployment state or
protected ref changed. `docs/branding/` and every unrelated untracked file
remain preserved.
