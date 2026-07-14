# LC4 DW1 — Development Scale Corpus Completion (Revised)

## Changed files

| File | Description |
|---|---|
| `app/services/bernie/scale_corpus.py` | Provider-free generic LC4 scale-corpus framework (models, loaders, generation APIs, validation, partition/holdout interfaces) — v2 schema with variant-payload hashing |
| `tests/fixtures/bernie_lc4_development/` | 96 development group fixture files (96 JSON + manifest) — 9+3=12 per group |
| `tests/test_bernie_lc4_scale_corpus.py` | 61+ focused tests covering all contract requirements including negative tests |
| `scripts/bernie_lc4_development_report.py` | Reproducible deterministic coverage report with `--check` flag |
| `scripts/generate_lc4_development_fixtures.py` | Deterministic fixture regeneration script |
| `docs/bernie-lc4-scale-corpus.md` | Framework and corpus documentation |
| `docs/bernie-lc4-development-report.json` | Generated deterministic coverage report |
| `orchestration/agent_inbox/codex/lc4-dw1-scale-corpus-completion.md` | This completion artifact |

## Exact generated counts

| Metric | Value |
|---|---|
| Development groups | 96 |
| Surface variants per group | 9 |
| Multi-turn trajectories per group | 3 |
| **Total variants per group** | **12** |
| Total surface variants | 864 |
| Total multi-turn trajectories | 288 |
| **Total individual scenario records** | **1,152** |
| Minimal gap-priority groups | 58 (actual: 92) |
| Gap target coverage | clarification (12), interval/unspecified temporal (30), entity ambiguity (48), tool selection (84) |
| Corpus hash | `sha256:...` (computed at generation time) |

## Dimension coverage

| Dimension | Values | Coverage |
|---|---|---|
| **Action** | create, move, resize, cancel, status_change, explain_schedule | 16 groups each |
| **Temporal relation** | exact, not_before, not_after, interval, approximate, unspecified | 18/18/18/18/12/12 groups |
| **Diary state** | all 11 states | All ≥8 groups each |
| **Entity semantics** | all 6 states | All 16 groups each |
| **Dialogue form** | all 8 forms | All 12 groups each |
| **Language form** | all 8 forms | All 12 groups each |
| **Provenance** | all silver/pending | 1,152/1,152 |
| **No write authority** | generator identity | enforced |

## Tests

61+ tests across 17 test classes:

| Class | Tests | Coverage |
|---|---|---|
| `TestExactCounts` | 8 | 96 groups, 9+3=12 variants/group, 864+288=1,152 totals |
| `TestModelValidation` | 4 | Every variant validates through model |
| `TestStableHashes` | 5 | Variant-payload hashes, deterministic and stable |
| `TestSemanticInvariance` | 5 | Action/temporal/diary-state/provenance/entity invariance |
| `TestUniqueIDs` | 3 | No duplicate variant/group/scenario IDs |
| `TestDimensionCoverage` | 8 | All dimensions, min 12 per action/temporal |
| `TestGapPriority` | 3 | ≥58 gap-priority, all 4 target categories used |
| `TestShuffleStability` | 2 | Deterministic load order, stable hash |
| `TestFailClosed` | 6 | Duplicate/missing/tampered/holdout/cross-group rejection |
| `TestProvenance` | 3 | Silver/pending/no-authority |
| `TestImportIsolation` | 2 | No prohibited imports |
| `TestPartitionSchema` | 4 | Dummy partition/holdout capability |
| `TestValidateCorpus` | 2 | Integrity detection |
| `TestSourceSpanIntegrity` | 1 | All source spans match utterance text |
| `TestTemporalConsistency` | 3 | Exact/not_before/interval constraints |
| `TestMeaningfulWording` | 2 | Distinct utterances, entity presence agrees with semantics |
| `TestNegativeRejectedDefects` | 8 | Negative tests for surface+MT>12, tampering, stale hash, semantic drift, evidence coords, dup IDs, unreferenced files, non-mutating check |

## Resolved limitations

The following limitations from the original were corrected in this revision:

1. **Count semantics**: Changed from 12 surface + 3 MT = 15/group to 9 surface + 3 MT = 12/group. Total records = 1,152 (not 1,440).

2. **Hash coverage**: Group hashes now chain from the complete canonical group spec AND every variant's content-addressable hash. Loader verifies all variant/group/corpus hashes on load. A changed utterance, label, value, span, ID, or semantic field changes the hash and fails loading.

3. **Entity-utterance agreement**: Utterance generation respects entity semantics — omitted entities are replaced with generic references, ambiguous entities use vague references. Tests assert entity presence/absence matches declared field-level semantics. No test requires a named entity in an omitted-entity variant.

4. **Semantic invariance**: `validate_variant` now cross-validates each variant against its group spec (action, temporal, diary state) when provided. All variants are checked for field-level entity semantics, normalized values, expected outcome/tools/deltas, tier/adjudication.

5. **Evidence coverage**: All source spans are verified against actual utterance text. Multi-turn variants preserve all uncorrected normalized values and place spans on actual turn coordinates.

6. **`--check` flag**: Report script now has explicit `--check` mode that computes in memory, compares exact bytes, fails on drift, and does NOT write. Default (no flag) writes the report.

## Boundaries preserved

- No provider SDK, adapter, live prompt, or external call
- No route, GraphQL, OpenAPI, database model, migration, or write gate
- No historical-diary/H-series/H15 access
- No external dataset download or licence acceptance
- T3.1-T3.4, interpretation/live-provider gates remain intact
- No candidate promotion or self-certification (all Silver/pending)
- No modification to LC3 interpretation/replay scoring, routes, APIs, DB, UI, providers, T3.1-T3.4, historical data, H-series/H15, memory/RAG, gates, or write/confirmation authority
- No protected master, push, or integration access
- No real holdout fixtures, IDs, labels, or manifests created

## Candidate commit

`candidate_commit: resolved_by_receipt`
