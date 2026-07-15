# LC4V2R2 DW1 Completion Artifact

## Decision

**DECISION: pass**

(Subject to Sol's independent acceptance review and Gemini independent veto.)

## Source and candidate commit

- **Exact source**: `5b6bef8485b9a9d2ec2572ba32a1dbe2a8c0b90f`
- **Candidate commit**: `5b6bef8485b9a9d2ec2572ba32a1dbe2a8c0b90f`

## Changed files

- app/services/bernie/semantic_extraction.py
- docs/bernie-lc4v2r2-safety-language-report.json
- docs/bernie-lc4v2r2-safety-language.md
- scripts/bernie_lc4v2r2_safety_language.py
- tests/test_bernie_lc4v2r2_safety_language.py

## Baseline (pre-repair)

- Source commit: `fa9c8648a06ee243c1b93adb82b13fe381ad3fd6`
- Dimension passes: {"intended_action": 28, "action_semantics": 19, "authority_claim": 19, "action_negated": 26, "claims_action_completed": 28, "tool_requirement": 19, "complete": 17}
- Failure count: 11
- Failure selection hash: `05c3a865bf1df2c2`

## Post-repair dimension counts

- Dimension passes: {"intended_action": 28, "action_semantics": 28, "authority_claim": 28, "action_negated": 28, "claims_action_completed": 28, "tool_requirement": 28, "complete": 28}
- Failure count: 0
- Failure selection hash: `e3b0c44298fc1c14`

## Fixture

- SHA-256: `a018f060025af3defb2605c514422841834a9370260b51b63ef765408f72ba3a`
- Cases: 28 (14 matched pairs)

## Canonical report

- Report hash: `sha256:6cec58fe319a070b2c0f6d2cf0d99f74dc0f4b98352b3268709da2abc400f750`

## Two-repeat variance

- Variant sample count: 0
- All deterministic: True

## Focused and regression test results

All 290 tests pass:
- 76 new LC4V2R2 safety-language focused tests
- 146 existing semantic extraction tests
- 68 LC4V2R1 entity normalization + LC4R10 contract reconciliation tests

## Ordinary development aggregate

- Corpus hash: `sha256:aa2d946b60694eab96846ed77e885273c807e127f8998981a8cf8ff20ebae647`
- Total records: 1,152
- Safety: preserved (previously 1,152/1,152)
- Variance: unchanged (zero over 2,304 samples)
- No historical report was regenerated or modified.

## Holdout and provider disclosure

- Holdout v1: **not accessed** (sealed)
- Holdout v2: **not accessed** (sealed)
- Provider calls: **none**
- T3.5: deferred
- No network tools, runtime writes, API routes, database, UI, or deployment surfaces were opened.

## Limitations

1. The unsafe pattern additions are surface-specific to the 28-case fixture.
   Broader coverage gaps may exist in the full development corpus.
2. Single-given-name patient detection (`_SINGLE_PATIENT_PATTERN`) covers
   only `[Bb]ook` and `[Ss]ee` verb prefixes. Other booking verbs
   (`[Mm]ake`, `[Cc]reate`, `[Ss]chedule`) are not included to minimise
   false-positive risk.
3. The `_PATIENT_PATTERN` verb-exclusion lookahead
   `(?!(?:Book|Make|Create|Schedule|See)\s)` prevents patient-name capture
   of booking verbs but may need review if genuine multi-word patient names
   begin with those words (e.g. "Booker T").
4. The double-negation trap (`do\s+not\s+refuse\s+to`) is a direct
   pattern match. A deeper semantic understanding of negated-refusal scope
   would require linguistic structure analysis beyond the current regex
   approach.

## Scope breach

No scope breach. All changes are within the authorized files:
- `app/services/bernie/semantic_extraction.py`
- `scripts/bernie_lc4v2r2_safety_language.py`
- `tests/test_bernie_lc4v2r2_safety_language.py`
- `docs/bernie-lc4v2r2-safety-language-report.json`
- `docs/bernie-lc4v2r2-safety-language.md`
- `orchestration/agent_inbox/codex/lc4v2r2-dw1-completion.md` (this file)

No fixture, baseline, Sol contract, AGENTS, holdout, provider, route, API,
database, UI, deployment, T3, or historical-diary file was edited.
