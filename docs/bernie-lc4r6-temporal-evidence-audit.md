# LC4R6 Temporal Source-Evidence Audit

**Date:** 2026-07-14  
**Role:** DeepSeek V4 Flash/high implementation/test worker (bounded report)  
**Conductor/acceptance:** GPT Sol  
**Independent review:** Gemini 3.5 Flash (pending)

## Summary

This audit classifies the 159 development scenarios that are both
`aligned_failure` (by the ordinary development candidate-quality firewall) and
fail the composed `temporal_relation` semantic field.  The frozen selection
hash is `f56b4a20aad6161c`.

Each scenario is classified into exactly one bucket by deriving the surface
temporal relation via the existing oracle-free temporal extractor
(`_extract_temporal` from `app.services.bernie.semantic_extraction`) over
every dialogue turn and retaining the last non-`unspecified` relation.

## Taxonomy

| Bucket | Count | Hash |
|---|---|---|
| insufficient surface evidence | 84 | `c341652065504d17` |
| surface/contract conflict | 75 | `fd04b9c86a54fea4` |
| parser gap | 0 | `e3b0c44298fc1c14` |

## Insufficient surface evidence — subtypes by expected relation

| Expected relation | Count |
|---|---|
| exact | 18 |
| not-before | 18 |
| not-after | 18 |
| interval | 18 |
| approximate | 12 |
| **Total** | **84** |

## Surface/contract conflict — expected/observed pairs

| Expected → Observed | Count |
|---|---|
| approximate → exact | 10 |
| exact → approximate | 2 |
| interval → approximate | 3 |
| interval → exact | 14 |
| not-after → approximate | 2 |
| not-after → exact | 16 |
| not-before → approximate | 3 |
| not-before → exact | 14 |
| unspecified → approximate | 2 |
| unspecified → exact | 9 |
| **Total** | **75** |

## Baselines

### Pre-LC4R5 baseline (historical — before LC4R5 action/classification repairs)

| Dimension | Value |
|---|---|
| intended action | 880 |
| action semantics | 730 |
| temporal relation | 628 |
| normalized values | 101 |
| entity semantics | 300 |
| clarification | 698 |
| safety | 1152 |

### LC4R5 baseline (authoritative current)

| Dimension | Value |
|---|---|
| intended action | 880/1152 |
| action semantics | 814/1152 |
| temporal relation | 628/1152 |
| normalized values | 101/1152 |
| entity semantics | 300/1152 |
| clarification | 782/1152 |
| safety | 1152/1152 (zero variance over 2304 samples) |

## Diagnostic note

The parser-gap bucket is empty (0 scenarios).  This means there is no scenario
where the surface dialogue evidence supports the contract relation AND the
interpreter observation disagrees.  All 159 temporal aligned failures fall
into either:

- **Insufficient surface evidence (84):** the contract expects a specific
  temporal relation (`exact`, `not_before`, `not_after`, `interval`,
  `approximate`), but the dialogue turns collectively contain no extractable
  point, bound, or interval relation.  No parser remediation can fix these —
  the evidence is not in the surface text.

- **Surface/contract conflict (75):** the dialogue has an explicit temporal
  relation, but it disagrees with the contract label.  These are labelling
  conflicts between the authored Silver surface and the contract specification,
  not parser errors.  Remediation requires contract reconciliation, not parser
  changes.

Because the parser-gap set is empty, there is no parser-remediation subset to
authorize.  LC4R6 is purely diagnostic.

## Files

- `scripts/bernie_lc4r6_temporal_evidence_report.py` — report helper with
  `--check`
- `tests/test_bernie_lc4r6_temporal_evidence_report.py` — focused tests
- `docs/bernie-lc4r6-temporal-evidence-report.json` — committed JSON report
- `docs/bernie-lc4r6-temporal-evidence-audit.md` — this note
- `orchestration/agent_inbox/codex/lc4r6-dw1-completion.md` — completion
  artifact

## Boundaries

- Ordinary LC4 development partition only (Silver/pending)
- No protected holdout v1 accessed, enumerated, or evaluated
- No provider calls, routes, API, database, UI, deployment, or write authority
- No fixture or generator modifications
- No source-span field names treated as interpreter truth
- `check_in` preserved as planned-not-implemented
- T3.1-T3.4 intact; T3.5 providers and all live/write authority deferred
