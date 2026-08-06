# Independent veto — observation-to-signal Sol recovery

Date: 2026-08-06

Decision: `revision_required`

Reviewed source HEAD:
`d3ce636a6ed12828a45eb0d17a2d5b8251e1a511`

Review worktree:
`C:\Users\sarashera\EMR4-worktrees\r13`

Branch:
`codex/review-observation-to-signal-d3ce636a`

## P0

None.

## P1 finding

Admission accepts source transaction timestamps on either side of the backend
observation clock when their absolute skew is within the frozen 120-second
bound. Mapping additionally required the source timestamp to be no later than
the observation timestamp.

The fresh reviewer independently used source time `03:00:20Z` and observation
time `03:00:11Z`, a contract-valid nine-second positive skew. Admission
returned `ADMIT_SIGNAL`; mapping then raised
`observation_time_window_invalid`. The recovery test covered only the reverse
ordering and therefore did not establish the full admitted clock domain.

The reviewer found no other P0-P2 issue. Alternate grammatical raw identity
and alternate sealed prior seen-ID set mapped; coordinated resealing rejected;
the low-level admission and mapping functions were absent from `__all__`; the
public builder released only after proofreading; and forced proofreader
`BLOCK` made the builder raise.

## Verification and postconditions

- focused tests: 88 passed;
- inherited temporal/API/architecture tests: 69 passed;
- Ariadne register/handover tests: 64 passed;
- compilation, Ruff check/format, Draft 2020-12 validation, three-artifact
  byte reproduction and diff check passed;
- before and after HEAD remained
  `d3ce636a6ed12828a45eb0d17a2d5b8251e1a511`;
- the worktree remained tracked-clean on the exact review branch;
- local/origin `master` and `handoff/current` remained
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`; and
- no file was edited and no provider, source, database, runtime, command,
  deployment, Pages, push or ref action occurred.

## Required disposition

Keep the Sol recovery lease active. Mapping must mirror the admission policy's
two-sided bounded clock-skew domain, with a positive-skew adversarial test and
a fresh exact-head veto before acceptance.
