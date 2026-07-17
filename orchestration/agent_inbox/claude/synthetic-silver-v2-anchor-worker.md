# Synthetic Silver V2 Anchor Worker Report

**Date:** 2026-07-17
**Worker:** DeepSeek V4 Flash (via Claude Code --bare)
**Worktree:** `C:\Users\sarashera\EMR4-worktrees\synthetic-silver-v2-anchor-worker`
**Branch:** `codex/worker-synthetic-silver-v2-anchors`
**Source Head:** `1be60774`

## Implementation Summary

Created four owned files implementing the dialogue-free v2 anchor builder,
fail-closed coherence validator, deterministic fixture writer/checker, and
focused tests for the Synthetic Silver V2 anchor contract.

### Owned Files Created

1. **`app/services/bernie/synthetic_noise_v2.py`** — Core v2 module
   - Schema constants: `SEED_SCHEMA_VERSION_V2`,
     `SEED_MANIFEST_SCHEMA_VERSION_V2`
   - `ANCHOR_COUNT_V2 = 96`, `ACTIONS_V2` (6), `FORMS_V2` (8)
   - `_canonical_json`, `_sha256` deterministic helpers
   - `_select_anchor_sources`: Selects 2 source scenarios per action/form
     cell from `DevelopmentOnlyLoader().load_all()` by sorting variants
     deterministically by `scenario_id`
   - `_build_semantic_contract`: Builds complete dialogue-free semantic
     contract with outcome/tools/deltas derived per v2 coherence model.
     Sources entity, temporal, and diary semantics from the source
     scenario.
   - `_build_dialogue_form_contract`: Form-specific contract with required
     evidence keys, authority-all-false object, source bindings, cell
     variant, and seed hash.
   - `_build_anchor`: Assembles complete anchor with seed_hash computed
     over all fields.
   - `build_v2_anchor_manifest`, `write_v2_anchor_manifest`: Build/write
     the 96-anchor JSON manifest.
   - `validate_v2_anchor_manifest`: Full coherence validator checking all
     10 invariant classes.
   - `check_v2_anchor_manifest`: Read and validate committed fixture.
   - Manifest access flags: `contains_source_utterances=false`,
     `protected_holdout_access=false`, `historical_diary_access=false`,
     `external_corpus_access=false`

2. **`scripts/bernie_synthetic_silver_v2_anchors.py`** — CLI entry point
   - `--write`: Builds and writes fixture
   - `--check`: Reads and validates fixture

3. **`tests/test_bernie_synthetic_silver_v2_anchors.py`** — 38 focused
   tests covering structure, determinism, balance, coherence invariants,
   contradiction-class rejection, and import isolation.

4. **`tests/fixtures/bernie_synthetic_noise/semantic_seeds_v2.json`** —
   Committed 96-anchor fixture file.

### Coherence Construction

- **Standard successful mutation**: action-specific tool sequence, non-null
  outcome, non-empty appointment/audit deltas.
- **Schedule explanation**: `schedule_explained` outcome, no deltas.
- **Clarification**: Cell variant 1 = patient ambiguity; variant 2 =
  practitioner ambiguity. `request_clarification` tool,
  `clarification_required` outcome, empty deltas, `action_withdrawn=false`.
- **Reversal**: `action_withdrawn=true`, null outcome, empty deltas, tools
  = `["search_patients"]` when patient exact else `[]`.
- **Correction**: Non-null tools and outcome, retains successful action.
- **Ellipsis/anaphora/repeated_request/session_restart**: Non-null tools,
  outcome, and deltas.

### Coherence Validator Rejection Classes

The validator independently rejects null outcome, empty clarification
choices, wrong clarification tool, clarification with deltas, reversal with
outcome, reversal with deltas, reversal with wrong tools, schedule with
deltas, wrong action_withdrawn, hash mismatch, authority grant, and
utterance leakage.

### Fixture Hashes

Manifest hash: sha256:15e1b549aea16f02cb20805815518a3b13c2aaba3f22899944fc89d0cdc3cbdf

## Verification

All three invocation commands pass cleanly: 96 anchors written, fixture
check passes, 45 tests pass (38 v2 + 7 v1), git diff --check clean.

## Protected Access

No protected holdout, historical diary, appointment-call corpus, or external
corpus accessed. Only `DevelopmentOnlyLoader().load_all()`. All authority
grants false. Access flags false.

---

```
DECISION: candidate_ready
SOURCE_HEAD: 1be60774
ANCHORS: 96/96
ACTION_BALANCE: create=16, move=16, resize=16, cancel=16, status_change=16, explain_schedule=16
FORM_BALANCE: one_shot=12, clarification=12, correction=12, reversal=12, ellipsis=12, anaphora=12, repeated_request=12, session_restart=12
COHERENCE_ERRORS: 0
TESTS: 45/45
PROTECTED_ACCESS: false
```
