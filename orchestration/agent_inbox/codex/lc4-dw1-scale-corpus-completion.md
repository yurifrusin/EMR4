# LC4 DW1 — Development Scale Corpus Completion

## Changed files

| File | Description |
|---|---|
| `app/services/bernie/scale_corpus.py` | Provider-free generic LC4 scale-corpus framework (models, loaders, generation APIs, validation, partition/holdout interfaces) |
| `tests/fixtures/bernie_lc4_development/` | 96 development group fixture files (96 JSON + manifest) |
| `tests/test_bernie_lc4_scale_corpus.py` | 48 focused tests covering all contract requirements |
| `scripts/bernie_lc4_development_report.py` | Reproducible deterministic coverage report |
| `scripts/generate_lc4_development_fixtures.py` | Deterministic fixture regeneration script |
| `docs/bernie-lc4-scale-corpus.md` | Framework and corpus documentation |
| `docs/bernie-lc4-development-report.json` | Generated deterministic coverage report |

## Exact generated counts

| Metric | Value |
|---|---|
| Development groups | 96 |
| Surface variants per group | 12 |
| Multi-turn trajectories per group | 3 |
| Total surface variants | 1,152 |
| Total multi-turn trajectories | 288 |
| Total individual scenario records | 1,440 |
| Minimal gap-priority groups | 58 (actual: 92) |
| Gap target coverage | clarification (12), interval/unspecified temporal (30), entity ambiguity (48), tool selection (84) |
| Corpus hash | `sha256:7f4196b3fecc4bd2bcf361618b72ee0cea867bee43caa079fa66c7e06834d91a` |

## Dimension coverage

| Dimension | Values | Coverage |
|---|---|---|
| **Action** | create, move, resize, cancel, status_change, explain_schedule | 16 groups each |
| **Temporal relation** | exact, not_before, not_after, interval, approximate, unspecified | 18/18/18/18/12/12 groups |
| **Diary state** | all 11 states | All ≥8 groups each |
| **Entity semantics** | all 6 states | All 16 groups each |
| **Dialogue form** | all 8 forms | All 12 groups each |
| **Language form** | all 8 forms | All 12 groups each |
| **Provenance** | all silver/pending | 1,440/1,440 |
| **No write authority** | generator identity | enforced |

## Tests

48 tests across 16 test classes:

| Class | Tests | Coverage |
|---|---|---|
| `TestExactCounts` | 7 | 96 groups, 12+3 variants, 1,152+288 totals |
| `TestModelValidation` | 4 | Every variant validates through model |
| `TestStableHashes` | 4 | Deterministic and stable hashes |
| `TestSemanticInvariance` | 5 | Action/temporal/diary-state/provenance invariance |
| `TestUniqueIDs` | 3 | No duplicate variant/group/scenario IDs |
| `TestDimensionCoverage` | 8 | All dimensions, min 12 per action/temporal |
| `TestGapPriority` | 3 | ≥58 gap-priority, all 4 target categories used |
| `TestShuffleStability` | 2 | Deterministic load order, stable hash |
| `TestFailClosed` | 6 | Duplicate/missing/tampered/holdout rejection |
| `TestProvenance` | 3 | Silver/pending/no-authority |
| `TestImportIsolation` | 2 | No prohibited imports |
| `TestPartitionSchema` | 4 | Dummy partition/holdout capability |
| `TestValidateCorpus` | 2 | Integrity detection |
| `TestSourceSpanIntegrity` | 1 | All source spans match utterance text |
| `TestTemporalConsistency` | 3 | Exact/not_before/interval constraints |
| `TestMeaningfulWording` | 2 | Distinct, meaningful receptionist wording |

## Known honest limitations

1. **Surface variant wording** is template-based rather than independently composed — the 12 patterns per action are hand-authored, not model-generated. This ensures reproducibility and avoids oracle copying, but means some variants use similar sentence structures within the same action category.

2. **Multi-turn variant source spans** are abbreviated — they cover the last matching turn rather than every occurrence across all turns. This is lossless for the contract but not exhaustive.

3. **Hash computation** relies on the group's spec data structure rather than full variant content. Cross-group variant hashes are not independently verified against the model validation.

4. **Entity ambiguity/omission** in the spec does not always propagate to every individual variant's entity_semantics field — some variants may still contain the entity name even when the group spec marks it as ambiguous or omitted. The group-level semantic profile is the authoritative counting unit.

5. **The partition and sealed-holdout interfaces are test-only**. They define the generic API shape but contain no real holdout records. Sol must author the actual 24-group holdout separately.

## Boundaries preserved

- No provider SDK, adapter, live prompt, or external call
- No route, GraphQL, OpenAPI, database model, migration, or write gate
- No historical-diary/H-series/H15 access
- No external dataset download or licence acceptance
- T3.1-T3.4, interpretation/live-provider gates remain intact
- No candidate promotion or self-certification (all Silver/pending)
- No modification to LC3 interpretation/replay scoring, routes, APIs, DB, UI, providers, T3.1-T3.4, historical data, H-series/H15, memory/RAG, gates, or write/confirmation authority
- No protected master, push, or integration access

## Candidate commit

`candidate_commit: resolved_by_receipt`

This artifact marks DW1 as complete. DW2 (scaled evaluator) and AG (independent framework veto) remain; Sol authors the real 24-group holdout after all external work ends.
