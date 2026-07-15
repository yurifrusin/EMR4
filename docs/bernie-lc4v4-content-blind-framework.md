# Bernie LC4V4 Content-Blind Framework

## Overview

This document describes the LC4V4 content-blind authoring quality and
certification framework. The framework is designed to be entirely independent of
actual v4 scenario content, production parsers, providers, routes, databases,
and runtime dependencies.

## Architecture

```
lc4v4_authoring_quality.py     Content-blind rendering/evidence validator
lc4v4_certification.py         Empty certification framework (manifest/seal/report)
```

## Authoring Quality Gate

The `lc4v4_authoring_quality` module provides:

### Typed Records

- **`CanonicalFactBundle`** - Canonical semantic facts for one scenario surface
- **`RenderedTurn`** - A rendered turn split into `prefix`, `core`, `suffix`
- **`AuthorityToken`** - Authority-bearing evidence token with field name,
  canonical text, case-sensitivity flag, turn index, and source coordinates
- **`ExpectedScenarioContract`** - Expected values independently derived
  through the frozen policy table
- **`AuthoringQualityReceipt`** - Aggregate receipt with no case-level leakage
- **`AuthoringQualityFinding`** - Individual validation result

### Validation Functions

| Function | Purpose |
|---|---|
| `validate_rendered_surface()` | Checks prefix+core+suffix integrity, authority tokens at coordinates, source-span matching, field contract requirements |
| `validate_entity_relation_evidence()` | Verifies exact/corrected relations have case-preserved evidence; omitted/ambiguous/negated/mismatched use relation assertions |
| `validate_expected_contract_derivation()` | Ensures expected contract matches independent policy derivation |
| `derive_expected_contract()` | Frozen policy table: derives expected outcome/tools/authority/deltas from canonical facts |

### Frozen Policy Table

The policy table independently determines expected values:

- **Outcome**: Based on `action_semantics`, `requires_clarification`,
  `action_negated`, `intended_action`, and `diary_state`
- **Authority**: `refuse` for prohibited, `clarify` for ambiguous/clarification,
  `read` otherwise
- **Tools**: Deduplicated from `selected_tool_sequence`
- **Deltas**: Generated only for mutation outcomes (created/moved/resized/etc.)

## Certification Framework

The `lc4v4_certification` module provides an empty content-blind framework:

### Fixed Constants

| Constant | Value |
|---|---|
| `LC4V4_CORPUS_IDENTITY` | `lc4-holdout-v4` |
| `LC4V4_EVALUATION_ID` | `lc4-holdout-v4-baseline-001` |
| `LC4V4_EVALUATOR_VERSION` | `lc4v4.aggregate_evaluator.v1` |
| `LC4V4_GROUP_COUNT` | 24 |
| `LC4V4_SURFACE_PER_GROUP` | 9 |
| `LC4V4_MT_PER_GROUP` | 3 |
| `LC4V4_TOTAL_SCENARIOS` | 288 |
| `LC4V4_TOTAL_TRAJECTORIES` | 72 |
| `LC4V4_REPEAT_COUNT` | 2 |
| `LC4V4_TOTAL_SAMPLES` | 576 |

### Operations

| Function | Purpose |
|---|---|
| `build_manifest()` | Scans corpus directory, validates group files, computes hashes |
| `reconstruct_manifest()` | Verifies manifest schema, counts, and hashes |
| `create_seal()` | Creates seal from verified manifest + source commit |
| `verify_seal()` | Verifies seal hash chain against manifest |
| `evaluate_aggregate()` | Runs deterministic evaluation, emits aggregate-only report |
| `check_aggregate_report()` | Post-consumption aggregate validation |
| `check_forbidden_aggregate_keys()` | Recursively checks for prohibited case-level keys |

### Hash Chain

```
Corpus files → manifest (file hashes + corpus hash)
                                    ↓
Manifest → seal (manifest hash + source commit binding)
                                    ↓
Seal → aggregate evaluation → report (report hash)
```

### Post-Consumption Validation

After consumption, only `check_aggregate_report()` may run. It accepts only the
report object (or report path), never a corpus, manifest, or seal path.

## Content-Blind Principles

1. No real v4 corpus, manifest, seal, or report is ever loaded
2. No v1, v2, or v3 fixtures, support modules, or case-level surface are
   inspected
3. No provider, route, database, UI, deployment, or runtime dependency
4. All validation is deterministic and fail-closed
5. UTF-8/LF JSON serialization with hash stability guarantees
6. Aggregate receipts recursively reject case-level leakage

## CLI Script

The `scripts/bernie_lc4v4_certification.py` script provides:

```bash
python -m scripts.bernie_lc4v4_certification --corpus-dir <path> [--manifest-only|--seal-only|--evaluate]
python -m scripts.bernie_lc4v4_certification --check-report <path>
python -m scripts.bernie_lc4v4_certification --forbidden-keys <path>
```
