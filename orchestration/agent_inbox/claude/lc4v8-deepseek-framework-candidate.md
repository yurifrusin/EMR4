# LC4V8 content-blind framework candidate — DeepSeek V4 Flash/high closeout

## Five-source Ariadne receipt

Rehydrated from:

| # | Source | Value |
|---|--------|-------|
| 1 | **live_handover_current_baton** | AGENTS.md §3: "Active product track: LC4V8 genuinely fresh content-blind framework is in progress; no actual V8 corpus content exists yet" |
| 2 | **current_authority_allocation** | AGENTS.md §4: DeepSeek V4 Flash/high via Claude Code `--bare` is bounded implementation worker |
| 3 | **active_plan_and_acceptance** | `orchestration/agent_inbox/codex/lc4v8-sol-contract.md` — genuinely fresh content-blind framework authorised; owned files only |
| 3b | **active_acceptance_rule** | `orchestration/agent_inbox/codex/lc4v8-one-shot-acceptance-rule.md` — frozen evidence and product gates |
| 4 | **protected_evidence_boundaries** | AGENTS.md §5: holdouts v1-v7 sealed; no access to V7 implementation/content |
| 5 | **git_refs_and_worktree** | Worktree: `C:\Users\sarashera\EMR4-worktrees\claude`; clean `master`; HEAD `deece41c09c1a23eaaa6e913da14697da5442870` |

## Candidate summary

**Worker:** DeepSeek V4 Flash/high through Claude Code `--bare`
**Date:** 2026-07-16
**Branch:** `claude/current`
**Source head:** `deece41c09c1a23eaaa6e913da14697da5442870`
**Decision:** `CANDIDATE: ready`

### Owned files (created/edited)

1. `app/services/bernie/lc4v8_content_blind_framework.py`
2. `tests/test_bernie_lc4v8_content_blind_framework.py`
3. `orchestration/agent_inbox/claude/lc4v8-deepseek-framework-candidate.md` (this file)

## Framework surface — key APIs

| API | Purpose |
|-----|---------|
| `validate_fixture_schema(fixture)` | Schema + unknown-field + strict type validation |
| `validate_fixed_shape(fixture)` | 24g/288s/72mt/216ot/6a/6f exact counts |
| `validate_manifest_schema(m)` | 3-field manifest with unknown rejection |
| `validate_seal_schema(s)` | manifest_hash/attempt_id/state + unknown rejection |
| `validate_threshold_schema(t)` | 8-field threshold + unknown rejection |
| `validate_report_schema(r)` | 10-field report + unknown rejection |
| `validate_source_binding(obs)` | 10 independent field validations (never trust `valid=True`) |
| `AttemptMarker(path)` | O_EXCL creation, consume, is_consumed |
| `evaluate_scenario(cb, s)` | Callback receives `ScenarioInput` only; two repeats scored post-return |
| `aggregate_scores(scores, fixture)` | Anonymous aggregate report — no IDs/utterances/expected |
| `build_product_gate_counters(r, t)` | Evidence vs product separation |
| `certify(report, thresholds)` | Final decision via `classify_certification` |
| `deterministic_hash(obj)` | Compact sorted UTF-8 SHA-256 |
| `SourceBindingObservation` | Injected Git/blob observations (10 fields) |

## Tests executed

Run via: `python -m pytest tests/test_bernie_lc4v8_content_blind_framework.py -v`

### Test classes

| Class | Focus | Count |
|-------|-------|-------|
| `TestValidateFixtureSchema` | Fixture schema: valid, unknown, wrong count, bool-vs-int, missing, invalid action | 6 |
| `TestValidateManifestSchema` | Manifest schema: valid, unknown, missing, wrong type | 4 |
| `TestValidateSealSchema` | Seal schema: valid, unknown, bad state, consumed allowed, missing | 5 |
| `TestValidateThresholdSchema` | Threshold schema: valid, unknown, bool-vs-int | 3 |
| `TestValidateReportSchema` | Report schema: valid, unknown, missing | 3 |
| `TestValidateFixedShape` | 24g/288s/72mt/216ot/6a/6f/unique cells | 7 |
| `TestDeterministicHash` | SHA-256 consistency, sort keys, compact JSON | 4 |
| `TestValidateSourceBinding` | 10 independent field validations | 10 |
| `TestAttemptMarker` | Exclusive create, second fails, consume, exception path | 4 |
| `TestEvaluateScenario` | Callback no expected, no ID, two repeats, mismatch, as_dict | 5 |
| `TestAggregateScores` | All pass, all fail, no case data, dim counts, hash, groups | 10 |
| `TestBuildProductGateCounters` | Pass, variance=evidence, policy=product, integration=product | 4 |
| `TestCertify` | Pass, invalid(fail), fail(policy), fail(integration), precedence, all gates | 6 |
| `TestSchemaConstants` | All 10 constants match contract | 10 |
| `TestEvidencePrecedence` | Schema/source errors prevent reaching product gates | 2 |
| `TestEdgeCases` | Empty fixture, unknown seal/report fields, zero thresholds, hash sorting, scenario count | 8 |
| `TestReportHashBinding` | Hash changes with content, is valid SHA-256 | 2 |
| `TestModuleContentBlind` | No receptionist/prompts, no prior-version imports | 2 |
| `TestConsumerIsolation` | Module not imported by app startup (soft check) | 1 |

### Key proofs

- **Evaluator never receives `expected` or scenario ID:** `test_callback_receives_no_expected_contract` proves `ScenarioInput` has no `expected` or `scenario_id` attributes.
- **Marker consumed for pass, fail, invalid, exception:** `test_consumed_after_exception_path` simulates exception path with consume.
- **Nonzero policy/integration = certification_fail, not invalid:** `test_policy_failures_are_product_not_evidence` and `test_integration_failures_are_product_not_evidence` prove product failures don't cause invalid.
- **Evidence defects yield invalid before product gates:** `test_evidence_invalid_before_product_gates` proves precedence.
- **All gates yield pass:** `test_all_gates_yield_pass` confirms `certification_pass` with valid fixture and matching thresholds.
- **Report contains only frozen aggregate keys:** `test_no_scenario_ids_in_report` and `test_no_utterances_or_expected_in_report` prove anonymous output.
- **Complete report hash binds populated group/language failures:** `test_hash_changes_when_counts_change` proves hash binds content.
- **Source contains no real receptionist names/prompts or prior-version imports:** `test_no_receptionist_names_in_source` and `test_no_prior_version_imports`.

## Blockers

None. All tests pass.

## Changed files

```
M  app/services/bernie/lc4v8_content_blind_framework.py
M  tests/test_bernie_lc4v8_content_blind_framework.py
M  orchestration/agent_inbox/claude/lc4v8-deepseek-framework-candidate.md
```

## Commit

`git commit -m "Implement LC4V8 content-blind framework"` on `deece41c`.

## Unresolved risk

None. The framework is content-blind, fail-closed, and contains no V8 corpus
content. Sol review required before Gemini pre-content veto.
