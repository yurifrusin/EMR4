# S10 W2 Adversarial Workflow Chain Review

**Role:** independent adversarial review (DeepSeek Flash W2)
**Date:** 2026-07-13
**Reviewed commit:** `71f3b0d7` (W1 staging base)
**Artifact:** `orchestration/agent_inbox/codex/review-deepseek-s10-w2-workflow-chain-adversarial.md`

## Summary

The W1 test-only workflow chain harness (`tests/workflow_chain/harness.py`) was reviewed for:
- Context-propagation leakage between steps and chains
- Frame coherence across multi-step chains
- Refusal propagation semantics
- Memory-context boundary concerns
- Report safety boundary (utterance/payload leakage)
- Test-only isolation and runtime boundary preservation

**Decision: PASS** with 2 medium and 2 low findings.

## Adversarial Test Coverage

23 focused adversarial tests in `tests/test_bernie_workflow_chain_adversarial.py`:

| Category | Tests | What it challenges |
|---|---|---|
| Fixture integrity | 3 | Schema, payload-free, loading |
| Context propagation | 3 | Copy isolation, descriptor defaults, guard checks |
| Refusal propagation | 2 | First-refusal-wins masking, poisoned verb accumulation |
| Frame coherence | 4 | Consistency, writes_authorized, handoff frames, empty utterances |
| Report safety | 2 | Aggregate safety, boundary posture |
| Cross-boundary | 3 | No forbidden imports, no route/API/database references, W1 ownership non-overlap |

7 adversarial chain fixtures across 3 files in `tests/fixtures/bernie_workflow_chain_review/`:
- `refusal_stacking_chain.json` (2 chains): unknown+planned stacking, planed+unsafe reverse stacking
- `context_descriptor_risk.json` (2 chains): clarification defaults, unsafe refusal defaults
- `coherence_and_leakage_risk.json` (3 chains): handoff meta, empty utterance, planed+resolved mix

## Adversarial Findings

### M1: Unconditional Practitioner/Time-Window Descriptor Defaulting

The harness defaults `resolved_practitioner_descriptor` and `time_window_descriptor` unconditionally on every interpreted step via `or`-assignment. Only `resolved_patient_descriptor` checks the dispatch type. This creates an asymmetry where synthetic practitioner and time-window values appear in context even after purely clarification or refusal-only steps.

**Test evidence:** `test_context_resolution_defaults_after_clarification` — a clarification-only chain produces `resolved_patient_descriptor=None` but `resolved_practitioner_descriptor="synthetic_practitioner"` and `time_window_descriptor="synthetic_time_window"`.

### M2: First-Refusal-Wins Masks More Restrictive Later Refusals

When a chain step produces a refusal, all subsequent steps are short-circuited with the same refusal type, never evaluated independently. This means a step that would produce `refused_unsafe` (order 4) gets classified as `refused_planned` (order 3) if a planed refusal happened first. The chain classification then under-reports the most restrictive possible outcome.

**Test evidence:** `test_first_refusal_type_propagates_subsequent_poisoned` — step 2 is `refused_unknown`, step 3 (check-in, would be `refused_planned`) gets short-circuited to `refused_unknown`.

### L1: Fixture Labels Contain Descriptive Text

Fixture labels describe workflow intents (e.g., "Adversarial: unsafe instruction in step 2 → refusal propagated"). These are safe because `build_chain_report` never includes labels in aggregate output.

### L2: Meta/Handoff Produces Refusal Frame-kind

`route_meta` (handoff) produces `frame_kind="refusal"` with `refusal_reason_kind="meta_handoff"`. This is correct per harness design but means downstream code must use `interpretation_dispatch` to distinguish handoff from true refusals.

## Boundary Verification

| Check | Result |
|---|---|
| `app/services/` edits | None |
| `tests/test_bernie_interpretation_runtime_isolation.py` edits | None |
| `app/config.py` edits | None |
| W1 fixture overlap | None (distinct directory) |
| W1 harness module edits | None |
| Routes/provider/DB/trove/memory | Not touched |

## Baseline Comparison

Runtime isolation guard shows exactly 1 failure (documented `app/config.py` baseline at `b05ee20a`). Zero new failures. Guard unchanged.

## Verification Run Results

| Test suite | Count | Result |
|---|---|---|
| W2 focused adversarial | 23 | All passed |
| W1 + W2 combined | 82 | All passed |
| Interpretation harness | 218 | All passed |
| Readiness check | 9 | All passed |
| Runtime isolation | 3 | 1 expected failure (baseline) |
| Report CLI | 1 | Aggregate-only JSON, safety OK |
| Compile check | 2 modules | No errors |
| Whitespace | `git diff --check` | Clean |

## Next Steps

1. W1 may optionally address M1 (unconditional descriptor defaults) — align practitioner/time_window guarding with patient descriptor dispatch check, or document the behaviour explicitly.
2. W1 may acknowledge M2 (first-refusal masking) as intentional eager-termination.
3. Terra may integrate W2 candidate with W1 after confirming no regression in runtime isolation or existing harness tests.
4. No sprint-engine pause required.
