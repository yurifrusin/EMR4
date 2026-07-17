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

## Recovered candidate

- Path: `tests/fixtures/bernie_synthetic_noise/candidates_sol_recovery.jsonl`
- Count: 192 candidates from 96 seeds
- File payload hash: `sha256:e4993ee85b2ad4c76f8a5db155364759f3b41fbafbf564816bc6e1594323df30`
- Canonical candidate-record hash: `sha256:a7d2292adb4aca76c86fcdd019dc44d1708d9723a9b282db181327af889039bf`
- Provenance/adjudication: `silver/pending`
- Protected holdout access: false
- Historical diary access: false
- External corpus access: false
- Live provider/runtime access: false

## Verification

```text
central candidate validator: pass, 192/192
pytest tests/test_bernie_synthetic_noise_corpus.py
       tests/test_bernie_synthetic_noise_sol_recovery.py: 10 passed
```

This is a recovered candidate set, not admission, Gold evidence,
certification, or a real-world representativeness claim. Fresh DeepSeek and
Gemini contexts must independently review this exact frozen set before Sol
can make an admission or quarantine decision.

DECISION: pending_independent_review
PROTECTED_ACCESS: false
EXTERNAL_CORPUS_ACCESS: false
