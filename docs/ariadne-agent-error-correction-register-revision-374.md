# Ariadne agent error and correction register — revision 374

Date: 2026-08-18

Timestamp: 2026-08-18T12:09:00+10:00 (Australia/Brisbane)

Status: accepted bounded correction

## Revision

Revision 374 adds AER-0426. The first worker-worktree command manually expanded
the displayed `4daa2d77` prefix into a nonexistent full Git object. Git rejected
the reference before creating the target path or branch. This repeats the
manual-short-SHA-expansion class already preserved by AER-0286 and AER-0399.

A standalone `git rev-parse HEAD` then supplied exact source
`4daa2d772ffcf64e55f69917d2fb21802e959673`. The corrected command created the
clean isolated branch and worktree at that exact source. No worker, provider,
database, product-data, protected-evidence or protected-ref action occurred in
the failed attempt.

## Population

- incidents: 426;
- corrected or explicitly contained: 426;
- open: 0;
- latest id: `AER-0426`.

The product candidate remains unchanged. Prevention remains literal machine
readback: full Git identities are copied from `git rev-parse`, never completed
from a display prefix.
