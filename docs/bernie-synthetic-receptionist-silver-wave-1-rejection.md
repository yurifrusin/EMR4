# Bernie Synthetic Receptionist Silver Wave 1 Rejection

Date: 2026-07-17

Decision: `wave_invalid_source_contract`

## Outcome

The first multi-model generation wave is rejected before integration. No
candidate is admitted, promoted, evaluated against product behavior, or used
for parser work.

The Sol-owned seed exporter selected the first multi-turn variant whenever a
group was not one-shot. That produced 84 `clarification` anchors and 12
`one_shot` anchors instead of the LC development design's balanced eight-form
distribution. The correct selection is the first ordinary development variant
whose dialogue form exactly matches its group's intended dialogue form. The
regenerated manifest now contains exactly 12 anchors for each of one-shot,
clarification, correction, reversal, ellipsis, anaphora, repeated, and session
restart.

This is an orchestrator source-contract defect. It invalidates every worker
output regardless of its own mechanical result.

## Preserved worker outcomes

### Gemini

Gemini committed candidate `d59888b5` from source `76e2516e`. Its local checks
self-reported pass over 192 records. The independent Sol validator found 168
duplicate dialogue payloads and 168 non-one-shot turn-contract failures.
Inspection showed repeated action templates that did not represent distinct
ambiguity and dialogue contracts. This is conceptual, not a missing hash or
one-line guard, so no same-lane generation correction is permitted. Gemini
remains valuable as a fresh-context reviewer of recovered material.

### Codex

Codex committed candidate `f6383ca8` from source `76e2516e`. Its 192 records
have 192 unique dialogue payloads and all authority fields false, but the
strengthened independent validator found 168 non-one-shot turn-contract
failures. The source-contract defect independently invalidates the complete
candidate. It receives no semantic acceptance. Sol may adopt only its
generator source as an untrusted recovery candidate, record every amendment,
regenerate from the corrected anchors, and require fresh independent review.

### DeepSeek

DeepSeek committed candidate `b0f951be` from source `76e2516e` and self-reported
pass. The independent validator found 666 mechanical failures: 192 candidate-
ID format mismatches, 306 invalid evidence-span coordinates, and 168 non-one-
shot turn-contract failures. The source defect independently invalidates the
complete candidate. This is not suitable for a same-lane correction loop or
source adoption. DeepSeek remains available as a fresh independent reviewer.

## Recovery

1. Select each seed representative by exact group dialogue form.
2. Fail closed unless the 96 anchors contain exactly 12 of every dialogue form.
3. Require exactly one turn for one-shot anchors and at least two for every
   other form.
4. Regenerate and freeze the seed manifest from a new exact source head.
5. Open the recovery lease over only the rejected Codex generator source;
   preserve the original failure and record every Sol amendment.
6. Regenerate 192 candidates from the corrected anchors and run the Sol-owned
   mechanical and semantic gates.
7. Use fresh Gemini and DeepSeek sessions to review the exact recovered
   candidate. Neither reviews its own accepted output.
8. Sol quarantines disagreements and owns the only acceptance decision.

Protected V1-V10 material, historical data, external corpora, provider/runtime
surfaces, product writes, database, deployment, release, and certification
remained untouched.
