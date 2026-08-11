# CF-D2 recovery diagnostic attempt 001 — anchor revision diagnosis

Date: 2026-08-12
Disposition: deterministic root cause established; one bounded correction eligible

## Immutable result

The first no-crash recovery diagnostic is preserved at
`orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal/provider-free-durability-restart-unknown-commit-recovery-diagnostic-evidence-attempt-001.json`.
It passed all ten fixed setup preconditions and the complete atomic delta for
`cfd2_r01_apply_position_1`, then stopped at
`cfd2_r01_append_anchor_2` with closed code
`unexpected_terminal_success`, nonzero return-code class, no allowlisted result
token and no released raw error. It performed zero `SIGKILL`, restart,
participant retry, provider call, product read, product command or external
network operation, and exact owned-container cleanup passed.

The result proves that the earlier coordinate-collapsed failure was in the
lifecycle-anchor participant, not the position-one coordinator participant. It
does not prove restart or unknown-commit behavior.

## Deterministic cause

The accepted inert SQL has one internally consistent lifecycle sequence:

1. generation registration inserts a checkpoint and baseline recovery anchor
   at lifecycle revision zero;
2. the first accepted decision inserts lifecycle, audit and receipt members at
   `checkpoint.lifecycle_revision + 1`, then advances the checkpoint to that
   revision; and
3. `append_recovery_anchor_v1` accepts only a nonzero argument equal to the
   checkpoint's current lifecycle revision.

Therefore, after position one applies, the only admissible next anchor is the
second anchor at lifecycle revision one. The CF-D2 harness instead passed
numeric lifecycle revision two and expected result token `2`. Position two had
not yet applied and was intentionally fenced behind that anchor, so no legal
harness reordering could make revision two current without defeating the
scenario.

This is an off-by-one contract/harness framing defect. It is not a PostgreSQL
durability, transaction, role, RLS or accepted-entry-point defect.

## Single bounded correction

The one correction retains coordinate names ending in `append_anchor_2`, where
`2` denotes the second anchor in the generation after the revision-zero
baseline. It changes the entry-point argument and expected terminal token to
lifecycle revision `1`, corrects the frozen prose and contract claim, opens
immutable diagnostic attempt 002 and full attempt 003 paths, and adds a static
cross-check tying the harness argument to the inert SQL lifecycle arithmetic.

The correction does not change the accepted inert SQL, any role or RLS grant,
atomic transition membership, recovery classification, anchor authority,
transaction isolation, durability setting, scenario order, fencing meaning or
claim boundary. Position two remains forbidden until lifecycle authority has
independently reverified and anchored the complete position-one state.

## Next gate

All deterministic tests and format checks must pass, then a fresh exact-HEAD
Gemini 3.6 Flash/high read-only veto must accept the correction. Only that
review opens diagnostic attempt 002. Only a passing attempt 002 plus the same
reviewed source opens the single four-scenario CF-D2 attempt 003.
