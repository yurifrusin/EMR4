# LC4 DW1 — Development Scale Corpus

## Purpose

DW1 builds a provider-free generic LC4 scale-corpus framework and exactly 96
development semantic groups (1,152 surface variants + 288 multi-turn trajectories)
targeting the LC3 measured gaps: clarification dialogue, interval/unspecified
temporal relations, entity ambiguity/omission/correction, and interpretation/replay
tool selection.

All development evidence is DeepSeek-generated Silver/pending with complete
deterministic provenance.  It must never be promoted or counted as adjudicated
coverage.

## Module

`app/services/bernie/scale_corpus.py`

### Framework models

| Model | Purpose |
|---|---|
| `DevelopmentGroupSpec` | Compact semantic specification for one group |
| `ScaleDevelopmentGroup` | Expanded group with 12 + 3 validated variants |
| `ScaleCorpus` | Collection of exactly 96 development groups |
| `PartitionSlot` / `PartitionSchema` | Generic partition interface (test only with dummy records) |
| `SealedHoldoutCapability` | Generic sealed-holdout capability (no real holdout) |

### Loader

`DevelopmentOnlyLoader` loads development fixtures from
`tests/fixtures/bernie_lc4_development/`.  It rejects holdout fixture paths.

- `load_all()` — loads all 96 groups via the manifest
- `load_group(path)` — loads a single group JSON file
- `reject_holdout_path(path)` — asserts path is not a holdout path

### Generator

`generate_development_fixture(output_dir)` — deterministic generator that
produces all 96 fixture files from the 96 group spec definitions.

### Validation helpers

- `validate_corpus(corpus)` — full integrity / coverage check
- `validate_variant(scenario)` — per-variant consistency check
- `validate_scale_corpus_isolation()` — import isolation guard

## Fixtures

`tests/fixtures/bernie_lc4_development/`

- `lc4_development_manifest.json` — manifest with corpus hash, group index
- `lc4_dw1_dev_group_001.json` … `lc4_dw1_dev_group_096.json` — group files

### Group distribution

| Dimension | Values | Coverage |
|---|---|---|
| **Action** | create, move, resize, cancel, status_change, explain_schedule | 16 groups each (96 total) |
| **Temporal** | exact, not_before, not_after, interval, approximate, unspecified | 18/18/18/18/12/12 groups |
| **Diary state** | 11 states | All covered |
| **Entity semantics** | 6 states | All covered |
| **Dialogue form** | 8 forms | All covered |
| **Language form** | 8 forms | All covered |

### Gap priority

At least 58 of 96 groups target LC3 weaknesses.  Current generation produces
92 gap-priority groups across four target categories.

## Tests

`tests/test_bernie_lc4_scale_corpus.py`

| Class | Coverage |
|---|---|
| `TestExactCounts` | 96 groups, 12 variants/group, 3 MT/group, total 1,152 + 288 |
| `TestModelValidation` | Every variant validates through model |
| `TestStableHashes` | Hashes are deterministic and stable |
| `TestSemanticInvariance` | All variants share group core semantics |
| `TestUniqueIDs` | No duplicate variant or group IDs |
| `TestDimensionCoverage` | All dimensions covered, min 12 per action/temporal |
| `TestGapPriority` | ≥58 gap-priority groups |
| `TestShuffleStability` | Deterministic load order |
| `TestFailClosed` | Duplicate/missing/tampered/cross-partition |
| `TestProvenance` | Silver/pending/no-authority |
| `TestImportIsolation` | No prohibited imports |
| `TestPartitionSchema` | Dummy partition/ holdout capability |
| `TestValidateCorpus` | validate_corpus integrity checks |
| `TestSourceSpanIntegrity` | Source spans match utterance text |
| `TestTemporalConsistency` | Temporal relation constraints satisfied |
| `TestMeaningfulWording` | Variants have distinct meaningful utterances |

## Scripts

- `scripts/bernie_lc4_development_report.py` — generates deterministic report
  at `docs/bernie-lc4-development-report.json`
- `scripts/generate_lc4_development_fixtures.py` — regenerates all fixture
  files deterministically (reproducible)

## Boundaries

- No provider SDK, adapter, live prompt, or external call
- No route, GraphQL, OpenAPI, database model, migration, or write gate
- No historical-diary/H-series/H15 access
- No external dataset download or licence acceptance
- No holdout fixtures, IDs, labels, or manifests
- T3.1-T3.4, interpretation/live-provider gates remain intact
- No candidate promotion or self-certification
- All evidence is Silver/pending discovery evidence only

## Usage

```python
from app.services.bernie.scale_corpus import DevelopmentOnlyLoader

loader = DevelopmentOnlyLoader()
corpus = loader.load_all()
print(f"Loaded {len(corpus.groups)} development groups")
print(f"Gap-priority groups: {corpus.gap_priority_group_count}")

# Validate
from app.services.bernie.scale_corpus import validate_corpus
errors = validate_corpus(corpus)
if errors:
    print("Validation errors:", errors)
```
