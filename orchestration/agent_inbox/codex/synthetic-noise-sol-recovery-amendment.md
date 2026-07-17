# Synthetic Noise Sol Recovery Amendment

Date: 2026-07-17

## Recovery basis

- Original worker commit: `f6383ca806ad3eb1e403d44394989dc8563e811d`
- Recovery source head: `960849f5cc359a2720e85e9bd283c62c6eb37978`
- Rejection evidence: `docs/bernie-synthetic-receptionist-silver-wave-1-rejection.md`
- Recovery authority: `docs/ariadne-orchestrator-recovery-lease.md`
- Generator identity after adoption: `openai/gpt-sol-recovery/synthetic-noise-sol-recovery`

The original worker completion is preserved unchanged in
`orchestration/agent_inbox/codex/synthetic-noise-generation-completion.md`.
Its candidate file was not admitted. Sol adopted only its generator source as
an untrusted candidate and changed the output identity and path before
regeneration.

## Sol amendments

1. Rebound the generator identity, candidate prefix, and output path to the
   Sol recovery lane so recovered evidence cannot be confused with the
   rejected worker result.
2. Generated dialogue only from the corrected, dialogue-free 96-anchor
   manifest; no worker candidate text was copied into the recovered output.
3. Made ambiguous and omitted patient/practitioner surfaces explicit without
   inventing evidence spans for unresolved entities.
4. Preserved all eight LC dialogue forms: one turn for `one_shot`, and two
   turns for clarification, correction, reversal, ellipsis, anaphora,
   repetition, and session restart.
5. Moved required evidence spans to the latest turn containing the exact
   surface and recorded the correct turn index.
6. Represented correction forms as a generic-practitioner first turn followed
   by a final `Dr Shera` correction.
7. Allowed omitted time, patient, practitioner, and duration fields in the
   inherited templates instead of assuming every LC anchor stated every slot.
8. Made corrected interval handling total when all temporal evidence values
   are already present in the final interval phrase.
9. Preserved reversal as an allowed operation only for reversal-form anchors;
   no candidate gains write, confirmation, override, provider, runtime, or
   product authority.
10. Added independent regression tests for deterministic regeneration,
    central validator parity, dialogue-form coverage, closed authority, and
    correction replacement.
11. After the first independent review round, removed `correction` operation
    labels from 18 candidates whose text did not explicitly exhibit a
    correction. The dialogue and semantic anchors were unchanged. Added a
    regression assertion that every remaining correction declaration has an
    explicit `Correction—` or `—sorry,` surface.

## Recovered candidate

- Path: `tests/fixtures/bernie_synthetic_noise/candidates_sol_recovery.jsonl`
- Count: 192 candidates from 96 seeds
- File payload hash: `sha256:193b705e0ce06fa32b72a063dec659e52a584fc489137bd7cbad8e511940e37f`
- Canonical candidate-record hash: `sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665`
- Provenance/adjudication: `silver/pending`
- Protected holdout access: false
- Historical diary access: false
- External corpus access: false
- Live provider/runtime access: false

## Verification

```text
central candidate validator: pass, 192/192
pytest tests/test_bernie_synthetic_noise_corpus.py
       tests/test_bernie_synthetic_noise_sol_recovery.py: 11 passed
```

This is a recovered candidate set, not admission, Gold evidence,
certification, or a real-world representativeness claim. Fresh DeepSeek and
Gemini contexts must independently review this exact frozen set before Sol
can make an admission or quarantine decision.

DECISION: pending_independent_review
PROTECTED_ACCESS: false
EXTERNAL_CORPUS_ACCESS: false
