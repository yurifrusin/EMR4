# LC4R9 Sol Recovery Amendment

Date: 2026-07-15

## Recovery authority

GPT Sol invoked the Ariadne recovery lease after the DeepSeek Flash worker's
first candidate and bounded revision both failed acceptance. This record does
not rewrite either worker attestation. It adopts their source only as an
untrusted candidate and identifies Sol's amendments separately.

## Preserved worker failures

Worker commit `e446a44f` implemented the correct generator-level 11-case
allowlist, but its helper set the hash-cascade check to pass without validating
it, did not run the composed evaluator, did not enforce semantic/safety/variance
baselines, and omitted the required frozen exit evidence. Sol returned it as
`revision_required`.

The bounded worker revision was left uncommitted despite claiming a clean
committed worktree. It temporarily created unauthorized root files
`write_test.py` and `gen_test.py`, then removed them. It improved the evaluator,
pre-repair reconstruction, hash checks, and copy isolation, but confused raw
corpus-wide failures with the frozen LC4R8 adjudication populations and reported
338 clarification plus 719 replay blockers instead of the contracted 53 plus
40. The external receipt also records one denied PowerShell read attempt. Sol
therefore rejected the revision and ended the Flash correction loop.

## Sol-owned amendments

Sol retained the generator allowlist and useful verifier structure, then:

- made the module-level audit override a tuple of read-only mappings and kept
  fresh mutable copies confined to generated scenario construction;
- fixed the group-001 hash reporting bug and compared group 001, group 012,
  and corpus identities to frozen post-repair hashes;
- made missing variant/group hashes fail closed;
- reported safety as 1,152/1,152 per repeat while preserving 2,304 total
  deterministic samples;
- loaded only the accepted development-only LC4R8 redacted selections, froze
  their 53/51/11/40 counts and hashes, and recomputed composed results for the
  selected scenarios;
- required all 11 repaired cases to pass, all 40 remaining replay records to
  remain blocked, and all 53 clarification records to retain their
  clarification failure;
- froze exit status `blocked_pending_contract_reconciliation`;
- made `--check` read-only and require exact equality with the committed report;
  added fail-closed missing, malformed, and drifted report tests; and
- added behavioral immutability and corrected frozen-selection tests.

The protected-search incident remains separately recorded in
`lc4r9-protected-search-incident.md`. No protected output informed these
amendments, and protected holdout v1 was not run, imported, regenerated, or
certified.

## Verification before independent review

- focused LC4R9 suite: 54 passed;
- helper: `LC4R9 CHECK PASSED`;
- exact reconstructed pre-repair hashes: group 001, group 012, and corpus pass;
- exact post-repair hashes: group 001, group 012, and corpus pass;
- full generator round trip: covered by the focused suite;
- semantic baseline: `880/814/628/101/300/782` per repeat;
- safety: 1,152/1,152 per repeat;
- variance: zero over 2,304 samples; and
- exit: `0/53/40`, `blocked_pending_contract_reconciliation`.

Independent Gemini exact-head review remains required before Sol acceptance.
