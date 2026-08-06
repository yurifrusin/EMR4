# Independent veto — observation-to-temporal-signal candidate

Date: 2026-08-06

Decision: `revision_required`

Reviewed source HEAD:
`79aac4333035b72281fb6a47033b78c04c0969e0`

Review worktree:
`C:\Users\sarashera\EMR4-worktrees\r12`

Branch:
`codex/review-observation-to-signal-79aac433`

## P0

None.

## P1 findings

### Mapper overfit to one literal fixture

Admission accepted a different grammatical raw event id, valid in-window
timestamps and a different sealed prior seen-id set, returning
`ADMIT_SIGNAL`. The mapper then rejected those admitted values because it
reconstructed the canonical prior, timestamps, raw id and key literally.

Reproduced outcomes:

- alternate valid raw id: `ADMIT_SIGNAL` then
  `observation_identity_not_exact`;
- alternate valid timestamps: `ADMIT_SIGNAL` then
  `observation_contract_not_exact`; and
- alternate valid prior seen-id digest: `ADMIT_SIGNAL` then
  `admission_contract_not_exact`.

This contradicts the frozen raw-id, trusted-clock and prior-coordinate domains
and means the admitted contract did not reliably produce its promised temporal
signal outside one evidence fixture.

Relevant reviewed lines were the mapper at source line 1583, hard-coded
coordinates at line 1590 and hard-coded identity at line 1621, reconciled
against plan lines 58 and 137.

### Proofreader bypass through exported functions

The exported admission function returned `ADMIT_SIGNAL` plus a signal digest,
and the exported mapper directly returned the accepted temporal signal and
trace without requiring the same-packet proofreader. An in-memory reproduction
obtained the admission, signal and trace without invoking proofreading. This
contradicts the frozen requirement that same-packet proofreading block bypass.

Relevant reviewed lines were signal construction at source line 1488, public
mapping at line 1523, exports at line 2027 and plan acceptance at line 175 and
line 264.

## P2

None.

## Verification and postconditions

- focused tests: 84 passed;
- inherited temporal/API/architecture tests: 69 passed;
- compilation, Ruff check/format, Draft 2020-12 validation, artifact
  reproduction/hashes and restricted diff check passed;
- before and after HEAD remained
  `79aac4333035b72281fb6a47033b78c04c0969e0`;
- the worktree remained clean on the exact review branch;
- local/origin `master` and `handoff/current` remained
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`; and
- no file was edited and no provider, source, database, runtime, command,
  deployment, Pages, push or ref action occurred.

## Required disposition

The worker already consumed its one bounded correction. These semantic egress
and contract-domain findings therefore move to the named Sol recovery lease.
The failed candidate and this veto remain immutable provenance. A corrected
candidate requires widened deterministic adversarial coverage and a genuinely
fresh exact-head independent veto before any acceptance claim.
