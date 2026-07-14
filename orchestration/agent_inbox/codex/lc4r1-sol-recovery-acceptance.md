# LC4R1 Sol Recovery Lease and Acceptance Evidence

Date: 2026-07-14

Source candidate commits:

- `6ed45c0a` — initial DeepSeek Flash implementation;
- `7798c2cd` — same-lane DeepSeek Flash revision.

Transport: DeepSeek V4 Flash/high through Claude Code `--bare`.

## Worker evidence disposition

The initial worker candidate was `revision_required` after Sol acceptance even
though its authored tests passed. It did not return normalized-turn evidence,
selected generic create tools for non-create actions, treated safe negation as
mutation intent, reduced multi-turn state inconsistently, and left development
normalized-value agreement unchanged at 71/1,152.

The same worker repaired normalized-turn evidence, explicit action negation,
action-specific tools, and final multi-turn reduction in `7798c2cd`. Its second
self-report still did not meet the committed acceptance criterion: development
normalized-value agreement remained 71/1,152. That failure is preserved in
`lc4r1-dw1-semantic-extraction-completion.md`; the worker did not certify its
own candidate.

## Recovery lease

Sol adopted the two worker commits as an untrusted candidate under the bounded
low-risk recovery policy. Sol owns two narrow amendments: speech-like filler
forms `after at <time>` and `before at <time>` preserve the explicit open-bound
operator instead of allowing the nested `at` token to erase it; and a later
temporal correction replaces the complete prior relation so an exact point
cannot leak a stale opposite bound into a new `not_before` or `not_after`
constraint. The amendments change only the pure semantic extraction module and
its focused tests. They do not change fixtures, expected values, routes, APIs,
database state, providers, UI, T3 gates, or write authority.

This is a semantic normalization rule, not a corpus-label shortcut: `after`
remains `not_before`, `before` remains `not_after`, and their single bound is
derived from the utterance. Dedicated tests assert both the relation and the
lossless normalized values. Correction regressions assert that absent bounds
are genuinely cleared from both the top-level observation and normalized map.

## Independent development evidence

One-repeat development evaluation after the Sol amendment:

| Field | LC4 baseline | LC4R1 | Delta |
|---|---:|---:|---:|
| intended action | 464 | 720 | +256 |
| action semantics | 512 | 674 | +162 |
| temporal relation | 477 | 628 | +151 |
| normalized values | 71 | 101 | +30 |
| entity semantics | 68 | 255 | +187 |
| clarification | 544 | 642 | +98 |
| safety | 1,152 | 1,152 | 0 |

There are still zero complete development scenarios. That remains honest
Silver/pending evidence: LC4R1 repairs root extraction but does not yet repair
every replay/policy consequence or contradictory candidate label.

## Independent deterministic gate

Sol reran:

```text
python -m pytest -q tests/test_bernie_semantic_extraction.py
python -m pytest -q tests/test_bernie_temporal_policy.py
python -m pytest -q tests/test_bernie_scenario_spec.py
python -m pytest -q tests/test_bernie_composed_evaluator.py
python -m pytest -q tests/test_bernie_composed_corpus_evaluator.py \
  -k "not test_regenerated_matches_committed"
python -m pytest -q tests/test_bernie_lc4_scaled_evaluator.py \
  -k "not test_exact_report_regeneration"
python -m pytest -q \
  tests/test_bernie_booking_classifier.py::test_tomorrow_at_3pm_interpret_then_duplicate_has_no_second_write
python scripts/bernie_shadow_live_gate_check.py
git diff --check
```

All selected tests passed. The real `tomorrow at 3pm` route regression still
returns the existing booking and produces no second appointment or audit write.
The T3 live-replay gate remains blocked as designed. No protected holdout file,
support module, seal receipt, or report was read or run.

Decision: `pass` for integration into LC4R staging and independent review.
