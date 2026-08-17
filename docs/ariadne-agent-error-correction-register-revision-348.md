# Ariadne agent error and correction register — revision 348

Date: 2026-08-18

Timestamp: 2026-08-18T04:28:00+10:00 (Australia/Brisbane)

Status: accepted bounded correction

## Revision

Revision 348 adds AER-0399. Sol manually completed the displayed orientation
candidate prefix `74da22d5` into a nonexistent forty-character object in the
first review-worktree command. Git rejected the reference before creating a
path or branch and before any verifier, provider, database, product or network
operation.

The exact sanitized failure is preserved. A standalone `git rev-parse HEAD`
returned `74da22d5372299eb2d2e38bb2266b76c89a97035`; the corrected attempt must
copy that literal identity and pass the existing clean-worktree preflight.

## Population

- incidents: 399;
- corrected or explicitly contained: 399;
- open: 0;
- latest id: `AER-0399`.

The incident extends the existing `orchestrator.manual_short_sha_expansion`
recurrence. It changes no product, data, provider, deployment or protected-ref
authority.
