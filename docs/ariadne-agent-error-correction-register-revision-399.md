# Ariadne agent error and correction register — revision 399

Date: 2026-08-18

Timestamp: 2026-08-18T17:44:15.2504768+10:00 (Australia/Brisbane)

Status: accepted correction

## Revision

Revision 399 carries forward AER-0454 through AER-0459 and adds AER-0460.

AER-0460 preserves the first rejected terminal-evidence precommit receipt. The
runtime state copied a `completed_stage` checkpoint longer than Ariadne's
bounded-text limit, so preflight returned `revision_required` with
`active_operation_latch_invalid` and did not authorise commit. Standalone latch
validation identified the exact defect before staging, commit, provider work,
candidate change or protected-ref movement.

The checkpoint was shortened without changing any fact: one occupied attempt,
one seven-tool request, zero provider calls, zero model/tool work, zero
candidate change, complete cleanup and no retry. The active latch now passes
standalone validation. A distinct corrected precommit receipt must pass before
the evidence commit.

## Population

- incidents: 460;
- corrected or explicitly contained: 460;
- open: 0;
- latest id: `AER-0460`.
