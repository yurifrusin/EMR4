# LC4V2R2 Safety-Language Classification & Repair

## Scope

LC4V2R2 implements deterministic safety-language classification repair for
14 matched unsafe/safe pairs (28 development cases) in the Sol-authored frozen
fixture `tests/fixtures/bernie_lc4v2r2_development/safety_language_cases.json`.

The repair is bounded to `app/services/bernie/semantic_extraction.py` and the
audit harness only. No fixture, baseline, contract, holdout, or provider
surface was modified or accessed.

## Baseline (pre-repair)

| Dimension | Passes (of 28) |
|---|---|
| intended_action | 28 |
| action_semantics | 19 |
| authority_claim | 19 |
| action_negated | 26 |
| claims_action_completed | 28 |
| tool_requirement | 19 |
| **complete** | **17** |

Failure selection hash: `05c3a865bf1df2c2`
11 failures across 9 pairs.

## Repairs applied

### 1. New unsafe demand patterns (8 additions)

Added the following patterns to `_UNSAFE_PATTERNS`:

| Pattern | Target case |
|---|---|
| `\bskip\b.*\b(?:clash\|check)\b` | clash_check_unsafe |
| `\b(?:hide\|suppress\|conceal)\b.*\baudit\b` | audit_suppression_unsafe |
| `\bsay\b.*\b(?:booked\|complete\|done\|finished)\b` | premature_completion_unsafe |
| `\bchoose\b.*\b(?:whichever\|looks right\|one that)\b` | ambiguous_patient_choice_unsafe |
| `\bguess\b.*\b(?:practitioner\|doctor\|who)\b` | practitioner_guess_unsafe |
| `\bforce\b.*\b(?:booking\|book\|slot)\b` | unavailable_slot_force_unsafe |
| `\bdo\s+not\s+refuse\s+to\b` | negated_refusal_trap_unsafe |
| `\bdo\s+not\s+need\s+to\s+check\b` | identity_check_not_required_unsafe |

### 2. Refined "no need" reversal scope

Changed `_REVERSAL_PATTERNS` entry from `\bno need\b` to
`\bno need\b(?!\s+(?:for|to))` to distinguish:

- *"There is no need for confirmation"* — unsafe guardrail removal
  (handled by existing `\bno.*need.*for.*confirm\w*\b` unsafe pattern);
- *"There is no need to bypass confirmation"* — safe guardrail
  (no reversal, no unsafe classification);
- *"No need, forget it"* — genuine action reversal
  (still caught by the refined pattern).

### 3. Single-given-name patient ambiguity

Added `_SINGLE_PATIENT_PATTERN` and updated `_extract_patient` to detect
single given names (e.g. "Alex") after booking verbs as `ambiguous` rather
than `omitted`. This enables the `ambiguous_patient_choice_safe` case to
correctly classify as `ambiguous` / `clarify`.

Added a verb-exclusion lookahead to `_PATIENT_PATTERN` to prevent the
multi-word patient pattern from accidentally capturing "Book Alex" when
the `[Bb]ook` prefix is consumed as optional.

## Post-repair results

| Dimension | Passes (of 28) |
|---|---|
| intended_action | 28 |
| action_semantics | 28 |
| authority_claim | 28 |
| action_negated | 28 |
| claims_action_completed | 28 |
| tool_requirement | 28 |
| **complete** | **28** |

Failure selection hash: `e3b0c44298fc1c14` (empty — all pass)
Two-repeat variance: zero (all 2,304 samples deterministic)

## Fixture integrity

- SHA-256: `a018f060025af3defb2605c514422841834a9370260b51b63ef765408f72ba3a`
- 28 cases, 14 matched pairs
- Every pair has contrasting unsafe/safe classifications
- No expected field leaks into the extraction boundary

## Baseline immutability

The committed baseline (`docs/bernie-lc4v2r2-baseline.json`) at source
`fa9c8648` is validated byte-for-byte and schema-checked. All dimension
counts, failure selection, and protected boundary flags are bound.

## Staging tool policy

The established staged positive-unsafe tool policy is preserved. Unsafe
demands after legitimate first-turn requests still include the first-turn
tools (search_patients, find_slots, create_booking) before
refuse_instruction. This tranche classifies refusal versus guardrail scope
only and does not revise the tool sequence.

## Regression

All 290 regression tests pass:
- 146 existing semantic extraction tests
- 68 LC4V2R1 entity normalization + LC4R10 contract reconciliation tests
- 76 new LC4V2R2 safety-language focused tests

Or dinary development corpus hash unchanged:
`sha256:aa2d946b60694eab96846ed77e885273c807e127f8998981a8cf8ff20ebae647`

## Protected boundaries

- Holdout v1: not accessed
- Holdout v2: not accessed
- Provider calls: none
- T3.1-T3.4: preserved, blocked by default
- T3.5: deferred
- Write authority: none opened

## Canonical report

`docs/bernie-lc4v2r2-safety-language-report.json`
Report hash: `sha256:6cec58fe319a070b2c0f6d2cf0d99f74dc0f4b98352b3268709da2abc400f750`
